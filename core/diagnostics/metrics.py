"""Diagnostics Metrics for EREN OS Diagnostics.

Collects and reports diagnostic metrics:
- Validation counts
- Error counts
- Warning counts
- Component timing
- Score trends

Philosophy:
    Diagnostics must be measurable. Metrics drive continuous improvement.
"""

from __future__ import annotations

import threading
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


@dataclass
class MetricSnapshot:
    """A point-in-time metric snapshot."""

    name: str
    value: float
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    tags: dict | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "value": self.value,
            "timestamp": self.timestamp.isoformat(),
            "tags": self.tags,
        }


class DiagnosticsMetrics:
    """Collects and reports diagnostics metrics.

    Tracks:
    - Validation counts and results
    - Error and warning counts
    - Component timing
    - Score history
    """

    def __init__(self):
        self._metrics: dict[str, float] = {}
        self._counters: dict[str, int] = defaultdict(int)
        self._timers: dict[str, list[float]] = defaultdict(list)
        self._snapshots: list[MetricSnapshot] = []
        self._lock = threading.RLock()
        self._start_time: datetime | None = None

    def start(self) -> None:
        """Start metrics collection."""
        with self._lock:
            self._start_time = datetime.now(UTC)

    def increment(self, name: str, value: int = 1) -> None:
        """Increment a counter metric.

        Args:
            name: Metric name.
            value: Increment value.
        """
        with self._lock:
            self._counters[name] += value

    def set_gauge(self, name: str, value: float) -> None:
        """Set a gauge metric.

        Args:
            name: Metric name.
            value: Metric value.
        """
        with self._lock:
            self._metrics[name] = value
            self._snapshots.append(MetricSnapshot(
                name=name,
                value=value,
                tags={"type": "gauge"},
            ))

    def record_time(self, name: str, duration_ms: float) -> None:
        """Record a timing metric.

        Args:
            name: Metric name.
            duration_ms: Duration in milliseconds.
        """
        with self._lock:
            self._timers[name].append(duration_ms)
            self._snapshots.append(MetricSnapshot(
                name=name,
                value=duration_ms,
                tags={"type": "timing", "unit": "ms"},
            ))

    def record_validation(self, passed: bool, validation_type: str) -> None:
        """Record a validation result.

        Args:
            passed: Whether validation passed.
            validation_type: Type of validation.
        """
        with self._lock:
            if passed:
                self._counters[f"validation_{validation_type}_passed"] += 1
            else:
                self._counters[f"validation_{validation_type}_failed"] += 1
            self._counters["validation_total"] += 1

    def record_issue(self, severity: str) -> None:
        """Record an issue detection.

        Args:
            severity: Issue severity.
        """
        with self._lock:
            self._counters[f"issue_{severity}"] += 1
            self._counters["issue_total"] += 1

    def record_score(self, category: str, score: float) -> None:
        """Record a score value.

        Args:
            category: Score category.
            score: Score value.
        """
        with self._lock:
            self._metrics[f"score_{category}"] = score
            self._snapshots.append(MetricSnapshot(
                name=f"score_{category}",
                value=score,
                tags={"type": "score", "category": category},
            ))

    def get_counter(self, name: str) -> int:
        """Get counter value.

        Args:
            name: Counter name.

        Returns:
            Counter value.
        """
        with self._lock:
            return self._counters.get(name, 0)

    def get_gauge(self, name: str) -> float | None:
        """Get gauge value.

        Args:
            name: Gauge name.

        Returns:
            Gauge value or None.
        """
        with self._lock:
            return self._metrics.get(name)

    def get_timing_stats(self, name: str) -> dict:
        """Get timing statistics.

        Args:
            name: Timing metric name.

        Returns:
            Dictionary with timing statistics.
        """
        with self._lock:
            times = self._timers.get(name, [])
            if not times:
                return {}

            return {
                "count": len(times),
                "min": min(times),
                "max": max(times),
                "avg": sum(times) / len(times),
                "total": sum(times),
            }

    def get_summary(self) -> dict:
        """Get metrics summary.

        Returns:
            Dictionary with all metrics.
        """
        with self._lock:
            summary = {
                "counters": dict(self._counters),
                "gauges": dict(self._metrics),
                "timers": {},
                "snapshots_count": len(self._snapshots),
            }

            for name in self._timers:
                summary["timers"][name] = self.get_timing_stats(name)

            if self._start_time:
                elapsed = (datetime.now(UTC) - self._start_time).total_seconds()
                summary["elapsed_seconds"] = elapsed

            return summary

    def to_dict(self) -> dict:
        """Convert to dictionary representation.

        Returns:
            Dictionary with complete metrics data.
        """
        return self.get_summary()

    def reset(self) -> None:
        """Reset all metrics."""
        with self._lock:
            self._metrics.clear()
            self._counters.clear()
            self._timers.clear()
            self._snapshots.clear()
            self._start_time = None

    def get_validation_summary(self) -> dict:
        """Get validation-specific metrics.

        Returns:
            Dictionary with validation metrics.
        """
        with self._lock:
            total = self._counters.get("validation_total", 0)
            passed = sum(
                v for k, v in self._counters.items()
                if k.startswith("validation_") and k.endswith("_passed")
            )
            failed = total - passed

            return {
                "total_validations": total,
                "passed_validations": passed,
                "failed_validations": failed,
                "pass_rate": (passed / total * 100) if total > 0 else 0,
            }

    def get_issue_summary(self) -> dict:
        """Get issue-specific metrics.

        Returns:
            Dictionary with issue metrics.
        """
        with self._lock:
            return {
                "total_issues": self._counters.get("issue_total", 0),
                "critical_issues": self._counters.get("issue_critical", 0),
                "major_issues": self._counters.get("issue_major", 0),
                "minor_issues": self._counters.get("issue_minor", 0),
            }

    def get_score_summary(self) -> dict:
        """Get score-specific metrics.

        Returns:
            Dictionary with score metrics.
        """
        with self._lock:
            scores = {
                k.replace("score_", ""): v
                for k, v in self._metrics.items()
                if k.startswith("score_")
            }

            overall = sum(scores.values()) / len(scores) if scores else 0

            return {
                "category_scores": scores,
                "overall_score": overall,
                "snapshot_count": len([s for s in self._snapshots if "score" in s.name]),
            }

    def get_component_timing_summary(self) -> dict:
        """Get component timing summary.

        Returns:
            Dictionary with component timing metrics.
        """
        with self._lock:
            component_timings = {}

            for name, times in self._timers.items():
                if name.startswith("component_"):
                    component = name.replace("component_", "")
                    component_timings[component] = self.get_timing_stats(name)

            return component_timings


# Global metrics instance
_metrics: DiagnosticsMetrics | None = None
_metrics_lock = threading.Lock()


def get_metrics() -> DiagnosticsMetrics:
    """Get the global diagnostics metrics instance.

    Returns:
        Global DiagnosticsMetrics instance.
    """
    global _metrics
    with _metrics_lock:
        if _metrics is None:
            _metrics = DiagnosticsMetrics()
        return _metrics


def reset_metrics() -> None:
    """Reset global metrics."""
    global _metrics
    with _metrics_lock:
        if _metrics is not None:
            _metrics.reset()
