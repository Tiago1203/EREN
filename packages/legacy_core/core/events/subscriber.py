"""Subscriber patterns for EREN's event system.

This module provides reusable subscriber implementations that engines can extend
or compose to handle events in common patterns.

Architecture only — these are concrete implementations of the `EventSubscriber`
protocol from `bus.py`. No business logic, AI, or dispatching lives here.
"""

from __future__ import annotations

import logging
from abc import abstractmethod
from collections.abc import Callable
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from core.events.models import Event, EventType

logger = logging.getLogger(__name__)


# =============================================================================
# Base Subscriber
# =============================================================================


class BaseSubscriber:
    """Base class for event subscribers.

    Provides common functionality for handling events including:
    - Event filtering
    - Error handling
    - Logging
    - Subscription management
    """

    def __init__(
        self,
        event_types: tuple[EventType, ...] | None = None,
        log_events: bool = False,
        raise_on_error: bool = False,
    ) -> None:
        """Initialize the subscriber.

        Args:
            event_types: Specific event types to subscribe to. None means all.
            log_events: Whether to log received events.
            raise_on_error: Whether to re-raise exceptions from handlers.
        """
        self._event_types = event_types or ()
        self._log_events = log_events
        self._raise_on_error = raise_on_error

    @property
    def subscribed_types(self) -> tuple[EventType, ...]:
        """Return the event types this subscriber is interested in."""
        return self._event_types

    def handle(self, event: Event) -> None:
        """Handle a received event.

        Args:
            event: The event to handle.
        """
        if self._log_events:
            logger.debug("Subscriber %s received event: %s", self, event.type)

        try:
            self.on_event(event)
        except Exception:
            logger.exception("Error handling event %s in %s", event.type, self)
            if self._raise_on_error:
                raise

    @abstractmethod
    def on_event(self, event: Event) -> None:
        """Process the event.

        Override this method to implement custom event handling logic.

        Args:
            event: The event to process.
        """
        ...


# =============================================================================
# Function-based Subscriber
# =============================================================================


class FunctionSubscriber:
    """A subscriber that wraps a function/callable.

    Useful for simple event handlers that don't need a full class.

    Example::

        def handle_plan_created(event):
            print(f"Plan created: {event.payload}")

        subscriber = FunctionSubscriber(
            event_types=(EventType.PLAN_CREATED,),
            handler=handle_plan_created,
        )
    """

    def __init__(
        self,
        event_types: tuple[EventType, ...] = (),
        handler: Callable[[Event], Any] | None = None,
        predicate: Callable[[Event], bool] | None = None,
    ) -> None:
        """Initialize the function subscriber.

        Args:
            event_types: Event types to subscribe to.
            handler: Function to call when an event is received.
            predicate: Optional filter function. Only events where
                      predicate(event) returns True are passed to handler.
        """
        self._event_types = event_types
        self._handler = handler
        self._predicate = predicate

    @property
    def subscribed_types(self) -> tuple[EventType, ...]:
        """Return the event types this subscriber is interested in."""
        return self._event_types

    def handle(self, event: Event) -> None:
        """Handle the event by calling the handler.

        Args:
            event: The event to handle.
        """
        if self._predicate is not None and not self._predicate(event):
            return

        if self._handler is not None:
            self._handler(event)


# =============================================================================
# Multi-handler Subscriber
# =============================================================================


class MultiHandlerSubscriber:
    """A subscriber that routes events to different handlers.

    Routes events to specific handlers based on event type or predicates.
    Useful when a single subscriber needs to handle multiple event types
    with different logic.

    Example::

        subscriber = MultiHandlerSubscriber()
        subscriber.register(EventType.PLAN_CREATED, handle_plan)
        subscriber.register(EventType.PLAN_FAILED, handle_failure)
        subscriber.register(
            lambda e: e.type == EventType.ENGINE_ERROR,
            handle_any_engine_error,
        )
    """

    def __init__(self) -> None:
        """Initialize the multi-handler subscriber."""
        self._handlers: list[tuple[Callable[[Event], bool], Callable[[Event], Any]]] = []
        self._fallback: Callable[[Event], Any] | None = None

    @property
    def subscribed_types(self) -> tuple[EventType, ...]:
        """Return all event types this subscriber handles."""
        types: set[EventType] = set()
        for predicate, _ in self._handlers:
            if isinstance(predicate, type(predicate)) and hasattr(predicate, "value"):
                # It's an EventType enum
                types.add(predicate)  # type: ignore
        return tuple(types)

    def register(
        self,
        event_type_or_predicate: EventType | Callable[[Event], bool],
        handler: Callable[[Event], Any],
    ) -> None:
        """Register a handler for an event type or predicate.

        Args:
            event_type_or_predicate: An EventType to match exactly, or a
                                   callable that returns True for matching events.
            handler: The function to call for matching events.
        """
        self._handlers.append((event_type_or_predicate, handler))  # type: ignore

    def register_fallback(self, handler: Callable[[Event], Any]) -> None:
        """Register a fallback handler for unmatched events.

        Args:
            handler: Function to call for events that don't match any predicate.
        """
        self._fallback = handler

    def handle(self, event: Event) -> None:
        """Route the event to the appropriate handler.

        Args:
            event: The event to route.
        """
        for predicate, handler in self._handlers:
            if callable(predicate):
                if predicate(event):  # type: ignore
                    handler(event)
                    return
            elif predicate == event.type:
                handler(event)
                return

        if self._fallback is not None:
            self._fallback(event)


