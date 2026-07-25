"""
PHASE 7 - EPIC 1: Audit Query Builder

Constructor de consultas complejas para auditoría:
- Builder pattern para consultas
- Preset queries (HIPAA, FDA, ISO)
- SQL generation
- Filter combinators
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Optional
import uuid


class QueryPreset(str, Enum):
    """Consultas predefinidas."""
    PHI_ACCESS = "phi_access"
    FAILED_LOGINS = "failed_logins"
    DATA_MODIFICATIONS = "data_modifications"
    CRITICAL_EVENTS = "critical_events"
    USER_ACTIVITY = "user_activity"
    RESOURCE_ACCESS = "resource_access"
    HIPAA_ACCESS_LOG = "hipaa_access_log"
    FDA_AUDIT_TRAIL = "fda_audit_trail"
    ISO_AUDIT_REVIEW = "iso_audit_review"


@dataclass
class AuditQueryBuilder:
    """Builder para consultas de auditoría."""

    def __init__(self):
        self._query_id = f"q-{uuid.uuid4().hex[:8]}"
        self._actor_ids: list[str] = []
        self._resource_ids: list[str] = []
        self._resource_types: list[str] = []
        self._categories: list[str] = []
        self._actions: list[str] = []
        self._severities: list[str] = []
        self._tenant_ids: list[str] = []
        self._establishment_ids: list[str] = []
        self._since: Optional[datetime] = None
        self._until: Optional[datetime] = None
        self._phi_only: bool = False
        self._search_text: str = ""
        self._limit: int = 100
        self._offset: int = 0
        self._sort_by: str = "timestamp"
        self._sort_order: str = "desc"
        self._include_metadata: bool = True
        self._group_by: Optional[str] = None

    # Filter methods
    def actor(self, actor_id: str) -> "AuditQueryBuilder":
        """Filtra por actor (user ID)."""
        self._actor_ids.append(actor_id)
        return self

    def actors(self, *actor_ids: str) -> "AuditQueryBuilder":
        """Filtra por múltiples actores."""
        self._actor_ids.extend(actor_ids)
        return self

    def resource(self, resource_id: str) -> "AuditQueryBuilder":
        """Filtra por recurso."""
        self._resource_ids.append(resource_id)
        return self

    def resource_type(self, resource_type: str) -> "AuditQueryBuilder":
        """Filtra por tipo de recurso."""
        self._resource_types.append(resource_type)
        return self

    def category(self, category: str) -> "AuditQueryBuilder":
        """Filtra por categoría."""
        self._categories.append(category)
        return self

    def action(self, action: str) -> "AuditQueryBuilder":
        """Filtra por acción."""
        self._actions.append(action)
        return self

    def severity(self, severity: str) -> "AuditQueryBuilder":
        """Filtra por severidad."""
        self._severities.append(severity)
        return self

    def tenant(self, tenant_id: str) -> "AuditQueryBuilder":
        """Filtra por tenant."""
        self._tenant_ids.append(tenant_id)
        return self

    def establishment(self, establishment_id: str) -> "AuditQueryBuilder":
        """Filtra por establecimiento."""
        self._establishment_ids.append(establishment_id)
        return self

    def time_range(
        self,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
    ) -> "AuditQueryBuilder":
        """Filtra por rango de tiempo."""
        self._since = since
        self._until = until
        return self

    def today(self) -> "AuditQueryBuilder":
        """Filtra eventos de hoy."""
        now = datetime.now(timezone.utc)
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        return self.time_range(since=start, until=now)

    def last_days(self, days: int) -> "AuditQueryBuilder":
        """Filtra últimos N días."""
        since = datetime.now(timezone.utc) - timedelta(days=days)
        return self.time_range(since=since)

    def last_hours(self, hours: int) -> "AuditQueryBuilder":
        """Filtra últimas N horas."""
        since = datetime.now(timezone.utc) - timedelta(hours=hours)
        return self.time_range(since=since)

    def phi_only(self) -> "AuditQueryBuilder":
        """Solo eventos PHI access."""
        self._phi_only = True
        return self

    def search(self, text: str) -> "AuditQueryBuilder":
        """Búsqueda de texto."""
        self._search_text = text
        return self

    def severity_at_least(self, min_severity: str) -> "AuditQueryBuilder":
        """Filtra por severidad mínima."""
        severity_order = ["info", "low", "medium", "high", "critical"]
        min_idx = severity_order.index(min_severity) if min_severity in severity_order else 0
        for sev in severity_order[min_idx:]:
            self._severities.append(sev)
        return self

    def pagination(self, limit: int = 100, offset: int = 0) -> "AuditQueryBuilder":
        """Configura paginación."""
        self._limit = limit
        self._offset = offset
        return self

    def sort(self, by: str = "timestamp", order: str = "desc") -> "AuditQueryBuilder":
        """Configura ordenamiento."""
        self._sort_by = by
        self._sort_order = order
        return self

    def group_by(self, field_name: str) -> "AuditQueryBuilder":
        """Agrupa resultados por campo."""
        self._group_by = field_name
        return self

    def build(self) -> dict:
        """Construye query dict."""
        return {
            "query_id": self._query_id,
            "actor_ids": list(self._actor_ids),
            "resource_ids": list(self._resource_ids),
            "resource_types": list(self._resource_types),
            "categories": list(self._categories),
            "actions": list(self._actions),
            "severities": list(self._severities),
            "tenant_ids": list(self._tenant_ids),
            "establishment_ids": list(self._establishment_ids),
            "since": self._since,
            "until": self._until,
            "phi_access_only": self._phi_only,
            "search_text": self._search_text,
            "limit": self._limit,
            "offset": self._offset,
            "sort_by": self._sort_by,
            "sort_order": self._sort_order,
            "include_metadata": self._include_metadata,
            "group_by": self._group_by,
        }

    @classmethod
    def from_preset(
        cls,
        preset: QueryPreset,
        **kwargs,
    ) -> "AuditQueryBuilder":
        """Crea query desde preset predefinido."""
        from core.PHASE_7.audit.logger.audit_logger import (
            AuditCategory, AuditAction, AuditSeverity,
        )

        builder = cls()

        if preset == QueryPreset.PHI_ACCESS:
            return builder.category(AuditCategory.PHI_ACCESS.value).phi_only()

        elif preset == QueryPreset.FAILED_LOGINS:
            return builder.category(AuditCategory.AUTHENTICATION.value).action(AuditAction.LOGIN_FAILED.value)

        elif preset == QueryPreset.DATA_MODIFICATIONS:
            return builder.category(AuditCategory.DATA_MODIFICATION.value)

        elif preset == QueryPreset.CRITICAL_EVENTS:
            return builder.severity_at_least("critical")

        elif preset == QueryPreset.USER_ACTIVITY:
            if "actor_id" in kwargs:
                return builder.actor(kwargs["actor_id"]).last_days(30)
            return builder.last_days(30)

        elif preset == QueryPreset.RESOURCE_ACCESS:
            if "resource_id" in kwargs:
                return builder.resource(kwargs["resource_id"]).last_days(90)
            return builder.last_days(90)

        elif preset == QueryPreset.HIPAA_ACCESS_LOG:
            return (
                builder
                .category(AuditCategory.PHI_ACCESS.value)
                .last_days(365)
                .sort(by="timestamp", order="desc")
                .pagination(limit=1000)
            )

        elif preset == QueryPreset.FDA_AUDIT_TRAIL:
            return (
                builder
                .category(AuditCategory.DATA_MODIFICATION.value)
                .action(AuditAction.SIGN.value)
                .last_days(365 * 6)
                .pagination(limit=5000)
            )

        elif preset == QueryPreset.ISO_AUDIT_REVIEW:
            return (
                builder
                .severity_at_least("medium")
                .last_days(365)
                .group_by("actor_id")
            )

        return builder


# Preset query helpers
class AuditPresetQueries:
    """Consultas predefinidas para compliance."""

    @staticmethod
    def hipaa_access_report(patient_id: str, since_days: int = 365) -> dict:
        """Reporte HIPAA de acceso a paciente."""
        return (
            AuditQueryBuilder()
            .category("phi_access")
            .resource(patient_id)
            .last_days(since_days)
            .sort(by="timestamp")
            .pagination(limit=10000)
            .build()
        )

    @staticmethod
    def security_incident_report(since_days: int = 7) -> dict:
        """Reporte de incidentes de seguridad."""
        return (
            AuditQueryBuilder()
            .category("security")
            .severity_at_least("high")
            .last_days(since_days)
            .build()
        )

    @staticmethod
    def user_access_review(user_id: str) -> dict:
        """Review de acceso de usuario para auditoría."""
        return (
            AuditQueryBuilder()
            .actor(user_id)
            .last_days(90)
            .group_by("resource_type")
            .build()
        )

    @staticmethod
    def fda_electronic_records_trail(record_id: str) -> dict:
        """Audit trail FDA 21 CFR Part 11 para registro electrónico."""
        return (
            AuditQueryBuilder()
            .resource(record_id)
            .last_days(365 * 6)
            .sort(by="timestamp")
            .pagination(limit=10000)
            .build()
        )

    @staticmethod
    def compliance_summary(tenant_id: str, since_days: int = 90) -> dict:
        """Resumen de compliance para tenant."""
        return (
            AuditQueryBuilder()
            .tenant(tenant_id)
            .last_days(since_days)
            .group_by("category")
            .build()
        )
