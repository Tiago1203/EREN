"""Performance Profiler for EREN OS Diagnostics.

Profiles system performance and identifies bottlenecks:
- Component execution times
- Memory usage
- Event throughput
- Queue depths
- Latency measurements

Philosophy:
    Performance is not assumed. EREN must prove it meets production targets.
"""

from __future__ import annotations

import threading
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


@dataclass
class PerformanceMetric:
    """A single performance metric."""

    name: str
    value: float
    unit: str  # ms, bytes, count, etc.
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    percentile_95: float = 0.0
    percentile_99: float = 0.0
    min_value: float = 0.0
    max_value: float = 0.0

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "value": self.value,
            "unit": self.unit,
            "timestamp": self.timestamp.isoformat(),
            "percentile_95": self.percentile_95,
            "percentile_99": self.percentile_99,
            "min_value": self.min_value,
            "max_value": self.max_value,
        }


@dataclass
class PerformanceReport:
    """Complete performance profiling report."""

    score: float
    metrics: list[PerformanceMetric]
    analyzed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    duration_ms: int = 0

    # Performance thresholds
    response_time_threshold_ms: float = 1000.0
    memory_threshold_mb: float = 512.0
    throughput_threshold_rps: float = 100.0

    # Bottlenecks identified
    bottlenecks: list[str] = field(default_factory=list)
    slow_components: list[tuple[str, float]] = field(default_factory=list)

    # Overall metrics
    average_response_time_ms: float = 0.0
    max_response_time_ms: float = 0.0
    memory_usage_mb: float = 0.0
    events_per_second: float = 0.0

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "score": self.score,
            "metrics": [m.to_dict() for m in self.metrics],
            "analyzed_at": self.analyzed_at.isoformat(),
            "duration_ms": self.duration_ms,
            "response_time_threshold_ms": self.response_time_threshold_ms,
            "memory_threshold_mb": self.memory_threshold_mb,
            "throughput_threshold_rps": self.throughput_threshold_rps,
            "bottlenecks": self.bottlenecks,
            "slow_components": self.slow_components,
            "average_response_time_ms": self.average_response_time_ms,
            "max_response_time_ms": self.max_response_time_ms,
            "memory_usage_mb": self.memory_usage_mb,
            "events_per_second": self.events_per_second,
        }


