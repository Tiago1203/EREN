"""Execution Events for EREN OS Cognitive Execution Coordinator.

Publishes execution events to the Event Bus.
"""

from __future__ import annotations

import threading
from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.PHASE_2.execution.result import ExecutionResult


class ExecutionEventType(str, Enum):
    """Event types for execution operations."""

    EXECUTION_STARTED = "execution_started"
    EXECUTION_COMPLETED = "execution_completed"
    EXECUTION_FAILED = "execution_failed"
    EXECUTION_CANCELLED = "execution_cancelled"
    SESSION_CREATED = "session_created"
    PIPELINE_SELECTED = "pipeline_selected"
    PIPELINE_STARTED = "pipeline_started"
    PIPELINE_COMPLETED = "pipeline_completed"
    CONTEXT_UPDATED = "context_updated"
    SESSION_COMPLETED = "session_completed"


class ExecutionEventPublisher:
    """Publishes execution events.

    Integrates with EREN's Event Bus to publish execution events.
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
        event_type: ExecutionEventType | str,
        result: ExecutionResult | None = None,
        execution_id: str = "",
        session_id: str = "",
        correlation_id: str = "",
        **kwargs,
    ) -> None:
        """Publish an execution event.

        Args:
            event_type: Type of event.
            result: Execution result.
            execution_id: Execution ID.
            session_id: Session ID.
            correlation_id: Correlation ID.
            **kwargs: Additional event data.
        """
        event_type_str = event_type.value if isinstance(event_type, Enum) else event_type

        event = {
            "event_type": event_type_str,
            "timestamp": datetime.now(UTC).isoformat(),
            "execution_id": execution_id,
            "session_id": session_id,
            "correlation_id": correlation_id,
            "kwargs": kwargs,
        }

        if result:
            event["result"] = {
                "status": result.status.value,
                "duration_ms": result.duration_ms,
                "selected_pipeline": result.selected_pipeline,
            }

        with self._lock:
            self._event_history.append(event)

        # Publish to Event Bus if available
        if self._event_bus:
            try:
                from core.PHASE_1.infrastructure.events.models import Event
                self._event_bus.publish(Event(
                    type=self._map_to_core_event_type(event_type),
                    source="execution",
                    correlation_id=correlation_id,
                    session_id=session_id,
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

    def _map_to_core_event_type(self, event_type: ExecutionEventType) -> EventType:
        """Map execution event to core event type.

        Args:
            event_type: Execution event type.

        Returns:
            Mapped core EventType.
        """
        from core.PHASE_1.infrastructure.events.models import EventType

        mapping = {
            ExecutionEventType.EXECUTION_STARTED: EventType.PLAN_CREATED,
            ExecutionEventType.EXECUTION_COMPLETED: EventType.PLAN_COMPLETED,
            ExecutionEventType.EXECUTION_FAILED: EventType.PLAN_FAILED,
        }

        return mapping.get(event_type, EventType.PLAN_CREATED)

    def subscribe(self, callback: callable) -> None:
        """Subscribe to execution events.

        Args:
            callback: Function to call with each event.
        """
        with self._lock:
            if callback not in self._subscribers:
                self._subscribers.append(callback)

    def unsubscribe(self, callback: callable) -> None:
        """Unsubscribe from execution events.

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


# Global event publisher
_event_publisher: ExecutionEventPublisher | None = None
_publisher_lock = threading.Lock()


def get_execution_event_publisher() -> ExecutionEventPublisher:
    """Get the global execution event publisher.

    Returns:
        Global ExecutionEventPublisher instance.
    """
    global _event_publisher
    with _publisher_lock:
        if _event_publisher is None:
            _event_publisher = ExecutionEventPublisher()
        return _event_publisher
