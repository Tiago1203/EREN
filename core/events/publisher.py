"""Publisher patterns for EREN's event system.

This module provides reusable publisher implementations that engines can use
to emit events in a consistent way.

Architecture only — these are concrete implementations that work with the
`EventBus` from `bus.py`. No business logic, AI, or dispatching lives here.
"""

from __future__ import annotations

import logging
from contextlib import contextmanager
from typing import TYPE_CHECKING, Any, Iterator

if TYPE_CHECKING:
    from core.events.bus import EventBus
    from core.events.models import Event, EventType

logger = logging.getLogger(__name__)


# =============================================================================
# Base Publisher Mixin
# =============================================================================


class EventPublisherMixin:
    """Mixin class for engines that publish events.

    Engines that need to emit events can inherit from this class to get
    a consistent publishing interface.

    Example::

        class MyEngine(EventPublisherMixin):
            def __init__(self, event_bus: EventBus):
                self._event_bus = event_bus
                self._source = "my_engine"

            def do_something(self):
                self.publish(
                    EventType.PLAN_CREATED,
                    step_count=5,
                    priority="high",
                )
    """

    def __init__(
        self,
        event_bus: "EventBus | None" = None,
        source: str = "",
        correlation_id: str = "",
        session_id: str = "",
    ) -> None:
        """Initialize the publisher mixin.

        Args:
            event_bus: The EventBus to publish to. Uses global bus if None.
            source: The source identifier for events from this publisher.
            correlation_id: Default correlation ID for events.
            session_id: Default session ID for events.
        """
        self._event_bus = event_bus
        self._source = source
        self._correlation_id = correlation_id
        self._session_id = session_id

    @property
    def event_bus(self) -> "EventBus":
        """Get the event bus.

        Returns:
            The EventBus instance to use.
        """
        if self._event_bus is None:
            from core.events.bus import get_global_bus
            return get_global_bus()
        return self._event_bus

    @property
    def source(self) -> str:
        """Get the source identifier."""
        return self._source

    def publish(
        self,
        event_type: "EventType",
        correlation_id: str | None = None,
        session_id: str | None = None,
        **payload: object,
    ) -> None:
        """Publish an event.

        Args:
            event_type: The type of event to publish.
            correlation_id: Override the default correlation ID.
            session_id: Override the default session ID.
            **payload: Event payload fields.
        """
        from core.events.models import create_event

        event = create_event(
            event_type=event_type,
            source=self._source,
            correlation_id=correlation_id or self._correlation_id,
            session_id=session_id or self._session_id,
            **payload,
        )

        self.event_bus.publish(event)
        logger.debug("Published event: %s from %s", event_type.value, self._source)

    def set_context(
        self,
        correlation_id: str | None = None,
        session_id: str | None = None,
    ) -> None:
        """Update the default context for future events.

        Args:
            correlation_id: New default correlation ID.
            session_id: New default session ID.
        """
        if correlation_id is not None:
            self._correlation_id = correlation_id
        if session_id is not None:
            self._session_id = session_id

    @contextmanager
    def context(
        self,
        correlation_id: str | None = None,
        session_id: str | None = None,
    ) -> Iterator[None]:
        """Temporarily set context for events within a block.

        Args:
            correlation_id: Temporary correlation ID.
            session_id: Temporary session ID.

        Yields:
            None
        """
        old_correlation = self._correlation_id
        old_session = self._session_id

        try:
            if correlation_id is not None:
                self._correlation_id = correlation_id
            if session_id is not None:
                self._session_id = session_id
            yield
        finally:
            self._correlation_id = old_correlation
            self._session_id = old_session


# =============================================================================
# Context Manager for Publishers
# =============================================================================


class EventContext:
    """Context manager for event publishing with automatic correlation.

    Useful for grouping related events under a single correlation ID.

    Example::

        with EventContext("request-123", source="planner") as ctx:
            ctx.publish(EventType.PLAN_CREATED, step_count=5)
            # ... do work ...
            ctx.publish(EventType.PLAN_COMPLETED, steps_done=5)
    """

    def __init__(
        self,
        correlation_id: str,
        source: str = "",
        session_id: str = "",
        event_bus: "EventBus | None" = None,
    ) -> None:
        """Initialize the event context.

        Args:
            correlation_id: Correlation ID for all events in this context.
            source: Source identifier for events.
            session_id: Session ID for events.
            event_bus: EventBus to publish to.
        """
        self.correlation_id = correlation_id
        self.source = source
        self.session_id = session_id
        self._event_bus = event_bus
        self._published_events: list["Event"] = []

    @property
    def event_bus(self) -> "EventBus":
        """Get the event bus."""
        if self._event_bus is None:
            from core.events.bus import get_global_bus
            return get_global_bus()
        return self._event_bus

    def publish(
        self,
        event_type: "EventType",
        session_id: str | None = None,
        **payload: object,
    ) -> None:
        """Publish an event within this context.

        Args:
            event_type: The type of event to publish.
            session_id: Optional session ID override.
            **payload: Event payload fields.
        """
        from core.events.models import create_event

        event = create_event(
            event_type=event_type,
            source=self.source,
            correlation_id=self.correlation_id,
            session_id=session_id or self.session_id,
            **payload,
        )

        self.event_bus.publish(event)
        self._published_events.append(event)

    def __enter__(self) -> "EventContext":
        """Enter the context."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit the context."""
        # Optionally publish context end event
        if exc_type is not None:
            self.publish(
                event_type=(
                    "error_occurred"
                    if hasattr(__import__("core.events.models", fromlist=["EventType"]), "EventType")
                    else None  # Will be filtered by caller
                ),
                error_type=str(exc_type.__name__),
                error_message=str(exc_val),
            ) if hasattr(__import__("core.events.models", fromlist=["EventType"]), "EventType") else None

    @property
    def published_events(self) -> list["Event"]:
        """Get all events published in this context.

        Returns:
            List of published events.
        """
        return self._published_events.copy()


