"""Embedding events for EREN Embedding Provider Layer."""

from __future__ import annotations

from enum import Enum
from typing import Callable


class EmbeddingEvent(str, Enum):
    """Embedding event types."""

    REQUEST_RECEIVED = "embedding:request_received"
    PROVIDER_SELECTED = "embedding:provider_selected"
    GENERATION_STARTED = "embedding:generation_started"
    GENERATION_COMPLETED = "embedding:generation_completed"
    GENERATION_FAILED = "embedding:generation_failed"
    HEALTH_CHECK_STARTED = "embedding:health_check_started"
    HEALTH_CHECK_COMPLETED = "embedding:health_check_completed"
    PROVIDER_REGISTERED = "embedding:provider_registered"
    PROVIDER_UNREGISTERED = "embedding:provider_unregistered"
    METRICS_RESET = "embedding:metrics_reset"


class EmbeddingEventBus:
    """Event bus for embedding events.

    Publishes and subscribes to embedding events.
    """

    def __init__(self):
        """Initialize event bus."""
        self._handlers: dict[EmbeddingEvent, list[Callable]] = {}

    def subscribe(self, event: EmbeddingEvent, handler: Callable) -> None:
        """Subscribe to an event.

        Args:
            event: Event to subscribe to.
            handler: Handler function.
        """
        if event not in self._handlers:
            self._handlers[event] = []
        if handler not in self._handlers[event]:
            self._handlers[event].append(handler)

    def unsubscribe(self, event: EmbeddingEvent, handler: Callable) -> None:
        """Unsubscribe from an event.

        Args:
            event: Event to unsubscribe from.
            handler: Handler function.
        """
        if event in self._handlers:
            if handler in self._handlers[event]:
                self._handlers[event].remove(handler)

    def publish(self, event: EmbeddingEvent, data: dict) -> None:
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
                pass

    def clear(self) -> None:
        """Clear all subscriptions."""
        self._handlers.clear()


# Global event bus
_global_event_bus: EmbeddingEventBus | None = None


def get_embedding_event_bus() -> EmbeddingEventBus:
    """Get the global event bus.

    Returns:
        Global EmbeddingEventBus instance.
    """
    global _global_event_bus
    if _global_event_bus is None:
        _global_event_bus = EmbeddingEventBus()
    return _global_event_bus


def reset_embedding_event_bus() -> None:
    """Reset the global event bus."""
    global _global_event_bus
    if _global_event_bus is not None:
        _global_event_bus.clear()
    _global_event_bus = None
