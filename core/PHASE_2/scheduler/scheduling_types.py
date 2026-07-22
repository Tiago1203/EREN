"""Type definitions for the Cognitive Scheduler.

Provides comprehensive type definitions for scheduling operations.

Architecture only -- no implementations, no business logic.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass


# =============================================================================
# Task States
# =============================================================================


class TaskState(str, Enum):
    """States of a cognitive task."""

    PENDING = "pending"  # Task created, waiting
    READY = "ready"  # Task ready to execute
    RUNNING = "running"  # Task executing
    WAITING = "waiting"  # Waiting for dependencies
    BLOCKED = "blocked"  # Blocked by resource
    COMPLETED = "completed"  # Successfully completed
    FAILED = "failed"  # Failed
    CANCELLED = "cancelled"  # Cancelled


# =============================================================================
# Task Priority
# =============================================================================


class TaskPriority(int, Enum):
    """Priority levels for tasks."""

    CRITICAL = 1  # Critical priority
    HIGH = 2  # High priority
    NORMAL = 3  # Normal priority
    LOW = 4  # Low priority
    BACKGROUND = 5  # Background priority


# =============================================================================
# Task Types
# =============================================================================


class TaskType(str, Enum):
    """Types of cognitive tasks."""

    PLANNING = "planning"  # Planning task
    KNOWLEDGE_QUERY = "knowledge_query"  # Knowledge query
    MEMORY_QUERY = "memory_query"  # Memory query
    REASONING = "reasoning"  # Reasoning task
    DECISION = "decision"  # Decision task
    TOOL_EXECUTION = "tool_execution"  # Tool execution
    CONTEXT_UPDATE = "context_update"  # Context update
    EVENT_PROCESSING = "event_processing"  # Event processing


# =============================================================================
# Cognitive Task
# =============================================================================


@dataclass(frozen=True)
class TaskMetadata:
    """Metadata for a task."""

    task_id: str
    session_id: str
    correlation_id: str
    created_at: str = ""
    started_at: str = ""
    completed_at: str = ""
    metadata: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Set timestamps if not provided."""
        if not self.created_at:
            object.__setattr__(self, 'created_at', datetime.now(UTC).isoformat())


@dataclass(frozen=True)
class TaskDependencies:
    """Task dependencies."""

    depends_on: tuple[str, ...] = field(default_factory=tuple)  # Task IDs
    required_capabilities: tuple[str, ...] = field(default_factory=tuple)
    required_resources: tuple[str, ...] = field(default_factory=tuple)