# =============================================================================
# Logging Subscriber
# =============================================================================


class LoggingSubscriber:
    """A subscriber that logs events.

    Useful for debugging, monitoring, and audit trails.
    """

    def __init__(
        self,
        event_types: tuple[EventType, ...] | None = None,
        log_level: int = logging.INFO,
        include_payload: bool = False,
    ) -> None:
        """Initialize the logging subscriber.

        Args:
            event_types: Event types to log. None means all.
            log_level: Logging level to use.
            include_payload: Whether to include event payload in logs.
        """
        self._event_types = event_types or ()
        self._log_level = log_level
        self._include_payload = include_payload
        self._logger = logging.getLogger(f"{__name__}.{id(self)}")

    @property
    def subscribed_types(self) -> tuple[EventType, ...]:
        """Return the event types this subscriber is interested in."""
        return self._event_types

    def handle(self, event: Event) -> None:
        """Log the event.

        Args:
            event: The event to log.
        """
        parts = [
            f"Event({event.type.value})",
            f"source={event.source}",
            f"id={event.event_id[:8]}",
        ]

        if event.correlation_id:
            parts.append(f"correlation={event.correlation_id}")

        if self._include_payload and event.payload:
            parts.append(f"payload={event.payload}")

        self._logger.log(self._log_level, " | ".join(parts))


# =============================================================================
# Audit Subscriber
# =============================================================================


class AuditSubscriber:
    """A subscriber that creates audit records.

    Useful for compliance, traceability, and incident investigation.
    """

    def __init__(self, record_store: Callable[[dict[str, Any]], None] | None = None) -> None:
        """Initialize the audit subscriber.

        Args:
            record_store: Optional function to store audit records.
                        If not provided, records are logged.
        """
        self._record_store = record_store
        self._records: list[dict[str, Any]] = []

    @property
    def subscribed_types(self) -> tuple[EventType, ...]:
        """Return all event types (audit subscriber sees everything)."""
        return ()

    def handle(self, event: Event) -> None:
        """Create an audit record for the event.

        Args:
            event: The event to audit.
        """
        record = {
            "event_id": event.event_id,
            "event_type": event.type.value,
            "timestamp": event.timestamp.isoformat(),
            "source": event.source,
            "correlation_id": event.correlation_id,
            "session_id": event.session_id,
            "payload_keys": list(event.payload.keys()),
        }

        self._records.append(record)

        if self._record_store is not None:
            self._record_store(record)
        else:
            logger.info("Audit: %s", record)

    def get_records(
        self,
        event_type: EventType | None = None,
        correlation_id: str | None = None,
    ) -> list[dict[str, Any]]:
        """Get audit records matching criteria.

        Args:
            event_type: Filter by event type.
            correlation_id: Filter by correlation ID.

        Returns:
            List of matching audit records.
        """
        records = self._records

        if event_type is not None:
            records = [r for r in records if r["event_type"] == event_type.value]

        if correlation_id is not None:
            records = [r for r in records if r["correlation_id"] == correlation_id]

        return records


# =============================================================================
# Metric Subscriber
# =============================================================================


class MetricSubscriber:
    """A subscriber that collects metrics.

    Useful for monitoring, alerting, and performance analysis.
    """

    def __init__(self) -> None:
        """Initialize the metric subscriber."""
        self._event_counts: dict[str, int] = {}
        self._events_by_type: dict[str, list[Event]] = {}

    @property
    def subscribed_types(self) -> tuple[EventType, ...]:
        """Return all event types."""
        return ()

    def handle(self, event: Event) -> None:
        """Collect metrics for the event.

        Args:
            event: The event to collect metrics for.
        """
        event_type = event.type.value
        self._event_counts[event_type] = self._event_counts.get(event_type, 0) + 1

        if event_type not in self._events_by_type:
            self._events_by_type[event_type] = []
        self._events_by_type[event_type].append(event)

    def get_counts(self) -> dict[str, int]:
        """Get event counts by type.

        Returns:
            Dictionary mapping event type to count.
        """
        return self._event_counts.copy()

    def get_total_count(self) -> int:
        """Get total number of events.

        Returns:
            Total event count.
        """
        return sum(self._event_counts.values())

    def get_events(self, event_type: EventType) -> list[Event]:
        """Get all events of a specific type.

        Args:
            event_type: The event type to retrieve.

        Returns:
            List of events of that type.
        """
        return self._events_by_type.get(event_type.value, []).copy()
