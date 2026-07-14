"""Pipeline Events for EREN OS Cognitive Capability Pipeline.

Publishes pipeline events to the Event Bus.
"""

from __future__ import annotations

import threading
from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.pipeline.context import PipelineContext
    from core.pipeline.pipeline import CognitivePipeline
    from core.pipeline.types import PipelineResult


class PipelineEventType(str, Enum):
    """Event types for pipeline operations."""

    PIPELINE_CREATED = "pipeline_created"
    PIPELINE_READY = "pipeline_ready"
    PIPELINE_STARTED = "pipeline_started"
    PIPELINE_PAUSED = "pipeline_paused"
    PIPELINE_RESUMED = "pipeline_resumed"
    PIPELINE_CANCELLED = "pipeline_cancelled"
    PIPELINE_COMPLETED = "pipeline_completed"
    PIPELINE_FAILED = "pipeline_failed"
    STAGE_STARTED = "stage_started"
    STAGE_COMPLETED = "stage_completed"
    STAGE_SKIPPED = "stage_skipped"
    STAGE_FAILED = "stage_failed"
    STAGE_CANCELLED = "stage_cancelled"
    PIPELINE_VALIDATED = "pipeline_validated"
    PIPELINE_EXECUTION_STARTED = "pipeline_execution_started"
    PIPELINE_EXECUTION_FINISHED = "pipeline_execution_finished"


class PipelineEventPublisher:
    """Publishes pipeline events.

    Integrates with EREN's Event Bus to publish pipeline events.
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
        event_type: PipelineEventType | str,
        pipeline: CognitivePipeline | None = None,
        context: PipelineContext | None = None,
        result: PipelineResult | None = None,
        **kwargs,
    ) -> None:
        """Publish a pipeline event.

        Args:
            event_type: Type of event.
            pipeline: Pipeline instance.
            context: Pipeline context.
            result: Pipeline result.
            **kwargs: Additional event data.
        """
        event_type_str = event_type.value if isinstance(event_type, Enum) else event_type

        event = {
            "event_type": event_type_str,
            "timestamp": datetime.now(UTC).isoformat(),
            "pipeline_id": pipeline.pipeline_id if pipeline else "",
            "pipeline_name": pipeline.name if pipeline else "",
            "correlation_id": context.correlation_id if context else "",
            "session_id": context.session_id if context else "",
            "kwargs": kwargs,
        }

        if result:
            event["result"] = {
                "status": result.status.value,
                "duration_ms": result.duration_ms,
                "stage_count": len(result.stage_results),
            }

        with self._lock:
            self._event_history.append(event)

        # Publish to Event Bus if available
        if self._event_bus:
            try:
                from core.events.models import Event
                self._event_bus.publish(Event(
                    type=self._map_to_core_event_type(event_type),
                    source="pipeline",
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

    def _map_to_core_event_type(self, event_type: PipelineEventType) -> EventType:
        """Map pipeline event to core event type.

        Args:
            event_type: Pipeline event type.

        Returns:
            Mapped core EventType.
        """
        from core.events.models import EventType

        mapping = {
            PipelineEventType.PIPELINE_STARTED: EventType.PLAN_CREATED,
            PipelineEventType.PIPELINE_COMPLETED: EventType.PLAN_COMPLETED,
            PipelineEventType.PIPELINE_FAILED: EventType.PLAN_FAILED,
        }

        return mapping.get(event_type, EventType.PLAN_CREATED)

    def subscribe(self, callback: callable) -> None:
        """Subscribe to pipeline events.

        Args:
            callback: Function to call with each event.
        """
        with self._lock:
            if callback not in self._subscribers:
                self._subscribers.append(callback)

    def unsubscribe(self, callback: callable) -> None:
        """Unsubscribe from pipeline events.

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
_publisher: PipelineEventPublisher | None = None
_publisher_lock = threading.Lock()


def get_pipeline_event_publisher() -> PipelineEventPublisher:
    """Get the global pipeline event publisher.

    Returns:
        Global PipelineEventPublisher instance.
    """
    global _publisher
    with _publisher_lock:
        if _publisher is None:
            _publisher = PipelineEventPublisher()
        return _publisher


def publish_pipeline_event(
    event_type: PipelineEventType,
    pipeline: CognitivePipeline | None = None,
    context: PipelineContext | None = None,
    result: PipelineResult | None = None,
) -> None:
    """Publish a pipeline event.

    Args:
        event_type: Type of event.
        pipeline: Pipeline instance.
        context: Pipeline context.
        result: Pipeline result.
    """
    get_pipeline_event_publisher().publish(
        event_type,
        pipeline,
        context,
        result,
    )
