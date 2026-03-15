"""In-process event bus for publishing domain events."""

from __future__ import annotations

import fnmatch
import logging
from collections import defaultdict
from typing import Any, Awaitable, Callable

logger = logging.getLogger(__name__)

Handler = Callable[[dict[str, Any]], Awaitable[None]]


class EventBus:
    """Simple pub/sub with glob-style pattern matching."""

    def __init__(self) -> None:
        self._handlers: dict[str, list[Handler]] = defaultdict(list)

    def subscribe(self, pattern: str, handler: Handler) -> None:
        self._handlers[pattern].append(handler)

    async def publish(self, event_type: str, payload: dict[str, Any]) -> None:
        for pattern, handlers in self._handlers.items():
            if fnmatch.fnmatch(event_type, pattern):
                for handler in handlers:
                    try:
                        await handler(payload)
                    except Exception:
                        logger.exception("Event handler error for %s", event_type)


event_bus = EventBus()
