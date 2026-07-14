"""Workflow metrics for EREN Cognitive Workflow Engine.

Metrics collection for workflows.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass


@dataclass
class WorkflowMetrics:
    """Workflow execution metrics."""

    workflows_created: int = 0
    workflows_completed: int = 0
    workflows_failed: int = 0
    workflows_cancelled: int = 0
    workflows_paused: int = 0

    total_executions: int = 0
    total_nodes_executed: int = 0
    total_checkpoints_created: int = 0

    avg_duration_seconds: float = 0.0
    avg_progress_percent: float = 0.0

    # By type
    by_type: dict[str, int] = field(default_factory=dict)

    # By status
    by_status: dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "workflows_created": self.workflows_created,
            "workflows_completed": self.workflows_completed,
            "workflows_failed": self.workflows_failed,
            "workflows_cancelled": self.workflows_cancelled,
            "workflows_paused": self.workflows_paused,
            "total_executions": self.total_executions,
            "total_nodes_executed": self.total_nodes_executed,
            "total_checkpoints_created": self.total_checkpoints_created,
            "avg_duration_seconds": self.avg_duration_seconds,
            "avg_progress_percent": self.avg_progress_percent,
            "by_type": self.by_type,
            "by_status": self.by_status,
        }

    def get_completion_rate(self) -> float:
        """Get completion rate.

        Returns:
            Completion rate as percentage.
        """
        if self.total_executions == 0:
            return 0.0
        return (self.workflows_completed / self.total_executions) * 100

    def get_success_rate(self) -> float:
        """Get success rate.

        Returns:
            Success rate as percentage.
        """
        if self.workflows_completed + self.workflows_failed == 0:
            return 0.0
        total = self.workflows_completed + self.workflows_failed
        return (self.workflows_completed / total) * 100


class MetricsCollector:
    """Collects workflow metrics.

    The Metrics Collector does NOT:
    - Execute tasks
    - Know about implementations

    It ONLY:
    - Collects metrics
    - Aggregates statistics
    - Tracks performance
    """

    def __init__(self):
        """Initialize metrics collector."""
        self._durations: list[float] = []
        self._progress: list[float] = []

    def record_duration(self, duration_seconds: float) -> None:
        """Record execution duration.

        Args:
            duration_seconds: Duration in seconds.
        """
        self._durations.append(duration_seconds)

    def record_progress(self, progress_percent: float) -> None:
        """Record progress percentage.

        Args:
            progress_percent: Progress percentage.
        """
        self._progress.append(progress_percent)

    def get_avg_duration(self) -> float:
        """Get average duration.

        Returns:
            Average duration in seconds.
        """
        if not self._durations:
            return 0.0
        return sum(self._durations) / len(self._durations)

    def get_avg_progress(self) -> float:
        """Get average progress.

        Returns:
            Average progress percentage.
        """
        if not self._progress:
            return 0.0
        return sum(self._progress) / len(self._progress)

    def clear(self) -> None:
        """Clear collected metrics."""
        self._durations.clear()
        self._progress.clear()


# Global metrics collector
_metrics_collector: MetricsCollector | None = None
_metrics_lock = __import__("threading").Lock()


def get_metrics_collector() -> MetricsCollector:
    """Get the global metrics collector.

    Returns:
        Global MetricsCollector instance.
    """
    global _metrics_collector
    with _metrics_lock:
        if _metrics_collector is None:
            _metrics_collector = MetricsCollector()
        return _metrics_collector


def reset_metrics_collector() -> None:
    """Reset the global metrics collector."""
    global _metrics_collector
    with _metrics_lock:
        _metrics_collector = None
