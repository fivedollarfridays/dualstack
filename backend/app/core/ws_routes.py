"""WebSocket endpoint for real-time event streaming (first-message auth)."""

import asyncio
import json
import logging
import time
from collections import defaultdict

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.events import event_bus
from app.core.rate_limit import resolve_client_ip
from app.core.websocket import manager
from app.core.ws_auth import authenticate_ws_from_message

logger = logging.getLogger(__name__)

router = APIRouter()

AUTH_TIMEOUT = 5.0  # seconds to wait for auth message
MAX_WS_MESSAGE_SIZE = 64 * 1024  # 64 KB max post-auth message size

# IP-level WebSocket connection rate limiting.
# Safe under asyncio because this function contains no await points — it runs
# atomically within the event loop. The rate check happens after accept()
# because Starlette requires accept before close with a reason code.
_ws_connection_timestamps: dict[str, list[float]] = defaultdict(list)
_ws_rate_check_counter = 0
WS_RATE_LIMIT = 30  # max connections per IP per window
WS_RATE_WINDOW = 60.0  # seconds
_MAX_TRACKED_IPS = 10000  # cap to prevent unbounded memory growth


def _check_ws_rate_limit(client_ip: str) -> bool:
    """Return True if the connection should be allowed, False if rate-limited."""
    global _ws_rate_check_counter
    now = time.monotonic()

    # Periodic full sweep: evict expired IPs every 100 checks
    _ws_rate_check_counter += 1
    if _ws_rate_check_counter >= 100:
        _ws_rate_check_counter = 0
        expired = [
            ip
            for ip, ts in _ws_connection_timestamps.items()
            if not ts or all(now - t >= WS_RATE_WINDOW for t in ts)
        ]
        for ip in expired:
            del _ws_connection_timestamps[ip]
        # Hard cap: if still too large, drop oldest entries
        if len(_ws_connection_timestamps) > _MAX_TRACKED_IPS:
            excess = len(_ws_connection_timestamps) - _MAX_TRACKED_IPS
            for ip in list(_ws_connection_timestamps)[:excess]:
                del _ws_connection_timestamps[ip]

    timestamps = _ws_connection_timestamps[client_ip]
    _ws_connection_timestamps[client_ip] = [
        t for t in timestamps if now - t < WS_RATE_WINDOW
    ]
    if len(_ws_connection_timestamps[client_ip]) >= WS_RATE_LIMIT:
        return False
    _ws_connection_timestamps[client_ip].append(now)
    return True


async def _await_auth_message(websocket: WebSocket) -> str:
    """Wait for the first-message auth handshake and return the user_id.

    Raises on timeout, invalid message format, or authentication failure.
    """
    raw = await asyncio.wait_for(
        websocket.receive_text(), timeout=AUTH_TIMEOUT
    )
    data = json.loads(raw)
    if data.get("type") != "auth" or not data.get("token"):
        raise ValueError("Invalid auth message")
    return await authenticate_ws_from_message(data["token"])


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    """Authenticated WebSocket endpoint using first-message auth pattern."""
    await websocket.accept()

    client_ip = resolve_client_ip(
        direct_ip=websocket.client.host if websocket.client else None,
        headers=dict(websocket.headers),
    )
    if not _check_ws_rate_limit(client_ip):
        await websocket.close(code=4029, reason="Too many connections")
        return

    try:
        user_id = await _await_auth_message(websocket)
    except asyncio.TimeoutError:
        await websocket.close(code=4001, reason="Auth timeout")
        return
    except (json.JSONDecodeError, ValueError):
        await websocket.close(code=4001, reason="Invalid auth message")
        return
    except Exception:
        await websocket.close(code=4001, reason="Authentication failed")
        return

    await websocket.send_json({"type": "auth_ok"})

    connected = await manager.connect(websocket, user_id=user_id)
    if not connected:
        return

    try:
        while True:
            data = await websocket.receive_text()
            if len(data) > MAX_WS_MESSAGE_SIZE:
                await websocket.close(code=4009, reason="Message too large")
                return
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(websocket)


async def _broadcast_event(payload: dict) -> None:
    """Forward domain events to the owning user's WebSocket connections."""
    user_id = payload.get("user_id")
    if user_id:
        await manager.send_to_user(user_id, payload)
    else:
        logger.warning(
            "Event missing user_id, dropping: %s", payload.get("type", "unknown")
        )


# Subscribe to all item events and route them to the owning user
event_bus.subscribe("item.*", _broadcast_event)