@dataclass
class CognitiveTask:
    """A cognitive task for scheduling.

    Represents a unit of work that the Scheduler coordinates
    for execution by the appropriate capability.
    """

    # Core identifiers
    metadata: TaskMetadata

    # Task details
    task_type: TaskType
    capability: str  # Capability to execute
    parameters: dict = field(default_factory=dict)

    # Priority and scheduling
    priority: TaskPriority = TaskPriority.NORMAL
    deadline: str = ""  # ISO timestamp
    created_at: str = ""

    # Dependencies
    dependencies: TaskDependencies = field(default_factory=TaskDependencies)

    # State
    state: TaskState = TaskState.PENDING

    # Execution tracking
    retries: int = 0
    max_retries: int = 3
    timeout_ms: int = 30000
    execution_time_ms: int = 0
    assigned_to: str = ""  # Capability instance

    # Result
    result: Any = None
    error: str = ""

    def __post_init__(self) -> None:
        """Set timestamps if not provided."""
        if not self.created_at:
            self.created_at = datetime.now(UTC).isoformat()
        if not self.metadata.created_at:
            self.metadata.created_at = self.created_at

    @property
    def is_completed(self) -> bool:
        """Check if task is completed."""
        return self.state in (TaskState.COMPLETED, TaskState.FAILED, TaskState.CANCELLED)

    @property
    def can_retry(self) -> bool:
        """Check if task can be retried."""
        return self.retries < self.max_retries and self.state == TaskState.FAILED

    def mark_running(self, assigned_to: str) -> None:
        """Mark task as running."""
        self.state = TaskState.RUNNING
        self.assigned_to = assigned_to
        self.metadata.started_at = datetime.now(UTC).isoformat()

    def mark_completed(self, result: Any = None) -> None:
        """Mark task as completed."""
        self.state = TaskState.COMPLETED
        self.result = result
        self.metadata.completed_at = datetime.now(UTC).isoformat()
        duration = datetime.fromisoformat(self.metadata.completed_at) - datetime.fromisoformat(self.metadata.started_at)
        self.execution_time_ms = int(duration.total_seconds() * 1000)

    def mark_failed(self, error: str) -> None:
        """Mark task as failed."""
        self.state = TaskState.FAILED
        self.error = error
        self.retries += 1
        self.metadata.completed_at = datetime.now(UTC).isoformat()

    def mark_cancelled(self) -> None:
        """Mark task as cancelled."""
        self.state = TaskState.CANCELLED
        self.metadata.completed_at = datetime.now(UTC).isoformat()

    def mark_ready(self) -> None:
        """Mark task as ready."""
        self.state = TaskState.READY

    def mark_waiting(self) -> None:
        """Mark task as waiting."""
        self.state = TaskState.WAITING

    def mark_blocked(self) -> None:
        """Mark task as blocked."""
        self.state = TaskState.BLOCKED


# =============================================================================
# Scheduling Decision
# =============================================================================


@dataclass(frozen=True)
class SchedulingDecision:
    """A scheduling decision."""

    decision_id: str
    task_id: str
    selected_capability: str
    reason: str
    queue_position: int
    estimated_wait_ms: int
    timestamp: str = ""

    def __post_init__(self) -> None:
        """Set timestamp if not provided."""
        if not self.timestamp:
            object.__setattr__(self, 'timestamp', datetime.now(UTC).isoformat())


# =============================================================================
# Queue Statistics
# =============================================================================


@dataclass
class QueueStatistics:
    """Statistics for a scheduling queue."""

    total_tasks: int = 0
    pending_tasks: int = 0
    ready_tasks: int = 0
    running_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    average_wait_time_ms: float = 0.0
    average_execution_time_ms: float = 0.0

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "total_tasks": self.total_tasks,
            "pending_tasks": self.pending_tasks,
            "ready_tasks": self.ready_tasks,
            "running_tasks": self.running_tasks,
            "completed_tasks": self.completed_tasks,
            "failed_tasks": self.failed_tasks,
            "average_wait_time_ms": self.average_wait_time_ms,
            "average_execution_time_ms": self.average_execution_time_ms,
        }


# =============================================================================
# Valid State Transitions
# =============================================================================


VALID_TASK_TRANSITIONS: dict[TaskState, tuple[TaskState, ...]] = {
    TaskState.PENDING: (
        TaskState.READY,
        TaskState.WAITING,
        TaskState.BLOCKED,
        TaskState.CANCELLED,
    ),
    TaskState.READY: (
        TaskState.RUNNING,
        TaskState.CANCELLED,
    ),
    TaskState.RUNNING: (
        TaskState.COMPLETED,
        TaskState.FAILED,
        TaskState.WAITING,
        TaskState.CANCELLED,
    ),
    TaskState.WAITING: (
        TaskState.READY,
        TaskState.BLOCKED,
        TaskState.CANCELLED,
    ),
    TaskState.BLOCKED: (
        TaskState.READY,
        TaskState.WAITING,
        TaskState.CANCELLED,
    ),
    TaskState.COMPLETED: (),
    TaskState.FAILED: (
        TaskState.PENDING,
        TaskState.READY,
        TaskState.CANCELLED,
    ),
    TaskState.CANCELLED: (),
}
