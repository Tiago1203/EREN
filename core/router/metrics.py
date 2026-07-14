"""Router Metrics for EREN OS Cognitive Capability Router.

Collects and reports router metrics.
"""

from __future__ import annotations

import threading
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import UTC, datetime

from core.router.result import RoutingResult


@dataclass
class MetricSnapshot:
    """A point-in-time metric snapshot."""

    name: str
    value: float
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    tags: dict | None = None


class RouterMetrics:
    """Collects and reports router metrics.

    Tracks:
    - Routings executed
    - Success/failure rates
    - Timing statistics
    - Most used pipelines
    - Fallbacks used
    - Rule evaluations
    """

    def __init__(self):
        """Initialize the metrics collector."""
        self._counters: dict[str, int] = defaultdict(int)
        self._timers: dict[str, list[float]] = defaultdict(list)
        self._snapshots: list[MetricSnapshot] = []
        self._pipeline_usage: dict[str, int] = defaultdict(int)
        self._fallback_usage: dict[str, int] = defaultdict(int)
        self._routing_durations: list[float] = []
        self._lock = threading.RLock()
        self._start_time: datetime | None = None

    def start(self) -> None:
        """Start metrics collection."""
        with self._lock:
            self._start_time = datetime.now(UTC)

    def record_routing(self, result: RoutingResult) -> None:
        """Record routing execution metrics.

        Args:
            result: Routing execution result.
        """
        with self._lock:
            # Counters
            self._counters["routings_executed"] += 1
            self._routing_durations.append(result.duration_ms)

            if result.is_success:
                self._counters["routings_succeeded"] += 1
            elif result.was_cancelled:
                self._counters["routings_cancelled"] += 1
            else:
                self._counters["routings_failed"] += 1

            # Pipeline usage
            if result.selected_pipeline:
                self._pipeline_usage[result.selected_pipeline.pipeline_name] += 1
                self._counters["pipeline_selections"] += 1

            # Candidates
            self._counters["candidates_evaluated"] += result.candidate_count

            # Eligible candidates
            eligible = len(result.eligible_candidates)
            self._counters["eligible_candidates"] += eligible

            # Snapshot
            self._snapshots.append(MetricSnapshot(
                name="routing_execution",
                value=result.duration_ms,
                tags={
                    "status": result.state.value,
                    "pipeline": (
                        result.selected_pipeline.pipeline_name
                        if result.selected_pipeline else None
                    ),
                },
            ))

    def record_fallback(self, policy_name: str) -> None:
        """Record fallback usage.

        Args:
            policy_name: Policy that was used as fallback.
        """
        with self._lock:
            self._fallback_usage[policy_name] += 1
            self._counters["fallbacks_activated"] += 1

    def record_rule_evaluation(self, rule_id: str, matched: bool) -> None:
        """Record rule evaluation.

        Args:
            rule_id: Rule that was evaluated.
            matched: Whether rule matched.
        """
        with self._lock:
            self._counters["rules_evaluated"] += 1
            if matched:
                self._counters["rules_matched"] += 1

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

    def get_routing_success_rate(self) -> float:
        """Get routing success rate.

        Returns:
            Success rate as percentage (0-100).
        """
        with self._lock:
            total = self._counters.get("routings_executed", 0)
            if total == 0:
                return 0.0
            succeeded = self._counters.get("routings_succeeded", 0)
            return succeeded / total * 100

    def get_average_routing_duration(self) -> float:
        """Get average routing duration.

        Returns:
            Average duration in milliseconds.
        """
        with self._lock:
            if not self._routing_durations:
                return 0.0
            return sum(self._routing_durations) / len(self._routing_durations)

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
                "routing_stats": {
                    "executed": self._counters.get("routings_executed", 0),
                    "succeeded": self._counters.get("routings_succeeded", 0),
                    "failed": self._counters.get("routings_failed", 0),
                    "cancelled": self._counters.get("routings_cancelled", 0),
                    "success_rate": self.get_routing_success_rate(),
                    "avg_duration_ms": self.get_average_routing_duration(),
                },
                "pipeline_stats": {
                    "selections": self._counters.get("pipeline_selections", 0),
                    "most_used": self.get_most_used_pipeline(),
                },
                "fallback_stats": {
                    "activated": self._counters.get("fallbacks_activated", 0),
                    "usage": dict(self._fallback_usage),
                },
                "rule_stats": {
                    "evaluated": self._counters.get("rules_evaluated", 0),
                    "matched": self._counters.get("rules_matched", 0),
                },
                "snapshots_count": len(self._snapshots),
            }

            if self._start_time:
                elapsed = (datetime.now(UTC) - self._start_time).total_seconds()
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
            self._fallback_usage.clear()
            self._routing_durations.clear()
            self._start_time = None


# Global metrics instance
_metrics: RouterMetrics | None = None
_metrics_lock = threading.Lock()


def get_router_metrics() -> RouterMetrics:
    """Get the global router metrics instance.

    Returns:
        Global RouterMetrics instance.
    """
    global _metrics
    with _metrics_lock:
        if _metrics is None:
            _metrics = RouterMetrics()
        return _metrics


def reset_router_metrics() -> None:
    """Reset global metrics."""
    global _metrics
    with _metrics_lock:
        if _metrics is not None:
            _metrics.reset()
