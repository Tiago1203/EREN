"""Execution Metrics for EREN OS Cognitive Execution Coordinator.

Collects and reports execution metrics.
"""

from __future__ import annotations

import threading
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone

from core.execution.result import ExecutionResult


@dataclass
class MetricSnapshot:
    """A point-in-time metric snapshot."""

    name: str
    value: float
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    tags: dict | None = None


class ExecutionMetrics:
    """Collects and reports execution metrics.

    Tracks:
    - Total executions
    - Success/failure rates
    - Timing statistics
    - Pipeline usage
    - Component performance
    """

    def __init__(self):
        """Initialize the metrics collector."""
        self._counters: dict[str, int] = defaultdict(int)
        self._timers: dict[str, list[float]] = defaultdict(list)
        self._snapshots: list[MetricSnapshot] = []
        self._pipeline_usage: dict[str, int] = defaultdict(int)
        self._execution_durations: list[float] = []
        self._lock = threading.RLock()
        self._start_time: datetime | None = None

    def start(self) -> None:
        """Start metrics collection."""
        with self._lock:
            self._start_time = datetime.now(timezone.utc)

    def record_execution(self, result: ExecutionResult) -> None:
        """Record execution metrics.

        Args:
            result: Execution result.
        """
        with self._lock:
            # Counters
            self._counters["executions_total"] += 1
            self._execution_durations.append(result.duration_ms)

            if result.is_success:
                self._counters["executions_succeeded"] += 1
            elif result.was_cancelled:
                self._counters["executions_cancelled"] += 1
            else:
                self._counters["executions_failed"] += 1

            # Pipeline usage
            if result.selected_pipeline:
                self._pipeline_usage[result.selected_pipeline] += 1

            # Timing
            self._timers["session_creation"].append(result.session_creation_time_ms)
            self._timers["routing"].append(result.routing_time_ms)
            self._timers["pipeline"].append(result.pipeline_time_ms)
            self._timers["context_update"].append(result.context_update_time_ms)
            self._timers["session_completion"].append(result.session_completion_time_ms)

            # Errors
            self._counters["errors_total"] += len(result.errors)
            self._counters["warnings_total"] += len(result.warnings)

            # Snapshot
            self._snapshots.append(MetricSnapshot(
                name="execution",
                value=result.duration_ms,
                tags={
                    "status": result.status.value,
                    "pipeline": result.selected_pipeline,
                },
            ))

    def record_session_creation(self, duration_ms: int) -> None:
        """Record session creation timing.

        Args:
            duration_ms: Duration in milliseconds.
        """
        with self._lock:
            self._timers["session_creation"].append(float(duration_ms))
            self._counters["sessions_created"] += 1

    def record_routing(self, duration_ms: int) -> None:
        """Record routing timing.

        Args:
            duration_ms: Duration in milliseconds.
        """
        with self._lock:
            self._timers["routing"].append(float(duration_ms))

    def record_pipeline_execution(self, duration_ms: int, pipeline_name: str = "") -> None:
        """Record pipeline execution timing.

        Args:
            duration_ms: Duration in milliseconds.
            pipeline_name: Name of the pipeline.
        """
        with self._lock:
            self._timers["pipeline"].append(float(duration_ms))
            if pipeline_name:
                self._pipeline_usage[pipeline_name] += 1

    def record_context_update(self, duration_ms: int) -> None:
        """Record context update timing.

        Args:
            duration_ms: Duration in milliseconds.
        """
        with self._lock:
            self._timers["context_update"].append(float(duration_ms))

    def increment(self, name: str, value: int = 1) -> None:
        """Increment a counter.

        Args:
            name: Metric name.
            value: Increment value.
        """
        with self._lock:
            self._counters[name] += value

    def record_time(self, name: str, duration_ms: float) -> None:
        """Record a timing metric.

        Args:
            name: Metric name.
            duration_ms: Duration in milliseconds.
        """
        with self._lock:
            self._timers[name].append(duration_ms)

    def get_counter(self, name: str) -> int:
        """Get counter value.

        Args:
            name: Counter name.

        Returns:
            Counter value.
        """
        with self._lock:
            return self._counters.get(name, 0)

    def get_execution_success_rate(self) -> float:
        """Get execution success rate.

        Returns:
            Success rate as percentage (0-100).
        """
        with self._lock:
            total = self._counters.get("executions_total", 0)
            if total == 0:
                return 0.0
            succeeded = self._counters.get("executions_succeeded", 0)
            return succeeded / total * 100

    def get_average_execution_duration(self) -> float:
        """Get average execution duration.

        Returns:
            Average duration in milliseconds.
        """
        with self._lock:
            if not self._execution_durations:
                return 0.0
            return sum(self._execution_durations) / len(self._execution_durations)

    def get_average_timing(self, name: str) -> float:
        """Get average timing for a specific metric.

        Args:
            name: Metric name.

        Returns:
            Average duration in milliseconds.
        """
        with self._lock:
            timings = self._timers.get(name, [])
            if not timings:
                return 0.0
            return sum(timings) / len(timings)

    def get_most_used_pipeline(self) -> tuple[str, int] | None:
        """Get most used pipeline.

        Returns:
            Tuple of (pipeline_name, count) or None.
        """
        with self._lock:
            if not self._pipeline_usage:
                return None
            name = max(self._pipeline_usage, key=self._pipeline_usage.get)
            return name, self._pipeline_usage[name]

    def get_pipeline_usage(self) -> dict[str, int]:
        """Get pipeline usage statistics.

        Returns:
            Dictionary of pipeline_name -> usage count.
        """
        with self._lock:
            return dict(self._pipeline_usage)

    def get_summary(self) -> dict:
        """Get metrics summary.

        Returns:
            Dictionary with metrics summary.
        """
        with self._lock:
            summary = {
                "counters": dict(self._counters),
                "execution_stats": {
                    "total": self._counters.get("executions_total", 0),
                    "succeeded": self._counters.get("executions_succeeded", 0),
                    "failed": self._counters.get("executions_failed", 0),
                    "cancelled": self._counters.get("executions_cancelled", 0),
                    "success_rate": self.get_execution_success_rate(),
                    "avg_duration_ms": self.get_average_execution_duration(),
                },
                "timing_stats": {
                    "session_creation": self.get_average_timing("session_creation"),
                    "routing": self.get_average_timing("routing"),
                    "pipeline": self.get_average_timing("pipeline"),
                    "context_update": self.get_average_timing("context_update"),
                },
                "pipeline_stats": {
                    "most_used": self.get_most_used_pipeline(),
                    "usage": dict(self._pipeline_usage),
                },
                "snapshots_count": len(self._snapshots),
            }

            if self._start_time:
                elapsed = (datetime.now(timezone.utc) - self._start_time).total_seconds()
                summary["elapsed_seconds"] = elapsed

            return summary

    def to_dict(self) -> dict:
        """Convert to dictionary.

        Returns:
            Dictionary representation.
        """
        return self.get_summary()

    def reset(self) -> None:
        """Reset all metrics."""
        with self._lock:
            self._counters.clear()
            self._timers.clear()
            self._snapshots.clear()
            self._pipeline_usage.clear()
            self._execution_durations.clear()
            self._start_time = None


# Global metrics instance
_metrics: ExecutionMetrics | None = None
_metrics_lock = threading.Lock()


def get_execution_metrics() -> ExecutionMetrics:
    """Get the global execution metrics instance.

    Returns:
        Global ExecutionMetrics instance.
    """
    global _metrics
    with _metrics_lock:
        if _metrics is None:
            _metrics = ExecutionMetrics()
        return _metrics


def reset_execution_metrics() -> None:
    """Reset global metrics."""
    global _metrics
    with _metrics_lock:
        if _metrics is not None:
            _metrics.reset()
