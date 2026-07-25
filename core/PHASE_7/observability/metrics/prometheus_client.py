"""
PHASE 7 - EPIC 4: Prometheus Client

Prometheus metrics exposition:
- Counters, Gauges, Histograms, Summaries
- Multi-tenant metric labels
- Integration con EPIC 2 (multi-tenant) y EPIC 3 (HA)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Callable, Optional
import threading
import time


class MetricType(str, Enum):
    """Tipos de métrica Prometheus."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


@dataclass
class Metric:
    """Definición de métrica."""
    name: str
    metric_type: MetricType
    description: str
    labels: list[str] = field(default_factory=list)
    buckets: list[float] = field(default_factory=lambda: [0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0])


@dataclass
class MetricValue:
    """Valor de métrica."""
    name: str
    labels: dict[str, str]
    value: float
    timestamp: datetime


class Counter:
    """Counter metric."""

    def __init__(self, name: str, description: str, labels: Optional[list[str]] = None):
        self._name = name
        self._description = description
        self._labels = labels or []
        self._values: dict[tuple, float] = {}
        self._lock = threading.Lock()

    def inc(self, value: float = 1.0, **labels) -> None:
        key = self._labels_to_key(labels)
        with self._lock:
            self._values[key] = self._values.get(key, 0) + value

    def _labels_to_key(self, labels: dict) -> tuple:
        return tuple(labels.get(l, "") for l in self._labels)

    def collect(self) -> list[MetricValue]:
        with self._lock:
            return [
                MetricValue(
                    name=self._name,
                    labels=dict(zip(self._labels, key)),
                    value=val,
                    timestamp=datetime.now(timezone.utc),
                )
                for key, val in self._values.items()
            ]

    def get_value(self, **labels) -> float:
        key = self._labels_to_key(labels)
        with self._lock:
            return self._values.get(key, 0.0)


class Gauge:
    """Gauge metric."""

    def __init__(self, name: str, description: str, labels: Optional[list[str]] = None):
        self._name = name
        self._description = description
        self._labels = labels or []
        self._values: dict[tuple, float] = {}
        self._lock = threading.Lock()

    def set(self, value: float, **labels) -> None:
        key = self._labels_to_key(labels)
        with self._lock:
            self._values[key] = value

    def inc(self, value: float = 1.0, **labels) -> None:
        key = self._labels_to_key(labels)
        with self._lock:
            self._values[key] = self._values.get(key, 0) + value

    def dec(self, value: float = 1.0, **labels) -> None:
        key = self._labels_to_key(labels)
        with self._lock:
            self._values[key] = self._values.get(key, 0) - value

    def _labels_to_key(self, labels: dict) -> tuple:
        return tuple(labels.get(l, "") for l in self._labels)

    def collect(self) -> list[MetricValue]:
        with self._lock:
            return [
                MetricValue(
                    name=self._name,
                    labels=dict(zip(self._labels, key)),
                    value=val,
                    timestamp=datetime.now(timezone.utc),
                )
                for key, val in self._values.items()
            ]

    def get_value(self, **labels) -> float:
        key = self._labels_to_key(labels)
        with self._lock:
            return self._values.get(key, 0.0)


