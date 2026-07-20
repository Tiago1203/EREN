"""Events for EREN OS Multi-Provider Layer.

Implements event system for provider lifecycle and metrics.
"""

from __future__ import annotations

import asyncio
import threading
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass


# =============================================================================
# Event Types
# =============================================================================


class EventType(str, Enum):
    """Provider event types."""

    # Lifecycle events
    PROVIDER_REGISTERED = "provider_registered"
    PROVIDER_UNREGISTERED = "provider_unregistered"
    PROVIDER_INITIALIZED = "provider_initialized"
    PROVIDER_SHUTDOWN = "provider_shutdown"

    # Health events
    PROVIDER_HEALTHY = "provider_healthy"
    PROVIDER_DEGRADED = "provider_degraded"
    PROVIDER_UNHEALTHY = "provider_unhealthy"
    HEALTH_CHECK_STARTED = "health_check_started"
    HEALTH_CHECK_COMPLETED = "health_check_completed"

    # Request events
    REQUEST_STARTED = "request_started"
    REQUEST_COMPLETED = "request_completed"
    REQUEST_FAILED = "request_failed"
    REQUEST_RETRY = "request_retry"
    REQUEST_TIMEOUT = "request_timeout"
    REQUEST_CANCELLED = "request_cancelled"

    # Failover events
    FAILOVER_STARTED = "failover_started"
    FAILOVER_COMPLETED = "failover_completed"
    FAILOVER_FAILED = "failover_failed"
    CIRCUIT_OPENED = "circuit_opened"
    CIRCUIT_CLOSED = "circuit_closed"
    CIRCUIT_HALF_OPEN = "circuit_half_open"

    # Rate limit events
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    RATE_LIMIT_RESET = "rate_limit_reset"

    # Metrics events
    METRICS_UPDATED = "metrics_updated"
    COST_THRESHOLD_EXCEEDED = "cost_threshold_exceeded"
    LATENCY_THRESHOLD_EXCEEDED = "latency_threshold_exceeded"

    # Selection events
    PROVIDER_SELECTED = "provider_selected"
    SELECTION_FAILED = "selection_failed"

    # Cache events
    CACHE_HIT = "cache_hit"
    CACHE_MISS = "cache_miss"
    CACHE_INVALIDATED = "cache_invalidated"

    # Streaming events
    STREAM_STARTED = "stream_started"
    STREAM_CHUNK = "stream_chunk"
    STREAM_COMPLETED = "stream_completed"
    STREAM_ERROR = "stream_error"


# =============================================================================
# Event Data
# =============================================================================


@dataclass
class Event:
    """A provider event."""

    event_type: EventType
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    provider_id: str = ""
    data: dict = field(default_factory=dict)
    trace_id: str = ""
    span_id: str = ""
    source: str = "provider_manager"

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "event_type": self.event_type.value,
            "timestamp": self.timestamp.isoformat(),
            "provider_id": self.provider_id,
            "data": self.data,
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "source": self.source,
        }


# =============================================================================
# Event Handler
# =============================================================================


EventHandler = Callable[[Event], None]
AsyncEventHandler = Callable[[Event], None]


class EventHandlerConfig:
    """Configuration for event handler."""

    def __init__(self):
        """Initialize config."""
        self.include_types: set[EventType] | None = None
        self.exclude_types: set[EventType] | None = None
        self.provider_ids: set[str] | None = None
        self.async_mode: bool = False
        self.buffer_size: int = 1000


# =============================================================================
# Event Bus
# =============================================================================