# =============================================================================
# Event Aggregator
# =============================================================================


class EventAggregator:
    """Collects events and publishes them as a batch.

    Useful when you want to defer publishing until multiple events are ready,
    or when you want to publish atomically.

    Example::

        aggregator = EventAggregator()
        aggregator.add(EventType.KNOWLEDGE_RETRIEVED, count=5)
        aggregator.add(EventType.REASONING_FINISHED, confidence=0.9)
        aggregator.publish_all()
    """

    def __init__(
        self,
        source: str = "",
        correlation_id: str = "",
        session_id: str = "",
        event_bus: "EventBus | None" = None,
    ) -> None:
        """Initialize the aggregator.

        Args:
            source: Source identifier for events.
            correlation_id: Correlation ID for events.
            session_id: Session ID for events.
            event_bus: EventBus to publish to.
        """
        self.source = source
        self.correlation_id = correlation_id
        self.session_id = session_id
        self._event_bus = event_bus
        self._events: list["Event"] = []

    @property
    def event_bus(self) -> "EventBus":
        """Get the event bus."""
        if self._event_bus is None:
            from core.events.bus import get_global_bus
            return get_global_bus()
        return self._event_bus

    def add(
        self,
        event_type: "EventType",
        **payload: object,
    ) -> None:
        """Add an event to the batch.

        Args:
            event_type: The type of event to add.
            **payload: Event payload fields.
        """
        from core.events.models import create_event

        event = create_event(
            event_type=event_type,
            source=self.source,
            correlation_id=self.correlation_id,
            session_id=self.session_id,
            **payload,
        )
        self._events.append(event)

    def publish_all(self) -> None:
        """Publish all collected events.

        Events are published in the order they were added.
        After publishing, the internal list is cleared.
        """
        for event in self._events:
            self.event_bus.publish(event)
        self._events.clear()

    def clear(self) -> None:
        """Clear all pending events without publishing."""
        self._events.clear()

    def __len__(self) -> int:
        """Get the number of pending events."""
        return len(self._events)


# =============================================================================
# Circuit Breaker Publisher
# =============================================================================


class CircuitBreakerPublisher:
    """Publisher wrapper that implements circuit breaker pattern.

    Prevents cascading failures by stopping event publishing when errors occur.

    Example::

        publisher = CircuitBreakerPublisher(
            wrapped=my_event_bus,
            failure_threshold=5,
            reset_timeout=60,
        )
    """

    def __init__(
        self,
        wrapped: "EventBus",
        failure_threshold: int = 5,
        reset_timeout: float = 60.0,
    ) -> None:
        """Initialize the circuit breaker publisher.

        Args:
            wrapped: The EventBus to wrap.
            failure_threshold: Number of failures before opening circuit.
            reset_timeout: Seconds to wait before attempting reset.
        """
        self._wrapped = wrapped
        self._failure_threshold = failure_threshold
        self._reset_timeout = reset_timeout
        self._failure_count = 0
        self._last_failure_time: float | None = None
        self._is_open = False

    def publish(self, event: "Event") -> None:
        """Publish an event with circuit breaker protection.

        Args:
            event: The event to publish.

        Raises:
            RuntimeError: If the circuit is open.
        """
        import time

        if self._is_open:
            if (
                self._last_failure_time is not None
                and time.time() - self._last_failure_time > self._reset_timeout
            ):
                # Attempt reset
                self._failure_count = 0
                self._is_open = False
                logger.info("Circuit breaker reset")
            else:
                raise RuntimeError(
                    f"Circuit breaker is open. "
                    f"Last failure: {self._last_failure_time}"
                )

        try:
            self._wrapped.publish(event)
            self._failure_count = 0
        except Exception:
            self._failure_count += 1
            self._last_failure_time = time.time()

            if self._failure_count >= self._failure_threshold:
                self._is_open = True
                logger.warning(
                    "Circuit breaker opened after %d failures",
                    self._failure_count,
                )
            raise

    @property
    def is_open(self) -> bool:
        """Check if the circuit is open."""
        return self._is_open

    @property
    def failure_count(self) -> int:
        """Get the current failure count."""
        return self._failure_count

    def reset(self) -> None:
        """Manually reset the circuit breaker."""
        self._failure_count = 0
        self._is_open = False
        self._last_failure_time = None
