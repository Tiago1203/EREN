"""
PHASE 7 - EPIC 2: Usage Tracker

Tracking de uso de recursos por tenant:
- Métricas de uso
- Agregaciones temporales
- Tendencias de consumo
- Billing integration
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Optional
from collections import defaultdict
import uuid


@dataclass
class UsageMetric:
    """Métrica de uso."""
    metric_id: str
    tenant_id: str
    resource_type: str
    amount: float
    period_start: datetime
    period_end: datetime
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class UsagePeriod:
    """Período de uso agregado."""
    period_type: str        # daily, monthly, yearly
    start_date: datetime
    end_date: datetime
    metrics: dict[str, float] = field(default_factory=dict)
    events_count: int = 0


class UsageTracker:
    """Tracker de uso de recursos por tenant."""

    def __init__(self, quota_manager: Any):
        self._quota_manager = quota_manager
        self._metrics: list[UsageMetric] = []
        self._counters: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))

    def track(
        self,
        tenant_id: str,
        resource_type: str,
        amount: float = 1.0,
        timestamp: Optional[datetime] = None,
    ) -> UsageMetric:
        """Registra uso de recurso."""
        now = timestamp or datetime.now(timezone.utc)
        metric = UsageMetric(
            metric_id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            resource_type=resource_type,
            amount=amount,
            period_start=now.replace(hour=0, minute=0, second=0, microsecond=0),
            period_end=now.replace(hour=23, minute=59, second=59, microsecond=999999),
            timestamp=now,
        )
        self._metrics.append(metric)
        self._counters[tenant_id][resource_type] += amount

        # Also update quota manager
        from core.PHASE_7.tenant.quotas.quota_manager import ResourceType
        try:
            res_type = ResourceType(resource_type)
            self._quota_manager.consume_quota(tenant_id, res_type, amount)
        except (ValueError, KeyError):
            pass

        return metric

    def get_current_usage(
        self,
        tenant_id: str,
        resource_type: str,
    ) -> float:
        """Obtiene uso actual del recurso."""
        return self._counters.get(tenant_id, {}).get(resource_type, 0.0)

    def get_daily_usage(
        self,
        tenant_id: str,
        resource_type: str,
        date: Optional[datetime] = None,
    ) -> float:
        """Obtiene uso del día."""
        if date is None:
            date = datetime.now(timezone.utc)

        start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end = date.replace(hour=23, minute=59, second=59, microsecond=999999)

        return sum(
            m.amount for m in self._metrics
            if m.tenant_id == tenant_id
            and m.resource_type == resource_type
            and start <= m.timestamp <= end
        )

    def get_monthly_usage(
        self,
        tenant_id: str,
        resource_type: str,
        year: Optional[int] = None,
        month: Optional[int] = None,
    ) -> float:
        """Obtiene uso del mes."""
        now = datetime.now(timezone.utc)
        y = year or now.year
        m = month or now.month

        start = datetime(y, m, 1, tzinfo=timezone.utc)
        if m == 12:
            end = datetime(y + 1, 1, 1, tzinfo=timezone.utc) - timedelta(seconds=1)
        else:
            end = datetime(y, m + 1, 1, tzinfo=timezone.utc) - timedelta(seconds=1)

        return sum(
            m.amount for m in self._metrics
            if m.tenant_id == tenant_id
            and m.resource_type == resource_type
            and start <= m.timestamp <= end
        )

    def get_usage_history(
        self,
        tenant_id: str,
        resource_type: str,
        days: int = 30,
    ) -> list[dict]:
        """Obtiene historial de uso (daily aggregates)."""
        now = datetime.now(timezone.utc)
        history = []

        for i in range(days):
            date = now - timedelta(days=i)
            daily = self.get_daily_usage(tenant_id, resource_type, date)
            history.append({
                "date": date.strftime("%Y-%m-%d"),
                "amount": daily,
            })

        return list(reversed(history))

    def get_period(
        self,
        tenant_id: str,
        period_type: str = "daily",
        periods_back: int = 12,
    ) -> list[UsagePeriod]:
        """Obtiene períodos de uso agregados."""
        now = datetime.now(timezone.utc)
        periods = []

        for i in range(periods_back):
            if period_type == "daily":
                start = (now - timedelta(days=i)).replace(
                    hour=0, minute=0, second=0, microsecond=0
                )
                end = start + timedelta(days=1) - timedelta(seconds=1)
            elif period_type == "monthly":
                start = (now.replace(day=1) - timedelta(days=i * 30)).replace(
                    day=1, hour=0, minute=0, second=0, microsecond=0
                )
                if start.month == 12:
                    end = start.replace(year=start.year + 1, month=1) - timedelta(seconds=1)
                else:
                    end = start.replace(month=start.month + 1) - timedelta(seconds=1)
            else:
                start = now - timedelta(days=i * 365)
                end = start + timedelta(days=365) - timedelta(seconds=1)

            # Aggregate metrics
            period_metrics = {}
            for metric in self._metrics:
                if (metric.tenant_id == tenant_id
                        and start <= metric.timestamp <= end):
                    period_metrics[metric.resource_type] = (
                        period_metrics.get(metric.resource_type, 0) + metric.amount
                    )

            periods.append(UsagePeriod(
                period_type=period_type,
                start_date=start,
                end_date=end,
                metrics=period_metrics,
                events_count=sum(period_metrics.values()),
            ))

        return list(reversed(periods))

    def get_trend(
        self,
        tenant_id: str,
        resource_type: str,
        days: int = 30,
    ) -> dict:
        """Calcula tendencia de uso."""
        history = self.get_usage_history(tenant_id, resource_type, days)
        if not history:
            return {"trend": "stable", "change_percent": 0.0, "average": 0.0}

        values = [h["amount"] for h in history]
        avg = sum(values) / len(values)

        # Compare first half vs second half
        half = len(values) // 2
        if half == 0:
            return {"trend": "stable", "change_percent": 0.0, "average": avg}

        first_half_avg = sum(values[:half]) / half
        second_half_avg = sum(values[half:]) / (len(values) - half)

        if first_half_avg == 0:
            change = 100.0 if second_half_avg > 0 else 0.0
        else:
            change = ((second_half_avg - first_half_avg) / first_half_avg) * 100

        trend = "increasing" if change > 10 else "decreasing" if change < -10 else "stable"

        return {
            "trend": trend,
            "change_percent": round(change, 1),
            "average": round(avg, 2),
            "total": round(sum(values), 2),
        }

    def reset_daily_counters(self, tenant_id: str) -> None:
        """Resetea contadores diarios (llamado por cron)."""
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        # In production: persist to DB, reset in-memory counters
        for resource_type in self._counters.get(tenant_id, {}):
            pass  # Reset logic here
