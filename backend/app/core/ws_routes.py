"""WebSocket endpoint for real-time event streaming."""

import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.events import event_bus
from app.core.websocket import manager
from app.core.ws_auth import authenticate_ws

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    """Authenticated WebSocket endpoint for real-time events."""
    try:
        user_id = await authenticate_ws(websocket)
    except Exception:
        # Accept then immediately close — ASGI requires accept before close frame.
        await websocket.accept()
        await websocket.close(code=4001, reason="Authentication failed")
        return

    await websocket.accept()
    connected = await manager.connect(websocket, user_id=user_id)
    if not connected:
        return

    try:
        while True:
            # Keep connection alive; client can send pings
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
