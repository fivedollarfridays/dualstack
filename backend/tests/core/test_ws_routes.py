"""Tests for WebSocket first-message auth pattern in ws_routes."""

import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import WebSocket, WebSocketDisconnect

from app.core.errors import AuthenticationError


class TestWebSocketFirstMessageAuth:
    """Test the first-message auth handshake in the WS endpoint."""

    @pytest.fixture
    def mock_websocket(self):
        """Create a mock WebSocket with controllable receive_text."""
        ws = AsyncMock(spec=WebSocket)
        ws.accept = AsyncMock()
        ws.close = AsyncMock()
        ws.send_json = AsyncMock()
        ws.receive_text = AsyncMock()
        return ws

    async def test_valid_auth_message_connects(self, mock_websocket):
        """A valid auth message with JWT should complete the handshake."""
        from app.core.ws_routes import websocket_endpoint

        auth_msg = json.dumps({"type": "auth", "token": "valid-jwt"})
        # First call (via asyncio.wait_for) returns auth, second raises disconnect
        mock_websocket.receive_text = AsyncMock(
            side_effect=[auth_msg, WebSocketDisconnect()]
        )

        with patch(
            "app.core.ws_routes.authenticate_ws_from_message"
        ) as mock_auth:
            mock_auth.return_value = "user-123"

            with patch("app.core.ws_routes.manager") as mock_manager:
                mock_manager.connect = AsyncMock(return_value=True)
                mock_manager.disconnect = MagicMock()

                await websocket_endpoint(mock_websocket)

        mock_websocket.accept.assert_called_once()
        mock_auth.assert_called_once_with("valid-jwt")
        mock_websocket.send_json.assert_called_once_with({"type": "auth_ok"})
        mock_manager.connect.assert_called_once_with(
            mock_websocket, user_id="user-123"
        )

    async def test_auth_timeout_closes_connection(self, mock_websocket):
        """If no auth message arrives within timeout, close with 4001."""
        from app.core.ws_routes import websocket_endpoint

        # Simulate timeout by making receive_text hang forever
        async def hang_forever():
            await asyncio.sleep(100)

        mock_websocket.receive_text = hang_forever

        # Patch AUTH_TIMEOUT to be very small so test is fast
        with patch("app.core.ws_routes.AUTH_TIMEOUT", 0.05):
            await websocket_endpoint(mock_websocket)

        mock_websocket.accept.assert_called_once()
        mock_websocket.close.assert_called_once_with(
            code=4001, reason="Auth timeout"
        )

    async def test_invalid_auth_type_closes(self, mock_websocket):
        """A message with wrong type field should close with 4001."""
        from app.core.ws_routes import websocket_endpoint

        bad_msg = json.dumps({"type": "not_auth", "token": "jwt"})
        mock_websocket.receive_text = AsyncMock(return_value=bad_msg)

        await websocket_endpoint(mock_websocket)

        mock_websocket.close.assert_called_once_with(
            code=4001, reason="Invalid auth message"
        )

    async def test_missing_token_in_auth_message_closes(self, mock_websocket):
        """An auth message without token field should close with 4001."""
        from app.core.ws_routes import websocket_endpoint

        bad_msg = json.dumps({"type": "auth"})
        mock_websocket.receive_text = AsyncMock(return_value=bad_msg)

        await websocket_endpoint(mock_websocket)

        mock_websocket.close.assert_called_once_with(
            code=4001, reason="Invalid auth message"
        )

    async def test_auth_failure_closes(self, mock_websocket):
        """An invalid JWT should close with 4001."""
        from app.core.ws_routes import websocket_endpoint

        auth_msg = json.dumps({"type": "auth", "token": "bad-jwt"})
        mock_websocket.receive_text = AsyncMock(return_value=auth_msg)

        with patch(
            "app.core.ws_routes.authenticate_ws_from_message"
        ) as mock_auth:
            mock_auth.side_effect = AuthenticationError(
                message="Invalid or expired token"
            )

            await websocket_endpoint(mock_websocket)

        mock_websocket.close.assert_called_once_with(
            code=4001, reason="Authentication failed"
        )

    async def test_non_json_auth_message_closes(self, mock_websocket):
        """A non-JSON first message should close with 4001."""
        from app.core.ws_routes import websocket_endpoint

        mock_websocket.receive_text = AsyncMock(return_value="not json at all")

        await websocket_endpoint(mock_websocket)

        mock_websocket.close.assert_called_once_with(
            code=4001, reason="Invalid auth message"
        )

    async def test_manager_disconnect_on_close(self, mock_websocket):
        """After auth succeeds, manager.disconnect is called on WS close."""
        from app.core.ws_routes import websocket_endpoint

        auth_msg = json.dumps({"type": "auth", "token": "valid-jwt"})
        mock_websocket.receive_text = AsyncMock(
            side_effect=[auth_msg, WebSocketDisconnect()]
        )

        with patch(
            "app.core.ws_routes.authenticate_ws_from_message"
        ) as mock_auth:
            mock_auth.return_value = "user-123"

            with patch("app.core.ws_routes.manager") as mock_manager:
                mock_manager.connect = AsyncMock(return_value=True)
                mock_manager.disconnect = MagicMock()

                await websocket_endpoint(mock_websocket)

        mock_manager.disconnect.assert_called_once_with(mock_websocket)
