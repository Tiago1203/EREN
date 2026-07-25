"""
PHASE 7 - EPIC 1: Audit API

REST API para auditoría:
- Query endpoints
- Event ingestion
- Statistics
- Integration with FastAPI/Pydantic
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
import uuid


# --- Request Models ---

@dataclass
class AuditQueryRequest:
    """Request para consulta de auditoría."""
    actor_ids: list[str] = field(default_factory=list)
    resource_ids: list[str] = field(default_factory=list)
    resource_types: list[str] = field(default_factory=list)
    categories: list[str] = field(default_factory=list)
    actions: list[str] = field(default_factory=list)
    severities: list[str] = field(default_factory=list)
    since: Optional[str] = None    # ISO format
    until: Optional[str] = None    # ISO format
    phi_access_only: bool = False
    search_text: str = ""
    limit: int = 100
    offset: int = 0
    sort_by: str = "timestamp"
    sort_order: str = "desc"


@dataclass
class AuditEventRequest:
    """Request para crear evento de auditoría."""
    actor_id: str
    actor_name: str
    actor_role: str
    category: str
    action: str
    resource_type: str
    resource_id: str = ""
    resource_name: str = ""
    session_id: str = ""
    ip_address: str = ""
    purpose_of_use: str = "treatment"
    reason: str = ""
    previous_value: str = ""
    new_value: str = ""
    is_phi_access: bool = False
    regulatory_flags: list[str] = field(default_factory=list)
    tenant_id: str = ""
    establishment_id: str = ""
    workstation: str = ""


@dataclass
class ComplianceReportRequest:
    """Request para reporte de compliance."""
    tenant_id: str
    report_type: str              # hipaa, fda, iso
    period_days: int = 365
    record_type: str = ""         # Para FDA
    actor_id: str = ""            # Para user-specific reports


# --- Response Models ---

@dataclass
class AuditEventResponse:
    """Response de evento de auditoría."""
    event_id: str
    timestamp: str
    actor_id: str
    actor_name: str
    actor_role: str
    category: str
    action: str
    resource_type: str
    resource_id: str
    resource_name: str
    severity: str
    is_phi_access: bool
    success: bool
    duration_ms: int
    reason: str


@dataclass
class AuditQueryResponse:
    """Response de consulta de auditoría."""
    query_id: str
    total: int
    returned: int
    offset: int
    limit: int
    events: list[dict]
    aggregations: dict


@dataclass
class AuditStatistics:
    """Estadísticas de auditoría."""
    total_events: int
    by_category: dict
    by_action: dict
    by_severity: dict
    phi_access_count: int
    failed_events_count: int
    chain_integrity: bool
    first_event: Optional[str]
    last_event: Optional[str]


# --- API Service ---

class AuditAPIService:
    """
    Servicio de API de auditoría.
    Provee endpoints lógicos para consumo por controllers FastAPI.
    """

    def __init__(
        self,
        audit_logger: Any,
        audit_repository: Any,
        hipaa_reporter: Any,
        fda_reporter: Any,
        iso_reporter: Any,
    ):
        self._logger = audit_logger
        self._repo = audit_repository
        self._hipaa = hipaa_reporter
        self._fda = fda_reporter
        self._iso = iso_reporter

    def query_events(self, request: AuditQueryRequest) -> AuditQueryResponse:
        """Consulta eventos de auditoría."""
        from core.PHASE_7.audit.repository.query_builder import AuditQueryBuilder

        since = datetime.fromisoformat(request.since) if request.since else None
        until = datetime.fromisoformat(request.until) if request.until else None

        builder = (
            AuditQueryBuilder()
            .pagination(request.limit, request.offset)
            .sort(request.sort_by, request.sort_order)
        )

        if request.actor_ids:
            for aid in request.actor_ids:
                builder.actor(aid)
        if request.resource_ids:
            for rid in request.resource_ids:
                builder.resource(rid)
        if request.resource_types:
            for rt in request.resource_types:
                builder.resource_type(rt)
        if request.categories:
            for cat in request.categories:
                builder.category(cat)
        if request.actions:
            for act in request.actions:
                builder.action(act)
        if request.severities:
            for sev in request.severities:
                builder.severity(sev)
        if request.since or request.until:
            builder.time_range(since, until)
        if request.phi_access_only:
            builder.phi_only()
        if request.search_text:
            builder.search(request.search_text)

        result = self._repo.query(builder.build())

        return AuditQueryResponse(
            query_id=result.get("query_id", ""),
            total=result.get("total", 0),
            returned=result.get("returned", 0),
            offset=request.offset,
            limit=request.limit,
            events=result.get("events", []),
            aggregations=result.get("aggregations", {}),
        )

    def log_event(self, request: AuditEventRequest) -> str:
        """Registra un nuevo evento de auditoría."""
        from core.PHASE_7.audit.logger.audit_logger import AuditCategory, AuditAction

        event = self._logger.log(
            actor_id=request.actor_id,
            actor_name=request.actor_name,
            actor_role=request.actor_role,
            category=AuditCategory(request.category),
            action=AuditAction(request.action),
            resource_type=request.resource_type,
            resource_id=request.resource_id,
            resource_name=request.resource_name,
            session_id=request.session_id,
            ip_address=request.ip_address,
            purpose_of_use=request.purpose_of_use,
            reason=request.reason,
            previous_value=request.previous_value,
            new_value=request.new_value,
            is_phi_access=request.is_phi_access,
            regulatory_flags=request.regulatory_flags,
            tenant_id=request.tenant_id,
            establishment_id=request.establishment_id,
            workstation=request.workstation,
        )

        # Also persist to repository
        self._repo.save_event(self._event_to_dict(event))

        return event.event_id

    def get_statistics(self, tenant_id: str, since_days: int = 7) -> AuditStatistics:
        """Obtiene estadísticas de auditoría."""
        from datetime import timedelta
        since = datetime.now(timezone.utc) - timedelta(days=since_days)
        stats = self._logger.get_statistics(since=since)

        return AuditStatistics(
            total_events=stats.get("total_events", 0),
            by_category=stats.get("by_category", {}),
            by_action=stats.get("by_action", {}),
            by_severity=stats.get("by_severity", {}),
            phi_access_count=stats.get("phi_access_count", 0),
            failed_events_count=stats.get("failed_events_count", 0),
            chain_integrity=stats.get("chain_integrity", True),
            first_event=stats.get("first_event"),
            last_event=stats.get("last_event"),
        )

    def get_phi_access_log(
        self,
        tenant_id: str,
        actor_id: Optional[str] = None,
        period_days: int = 365,
    ) -> list[dict]:
        """Obtiene log de acceso PHI (HIPAA requirement)."""
        from datetime import timedelta
        since = datetime.now(timezone.utc) - timedelta(days=period_days)
        events = self._logger.get_phi_access_events(since=since)
        if actor_id:
            events = [e for e in events if e.actor_id == actor_id]
        return [self._event_to_dict(e) for e in events]

    def verify_chain_integrity(self) -> dict:
        """Verifica integridad de la cadena de auditoría."""
        valid, errors = self._logger.verify_chain_integrity()
        return {
            "valid": valid,
            "total_errors": len(errors),
            "errors": errors[:10],
            "verified_at": datetime.now(timezone.utc).isoformat(),
        }

    def _event_to_dict(self, event) -> dict:
        """Convierte AuditEvent a dict."""
        return {
            "event_id": event.event_id,
            "timestamp": event.timestamp.isoformat(),
            "actor_id": event.actor_id,
            "actor_name": event.actor_name,
            "actor_role": event.actor_role,
            "category": event.category.value,
            "action": event.action.value,
            "resource_type": event.resource_type,
            "resource_id": event.resource_id,
            "resource_name": event.resource_name,
            "severity": event.severity.value,
            "is_phi_access": event.is_phi_access,
            "success": event.success,
            "duration_ms": event.duration_ms,
            "reason": event.reason,
            "ip_address": event.ip_address,
            "session_id": event.session_id,
            "event_hash": event.event_hash,
            "previous_event_hash": event.previous_event_hash,
            "metadata": event.metadata,
        }
