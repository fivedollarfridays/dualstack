"""WebSocket endpoint for real-time event streaming (first-message auth)."""

import asyncio
import json
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.events import event_bus
from app.core.websocket import manager
from app.core.ws_auth import authenticate_ws_from_message

logger = logging.getLogger(__name__)

router = APIRouter()

AUTH_TIMEOUT = 5.0  # seconds to wait for auth message


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
            await websocket.receive_text()
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
