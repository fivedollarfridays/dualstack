"""Tests for WebSocket connection manager."""

from unittest.mock import AsyncMock, patch


class TestConnect:
    async def test_adds_connection_to_active_set(self):
        from app.core.websocket import ConnectionManager

        mgr = ConnectionManager()
        ws = AsyncMock()

        await mgr.connect(ws, user_id="user-1")

        assert mgr.active_count == 1

    async def test_multiple_connections_for_same_user(self):
        from app.core.websocket import ConnectionManager

        mgr = ConnectionManager()
        ws1 = AsyncMock()
        ws2 = AsyncMock()

        await mgr.connect(ws1, user_id="user-1")
        await mgr.connect(ws2, user_id="user-1")

        assert mgr.active_count == 2


class TestDisconnect:
    async def test_removes_connection(self):
        from app.core.websocket import ConnectionManager

        mgr = ConnectionManager()
        ws = AsyncMock()

        await mgr.connect(ws, user_id="user-1")
        mgr.disconnect(ws)

        assert mgr.active_count == 0

    async def test_disconnect_nonexistent_is_noop(self):
        from app.core.websocket import ConnectionManager

        mgr = ConnectionManager()
        ws = AsyncMock()

        mgr.disconnect(ws)  # should not raise

        assert mgr.active_count == 0


class TestNoBroadcast:
    """Confirm broadcast() method has been removed (security footgun)."""

    def test_no_broadcast_method(self):
        from app.core.websocket import ConnectionManager

        mgr = ConnectionManager()
        assert not hasattr(mgr, "broadcast"), (
            "broadcast() should be removed — use send_to_user() instead"
        )


class TestSendToUser:
    async def test_sends_only_to_target_user(self):
        from app.core.websocket import ConnectionManager

        mgr = ConnectionManager()
        ws1 = AsyncMock()
        ws2 = AsyncMock()

        await mgr.connect(ws1, user_id="user-1")
        await mgr.connect(ws2, user_id="user-2")

        await mgr.send_to_user("user-1", {"type": "notification"})

        ws1.send_json.assert_called_once_with({"type": "notification"})
        ws2.send_json.assert_not_called()

    async def test_noop_for_unknown_user(self):
        from app.core.websocket import ConnectionManager

        mgr = ConnectionManager()
        # Should not raise
        await mgr.send_to_user("ghost", {"type": "ping"})


class TestBroadcastEventHandler:
    """Tests for _broadcast_event user-scoped routing (no broadcast leak)."""

    async def test_event_with_user_id_sent_only_to_owner(self):
        """User A should NOT receive events owned by User B."""
        from app.core.websocket import ConnectionManager

        mgr = ConnectionManager()
        ws_a = AsyncMock()
        ws_b = AsyncMock()

        await mgr.connect(ws_a, user_id="user-a")
        await mgr.connect(ws_b, user_id="user-b")

        with patch("app.core.ws_routes.manager", mgr):
            from app.core.ws_routes import _broadcast_event

            await _broadcast_event(
                {"type": "item.created", "user_id": "user-b", "data": {"id": "x1"}}
            )

        ws_b.send_json.assert_called_once()
        ws_a.send_json.assert_not_called()

    async def test_event_with_user_id_reaches_owner(self):
        """User B should receive events owned by User B."""
        from app.core.websocket import ConnectionManager

        mgr = ConnectionManager()
        ws_b = AsyncMock()

        await mgr.connect(ws_b, user_id="user-b")

        with patch("app.core.ws_routes.manager", mgr):
            from app.core.ws_routes import _broadcast_event

            payload = {
                "type": "item.updated",
                "user_id": "user-b",
                "data": {"id": "x2"},
            }
            await _broadcast_event(payload)

        ws_b.send_json.assert_called_once_with(payload)

    async def test_event_missing_user_id_is_dropped(self):
        """Events without user_id should be dropped with a warning log."""
        from app.core.websocket import ConnectionManager

        mgr = ConnectionManager()
        ws = AsyncMock()

        await mgr.connect(ws, user_id="user-a")

        with patch("app.core.ws_routes.manager", mgr):
            from app.core.ws_routes import _broadcast_event

            with patch("app.core.ws_routes.logger") as mock_logger:
                await _broadcast_event({"type": "item.deleted", "data": {"id": "x3"}})

            ws.send_json.assert_not_called()
            mock_logger.warning.assert_called_once()
