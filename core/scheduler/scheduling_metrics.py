"""Metrics for the Cognitive Scheduler.

Collects and calculates scheduling metrics.

Architecture only -- no implementations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class SchedulingMetricsCollector:
    """Collects scheduling metrics."""

    tasks_submitted: int = 0
    tasks_scheduled: int = 0
    tasks_completed: int = 0
    tasks_failed: int = 0
    tasks_cancelled: int = 0
    tasks_retried: int = 0
    tasks_in_queue: int = 0
    peak_queue_size: int = 0
    total_execution_time_ms: int = 0
    average_execution_time_ms: float = 0.0
    peak_execution_time_ms: int = 0
    scheduling_decisions: int = 0
    strategy_changes: int = 0
    capabilities_reserved: int = 0
    capabilities_released: int = 0
    capacity_exceeded_count: int = 0

    def record_task_submitted(self) -> None:
        """Record a task submission."""
        self.tasks_submitted += 1
        self.tasks_in_queue += 1
        if self.tasks_in_queue > self.peak_queue_size:
            self.peak_queue_size = self.tasks_in_queue

    def record_task_scheduled(self) -> None:
        """Record a task scheduling."""
        self.tasks_scheduled += 1

    def record_task_completed(self, execution_time_ms: int) -> None:
        """Record a task completion."""
        self.tasks_completed += 1
        self.tasks_in_queue = max(0, self.tasks_in_queue - 1)
        self.total_execution_time_ms += execution_time_ms
        if self.tasks_completed > 0:
            self.average_execution_time_ms = (
                self.total_execution_time_ms / self.tasks_completed
            )
        if execution_time_ms > self.peak_execution_time_ms:
            self.peak_execution_time_ms = execution_time_ms

    def record_task_failed(self) -> None:
        """Record a task failure."""
        self.tasks_failed += 1
        self.tasks_in_queue = max(0, self.tasks_in_queue - 1)

    def record_task_cancelled(self) -> None:
        """Record a task cancellation."""
        self.tasks_cancelled += 1
        self.tasks_in_queue = max(0, self.tasks_in_queue - 1)

    def record_task_retry(self) -> None:
        """Record a task retry."""
        self.tasks_retried += 1

    def record_scheduling_decision(self) -> None:
        """Record a scheduling decision."""
        self.scheduling_decisions += 1

    def record_strategy_change(self) -> None:
        """Record a strategy change."""
        self.strategy_changes += 1

    def record_capacity_reserved(self) -> None:
        """Record a capability reservation."""
        self.capabilities_reserved += 1

    def record_capacity_released(self) -> None:
        """Record a capability release."""
        self.capabilities_released += 1

    def record_capacity_exceeded(self) -> None:
        """Record a capacity exceeded event."""
        self.capacity_exceeded_count += 1

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "tasks_submitted": self.tasks_submitted,
            "tasks_scheduled": self.tasks_scheduled,
            "tasks_completed": self.tasks_completed,
            "tasks_failed": self.tasks_failed,
            "tasks_cancelled": self.tasks_cancelled,
            "tasks_retried": self.tasks_retried,
            "tasks_in_queue": self.tasks_in_queue,
            "peak_queue_size": self.peak_queue_size,
            "average_execution_time_ms": self.average_execution_time_ms,
            "peak_execution_time_ms": self.peak_execution_time_ms,
            "scheduling_decisions": self.scheduling_decisions,
            "strategy_changes": self.strategy_changes,
            "capabilities_reserved": self.capabilities_reserved,
            "capabilities_released": self.capabilities_released,
            "capacity_exceeded_count": self.capacity_exceeded_count,
        }


@dataclass
class SchedulingHealthCheck:
    """Health check for the scheduler."""

    is_healthy: bool = True
    queue_size: int = 0
    tasks_completed: int = 0
    tasks_failed: int = 0
    error_rate: float = 0.0
    average_execution_time_ms: float = 0.0
    warnings: tuple[str, ...] = field(default_factory=tuple)
    checked_at: str = ""

    def __post_init__(self) -> None:
        """Set timestamp."""
        object.__setattr__(self, 'checked_at', datetime.now(timezone.utc).isoformat())
