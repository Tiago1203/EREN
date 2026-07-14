"""Router Events for EREN OS Cognitive Capability Router.

Publishes router events to the Event Bus.
"""

from __future__ import annotations

import threading
from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.router.context import RouterContext
    from core.router.result import RoutingResult
    from core.router.router import CapabilityRouter


class RouterEventType(str, Enum):
    """Event types for router operations."""

    ROUTING_STARTED = "routing_started"
    ROUTING_COMPLETED = "routing_completed"
    ROUTING_FAILED = "routing_failed"
    ROUTING_CANCELLED = "routing_cancelled"
    PIPELINE_MATCHED = "pipeline_matched"
    PIPELINE_SELECTED = "pipeline_selected"
    PIPELINE_REJECTED = "pipeline_rejected"
    FALLBACK_ACTIVATED = "fallback_activated"
    RULE_EVALUATED = "rule_evaluated"


class RouterEventPublisher:
    """Publishes router events.

    Integrates with EREN's Event Bus to publish router events.
    """

    def __init__(self, event_bus=None):
        """Initialize the event publisher.

        Args:
            event_bus: Optional Event Bus instance.
        """
        self._event_bus = event_bus
        self._event_history: list[dict] = []
        self._lock = threading.RLock()
        self._subscribers: list[callable] = []

    def set_event_bus(self, event_bus) -> None:
        """Set the Event Bus instance.

        Args:
            event_bus: Event Bus to use.
        """
        self._event_bus = event_bus

    def publish(
        self,
        event_type: RouterEventType | str,
        router: CapabilityRouter | None = None,
        context: RouterContext | None = None,
        result: RoutingResult | None = None,
        **kwargs,
    ) -> None:
        """Publish a router event.

        Args:
            event_type: Type of event.
            router: Router instance.
            context: Routing context.
            result: Routing result.
            **kwargs: Additional event data.
        """
        event_type_str = event_type.value if isinstance(event_type, Enum) else event_type

        event = {
            "event_type": event_type_str,
            "timestamp": datetime.now(UTC).isoformat(),
            "router_state": router.state.value if router else "",
            "correlation_id": context.correlation_id if context else "",
            "session_id": context.session_id if context else "",
            "kwargs": kwargs,
        }

        if context:
            event["intent_type"] = context.intent_type

        if result:
            event["result"] = {
                "state": result.state.value,
                "selected_pipeline": (
                    result.selected_pipeline.pipeline_name
                    if result.selected_pipeline else None
                ),
                "candidate_count": result.candidate_count,
                "duration_ms": result.duration_ms,
            }

        with self._lock:
            self._event_history.append(event)

        # Publish to Event Bus if available
        if self._event_bus:
            try:
                from core.events.models import Event
                self._event_bus.publish(Event(
                    type=self._map_to_core_event_type(event_type),
                    source="router",
                    correlation_id=event["correlation_id"],
                    session_id=event["session_id"],
                    payload=event,
                ))
            except Exception:
                pass

        # Notify subscribers
        for subscriber in self._subscribers:
            try:
                subscriber(event)
            except Exception:
                pass

    def _map_to_core_event_type(self, event_type: RouterEventType) -> EventType:
        """Map router event to core event type.

        Args:
            event_type: Router event type.

        Returns:
            Mapped core EventType.
        """
        from core.events.models import EventType

        mapping = {
            RouterEventType.ROUTING_STARTED: EventType.PLAN_CREATED,
            RouterEventType.ROUTING_COMPLETED: EventType.PLAN_COMPLETED,
            RouterEventType.ROUTING_FAILED: EventType.PLAN_FAILED,
        }

        return mapping.get(event_type, EventType.PLAN_CREATED)

    def subscribe(self, callback: callable) -> None:
        """Subscribe to router events.

        Args:
            callback: Function to call with each event.
        """
        with self._lock:
            if callback not in self._subscribers:
                self._subscribers.append(callback)

    def unsubscribe(self, callback: callable) -> None:
        """Unsubscribe from router events.

        Args:
            callback: Function to remove.
        """
        with self._lock:
            if callback in self._subscribers:
                self._subscribers.remove(callback)

    def get_event_history(self) -> list[dict]:
        """Get history of published events.

        Returns:
            List of event dictionaries.
        """
        with self._lock:
            return list(self._event_history)

    def clear_history(self) -> None:
        """Clear event history."""
        with self._lock:
            self._event_history.clear()


# Convenience functions
_publisher: RouterEventPublisher | None = None
_publisher_lock = threading.Lock()


def get_router_event_publisher() -> RouterEventPublisher:
    """Get the global router event publisher.

    Returns:
        Global RouterEventPublisher instance.
    """
    global _publisher
    with _publisher_lock:
        if _publisher is None:
            _publisher = RouterEventPublisher()
        return _publisher


def publish_router_event(
    event_type: RouterEventType,
    router: CapabilityRouter | None = None,
    context: RouterContext | None = None,
    result: RoutingResult | None = None,
) -> None:
    """Publish a router event.

    Args:
        event_type: Type of event.
        router: Router instance.
        context: Routing context.
        result: Routing result.
    """
    get_router_event_publisher().publish(
        event_type,
        router,
        context,
        result,
    )
