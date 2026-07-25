"""
PHASE 7 - EPIC 1: Audit Logger

Sistema de auditoría estructurado:
- Captura de eventos de auditoría
- Campos obligatorios HIPAA/FDA
- Clasificación por severidad
- Integración con EPIC 0 (security)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Optional, Any
import uuid
import json
import hashlib


class AuditCategory(str, Enum):
    """Categorías de auditoría."""
    AUTHENTICATION = "authentication"       # Login, logout, MFA
    AUTHORIZATION = "authorization"         # Permisos, accesos
    DATA_ACCESS = "data_access"           # Lectura de datos
    DATA_MODIFICATION = "data_modification" # Crear, actualizar, eliminar
    PHI_ACCESS = "phi_access"             # Acceso a PHI (HIPAA required)
    SYSTEM_CONFIG = "system_config"       # Cambios de configuración
    USER_MANAGEMENT = "user_management"    # CRUD de usuarios
    TENANT_OPERATION = "tenant_operation"   # Operaciones de tenant
    COMPLIANCE = "compliance"             # Acciones de compliance
    SECURITY = "security"                # Eventos de seguridad


class AuditSeverity(str, Enum):
    """Severidad del evento."""
    CRITICAL = "critical"    # PHI access, security breach, config change
    HIGH = "high"          # Unauthorized access attempt
    MEDIUM = "medium"     # Data modification
    LOW = "low"           # Read operations
    INFO = "info"          # Informational only


class AuditAction(str, Enum):
    """Acciones de auditoría."""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    LOGIN_FAILED = "login_failed"
    ACCESS_ATTEMPT = "access_attempt"
    ACCESS_DENIED = "access_denied"
    EXPORT = "export"
    PRINT = "print"
    SIGN = "sign"
    APPROVE = "approve"
    REJECT = "reject"
    CONFIG_CHANGE = "config_change"
    ROLE_CHANGE = "role_change"
    EXPORT_DATA = "export_data"
    VIEW = "view"


@dataclass
class AuditEvent:
    """Evento de auditoría individual."""
    event_id: str
    timestamp: datetime
    actor_id: str
    actor_name: str
    actor_role: str
    category: AuditCategory
    action: AuditAction
    resource_type: str
    session_id: str = ""
    ip_address: str = ""
    user_agent: str = ""
    resource_id: str = ""
    resource_name: str = ""
    previous_value: str = ""
    new_value: str = ""
    change_summary: str = ""
    purpose_of_use: str = "treatment"
    reason: str = ""
    workstation: str = ""
    tenant_id: str = ""
    establishment_id: str = ""
    department_id: str = ""
    severity: AuditSeverity = AuditSeverity.LOW
    is_phi_access: bool = False
    regulatory_flags: list[str] = field(default_factory=list)
    event_hash: str = ""
    previous_event_hash: str = ""
    duration_ms: int = 0
    success: bool = True
    error_message: str = ""
    metadata: dict = field(default_factory=dict)


@dataclass
class AuditLog:
    """Log de auditoría (colección de eventos)."""
    log_id: str
    tenant_id: str
    start_time: datetime
    end_time: datetime
    total_events: int = 0
    critical_events: int = 0
    phi_access_count: int = 0


@dataclass
class AuditRetentionPolicy:
    """Política de retención."""
    policy_id: str
    name: str
    retention_days: int
    archive_after_days: int
    delete_after_days: int
    categories: list[AuditCategory]


class AuditLogger:
    """Logger de auditoría principal."""

    # Retention policies
    DEFAULT_RETENTION = AuditRetentionPolicy(
        policy_id="default",
        name="Default Retention",
        retention_days=2190,        # 6 years (HIPAA)
        archive_after_days=365,     # 1 year online
        delete_after_days=2190,
        categories=list(AuditCategory),
    )

    PHI_RETENTION = AuditRetentionPolicy(
        policy_id="phi",
        name="PHI Access Retention",
        retention_days=2190,        # 6 years HIPAA
        archive_after_days=365,
        delete_after_days=2190,
        categories=[AuditCategory.PHI_ACCESS, AuditCategory.AUTHENTICATION],
    )

    def __init__(self):
        self._events: list[AuditEvent] = []
        self._last_hash: str = ""
        self._event_counts: dict[str, int] = {}
        self._retention_policies: dict[str, AuditRetentionPolicy] = {
            "default": self.DEFAULT_RETENTION,
            "phi": self.PHI_RETENTION,
        }

    def _compute_hash(self, event: AuditEvent, prev_hash: str) -> str:
        """Computa hash del evento para tamper-evidence."""
        data = (
            f"{event.event_id}:{event.timestamp.isoformat()}:"
            f"{event.actor_id}:{event.action.value}:"
            f"{event.resource_id}:{prev_hash}"
        )
        return hashlib.sha256(data.encode()).hexdigest()

    def log(
        self,
        actor_id: str,
        actor_name: str,
        actor_role: str,
        category: AuditCategory,
        action: AuditAction,
        resource_type: str,
        resource_id: str = "",
        resource_name: str = "",
        session_id: str = "",
        ip_address: str = "",
        user_agent: str = "",
        purpose_of_use: str = "treatment",
        reason: str = "",
        previous_value: str = "",
        new_value: str = "",
        change_summary: str = "",
        is_phi_access: bool = False,
        regulatory_flags: Optional[list[str]] = None,
        success: bool = True,
        error_message: str = "",
        duration_ms: int = 0,
        metadata: Optional[dict] = None,
        tenant_id: str = "",
        establishment_id: str = "",
        department_id: str = "",
        workstation: str = "",
    ) -> AuditEvent:
        """Registra un evento de auditoría."""
        event_id = f"audit-{uuid.uuid4().hex[:16]}"

        # Determine severity based on category and action
        severity = self._determine_severity(category, action, is_phi_access, success)

        event = AuditEvent(
            event_id=event_id,
            timestamp=datetime.now(timezone.utc),
            actor_id=actor_id,
            actor_name=actor_name,
            actor_role=actor_role,
            session_id=session_id,
            ip_address=ip_address,
            user_agent=user_agent,
            category=category,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            resource_name=resource_name,
            previous_value=previous_value,
            new_value=new_value,
            change_summary=change_summary,
            purpose_of_use=purpose_of_use,
            reason=reason,
            tenant_id=tenant_id,
            establishment_id=establishment_id,
            department_id=department_id,
            workstation=workstation,
            severity=severity,
            is_phi_access=is_phi_access,
            regulatory_flags=regulatory_flags or [],
            success=success,
            error_message=error_message,
            duration_ms=duration_ms,
            metadata=metadata or {},
            previous_event_hash=self._last_hash,
        )

        # Compute tamper-evident hash
        event.event_hash = self._compute_hash(event, self._last_hash)
        self._last_hash = event.event_hash

        self._events.append(event)

        # Update counters
        self._event_counts[category.value] = self._event_counts.get(category.value, 0) + 1
        if is_phi_access:
            self._event_counts["phi_access"] = self._event_counts.get("phi_access", 0) + 1

        return event

    def _determine_severity(
        self,
        category: AuditCategory,
        action: AuditAction,
        is_phi_access: bool,
        success: bool,
    ) -> AuditSeverity:
        """Determina severidad del evento."""
        if is_phi_access:
            return AuditSeverity.CRITICAL
        if category == AuditCategory.SECURITY:
            return AuditSeverity.HIGH
        if action == AuditAction.ACCESS_DENIED:
            return AuditSeverity.HIGH
        if action == AuditAction.LOGIN_FAILED:
            return AuditSeverity.MEDIUM
        if category == AuditCategory.DATA_MODIFICATION:
            return AuditSeverity.MEDIUM
        if category == AuditCategory.SYSTEM_CONFIG:
            return AuditSeverity.MEDIUM
        return AuditSeverity.LOW

    def log_phi_access(
        self,
        actor_id: str,
        actor_name: str,
        actor_role: str,
        resource_type: str,
        resource_id: str,
        purpose_of_use: str = "treatment",
        reason: str = "",
        session_id: str = "",
        ip_address: str = "",
    ) -> AuditEvent:
        """Registra acceso PHI (HIPAA requirement)."""
        return self.log(
            actor_id=actor_id,
            actor_name=actor_name,
            actor_role=actor_role,
            category=AuditCategory.PHI_ACCESS,
            action=AuditAction.READ,
            resource_type=resource_type,
            resource_id=resource_id,
            session_id=session_id,
            ip_address=ip_address,
            purpose_of_use=purpose_of_use,
            reason=reason,
            is_phi_access=True,
            regulatory_flags=["HIPAA_164_312_b"],
        )

    def log_authentication(
        self,
        actor_id: str,
        actor_name: str,
        success: bool,
        ip_address: str = "",
        reason: str = "",
    ) -> AuditEvent:
        """Registra evento de autenticación."""
        return self.log(
            actor_id=actor_id,
            actor_name=actor_name,
            actor_role="",
            category=AuditCategory.AUTHENTICATION,
            action=AuditAction.LOGIN if success else AuditAction.LOGIN_FAILED,
            resource_type="session",
            ip_address=ip_address,
            success=success,
            error_message=reason if not success else "",
        )

    def log_data_access(
        self,
        actor_id: str,
        actor_name: str,
        actor_role: str,
        resource_type: str,
        resource_id: str,
        action: AuditAction = AuditAction.READ,
        session_id: str = "",
        ip_address: str = "",
    ) -> AuditEvent:
        """Registra acceso a datos."""
        category = AuditCategory.PHI_ACCESS if self._is_phi_resource(resource_type) else AuditCategory.DATA_ACCESS
        is_phi = category == AuditCategory.PHI_ACCESS
        return self.log(
            actor_id=actor_id,
            actor_name=actor_name,
            actor_role=actor_role,
            category=category,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            session_id=session_id,
            ip_address=ip_address,
            is_phi_access=is_phi,
        )

    def log_data_modification(
        self,
        actor_id: str,
        actor_name: str,
        actor_role: str,
        resource_type: str,
        resource_id: str,
        action: AuditAction,
        previous_value: str = "",
        new_value: str = "",
        reason: str = "",
        session_id: str = "",
        ip_address: str = "",
    ) -> AuditEvent:
        """Registra modificación de datos."""
        is_phi = self._is_phi_resource(resource_type)
        return self.log(
            actor_id=actor_id,
            actor_name=actor_name,
            actor_role=actor_role,
            category=AuditCategory.PHI_ACCESS if is_phi else AuditCategory.DATA_MODIFICATION,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            previous_value=previous_value,
            new_value=new_value,
            change_summary=f"{action.value}: {resource_type}/{resource_id}",
            reason=reason,
            session_id=session_id,
            ip_address=ip_address,
            is_phi_access=is_phi,
        )

    def _is_phi_resource(self, resource_type: str) -> bool:
        """Determina si recurso es PHI."""
        phi_resources = {"paciente", "patient", "medical_record", "diagnosis", "treatment", "medication"}
        return resource_type.lower() in phi_resources

    def get_events(
        self,
        actor_id: Optional[str] = None,
        resource_id: Optional[str] = None,
        category: Optional[AuditCategory] = None,
        action: Optional[AuditAction] = None,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        is_phi_access: Optional[bool] = None,
        limit: int = 1000,
    ) -> list[AuditEvent]:
        """Consulta eventos de auditoría."""
        events = self._events

        if actor_id:
            events = [e for e in events if e.actor_id == actor_id]
        if resource_id:
            events = [e for e in events if e.resource_id == resource_id]
        if category:
            events = [e for e in events if e.category == category]
        if action:
            events = [e for e in events if e.action == action]
        if since:
            events = [e for e in events if e.timestamp >= since]
        if until:
            events = [e for e in events if e.timestamp <= until]
        if is_phi_access is not None:
            events = [e for e in events if e.is_phi_access == is_phi_access]

        # Sort by timestamp descending
        events.sort(key=lambda e: e.timestamp, reverse=True)
        return events[:limit]

    def get_phi_access_events(
        self,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
    ) -> list[AuditEvent]:
        """Obtiene todos los accesos PHI."""
        return self.get_events(
            category=AuditCategory.PHI_ACCESS,
            since=since,
            until=until,
            is_phi_access=True,
        )

    def get_critical_events(
        self,
        since: Optional[datetime] = None,
        limit: int = 100,
    ) -> list[AuditEvent]:
        """Obtiene eventos críticos."""
        return self.get_events(
            since=since,
            limit=limit,
        )

    def get_user_activity(
        self,
        actor_id: str,
        since: Optional[datetime] = None,
    ) -> list[AuditEvent]:
        """Obtiene actividad de un usuario."""
        return self.get_events(actor_id=actor_id, since=since)

    def get_resource_history(
        self,
        resource_id: str,
        since: Optional[datetime] = None,
    ) -> list[AuditEvent]:
        """Obtiene historial de un recurso."""
        return self.get_events(resource_id=resource_id, since=since)

    def verify_chain_integrity(self) -> tuple[bool, list[str]]:
        """Verifica integridad de la cadena de auditoría."""
        errors = []
        if not self._events:
            return True, []

        for i, event in enumerate(self._events):
            computed = self._compute_hash(event, event.previous_event_hash)
            if computed != event.event_hash:
                errors.append(f"Event {event.event_id}: hash mismatch")
            if i > 0:
                prev_event = self._events[i - 1]
                if event.previous_event_hash != prev_event.event_hash:
                    errors.append(f"Event {event.event_id}: broken chain link")

        return len(errors) == 0, errors

    def get_statistics(
        self,
        since: Optional[datetime] = None,
    ) -> dict:
        """Obtiene estadísticas de auditoría."""
        events = self.get_events(since=since, limit=100000)

        by_category = {}
        by_action = {}
        by_severity = {}
        by_user = {}

        for e in events:
            by_category[e.category.value] = by_category.get(e.category.value, 0) + 1
            by_action[e.action.value] = by_action.get(e.action.value, 0) + 1
            by_severity[e.severity.value] = by_severity.get(e.severity.value, 0) + 1
            by_user[e.actor_name] = by_user.get(e.actor_name, 0) + 1

        phi_events = [e for e in events if e.is_phi_access]
        failed_events = [e for e in events if not e.success]

        return {
            "total_events": len(events),
            "by_category": by_category,
            "by_action": by_action,
            "by_severity": by_severity,
            "by_user": by_user,
            "phi_access_count": len(phi_events),
            "failed_events_count": len(failed_events),
            "chain_integrity": self.verify_chain_integrity()[0],
            "first_event": events[-1].timestamp.isoformat() if events else None,
            "last_event": events[0].timestamp.isoformat() if events else None,
        }

    def generate_summary(
        self,
        since: Optional[datetime] = None,
    ) -> AuditLog:
        """Genera resumen de log."""
        events = self.get_events(since=since, limit=100000)
        return AuditLog(
            log_id=f"log-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
            tenant_id=events[0].tenant_id if events else "",
            start_time=events[-1].timestamp if events else datetime.now(timezone.utc),
            end_time=events[0].timestamp if events else datetime.now(timezone.utc),
            total_events=len(events),
            critical_events=sum(1 for e in events if e.severity == AuditSeverity.CRITICAL),
            phi_access_count=sum(1 for e in events if e.is_phi_access),
        )