class Histogram:
    """Histogram metric."""

    def __init__(
        self,
        name: str,
        description: str,
        labels: Optional[list[str]] = None,
        buckets: Optional[list[float]] = None,
    ):
        self._name = name
        self._description = description
        self._labels = labels or []
        self._buckets = buckets or [0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
        self._values: dict[tuple, dict] = {}
        self._lock = threading.Lock()

    def observe(self, value: float, **labels) -> None:
        key = self._labels_to_key(labels)
        with self._lock:
            if key not in self._values:
                self._values[key] = {
                    "count": 0, "sum": 0.0,
                    **{f"le_{b}": 0 for b in self._buckets},
                    f"le_{float('inf')}": 0,
                }
            v = self._values[key]
            v["count"] += 1
            v["sum"] += value
            for b in self._buckets:
                if value <= b:
                    v[f"le_{b}"] += 1
            v[f"le_{float('inf')}"] += 1

    def _labels_to_key(self, labels: dict) -> tuple:
        return tuple(labels.get(l, "") for l in self._labels)

    def collect(self) -> list[MetricValue]:
        with self._lock:
            results = []
            for key, vals in self._values.items():
                results.append(MetricValue(
                    name=f"{self._name}_count",
                    labels=dict(zip(self._labels, key)),
                    value=vals["count"],
                    timestamp=datetime.now(timezone.utc),
                ))
                results.append(MetricValue(
                    name=f"{self._name}_sum",
                    labels=dict(zip(self._labels, key)),
                    value=vals["sum"],
                    timestamp=datetime.now(timezone.utc),
                ))
                for b in self._buckets:
                    results.append(MetricValue(
                        name=f"{self._name}_bucket",
                        labels={**dict(zip(self._labels, key)), "le": str(b)},
                        value=vals[f"le_{b}"],
                        timestamp=datetime.now(timezone.utc),
                    ))
            return results


class PrometheusMetricsRegistry:
    """Registry centralizado de métricas Prometheus."""

    def __init__(self, namespace: str = "eren"):
        self._namespace = namespace
        self._counters: dict[str, Counter] = {}
        self._gauges: dict[str, Gauge] = {}
        self._histograms: dict[str, Histogram] = {}
        self._lock = threading.Lock()

    def counter(
        self,
        name: str,
        description: str,
        labels: Optional[list[str]] = None,
    ) -> Counter:
        """Registra o retorna counter."""
        full_name = f"{self._namespace}_{name}"
        with self._lock:
            if full_name not in self._counters:
                self._counters[full_name] = Counter(full_name, description, labels)
            return self._counters[full_name]

    def gauge(
        self,
        name: str,
        description: str,
        labels: Optional[list[str]] = None,
    ) -> Gauge:
        """Registra o retorna gauge."""
        full_name = f"{self._namespace}_{name}"
        with self._lock:
            if full_name not in self._gauges:
                self._gauges[full_name] = Gauge(full_name, description, labels)
            return self._gauges[full_name]

    def histogram(
        self,
        name: str,
        description: str,
        labels: Optional[list[str]] = None,
        buckets: Optional[list[float]] = None,
    ) -> Histogram:
        """Registra o retorna histogram."""
        full_name = f"{self._namespace}_{name}"
        with self._lock:
            if full_name not in self._histograms:
                self._histograms[full_name] = Histogram(full_name, description, labels, buckets)
            return self._histograms[full_name]

    def collect_all(self) -> list[MetricValue]:
        """Recolecta todas las métricas."""
        results = []
        for c in self._counters.values():
            results.extend(c.collect())
        for g in self._gauges.values():
            results.extend(g.collect())
        for h in self._histograms.values():
            results.extend(h.collect())
        return results

    def render_prometheus(self) -> str:
        """Renderiza en formato Prometheus /metrics."""
        output = []
        for c in self._counters.values():
            output.append(f"# HELP {c._name} {c._description}")
            output.append(f"# TYPE {c._name} counter")
            for mv in c.collect():
                labels = ",".join(f'{k}="{v}"' for k, v in mv.labels.items())
                output.append(f"{c._name}{{{labels}}} {mv.value}")
        for g in self._gauges.values():
            output.append(f"# HELP {g._name} {g._description}")
            output.append(f"# TYPE {g._name} gauge")
            for mv in g.collect():
                labels = ",".join(f'{k}="{v}"' for k, v in mv.labels.items())
                output.append(f"{g._name}{{{labels}}} {mv.value}")
        for h in self._histograms.values():
            for mv in h.collect():
                labels = ",".join(f'{k}="{v}"' for k, v in mv.labels.items())
                output.append(f"{mv.name}{{{labels}}} {mv.value}")
        return "\n".join(output) + "\n"


# Default registry
_default_registry: Optional[PrometheusMetricsRegistry] = None


def get_registry() -> PrometheusMetricsRegistry:
    """Obtiene el registry por defecto."""
    global _default_registry
    if _default_registry is None:
        _default_registry = PrometheusMetricsRegistry()
    return _default_registry


def register_counter(name: str, description: str, labels: Optional[list[str]] = None) -> Counter:
    return get_registry().counter(name, description, labels)


def register_gauge(name: str, description: str, labels: Optional[list[str]] = None) -> Gauge:
    return get_registry().gauge(name, description, labels)


def register_histogram(
    name: str,
    description: str,
    labels: Optional[list[str]] = None,
    buckets: Optional[list[float]] = None,
) -> Histogram:
    return get_registry().histogram(name, description, labels, buckets)
