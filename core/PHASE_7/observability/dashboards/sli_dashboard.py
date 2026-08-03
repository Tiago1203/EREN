"""
PHASE 7 - EPIC 4: SLI/SLO Manager

Service Level Objectives management:
- SLI definitions
- SLO tracking
- Error budget
- Reports
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Optional
import threading


class SLOStatus(str, Enum):
    """Estado de SLO."""
    HEALTHY = "healthy"       # > 99%
    AT_RISK = "at_risk"         # 95-99%
    BREACHED = "breached"       # < 95%


class SLIMetric(str, Enum):
    """Tipos de SLI."""
    AVAILABILITY = "availability"
    LATENCY_P50 = "latency_p50"
    LATENCY_P95 = "latency_p95"
    LATENCY_P99 = "latency_p99"
    ERROR_RATE = "error_rate"
    THROUGHPUT = "throughput"


@dataclass
class SLO:
    """Service Level Objective."""
    slo_id: str
    name: str
    sli_metric: SLIMetric
    target_percent: float      # e.g., 99.9
    window_days: int = 30
    tenant_id: Optional[str] = None
    service_name: str = "api"


@dataclass
class SLOStatusRecord:
    """Registro de estado de SLO."""
    slo_id: str
    timestamp: datetime
    status: SLOStatus
    current_value: float
    target_value: float
    error_budget_remaining_percent: float
    burn_rate: float


class SLOManager:
    """Gestor de SLIs y SLOs."""

    def __init__(self):
        self._slos: dict[str, SLO] = {}
        self._status_history: dict[str, list[SLOStatusRecord]] = {}
        self._measurements: dict[str, list[tuple[datetime, float]]] = {}
        self._lock = threading.Lock()

    def add_slo(self, slo: SLO) -> None:
        """Añade SLO."""
        with self._lock:
            self._slos[slo.slo_id] = slo
            self._measurements.setdefault(slo.slo_id, [])

    def record_measurement(
        self,
        slo_id: str,
        value: float,
        timestamp: Optional[datetime] = None,
    ) -> None:
        """Registra medición de SLI."""
        with self._lock:
            if slo_id not in self._measurements:
                self._measurements[slo_id] = []

            ts = timestamp or datetime.now(timezone.utc)
            # Normalize to UTC if naive
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            self._measurements[slo_id].append((ts, value))

            # Keep 30 days of measurements
            cutoff = datetime.now(timezone.utc) - timedelta(days=30)
            self._measurements[slo_id] = [
                (t, v) for t, v in self._measurements[slo_id]
                if t >= cutoff
            ]

    def get_current_status(self, slo_id: str) -> Optional[SLOStatusRecord]:
        """Obtiene estado actual de SLO."""
        with self._lock:
            slo = self._slos.get(slo_id)
            if not slo:
                return None

            measurements = self._measurements.get(slo_id, [])
            if not measurements:
                return None

            # Calculate current value
            window_cutoff = datetime.now(timezone.utc) - timedelta(days=slo.window_days)
            recent = [(t, v) for t, v in measurements if t >= window_cutoff]

            if not recent:
                return None

            current_value = self._calculate_sli_value(slo.sli_metric, recent)

            # Determine status
            if current_value >= slo.target_percent:
                status = SLOStatus.HEALTHY
            elif current_value >= slo.target_percent - 5:
                status = SLOStatus.AT_RISK
            else:
                status = SLOStatus.BREACHED

            # Error budget
            error_budget = max(0, 100 - current_value)
            target_budget = 100 - slo.target_percent
            remaining = (error_budget / target_budget * 100) if target_budget > 0 else 100

            # Burn rate (simplified)
            if len(recent) >= 2:
                burn_rate = 1.0  # Simplified
            else:
                burn_rate = 1.0

            record = SLOStatusRecord(
                slo_id=slo_id,
                timestamp=datetime.now(timezone.utc),
                status=status,
                current_value=current_value,
                target_value=slo.target_percent,
                error_budget_remaining_percent=min(100, remaining),
                burn_rate=burn_rate,
            )

            self._status_history.setdefault(slo_id, []).append(record)
            if len(self._status_history[slo_id]) > 1000:
                self._status_history[slo_id] = self._status_history[slo_id][-500:]

            return record

    def _calculate_sli_value(self, metric: SLIMetric, measurements: list) -> float:
        """Calcula valor de SLI."""
        if not measurements:
            return 0.0

        if metric == SLIMetric.AVAILABILITY:
            # Percentage of measurements meeting threshold
            good = sum(1 for _, v in measurements if v >= 99.0)
            return round(good / len(measurements) * 100, 3)

        elif metric == SLIMetric.ERROR_RATE:
            # Lower is better for error rate
            avg_error = sum(v for _, v in measurements) / len(measurements)
            return round(max(0, 100 - avg_error), 3)

        elif metric in (SLIMetric.LATENCY_P50, SLIMetric.LATENCY_P95, SLIMetric.LATENCY_P99):
            # Lower is better
            values = sorted(v for _, v in measurements)
            if not values:
                return 100.0
            p = {"latency_p50": 0.5, "latency_p95": 0.95, "latency_p99": 0.99}[metric.value]
            idx = int(len(values) * p)
            latency = values[min(idx, len(values) - 1)]
            # Assume 1000ms target
            return round(max(0, 100 - latency / 10), 3)

        elif metric == SLIMetric.THROUGHPUT:
            avg = sum(v for _, v in measurements) / len(measurements)
            # Assume target is average
            return round(min(100, avg), 3)

        return 0.0

    def get_all_status(self) -> list[dict]:
        """Estado de todos los SLOs."""
        results = []
        for slo_id in self._slos:
            status = self.get_current_status(slo_id)
            if status:
                slo = self._slos[slo_id]
                results.append({
                    "slo_id": slo_id,
                    "name": slo.name,
                    "metric": slo.sli_metric.value,
                    "target": slo.target_percent,
                    "current": status.current_value,
                    "status": status.status.value,
                    "error_budget_remaining": status.error_budget_remaining_percent,
                    "burn_rate": status.burn_rate,
                })
        return results

    def get_error_budget_report(self, slo_id: str) -> dict:
        """Reporte de error budget."""
        with self._lock:
            slo = self._slos.get(slo_id)
            if not slo:
                return {}

            measurements = self._measurements.get(slo_id, [])
            if not measurements:
                return {}

            window_cutoff = datetime.now(timezone.utc) - timedelta(days=slo.window_days)
            recent = [(t, v) for t, v in measurements if t >= window_cutoff]

            if not recent:
                return {}

            current = self._calculate_sli_value(slo.sli_metric, recent)
            error_budget = max(0, 100 - current)
            target_budget = 100 - slo.target_percent

            days_remaining = slo.window_days
            consumed_budget = max(0, target_budget - (error_budget if current >= slo.target_percent else error_budget + (slo.target_percent - current)))

            return {
                "slo_id": slo_id,
                "name": slo.name,
                "window_days": slo.window_days,
                "target_slo": slo.target_percent,
                "current_slo": round(current, 3),
                "target_budget_percent": target_budget,
                "consumed_budget_percent": round(consumed_budget, 2),
                "remaining_budget_percent": round(max(0, target_budget - consumed_budget), 2),
                "at_risk": current < slo.target_percent,
            }

    # ── Default SLOs ─────────────────────────────────────────
    def setup_default_slos(self) -> None:
        """Configura SLOs por defecto."""
        slos = [
            SLO("slo-availability", "API Availability", SLIMetric.AVAILABILITY, 99.9, 30),
            SLO("slo-latency-p95", "API Latency P95", SLIMetric.LATENCY_P95, 99.0, 30),
            SLO("slo-error-rate", "API Error Rate", SLIMetric.ERROR_RATE, 99.5, 30),
            SLO("slo-throughput", "API Throughput", SLIMetric.THROUGHPUT, 95.0, 30),
            SLO("slo-database-availability", "Database Availability", SLIMetric.AVAILABILITY, 99.9, 30),
            SLO("slo-ai-availability", "AI Service Availability", SLIMetric.AVAILABILITY, 99.5, 30),
        ]
        for slo in slos:
            self.add_slo(slo)


# Global manager
_slo_manager: Optional[SLOManager] = None


def get_slo_manager() -> SLOManager:
    """Obtiene manager global."""
    global _slo_manager
    if _slo_manager is None:
        _slo_manager = SLOManager()
        _slo_manager.setup_default_slos()
    return _slo_manager
