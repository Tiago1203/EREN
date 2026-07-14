"""Plugin Metrics for EREN OS Cognitive Plugin Framework.

Collects and reports plugin metrics.
"""

from __future__ import annotations

import threading
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone

from core.plugins.types import PluginState


@dataclass
class MetricSnapshot:
    """A point-in-time metric snapshot."""

    name: str
    value: float
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    tags: dict | None = None


class PluginMetrics:
    """Collects and reports plugin metrics.

    Tracks:
    - Plugins loaded/unloaded
    - Activation/deactivation
    - Load times
    - Failures
    - Dependencies
    """

    def __init__(self):
        """Initialize the metrics collector."""
        self._counters: dict[str, int] = defaultdict(int)
        self._timers: dict[str, list[float]] = defaultdict(list)
        self._snapshots: list[MetricSnapshot] = []
        self._plugin_states: dict[str, str] = {}
        self._load_times: dict[str, float] = {}
        self._lock = threading.RLock()
        self._start_time: datetime | None = None

    def start(self) -> None:
        """Start metrics collection."""
        with self._lock:
            self._start_time = datetime.now(timezone.utc)

    def record_load(self, plugin_id: str, duration_ms: float) -> None:
        """Record plugin load.

        Args:
            plugin_id: Plugin ID.
            duration_ms: Load duration in milliseconds.
        """
        with self._lock:
            self._counters["plugins_loaded"] += 1
            self._timers["load_time"].append(duration_ms)
            self._load_times[plugin_id] = duration_ms

            self._snapshot("plugin_load", duration_ms, {"plugin_id": plugin_id})

    def record_initialize(self, plugin_id: str, duration_ms: float) -> None:
        """Record plugin initialization.

        Args:
            plugin_id: Plugin ID.
            duration_ms: Initialization duration in milliseconds.
        """
        with self._lock:
            self._timers["init_time"].append(duration_ms)

            self._snapshot("plugin_init", duration_ms, {"plugin_id": plugin_id})

    def record_activate(self, plugin_id: str) -> None:
        """Record plugin activation.

        Args:
            plugin_id: Plugin ID.
        """
        with self._lock:
            self._counters["plugins_activated"] += 1
            self._plugin_states[plugin_id] = PluginState.ACTIVE.value

    def record_deactivate(self, plugin_id: str) -> None:
        """Record plugin deactivation.

        Args:
            plugin_id: Plugin ID.
        """
        with self._lock:
            self._counters["plugins_deactivated"] += 1
            self._plugin_states[plugin_id] = PluginState.PAUSED.value

    def record_failure(self, plugin_id: str, error: str) -> None:
        """Record plugin failure.

        Args:
            plugin_id: Plugin ID.
            error: Error message.
        """
        with self._lock:
            self._counters["plugin_failures"] += 1
            self._plugin_states[plugin_id] = PluginState.FAILED.value

            self._snapshot("plugin_failure", 1, {
                "plugin_id": plugin_id,
                "error": error,
            })

    def record_dependency(self, plugin_id: str, dependency_id: str) -> None:
        """Record plugin dependency.

        Args:
            plugin_id: Plugin ID.
            dependency_id: Dependency plugin ID.
        """
        with self._lock:
            self._counters["dependencies_checked"] += 1

    def _snapshot(self, name: str, value: float, tags: dict | None = None) -> None:
        """Create a metric snapshot.

        Args:
            name: Metric name.
            value: Metric value.
            tags: Optional tags.
        """
        self._snapshots.append(MetricSnapshot(
            name=name,
            value=value,
            tags=tags,
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

    def get_average_load_time(self) -> float:
        """Get average plugin load time.

        Returns:
            Average load time in milliseconds.
        """
        with self._lock:
            times = self._timers.get("load_time", [])
            if not times:
                return 0.0
            return sum(times) / len(times)

    def get_average_init_time(self) -> float:
        """Get average plugin initialization time.

        Returns:
            Average initialization time in milliseconds.
        """
        with self._lock:
            times = self._timers.get("init_time", [])
            if not times:
                return 0.0
            return sum(times) / len(times)

    def get_plugin_state(self, plugin_id: str) -> str | None:
        """Get plugin state.

        Args:
            plugin_id: Plugin ID.

        Returns:
            Plugin state or None.
        """
        with self._lock:
            return self._plugin_states.get(plugin_id)

    def get_summary(self) -> dict:
        """Get metrics summary.

        Returns:
            Dictionary with metrics summary.
        """
        with self._lock:
            return {
                "counters": dict(self._counters),
                "load_stats": {
                    "total_loaded": self._counters.get("plugins_loaded", 0),
                    "total_activated": self._counters.get("plugins_activated", 0),
                    "total_failures": self._counters.get("plugin_failures", 0),
                    "avg_load_time_ms": self.get_average_load_time(),
                    "avg_init_time_ms": self.get_average_init_time(),
                },
                "state_counts": {
                    state: sum(1 for s in self._plugin_states.values() if s == state)
                    for state in [s.value for s in PluginState]
                },
                "snapshots_count": len(self._snapshots),
            }

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
            self._plugin_states.clear()
            self._load_times.clear()
            self._start_time = None


# Global metrics instance
_metrics: PluginMetrics | None = None
_metrics_lock = threading.Lock()


def get_plugin_metrics() -> PluginMetrics:
    """Get the global plugin metrics instance.

    Returns:
        Global PluginMetrics instance.
    """
    global _metrics
    with _metrics_lock:
        if _metrics is None:
            _metrics = PluginMetrics()
        return _metrics


def reset_plugin_metrics() -> None:
    """Reset global metrics."""
    global _metrics
    with _metrics_lock:
        if _metrics is not None:
            _metrics.reset()
