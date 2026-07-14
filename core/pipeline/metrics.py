"""Pipeline Metrics for EREN OS Cognitive Capability Pipeline.

Collects and reports pipeline metrics.
"""

from __future__ import annotations

import threading
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone

from core.pipeline.types import PipelineResult, PipelineState


@dataclass
class MetricSnapshot:
    """A point-in-time metric snapshot."""

    name: str
    value: float
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    tags: dict | None = None


class PipelineMetrics:
    """Collects and reports pipeline metrics.

    Tracks:
    - Pipelines executed
    - Stages executed
    - Success/failure rates
    - Timing statistics
    - Cancellation rates
    """

    def __init__(self):
        """Initialize the metrics collector."""
        self._counters: dict[str, int] = defaultdict(int)
        self._timers: dict[str, list[float]] = defaultdict(list)
        self._snapshots: list[MetricSnapshot] = []
        self._pipeline_durations: list[float] = []
        self._stage_durations: dict[str, list[float]] = defaultdict(list)
        self._lock = threading.RLock()
        self._start_time: datetime | None = None

    def start(self) -> None:
        """Start metrics collection."""
        with self._lock:
            self._start_time = datetime.now(timezone.utc)

    def record_pipeline_execution(self, result: PipelineResult) -> None:
        """Record pipeline execution metrics.

        Args:
            result: Pipeline execution result.
        """
        with self._lock:
            # Counters
            self._counters["pipelines_executed"] += 1
            self._pipeline_durations.append(result.duration_ms)

            if result.is_success:
                self._counters["pipelines_succeeded"] += 1
            elif result.was_cancelled:
                self._counters["pipelines_cancelled"] += 1
            else:
                self._counters["pipelines_failed"] += 1

            # Stage metrics
            for stage_result in result.stage_results:
                self._counters["stages_executed"] += 1

                if stage_result.is_success:
                    self._counters["stages_succeeded"] += 1
                elif stage_result.is_skipped:
                    self._counters["stages_skipped"] += 1
                else:
                    self._counters["stages_failed"] += 1

                # Stage duration
                self._stage_durations[stage_result.stage_name].append(
                    stage_result.duration_ms
                )

            # Snapshot
            self._snapshots.append(MetricSnapshot(
                name="pipeline_execution",
                value=result.duration_ms,
                tags={
                    "status": result.status.value,
                    "stage_count": len(result.stage_results),
                },
            ))

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

    def get_pipeline_success_rate(self) -> float:
        """Get pipeline success rate.

        Returns:
            Success rate as percentage (0-100).
        """
        with self._lock:
            total = self._counters.get("pipelines_executed", 0)
            if total == 0:
                return 0.0
            succeeded = self._counters.get("pipelines_succeeded", 0)
            return succeeded / total * 100

    def get_stage_success_rate(self) -> float:
        """Get stage success rate.

        Returns:
            Success rate as percentage (0-100).
        """
        with self._lock:
            total = self._counters.get("stages_executed", 0)
            if total == 0:
                return 0.0
            succeeded = self._counters.get("stages_succeeded", 0)
            return succeeded / total * 100

    def get_average_pipeline_duration(self) -> float:
        """Get average pipeline duration.

        Returns:
            Average duration in milliseconds.
        """
        with self._lock:
            if not self._pipeline_durations:
                return 0.0
            return sum(self._pipeline_durations) / len(self._pipeline_durations)

    def get_max_pipeline_duration(self) -> float:
        """Get maximum pipeline duration.

        Returns:
            Maximum duration in milliseconds.
        """
        with self._lock:
            if not self._pipeline_durations:
                return 0.0
            return max(self._pipeline_durations)

    def get_min_pipeline_duration(self) -> float:
        """Get minimum pipeline duration.

        Returns:
            Minimum duration in milliseconds.
        """
        with self._lock:
            if not self._pipeline_durations:
                return 0.0
            return min(self._pipeline_durations)

    def get_stage_statistics(self, stage_name: str) -> dict:
        """Get statistics for a specific stage.

        Args:
            stage_name: Name of the stage.

        Returns:
            Dictionary with stage statistics.
        """
        with self._lock:
            durations = self._stage_durations.get(stage_name, [])
            if not durations:
                return {}

            return {
                "count": len(durations),
                "min_ms": min(durations),
                "max_ms": max(durations),
                "avg_ms": sum(durations) / len(durations),
            }

    def get_summary(self) -> dict:
        """Get metrics summary.

        Returns:
            Dictionary with metrics summary.
        """
        with self._lock:
            summary = {
                "counters": dict(self._counters),
                "pipeline_stats": {
                    "executed": self._counters.get("pipelines_executed", 0),
                    "succeeded": self._counters.get("pipelines_succeeded", 0),
                    "failed": self._counters.get("pipelines_failed", 0),
                    "cancelled": self._counters.get("pipelines_cancelled", 0),
                    "success_rate": self.get_pipeline_success_rate(),
                    "avg_duration_ms": self.get_average_pipeline_duration(),
                    "max_duration_ms": self.get_max_pipeline_duration(),
                    "min_duration_ms": self.get_min_pipeline_duration(),
                },
                "stage_stats": {
                    "executed": self._counters.get("stages_executed", 0),
                    "succeeded": self._counters.get("stages_succeeded", 0),
                    "failed": self._counters.get("stages_failed", 0),
                    "skipped": self._counters.get("stages_skipped", 0),
                    "success_rate": self.get_stage_success_rate(),
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
            self._pipeline_durations.clear()
            self._stage_durations.clear()
            self._start_time = None


# Global metrics instance
_metrics: PipelineMetrics | None = None
_metrics_lock = threading.Lock()


def get_pipeline_metrics() -> PipelineMetrics:
    """Get the global pipeline metrics instance.

    Returns:
        Global PipelineMetrics instance.
    """
    global _metrics
    with _metrics_lock:
        if _metrics is None:
            _metrics = PipelineMetrics()
        return _metrics


def reset_pipeline_metrics() -> None:
    """Reset global metrics."""
    global _metrics
    with _metrics_lock:
        if _metrics is not None:
            _metrics.reset()
