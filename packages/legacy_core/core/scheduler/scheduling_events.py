"""Events for the Cognitive Scheduler.

Defines all scheduling events.

Architecture only -- no implementations.
"""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass


# =============================================================================
# Event Types
# =============================================================================


class SchedulingEventType(str, Enum):
    """Types of scheduling events."""

    # Task lifecycle
    TASK_SUBMITTED = "TaskSubmitted"
    TASK_SCHEDULED = "TaskScheduled"
    TASK_STARTED = "TaskStarted"
    TASK_COMPLETED = "TaskCompleted"
    TASK_FAILED = "TaskFailed"
    TASK_CANCELLED = "TaskCancelled"
    TASK_RETRY = "TaskRetry"

    # Queue events
    TASK_ENQUEUED = "TaskEnqueued"
    TASK_DEQUEUED = "TaskDequeued"
    TASK_REQUEUED = "TaskRequeued"

    # Scheduling events
    SCHEDULING_DECISION = "SchedulingDecision"
    SCHEDULING_STRATEGY_CHANGED = "SchedulingStrategyChanged"

    # Capacity events
    CAPABILITY_RESERVED = "CapabilityReserved"
    CAPABILITY_RELEASED = "CapabilityReleased"
    CAPACITY_EXCEEDED = "CapacityExceeded"

    # Queue events
    QUEUE_CLEARED = "QueueCleared"
    QUEUE_STATS_UPDATED = "QueueStatsUpdated"


# =============================================================================
# Event Publisher
# =============================================================================


class SchedulingEventPublisher:
    """Publishes scheduling events."""

    def __init__(self) -> None:
        """Initialize the publisher."""
        self._enabled = True
        self._events_published = 0

    def publish(
        self,
        event_type: str,
        **data: Any,
    ) -> None:
        """Publish an event.

        Args:
            event_type: Type of event.
            **data: Event data.
        """
        self._events_published += 1

    @property
    def events_published(self) -> int:
        """Get number of events published."""
        return self._events_published

    def disable(self) -> None:
        """Disable event publishing."""
        self._enabled = False

    def enable(self) -> None:
        """Enable event publishing."""
        self._enabled = True
