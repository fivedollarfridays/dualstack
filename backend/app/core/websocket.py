"""WebSocket connection manager for real-time user-scoped events."""

from __future__ import annotations

import logging
from collections import defaultdict
from typing import Any

from fastapi import WebSocket

logger = logging.getLogger(__name__)

MAX_CONNECTIONS_PER_USER = 5


class ConnectionManager:
    """Tracks active WebSocket connections and sends user-scoped events."""

    def __init__(self) -> None:
        self._connections: dict[WebSocket, str] = {}
        self._user_connections: dict[str, set[WebSocket]] = defaultdict(set)

    @property
    def active_count(self) -> int:
        return len(self._connections)

    async def connect(self, websocket: WebSocket, user_id: str) -> bool:
        """Register a WebSocket connection. Returns False if rejected."""
        if len(self._user_connections[user_id]) >= MAX_CONNECTIONS_PER_USER:
            logger.warning("User %s exceeded max WS connections (%d)", user_id, MAX_CONNECTIONS_PER_USER)
            await websocket.close(code=4008, reason="Too many connections")
            return False
        self._connections[websocket] = user_id
        self._user_connections[user_id].add(websocket)
        return True

    def disconnect(self, websocket: WebSocket) -> None:
        user_id = self._connections.pop(websocket, None)
        if user_id and websocket in self._user_connections.get(user_id, set()):
            self._user_connections[user_id].discard(websocket)
            if not self._user_connections[user_id]:
                del self._user_connections[user_id]

    async def send_to_user(self, user_id: str, event: dict[str, Any]) -> None:
        sockets = self._user_connections.get(user_id, set())
        broken: list[WebSocket] = []
        for ws in list(sockets):
            try:
                await ws.send_json(event)
            except Exception:
                broken.append(ws)
        for ws in broken:
            self.disconnect(ws)


manager = ConnectionManager()
