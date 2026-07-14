"""Retrieval events for EREN Semantic Retrieval Engine."""

from __future__ import annotations

from enum import Enum
from typing import Callable


class RetrievalEvent(str, Enum):
    """Retrieval event types."""

    QUERY_RECEIVED = "retrieval:query_received"
    PLANNING_STARTED = "retrieval:planning_started"
    PLANNING_COMPLETED = "retrieval:planning_completed"
    RETRIEVAL_STARTED = "retrieval:retrieval_started"
    RETRIEVAL_COMPLETED = "retrieval:retrieval_completed"
    RANKING_STARTED = "retrieval:ranking_started"
    RANKING_COMPLETED = "retrieval:ranking_completed"
    CONTEXT_BUILT = "retrieval:context_built"
    QUERY_COMPLETED = "retrieval:query_completed"
    QUERY_FAILED = "retrieval:query_failed"
    SOURCE_QUERIED = "retrieval:source_queried"
    CACHE_HIT = "retrieval:cache_hit"
    CACHE_MISS = "retrieval:cache_miss"


class RetrievalEventBus:
    """Event bus for retrieval events.

    Publishes and subscribes to retrieval events.
    """

    def __init__(self):
        """Initialize event bus."""
        self._handlers: dict[RetrievalEvent, list[Callable]] = {}

    def subscribe(self, event: RetrievalEvent, handler: Callable) -> None:
        """Subscribe to an event.

        Args:
            event: Event to subscribe to.
            handler: Handler function.
        """
        if event not in self._handlers:
            self._handlers[event] = []
        if handler not in self._handlers[event]:
            self._handlers[event].append(handler)

    def unsubscribe(self, event: RetrievalEvent, handler: Callable) -> None:
        """Unsubscribe from an event.

        Args:
            event: Event to unsubscribe from.
            handler: Handler function.
        """
        if event in self._handlers:
            if handler in self._handlers[event]:
                self._handlers[event].remove(handler)

    def publish(self, event: RetrievalEvent, data: dict) -> None:
        """Publish an event.

        Args:
            event: Event to publish.
            data: Event data.
        """
        handlers = self._handlers.get(event, [])
        for handler in handlers:
            try:
                handler(data)
            except Exception:
                pass  # Don't let handler errors break event publishing

    def clear(self) -> None:
        """Clear all subscriptions."""
        self._handlers.clear()


# Global event bus
_global_event_bus: RetrievalEventBus | None = None
_event_bus_lock = None


def get_retrieval_event_bus() -> RetrievalEventBus:
    """Get the global event bus.

    Returns:
        Global RetrievalEventBus instance.
    """
    global _global_event_bus
    if _global_event_bus is None:
        _global_event_bus = RetrievalEventBus()
    return _global_event_bus


def reset_retrieval_event_bus() -> None:
    """Reset the global event bus."""
    global _global_event_bus
    if _global_event_bus is not None:
        _global_event_bus.clear()
    _global_event_bus = None