class PerformanceProfiler:
    """Profiles EREN OS performance.

    Tracks:
    - Component execution times
    - Memory usage
    - Event throughput
    - Queue depths
    - Latency measurements
    """

    # Performance thresholds
    THRESHOLDS = {
        "response_time_ms": 1000,
        "memory_mb": 512,
        "event_latency_ms": 100,
        "queue_depth": 1000,
        "throughput_rps": 100,
    }

    def __init__(self):
        self._measurements: dict[str, list[float]] = defaultdict(list)
        self._component_times: dict[str, list[float]] = defaultdict(list)
        self._event_counts: dict[str, int] = defaultdict(int)
        self._event_times: list[float] = []
        self._start_time: datetime | None = None
        self._lock = threading.RLock()

    def start_profiling(self) -> None:
        """Start performance profiling session."""
        with self._lock:
            self._start_time = datetime.now(timezone.utc)

    def record_component_time(
        self,
        component: str,
        duration_ms: float,
    ) -> None:
        """Record component execution time.

        Args:
            component: Component name.
            duration_ms: Execution duration in milliseconds.
        """
        with self._lock:
            self._component_times[component].append(duration_ms)

    def record_event(self, event_type: str) -> None:
        """Record an event occurrence.

        Args:
            event_type: Type of event.
        """
        with self._lock:
            self._event_counts[event_type] += 1
            if self._start_time:
                elapsed = (datetime.now(timezone.utc) - self._start_time).total_seconds()
                self._event_times.append(elapsed)

    def record_metric(
        self,
        name: str,
        value: float,
        unit: str = "count",
    ) -> None:
        """Record a generic performance metric.

        Args:
            name: Metric name.
            value: Metric value.
            unit: Metric unit.
        """
        with self._lock:
            self._measurements[name].append(value)

    def profile(self) -> PerformanceReport:
        """Generate performance profile report.

        Returns:
            PerformanceReport with profiling results.
        """
        import time
        start_time = time.time()

        metrics = []
        bottlenecks = []
        slow_components = []

        with self._lock:
            # Process component times
            for component, times in self._component_times.items():
                if not times:
                    continue

                avg_time = sum(times) / len(times)
                max_time = max(times)
                sorted_times = sorted(times)
                p95_idx = int(len(sorted_times) * 0.95)
                p99_idx = int(len(sorted_times) * 0.99)

                metric = PerformanceMetric(
                    name=f"component_{component}",
                    value=avg_time,
                    unit="ms",
                    percentile_95=sorted_times[p95_idx] if p95_idx < len(sorted_times) else avg_time,
                    percentile_99=sorted_times[p99_idx] if p99_idx < len(sorted_times) else avg_time,
                    min_value=min(times),
                    max_value=max_time,
                )
                metrics.append(metric)

                # Check for slow components
                if avg_time > self.THRESHOLDS["response_time_ms"]:
                    slow_components.append((component, avg_time))
                    bottlenecks.append(f"{component}: avg {avg_time:.1f}ms")

            # Process event throughput
            if self._event_times and self._start_time:
                elapsed = (datetime.now(timezone.utc) - self._start_time).total_seconds()
                total_events = sum(self._event_counts.values())
                events_per_second = total_events / elapsed if elapsed > 0 else 0

                metric = PerformanceMetric(
                    name="events_per_second",
                    value=events_per_second,
                    unit="rps",
                )
                metrics.append(metric)

                # Check throughput threshold
                if events_per_second < self.THRESHOLDS["throughput_rps"]:
                    bottlenecks.append(f"Low throughput: {events_per_second:.1f} rps")

            # Process other measurements
            for name, values in self._measurements.items():
                if not values:
                    continue

                metric = PerformanceMetric(
                    name=name,
                    value=sum(values) / len(values),
                    unit="count",
                    min_value=min(values),
                    max_value=max(values),
                )
                metrics.append(metric)

        duration_ms = int((time.time() - start_time) * 1000)

        # Calculate score
        score = self._calculate_score(bottlenecks, slow_components)

        # Calculate averages
        all_component_times = []
        for times in self._component_times.values():
            all_component_times.extend(times)

        avg_response_time = sum(all_component_times) / len(all_component_times) if all_component_times else 0
        max_response_time = max(all_component_times) if all_component_times else 0

        return PerformanceReport(
            score=score,
            metrics=metrics,
            duration_ms=duration_ms,
            bottlenecks=bottlenecks,
            slow_components=sorted(slow_components, key=lambda x: x[1], reverse=True),
            average_response_time_ms=avg_response_time,
            max_response_time_ms=max_response_time,
        )

    def _calculate_score(
        self,
        bottlenecks: list[str],
        slow_components: list[tuple[str, float]],
    ) -> float:
        """Calculate performance score.

        Args:
            bottlenecks: List of identified bottlenecks.
            slow_components: List of slow components.

        Returns:
            Score from 0-100.
        """
        # Start with perfect score
        score = 100.0

        # Deduct for bottlenecks
        score -= len(bottlenecks) * 10

        # Deduct for slow components
        for component, avg_time in slow_components:
            if avg_time > self.THRESHOLDS["response_time_ms"] * 2:
                score -= 15
            elif avg_time > self.THRESHOLDS["response_time_ms"]:
                score -= 5

        return max(0, min(100, score))

    def get_component_summary(self) -> dict:
        """Get summary of component performance.

        Returns:
            Dictionary with component performance summary.
        """
        with self._lock:
            summary = {}
            for component, times in self._component_times.items():
                if not times:
                    continue

                summary[component] = {
                    "count": len(times),
                    "avg_ms": sum(times) / len(times),
                    "min_ms": min(times),
                    "max_ms": max(times),
                }

            return summary

    def reset(self) -> None:
        """Reset all profiling data."""
        with self._lock:
            self._measurements.clear()
            self._component_times.clear()
            self._event_counts.clear()
            self._event_times.clear()
            self._start_time = None
