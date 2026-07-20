"""Cognitive Scheduler (CS).

The scheduling component of EREN. Coordinates task execution timing
for cognitive engines.

Architecture only -- no implementations, no business logic.
"""

from __future__ import annotations

from core.scheduler.exceptions import (
    CapacityExceededError,
    DependencyError,
    InvalidTaskStateError,
    QueueFullError,
    SchedulingError,
    StrategyError,
    TaskAlreadyScheduledError,
    TaskNotFoundError,
    TaskTimeoutError,
)
from core.scheduler.scheduler import (
    CognitiveScheduler,
    SchedulerFactory,
)
from core.scheduler.scheduling_events import (
    SchedulingEventPublisher,
    SchedulingEventType,
)
from core.scheduler.scheduling_metrics import (
    SchedulingHealthCheck,
    SchedulingMetricsCollector,
)
from core.scheduler.scheduling_policy import (
    CapacityPolicy,
    PolicyPresets,
    QueuePolicy,
    RetryPolicy,
    SchedulingPolicy,
    TimeoutPolicy,
)
from core.scheduler.scheduling_queue import (
    MultiQueueManager,
    QueueEntry,
    QueueStatistics,
    SchedulingQueue,
)
from core.scheduler.scheduling_strategy import (
    CriticalFirstStrategy,
    DeadlineFirstStrategy,
    FairSchedulingStrategy,
    FIFOStrategy,
    PriorityStrategy,
    SchedulingStrategy,
    StrategyFactory,
)
from core.scheduler.scheduling_trace import (
    SchedulingTraceCollector,
    SchedulingTraceEntry,
)
from core.scheduler.scheduling_types import (
    VALID_TASK_TRANSITIONS,
    CognitiveTask,
    QueueStatistics,
    SchedulingDecision,
    TaskDependencies,
    TaskMetadata,
    TaskPriority,
    TaskState,
    TaskType,
)

__all__ = [
    # Core Engine
    "CognitiveScheduler",
    "SchedulerFactory",
    # Types
    "CognitiveTask",
    "TaskMetadata",
    "TaskDependencies",
    "TaskState",
    "TaskPriority",
    "TaskType",
    "SchedulingDecision",
    "VALID_TASK_TRANSITIONS",
    # Queue
    "SchedulingQueue",
    "MultiQueueManager",
    "QueueEntry",
    "QueueStatistics",
    # Strategy
    "SchedulingStrategy",
    "FIFOStrategy",
    "PriorityStrategy",
    "DeadlineFirstStrategy",
    "CriticalFirstStrategy",
    "FairSchedulingStrategy",
    "StrategyFactory",
    # Policy
    "SchedulingPolicy",
    "TimeoutPolicy",
    "RetryPolicy",
    "QueuePolicy",
    "CapacityPolicy",
    "PolicyPresets",
    # Events
    "SchedulingEventPublisher",
    "SchedulingEventType",
    # Metrics
    "SchedulingMetricsCollector",
    "SchedulingHealthCheck",
    # Trace
    "SchedulingTraceCollector",
    "SchedulingTraceEntry",
    # Exceptions
    "SchedulingError",
    "TaskNotFoundError",
    "TaskAlreadyScheduledError",
    "InvalidTaskStateError",
    "CapacityExceededError",
    "QueueFullError",
    "TaskTimeoutError",
    "DependencyError",
    "StrategyError",
]
