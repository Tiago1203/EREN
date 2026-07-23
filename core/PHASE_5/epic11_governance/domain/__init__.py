"""
PHASE 5 - EPIC 11: Governance Domain Objects

Domain objects especializados para gobierno:
- AgentPolicy
- AgentPermission
- AgentAudit
- GovernanceRule
- AgentVersion
- GovernanceReport
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any, Optional
import uuid


# =============================================================================
# ENUMS
# =============================================================================

class PolicyType(str, Enum):
    """Tipos de política."""
    SECURITY = "security"           # Seguridad
    ACCESS = "access"             # Acceso
    BEHAVIOR = "behavior"         # Comportamiento
    DATA = "data"                 # Datos
    COMPLIANCE = "compliance"     # Cumplimiento


class PolicyStatus(str, Enum):
    """Estado de política."""
    DRAFT = "draft"             # Borrador
    ACTIVE = "active"           # Activa
    SUSPENDED = "suspended"     # Suspendida
    DEPRECATED = "deprecated"   # Obsoleta


class PermissionType(str, Enum):
    """Tipos de permiso."""
    READ = "read"               # Lectura
    WRITE = "write"             # Escritura
    EXECUTE = "execute"         # Ejecución
    ADMIN = "admin"             # Administración
    DELEGATE = "delegate"        # Delegación


class AuditType(str, Enum):
    """Tipos de auditoría."""
    ACTION = "action"           # Acción
    ACCESS = "access"           # Acceso
    CHANGE = "change"            # Cambio
    SECURITY = "security"       # Seguridad
    COMPLIANCE = "compliance"    # Cumplimiento


class AuditStatus(str, Enum):
    """Estado de auditoría."""
    PENDING = "pending"         # Pendiente
    COMPLETED = "completed"      # Completada
    FAILED = "failed"           # Fallida
    REVIEWED = "reviewed"        # Revisada


class RuleType(str, Enum):
    """Tipos de regla."""
    PERMISSION = "permission"    # Permiso
    RESTRICTION = "restriction"  # Restricción
    REQUIREMENT = "requirement"  # Requisito
    BEST_PRACTICE = "best_practice"  # Mejores prácticas


class VersionStatus(str, Enum):
    """Estado de versión."""
    DRAFT = "draft"           # Borrador
    TESTING = "testing"       # En pruebas
    RELEASED = "released"     # Liberada
    DEPRECATED = "deprecated" # Obsoleta
    ROLLBACK = "rollback"     # Reversión


class ReportType(str, Enum):
    """Tipos de reporte."""
    COMPLIANCE = "compliance"     # Cumplimiento
    SECURITY = "security"       # Seguridad
    PERFORMANCE = "performance" # Rendimiento
    AUDIT = "audit"             # Auditoría
    SUMMARY = "summary"         # Resumen


# =============================================================================
# AGENT POLICY
# =============================================================================

@dataclass
class AgentPolicy:
    """Política de agente."""
    policy_id: str = ""
    name: str = ""
    description: str = ""
    
    # Tipo y estado
    policy_type: PolicyType = PolicyType.SECURITY
    status: PolicyStatus = PolicyStatus.DRAFT
    
    # Contenido
    rules: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    
    # Alcance
    agent_ids: list[str] = field(default_factory=list)
    
    # Metadatos
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    created_by: str = ""
    
    def __post_init__(self):
        if not self.policy_id:
            self.policy_id = str(uuid.uuid4())
    
    def activate(self) -> None:
        """Activa la política."""
        self.status = PolicyStatus.ACTIVE
        self.updated_at = datetime.now(UTC)
    
    def suspend(self) -> None:
        """Suspende la política."""
        self.status = PolicyStatus.SUSPENDED
        self.updated_at = datetime.now(UTC)
    
    def add_rule(self, rule: str) -> None:
        """Agrega una regla."""
        if rule not in self.rules:
            self.rules.append(rule)
            self.updated_at = datetime.now(UTC)


# =============================================================================
# AGENT PERMISSION
# =============================================================================

@dataclass
class AgentPermission:
    """Permiso de agente."""
    permission_id: str = ""
    agent_id: str = ""
    resource: str = ""
    
    # Tipo
    permission_type: PermissionType = PermissionType.READ
    
    # Estado
    granted: bool = False
    granted_by: str = ""
    granted_at: datetime | None = None
    
    # Validez
    valid_from: datetime = field(default_factory=lambda: datetime.now(UTC))
    valid_until: datetime | None = None
    
    def __post_init__(self):
        if not self.permission_id:
            self.permission_id = str(uuid.uuid4())
    
    def grant(self, granted_by: str) -> None:
        """Otorga el permiso."""
        self.granted = True
        self.granted_by = granted_by
        self.granted_at = datetime.now(UTC)
    
    def revoke(self) -> None:
        """Revoca el permiso."""
        self.granted = False
    
    def is_valid(self) -> bool:
        """Verifica si el permiso es válido."""
        if not self.granted:
            return False
        
        now = datetime.now(UTC)
        if self.valid_until and now > self.valid_until:
            return False
        
        return True


# =============================================================================
# AGENT AUDIT
# =============================================================================

@dataclass
class AgentAudit:
    """Auditoría de agente."""
    audit_id: str = ""
    agent_id: str = ""
    
    # Tipo
    audit_type: AuditType = AuditType.ACTION
    
    # Detalles
    action: str = ""
    details: str = ""
    
    # Resultado
    status: AuditStatus = AuditStatus.PENDING
    result: str = ""
    
    # Usuario
    performed_by: str = ""
    
    # Metadatos
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    completed_at: datetime | None = None
    
    def __post_init__(self):
        if not self.audit_id:
            self.audit_id = str(uuid.uuid4())
    
    def complete(self, result: str) -> None:
        """Completa la auditoría."""
        self.status = AuditStatus.COMPLETED
        self.result = result
        self.completed_at = datetime.now(UTC)
    
    def fail(self, reason: str) -> None:
        """Marca como fallida."""
        self.status = AuditStatus.FAILED
        self.result = reason
        self.completed_at = datetime.now(UTC)


# =============================================================================
# GOVERNANCE RULE
# =============================================================================

@dataclass
class GovernanceRule:
    """Regla de gobierno."""
    rule_id: str = ""
    name: str = ""
    description: str = ""
    
    # Tipo
    rule_type: RuleType = RuleType.PERMISSION
    
    # Condición
    condition: str = ""
    action: str = ""
    
    # Estado
    enabled: bool = True
    priority: int = 5  # 1-10
    
    # Metadatos
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    
    def __post_init__(self):
        if not self.rule_id:
            self.rule_id = str(uuid.uuid4())
    
    def enable(self) -> None:
        """Habilita la regla."""
        self.enabled = True
    
    def disable(self) -> None:
        """Deshabilita la regla."""
        self.enabled = False


# =============================================================================
# AGENT VERSION
# =============================================================================

@dataclass
class AgentVersion:
    """Versión de agente."""
    version_id: str = ""
    agent_id: str = ""
    version: str = ""
    
    # Estado
    status: VersionStatus = VersionStatus.DRAFT
    
    # Detalles
    changelog: str = ""
    dependencies: list[str] = field(default_factory=list)
    
    # Metadatos
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    released_at: datetime | None = None
    deprecated_at: datetime | None = None
    
    def __post_init__(self):
        if not self.version_id:
            self.version_id = str(uuid.uuid4())
    
    def release(self) -> None:
        """Libera la versión."""
        self.status = VersionStatus.RELEASED
        self.released_at = datetime.now(UTC)
    
    def deprecate(self) -> None:
        """Obsoleta la versión."""
        self.status = VersionStatus.DEPRECATED
        self.deprecated_at = datetime.now(UTC)


# =============================================================================
# GOVERNANCE REPORT
# =============================================================================

@dataclass
class GovernanceReport:
    """Reporte de gobierno."""
    report_id: str = ""
    
    # Tipo
    report_type: ReportType = ReportType.SUMMARY
    
    # Contenido
    title: str = ""
    summary: str = ""
    findings: list[str] = field(default_factory=list)
    
    # Métricas
    metrics: dict = field(default_factory=dict)
    
    # Período
    period_start: datetime = field(default_factory=lambda: datetime.now(UTC))
    period_end: datetime = field(default_factory=lambda: datetime.now(UTC))
    
    # Metadatos
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    created_by: str = ""
    
    def __post_init__(self):
        if not self.report_id:
            self.report_id = str(uuid.uuid4())
    
    def add_finding(self, finding: str) -> None:
        """Agrega un hallazgo."""
        if finding not in self.findings:
            self.findings.append(finding)
    
    def add_metric(self, key: str, value: Any) -> None:
        """Agrega una métrica."""
        self.metrics[key] = value


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Enums
    "PolicyType",
    "PolicyStatus",
    "PermissionType",
    "AuditType",
    "AuditStatus",
    "RuleType",
    "VersionStatus",
    "ReportType",
    # Domain Objects
    "AgentPolicy",
    "AgentPermission",
    "AgentAudit",
    "GovernanceRule",
    "AgentVersion",
    "GovernanceReport",
]
