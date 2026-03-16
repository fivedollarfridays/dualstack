"""Tests for event bus — publish/subscribe with pattern matching."""

from unittest.mock import AsyncMock


class TestPublish:
    async def test_notifies_exact_subscriber(self):
        from app.core.events import EventBus

        bus = EventBus()
        handler = AsyncMock()
        bus.subscribe("item.created", handler)

        await bus.publish("item.created", {"id": "123"})

        handler.assert_called_once_with({"id": "123"})

    async def test_does_not_notify_unrelated_subscriber(self):
        from app.core.events import EventBus

        bus = EventBus()
        handler = AsyncMock()
        bus.subscribe("item.deleted", handler)

        await bus.publish("item.created", {"id": "123"})

        handler.assert_not_called()

    async def test_notifies_wildcard_subscriber(self):
        from app.core.events import EventBus

        bus = EventBus()
        handler = AsyncMock()
        bus.subscribe("item.*", handler)

        await bus.publish("item.created", {"id": "1"})
        await bus.publish("item.deleted", {"id": "2"})

        assert handler.call_count == 2

    async def test_wildcard_does_not_match_different_prefix(self):
        from app.core.events import EventBus

        bus = EventBus()
        handler = AsyncMock()
        bus.subscribe("item.*", handler)

        await bus.publish("user.created", {"id": "1"})

        handler.assert_not_called()


class TestSubscribe:
    async def test_multiple_handlers_for_same_event(self):
        from app.core.events import EventBus

        bus = EventBus()
        h1 = AsyncMock()
        h2 = AsyncMock()
        bus.subscribe("item.created", h1)
        bus.subscribe("item.created", h2)

        await bus.publish("item.created", {"id": "1"})

        h1.assert_called_once()
        h2.assert_called_once()

    async def test_handler_error_does_not_block_others(self):
        from app.core.events import EventBus

        bus = EventBus()
        h_bad = AsyncMock(side_effect=Exception("oops"))
        h_good = AsyncMock()
        bus.subscribe("item.created", h_bad)
        bus.subscribe("item.created", h_good)

        await bus.publish("item.created", {"id": "1"})

        h_good.assert_called_once()
