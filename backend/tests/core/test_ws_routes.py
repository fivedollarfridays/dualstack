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


class TestWebSocketMessageSizeLimit:
    """Test post-auth receive loop enforces message size limits."""

    @pytest.fixture
    def mock_websocket(self):
        """Create a mock WebSocket with controllable receive_text."""
        ws = AsyncMock(spec=WebSocket)
        ws.accept = AsyncMock()
        ws.close = AsyncMock()
        ws.send_json = AsyncMock()
        ws.receive_text = AsyncMock()
        return ws

    def _auth_msg(self) -> str:
        return json.dumps({"type": "auth", "token": "valid-jwt"})

    async def test_oversized_message_closes_with_4009(self, mock_websocket):
        """A message exceeding MAX_WS_MESSAGE_SIZE closes with code 4009."""
        from app.core.ws_routes import MAX_WS_MESSAGE_SIZE, websocket_endpoint

        oversized = "x" * (MAX_WS_MESSAGE_SIZE + 1)
        mock_websocket.receive_text = AsyncMock(
            side_effect=[self._auth_msg(), oversized]
        )

        with patch(
            "app.core.ws_routes.authenticate_ws_from_message"
        ) as mock_auth:
            mock_auth.return_value = "user-123"
            with patch("app.core.ws_routes.manager") as mock_manager:
                mock_manager.connect = AsyncMock(return_value=True)
                mock_manager.disconnect = MagicMock()

                await websocket_endpoint(mock_websocket)

        mock_websocket.close.assert_called_once_with(
            code=4009, reason="Message too large"
        )
        mock_manager.disconnect.assert_called_once_with(mock_websocket)

    async def test_normal_message_not_rejected(self, mock_websocket):
        """A message within size limit is accepted; loop continues."""
        from app.core.ws_routes import MAX_WS_MESSAGE_SIZE, websocket_endpoint

        normal_msg = "x" * (MAX_WS_MESSAGE_SIZE - 1)
        mock_websocket.receive_text = AsyncMock(
            side_effect=[self._auth_msg(), normal_msg, WebSocketDisconnect()]
        )

        with patch(
            "app.core.ws_routes.authenticate_ws_from_message"
        ) as mock_auth:
            mock_auth.return_value = "user-123"
            with patch("app.core.ws_routes.manager") as mock_manager:
                mock_manager.connect = AsyncMock(return_value=True)
                mock_manager.disconnect = MagicMock()

                await websocket_endpoint(mock_websocket)

        # Should NOT have been closed with 4009
        for call in mock_websocket.close.call_args_list:
            assert call != ((4009,), {"reason": "Message too large"})
        # Should have disconnected normally via WebSocketDisconnect
        mock_manager.disconnect.assert_called_once_with(mock_websocket)

    async def test_max_ws_message_size_is_64kb(self):
        """The constant MAX_WS_MESSAGE_SIZE should be 64 KB."""
        from app.core.ws_routes import MAX_WS_MESSAGE_SIZE

        assert MAX_WS_MESSAGE_SIZE == 64 * 1024


class TestWebSocketRateLimit:
    """Test IP-level connection rate limiting on WebSocket upgrades."""

    @pytest.fixture(autouse=True)
    def reset_rate_limit_state(self):
        """Reset the rate limit tracker between tests."""
        from app.core.ws_routes import _ws_connection_timestamps

        _ws_connection_timestamps.clear()
        yield
        _ws_connection_timestamps.clear()

    @pytest.fixture
    def mock_websocket(self):
        """Create a mock WebSocket with client IP."""
        ws = AsyncMock(spec=WebSocket)
        ws.accept = AsyncMock()
        ws.close = AsyncMock()
        ws.send_json = AsyncMock()
        ws.receive_text = AsyncMock()
        ws.client = MagicMock()
        ws.client.host = "10.0.0.1"
        return ws

    def test_rate_limit_allows_normal_connections(self):
        """Connections under the limit should be allowed."""
        from app.core.ws_routes import WS_RATE_LIMIT, _check_ws_rate_limit

        for i in range(WS_RATE_LIMIT):
            assert _check_ws_rate_limit("10.0.0.1") is True

    def test_rate_limit_rejects_excess_connections(self):
        """Connections exceeding the limit should be rejected."""
        from app.core.ws_routes import WS_RATE_LIMIT, _check_ws_rate_limit

        for _ in range(WS_RATE_LIMIT):
            _check_ws_rate_limit("10.0.0.1")

        assert _check_ws_rate_limit("10.0.0.1") is False

    def test_rate_limit_per_ip(self):
        """Rate limit is tracked per IP independently."""
        from app.core.ws_routes import WS_RATE_LIMIT, _check_ws_rate_limit

        for _ in range(WS_RATE_LIMIT):
            _check_ws_rate_limit("10.0.0.1")

        # Different IP should still be allowed
        assert _check_ws_rate_limit("10.0.0.2") is True

    def test_rate_limit_cleans_stale_entries(self):
        """Entries older than the window should be cleaned up."""
        import time

        from app.core.ws_routes import (
            WS_RATE_LIMIT,
            WS_RATE_WINDOW,
            _check_ws_rate_limit,
            _ws_connection_timestamps,
        )

        # Insert timestamps that are older than the window
        old_time = time.monotonic() - WS_RATE_WINDOW - 1.0
        _ws_connection_timestamps["10.0.0.1"] = [old_time] * WS_RATE_LIMIT

        # Should be allowed because old entries are cleaned
        assert _check_ws_rate_limit("10.0.0.1") is True

    def test_rate_limit_constants(self):
        """Rate limit constants should have expected values."""
        from app.core.ws_routes import WS_RATE_LIMIT, WS_RATE_WINDOW

        assert WS_RATE_LIMIT == 30
        assert WS_RATE_WINDOW == 60.0

    async def test_rate_limited_connection_closes_with_4029(self, mock_websocket):
        """A rate-limited WebSocket connection should close with code 4029."""
        from app.core.ws_routes import websocket_endpoint

        with patch(
            "app.core.ws_routes._check_ws_rate_limit", return_value=False
        ):
            await websocket_endpoint(mock_websocket)

        mock_websocket.accept.assert_called_once()
        mock_websocket.close.assert_called_once_with(
            code=4029, reason="Too many connections"
        )

    async def test_normal_rate_connection_proceeds(self, mock_websocket):
        """A non-rate-limited connection should proceed to auth."""
        from app.core.ws_routes import websocket_endpoint

        auth_msg = json.dumps({"type": "auth", "token": "valid-jwt"})
        mock_websocket.receive_text = AsyncMock(
            side_effect=[auth_msg, WebSocketDisconnect()]
        )

        with patch(
            "app.core.ws_routes._check_ws_rate_limit", return_value=True
        ):
            with patch(
                "app.core.ws_routes.authenticate_ws_from_message"
            ) as mock_auth:
                mock_auth.return_value = "user-123"
                with patch("app.core.ws_routes.manager") as mock_manager:
                    mock_manager.connect = AsyncMock(return_value=True)
                    mock_manager.disconnect = MagicMock()

                    await websocket_endpoint(mock_websocket)

        mock_websocket.send_json.assert_called_once_with({"type": "auth_ok"})