class EventBus:
    """Event bus for provider events.

    Features:
    - Synchronous and asynchronous handlers
    - Event filtering
    - Event buffering
    - Event history
    """

    def __init__(self, max_history: int = 1000):
        """Initialize event bus.

        Args:
            max_history: Maximum event history size.
        """
        self._handlers: dict[EventType, list[EventHandler | AsyncEventHandler]] = {}
        self._handler_configs: dict[EventHandler | AsyncEventHandler, EventHandlerConfig] = {}
        self._history: list[Event] = []
        self._max_history = max_history
        self._lock = threading.RLock()

        # Async handling
        self._async_loop: asyncio.AbstractEventLoop | None = None
        self._async_queue: asyncio.Queue[Event] | None = None
        self._async_task: asyncio.Task | None = None

    def subscribe(
        self,
        event_type: EventType,
        handler: EventHandler | AsyncEventHandler,
        config: EventHandlerConfig | None = None,
    ) -> None:
        """Subscribe to an event type.

        Args:
            event_type: Event type to subscribe.
            handler: Handler function.
            config: Optional handler configuration.
        """
        with self._lock:
            if event_type not in self._handlers:
                self._handlers[event_type] = []

            if handler not in self._handlers[event_type]:
                self._handlers[event_type].append(handler)
                self._handler_configs[handler] = config or EventHandlerConfig()

    def unsubscribe(
        self,
        event_type: EventType,
        handler: EventHandler | AsyncEventHandler,
    ) -> bool:
        """Unsubscribe from an event type.

        Args:
            event_type: Event type.
            handler: Handler to remove.

        Returns:
            True if unsubscribed.
        """
        with self._lock:
            if event_type in self._handlers:
                if handler in self._handlers[event_type]:
                    self._handlers[event_type].remove(handler)
                    self._handler_configs.pop(handler, None)
                    return True
            return False

    def unsubscribe_all(self, handler: EventHandler | AsyncEventHandler) -> int:
        """Unsubscribe handler from all events.

        Args:
            handler: Handler to remove.

        Returns:
            Number of unsubscriptions.
        """
        count = 0
        with self._lock:
            for event_type in list(self._handlers.keys()):
                if handler in self._handlers[event_type]:
                    self._handlers[event_type].remove(handler)
                    count += 1
            self._handler_configs.pop(handler, None)
        return count

    def emit(self, event: Event) -> None:
        """Emit an event.

        Args:
            event: Event to emit.
        """
        # Add to history
        self._add_to_history(event)

        # Get handlers
        handlers = self._get_handlers(event)

        # Call handlers
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    # Schedule async handler
                    self._schedule_async_handler(handler, event)
                else:
                    handler(event)
            except Exception:
                pass

    def _get_handlers(self, event: Event) -> list[EventHandler | AsyncEventHandler]:
        """Get matching handlers for event.

        Args:
            event: Event.

        Returns:
            List of handlers.
        """
        handlers = []

        with self._lock:
            # Get handlers for this event type
            type_handlers = self._handlers.get(event.event_type, [])

            for handler in type_handlers:
                config = self._handler_configs.get(handler)
                if config and not self._matches_config(event, config):
                    continue
                handlers.append(handler)

        return handlers

    def _matches_config(self, event: Event, config: EventHandlerConfig) -> bool:
        """Check if event matches handler config.

        Args:
            event: Event.
            config: Handler config.

        Returns:
            True if matches.
        """
        # Check include types
        if config.include_types and event.event_type not in config.include_types:
            return False

        # Check exclude types
        if config.exclude_types and event.event_type in config.exclude_types:
            return False

        # Check provider IDs
        if config.provider_ids and event.provider_id not in config.provider_ids:
            return False

        return True

    def _add_to_history(self, event: Event) -> None:
        """Add event to history.

        Args:
            event: Event to add.
        """
        with self._lock:
            self._history.append(event)
            if len(self._history) > self._max_history:
                self._history.pop(0)

    def get_history(
        self,
        event_type: EventType | None = None,
        provider_id: str | None = None,
        limit: int = 100,
    ) -> list[Event]:
        """Get event history.

        Args:
            event_type: Filter by event type.
            provider_id: Filter by provider.
            limit: Maximum events to return.

        Returns:
            List of events.
        """
        with self._lock:
            events = self._history

            if event_type:
                events = [e for e in events if e.event_type == event_type]

            if provider_id:
                events = [e for e in events if e.provider_id == provider_id]

            return events[-limit:]

    def start_async_processing(self) -> None:
        """Start async event processing."""
        if self._async_task is not None:
            return

        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        self._async_loop = loop
        self._async_queue = asyncio.Queue()
        self._async_task = loop.create_task(self._process_async_events())

    async def _process_async_events(self) -> None:
        """Process async event queue."""
        if not self._async_queue:
            return

        while True:
            try:
                event = await asyncio.wait_for(self._async_queue.get(), timeout=1.0)
                handlers = self._get_handlers(event)

                for handler in handlers:
                    if asyncio.iscoroutinefunction(handler):
                        try:
                            await handler(event)
                        except Exception:
                            pass

            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break

    def _schedule_async_handler(
        self,
        handler: AsyncEventHandler,
        event: Event,
    ) -> None:
        """Schedule async handler.

        Args:
            handler: Async handler.
            event: Event.
        """
        if self._async_queue:
            try:
                self._async_queue.put_nowait(event)
            except asyncio.QueueFull:
                pass
        else:
            # Run synchronously if async not started
            try:
                loop = asyncio.get_event_loop()
                loop.run_until_complete(handler(event))
            except Exception:
                pass

    def stop_async_processing(self) -> None:
        """Stop async event processing."""
        if self._async_task:
            self._async_task.cancel()
            self._async_task = None
        self._async_queue = None

    def clear_history(self) -> None:
        """Clear event history."""
        with self._lock:
            self._history.clear()

    def get_stats(self) -> dict:
        """Get event bus statistics."""
        with self._lock:
            handler_counts = {et.value: len(handlers) for et, handlers in self._handlers.items()}
            return {
                "total_handlers": sum(len(h) for h in self._handlers.values()),
                "event_types_subscribed": len(self._handlers),
                "history_size": len(self._history),
                "max_history": self._max_history,
                "handlers_per_type": handler_counts,
            }

    def __len__(self) -> int:
        """Get number of subscribed handlers."""
        with self._lock:
            return sum(len(h) for h in self._handlers.values())


# Global event bus
_global_event_bus: EventBus | None = None
_event_bus_lock = threading.Lock()


def get_event_bus() -> EventBus:
    """Get the global event bus.

    Returns:
        Global EventBus instance.
    """
    global _global_event_bus
    with _event_bus_lock:
        if _global_event_bus is None:
            _global_event_bus = EventBus()
        return _global_event_bus


def reset_event_bus() -> None:
    """Reset the global event bus."""
    global _global_event_bus
    with _event_bus_lock:
        if _global_event_bus is not None:
            _global_event_bus.stop_async_processing()
            _global_event_bus.clear_history()
        _global_event_bus = None


# =============================================================================
# Convenience Functions
# =============================================================================


def emit_event(
    event_type: EventType,
    provider_id: str = "",
    data: dict | None = None,
    trace_id: str = "",
    span_id: str = "",
) -> None:
    """Emit an event.

    Args:
        event_type: Type of event.
        provider_id: Provider identifier.
        data: Event data.
        trace_id: Trace identifier.
        span_id: Span identifier.
    """
    event = Event(
        event_type=event_type,
        provider_id=provider_id,
        data=data or {},
        trace_id=trace_id,
        span_id=span_id,
    )
    get_event_bus().emit(event)


def on_provider_event(
    event_type: EventType,
    handler: EventHandler,
) -> None:
    """Subscribe to provider event.

    Args:
        event_type: Event type.
        handler: Handler function.
    """
    get_event_bus().subscribe(event_type, handler)
