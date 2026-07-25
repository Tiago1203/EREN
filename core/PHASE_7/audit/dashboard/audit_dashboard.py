"""
PHASE 7 - EPIC 1: Audit Dashboard

Dashboard de auditoría para administradores:
- Resumen de actividad
- Gráficos de tendencias
- Top usuarios
- Eventos críticos recientes
- PHI access overview
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Optional
import uuid


@dataclass
class DashboardMetrics:
    """Métricas del dashboard."""
    total_events_24h: int = 0
    total_events_7d: int = 0
    phi_access_24h: int = 0
    phi_access_7d: int = 0
    critical_events_24h: int = 0
    failed_logins_24h: int = 0
    chain_integrity: bool = True
    events_by_hour: dict = field(default_factory=dict)
    events_by_category: dict = field(default_factory=dict)
    events_by_severity: dict = field(default_factory=dict)


@dataclass
class TopUserActivity:
    """Actividad de usuario."""
    user_id: str
    user_name: str
    total_events: int
    phi_access_count: int
    last_activity: str


@dataclass
class CriticalEventItem:
    """Evento crítico reciente."""
    event_id: str
    timestamp: str
    actor_name: str
    description: str
    severity: str
    resource_type: str
    resource_id: str


class AuditDashboard:
    """Dashboard de auditoría."""

    def __init__(self, audit_logger: Any, audit_repository: Any):
        self._logger = audit_logger
        self._repo = audit_repository

    def get_metrics(self, tenant_id: str = "") -> DashboardMetrics:
        """Obtiene métricas del dashboard."""
        now = datetime.now(timezone.utc)
        last_24h = now - timedelta(hours=24)
        last_7d = now - timedelta(days=7)

        # Get events
        events_24h = self._logger.get_events(since=last_24h, limit=10000)
        events_7d = self._logger.get_events(since=last_7d, limit=100000)

        if tenant_id:
            events_24h = [e for e in events_24h if e.tenant_id == tenant_id]
            events_7d = [e for e in events_7d if e.tenant_id == tenant_id]

        # Calculate metrics
        phi_24h = sum(1 for e in events_24h if e.is_phi_access)
        phi_7d = sum(1 for e in events_7d if e.is_phi_access)
        critical_24h = sum(1 for e in events_24h if e.severity.value == "critical")
        failed_logins_24h = sum(
            1 for e in events_24h
            if e.category.value == "authentication" and e.action.value == "login_failed"
        )

        # Events by hour (last 24h)
        events_by_hour = {}
        for event in events_24h:
            hour_key = event.timestamp.strftime("%Y-%m-%d %H:00")
            events_by_hour[hour_key] = events_by_hour.get(hour_key, 0) + 1

        # Events by category
        events_by_category = {}
        events_by_severity = {}
        for event in events_7d:
            events_by_category[event.category.value] = events_by_category.get(event.category.value, 0) + 1
            events_by_severity[event.severity.value] = events_by_severity.get(event.severity.value, 0) + 1

        # Verify chain
        chain_ok, _ = self._logger.verify_chain_integrity()

        return DashboardMetrics(
            total_events_24h=len(events_24h),
            total_events_7d=len(events_7d),
            phi_access_24h=phi_24h,
            phi_access_7d=phi_7d,
            critical_events_24h=critical_24h,
            failed_logins_24h=failed_logins_24h,
            chain_integrity=chain_ok,
            events_by_hour=events_by_hour,
            events_by_category=events_by_category,
            events_by_severity=events_by_severity,
        )

    def get_top_users(
        self,
        tenant_id: str = "",
        limit: int = 10,
        since_days: int = 7,
    ) -> list[TopUserActivity]:
        """Obtiene usuarios más activos."""
        since = datetime.now(timezone.utc) - timedelta(days=since_days)
        events = self._logger.get_events(since=since, limit=50000)

        if tenant_id:
            events = [e for e in events if e.tenant_id == tenant_id]

        # Aggregate by user
        user_stats: dict = {}
        for event in events:
            uid = event.actor_id
            if uid not in user_stats:
                user_stats[uid] = {
                    "user_name": event.actor_name,
                    "total_events": 0,
                    "phi_access_count": 0,
                    "last_activity": event.timestamp,
                }
            user_stats[uid]["total_events"] += 1
            if event.is_phi_access:
                user_stats[uid]["phi_access_count"] += 1
            if event.timestamp > user_stats[uid]["last_activity"]:
                user_stats[uid]["last_activity"] = event.timestamp

        # Sort and take top
        sorted_users = sorted(
            user_stats.items(),
            key=lambda x: x[1]["total_events"],
            reverse=True,
        )[:limit]

        return [
            TopUserActivity(
                user_id=uid,
                user_name=stats["user_name"],
                total_events=stats["total_events"],
                phi_access_count=stats["phi_access_count"],
                last_activity=stats["last_activity"].isoformat(),
            )
            for uid, stats in sorted_users
        ]

    def get_critical_events(
        self,
        tenant_id: str = "",
        limit: int = 20,
        since_days: int = 7,
    ) -> list[CriticalEventItem]:
        """Obtiene eventos críticos recientes."""
        since = datetime.now(timezone.utc) - timedelta(days=since_days)
        events = self._logger.get_events(since=since, limit=5000)

        if tenant_id:
            events = [e for e in events if e.tenant_id == tenant_id]

        # Filter critical/high severity
        critical = [
            e for e in events
            if e.severity.value in ["critical", "high"]
        ]

        # Sort by timestamp desc
        critical.sort(key=lambda e: e.timestamp, reverse=True)

        return [
            CriticalEventItem(
                event_id=e.event_id,
                timestamp=e.timestamp.isoformat(),
                actor_name=e.actor_name,
                description=f"{e.action.value} on {e.resource_type}/{e.resource_id}",
                severity=e.severity.value,
                resource_type=e.resource_type,
                resource_id=e.resource_id,
            )
            for e in critical[:limit]
        ]

    def get_phi_access_summary(
        self,
        tenant_id: str = "",
        since_days: int = 30,
    ) -> dict:
        """Obtiene resumen de acceso PHI."""
        since = datetime.now(timezone.utc) - timedelta(days=since_days)
        events = self._logger.get_phi_access_events(since=since)

        if tenant_id:
            events = [e for e in events if e.tenant_id == tenant_id]

        # By patient/resource
        by_resource: dict = {}
        by_user: dict = {}
        by_hour: dict = {}

        for event in events:
            # By resource
            rid = event.resource_id
            by_resource[rid] = by_resource.get(rid, 0) + 1

            # By user
            uid = event.actor_id
            if uid not in by_user:
                by_user[uid] = {"name": event.actor_name, "count": 0}
            by_user[uid]["count"] += 1

            # By hour
            hour_key = event.timestamp.strftime("%Y-%m-%d %H:00")
            by_hour[hour_key] = by_hour.get(hour_key, 0) + 1

        # Top accessed patients
        top_resources = sorted(by_resource.items(), key=lambda x: x[1], reverse=True)[:20]
        top_users = sorted(by_user.items(), key=lambda x: x[1]["count"], reverse=True)[:20]

        return {
            "total_phi_accesses": len(events),
            "unique_resources_accessed": len(by_resource),
            "unique_users_with_access": len(by_user),
            "period_days": since_days,
            "top_accessed_resources": [{"id": r[0], "count": r[1]} for r in top_resources],
            "top_users_by_phi_access": [{"id": u[0], **u[1]} for u in top_users],
            "accesses_by_hour": by_hour,
        }

    def get_activity_timeline(
        self,
        actor_id: str,
        days: int = 7,
    ) -> dict:
        """Obtiene timeline de actividad de un usuario."""
        since = datetime.now(timezone.utc) - timedelta(days=days)
        events = self._logger.get_user_activity(actor_id, since=since)

        # Group by date
        by_date = {}
        for event in events:
            date_key = event.timestamp.strftime("%Y-%m-%d")
            if date_key not in by_date:
                by_date[date_key] = []
            by_date[date_key].append({
                "event_id": event.event_id,
                "timestamp": event.timestamp.isoformat(),
                "action": event.action.value,
                "resource_type": event.resource_type,
                "resource_id": event.resource_id,
                "success": event.success,
                "is_phi_access": event.is_phi_access,
            })

        return {
            "actor_id": actor_id,
            "period_days": days,
            "total_events": len(events),
            "phi_accesses": sum(1 for e in events if e.is_phi_access),
            "by_date": by_date,
        }
