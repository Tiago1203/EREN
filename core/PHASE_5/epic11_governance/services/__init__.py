"""
PHASE 5 - EPIC 11: Governance Services

Servicios especializados para gobierno:
- GovernanceService
- PermissionService
- AuditService
- PolicyEngine
- ComplianceValidator
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Optional
import logging

logger = logging.getLogger(__name__)

# =============================================================================
# IMPORTS FROM EPIC 11 DOMAIN
# =============================================================================

from core.PHASE_5.epic11_governance.domain import (
    AgentPolicy,
    PolicyType,
    PolicyStatus,
    AgentPermission,
    PermissionType,
    AgentAudit,
    AuditType,
    AuditStatus,
    GovernanceRule,
    RuleType,
    AgentVersion,
    VersionStatus,
    GovernanceReport,
    ReportType,
)


# =============================================================================
# RESULT CLASSES
# =============================================================================

@dataclass
class PermissionResult:
    """Resultado de permiso."""
    granted: bool
    permission: AgentPermission | None = None
    reason: str = ""


@dataclass
class AuditResult:
    """Resultado de auditoría."""
    audit_id: str
    success: bool = False
    findings: list[str] = field(default_factory=list)


@dataclass
class PolicyResult:
    """Resultado de política."""
    policy_id: str
    compliant: bool = False
    violations: list[str] = field(default_factory=list)


@dataclass
class ComplianceResult:
    """Resultado de cumplimiento."""
    compliant: bool = False
    violations: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


# =============================================================================
# PERMISSION SERVICE
# =============================================================================

class PermissionService:
    """
    Servicio de permisos.
    
    Responsabilidades:
    - Gestionar permisos de agentes
    - Validar acceso a recursos
    - Delegar permisos
    """
    
    def __init__(self):
        self._permissions: dict[str, AgentPermission] = {}
    
    async def grant_permission(
        self,
        agent_id: str,
        resource: str,
        permission_type: PermissionType,
        granted_by: str,
    ) -> PermissionResult:
        """Otorga un permiso."""
        permission = AgentPermission(
            agent_id=agent_id,
            resource=resource,
            permission_type=permission_type,
        )
        permission.grant(granted_by)
        
        self._permissions[permission.permission_id] = permission
        
        logger.info(f"Granted {permission_type.value} permission to {agent_id}")
        
        return PermissionResult(
            granted=True,
            permission=permission,
            reason=f"Permission {permission_type.value} granted",
        )
    
    async def revoke_permission(self, permission_id: str) -> bool:
        """Revoca un permiso."""
        if permission_id in self._permissions:
            self._permissions[permission_id].revoke()
            return True
        return False
    
    async def check_permission(
        self,
        agent_id: str,
        resource: str,
        permission_type: PermissionType,
    ) -> bool:
        """Verifica un permiso."""
        for perm in self._permissions.values():
            if (perm.agent_id == agent_id and 
                perm.resource == resource and 
                perm.permission_type == permission_type):
                return perm.is_valid()
        return False
    
    async def get_agent_permissions(self, agent_id: str) -> list[AgentPermission]:
        """Obtiene permisos de un agente."""
        return [p for p in self._permissions.values() if p.agent_id == agent_id]


# =============================================================================
# AUDIT SERVICE
# =============================================================================

class AuditService:
    """
    Servicio de auditoría.
    
    Responsabilidades:
    - Registrar acciones de agentes
    - Auditar accesos
    - Generar reportes de auditoría
    """
    
    def __init__(self):
        self._audits: dict[str, AgentAudit] = {}
    
    async def create_audit(
        self,
        agent_id: str,
        audit_type: AuditType,
        action: str,
        performed_by: str,
        details: str = "",
    ) -> AgentAudit:
        """Crea una auditoría."""
        audit = AgentAudit(
            agent_id=agent_id,
            audit_type=audit_type,
            action=action,
            details=details,
            performed_by=performed_by,
        )
        
        self._audits[audit.audit_id] = audit
        
        logger.info(f"Created audit {audit.audit_id} for {agent_id}")
        
        return audit
    
    async def complete_audit(self, audit_id: str, result: str) -> bool:
        """Completa una auditoría."""
        if audit_id in self._audits:
            self._audits[audit_id].complete(result)
            return True
        return False
    
    async def get_agent_audits(
        self,
        agent_id: str,
        limit: int = 100,
    ) -> list[AgentAudit]:
        """Obtiene auditorías de un agente."""
        audits = [a for a in self._audits.values() if a.agent_id == agent_id]
        audits.sort(key=lambda a: a.created_at, reverse=True)
        return audits[:limit]
    
    async def generate_report(self) -> GovernanceReport:
        """Genera reporte de auditoría."""
        report = GovernanceReport(
            report_type=ReportType.AUDIT,
            title="Audit Summary Report",
            summary=f"Total audits: {len(self._audits)}",
        )
        
        # Métricas
        completed = sum(1 for a in self._audits.values() if a.status == AuditStatus.COMPLETED)
        failed = sum(1 for a in self._audits.values() if a.status == AuditStatus.FAILED)
        
        report.add_metric("total_audits", len(self._audits))
        report.add_metric("completed_audits", completed)
        report.add_metric("failed_audits", failed)
        
        return report


# =============================================================================
# POLICY ENGINE
# =============================================================================

class PolicyEngine:
    """
    Motor de políticas.
    
    Responsabilidades:
    - Gestionar políticas de agentes
    - Evaluar cumplimiento
    - Aplicar reglas
    """
    
    def __init__(self):
        self._policies: dict[str, AgentPolicy] = {}
        self._rules: dict[str, GovernanceRule] = {}
    
    async def create_policy(
        self,
        name: str,
        policy_type: PolicyType,
        created_by: str,
        description: str = "",
    ) -> AgentPolicy:
        """Crea una política."""
        policy = AgentPolicy(
            name=name,
            description=description,
            policy_type=policy_type,
            created_by=created_by,
        )
        
        self._policies[policy.policy_id] = policy
        
        logger.info(f"Created policy {policy.policy_id}")
        
        return policy
    
    async def add_rule_to_policy(
        self,
        policy_id: str,
        rule: GovernanceRule,
    ) -> bool:
        """Agrega una regla a una política."""
        if policy_id in self._policies:
            self._policies[policy_id].add_rule(rule.condition)
            self._rules[rule.rule_id] = rule
            return True
        return False
    
    async def evaluate_policy(
        self,
        policy_id: str,
        agent_id: str,
    ) -> PolicyResult:
        """Evalúa una política."""
        if policy_id not in self._policies:
            return PolicyResult(policy_id=policy_id, compliant=False)
        
        policy = self._policies[policy_id]
        
        # Placeholder - en producción evaluaría las reglas
        violations = []
        
        return PolicyResult(
            policy_id=policy_id,
            compliant=policy.status == PolicyStatus.ACTIVE and len(violations) == 0,
            violations=violations,
        )
    
    async def get_active_policies(self) -> list[AgentPolicy]:
        """Obtiene políticas activas."""
        return [p for p in self._policies.values() if p.status == PolicyStatus.ACTIVE]


# =============================================================================
# COMPLIANCE VALIDATOR
# =============================================================================

class ComplianceValidator:
    """
    Validador de cumplimiento.
    
    Responsabilidades:
    - Validar cumplimiento de políticas
    - Detectar violaciones
    - Generar reportes de cumplimiento
    """
    
    def __init__(self):
        self._validations: list[dict] = []
    
    async def validate_agent(
        self,
        agent_id: str,
        policies: list[AgentPolicy],
    ) -> ComplianceResult:
        """Valida cumplimiento de un agente."""
        violations = []
        warnings = []
        
        # Placeholder - en producción evaluaría contra todas las políticas
        compliant = len(violations) == 0
        
        logger.info(f"Validated agent {agent_id}: compliant={compliant}")
        
        return ComplianceResult(
            compliant=compliant,
            violations=violations,
            warnings=warnings,
        )
    
    async def validate_system(self) -> ComplianceResult:
        """Valida cumplimiento del sistema."""
        violations = []
        warnings = []
        
        # Placeholder
        compliant = True
        
        return ComplianceResult(
            compliant=compliant,
            violations=violations,
            warnings=warnings,
        )
    
    async def generate_compliance_report(self) -> GovernanceReport:
        """Genera reporte de cumplimiento."""
        report = GovernanceReport(
            report_type=ReportType.COMPLIANCE,
            title="Compliance Report",
            summary="System compliance status",
        )
        
        result = await self.validate_system()
        report.add_finding(f"Compliant: {result.compliant}")
        report.add_finding(f"Violations: {len(result.violations)}")
        report.add_finding(f"Warnings: {len(result.warnings)}")
        
        return report


# =============================================================================
# GOVERNANCE SERVICE CONFIG
# =============================================================================

@dataclass
class GovernanceServiceConfig:
    """Configuración del servicio de gobierno."""
    enable_audit: bool = True
    enable_policy: bool = True
    enable_compliance: bool = True
    enable_permissions: bool = True
    
    audit_retention_days: int = 90
    require_audit: bool = True


# =============================================================================
# GOVERNANCE SERVICE
# =============================================================================

class GovernanceService:
    """
    Servicio principal de gobierno.
    
    Responsabilidades:
    - Coordinar todos los servicios de gobierno
    - Proveer interfaz unificada
    - Gestionar configuración
    """
    
    def __init__(self, config: GovernanceServiceConfig | None = None):
        self.config = config or GovernanceServiceConfig()
        
        # Inicializar servicios
        self._permission_service = PermissionService() if self.config.enable_permissions else None
        self._audit_service = AuditService() if self.config.enable_audit else None
        self._policy_engine = PolicyEngine() if self.config.enable_policy else None
        self._compliance_validator = ComplianceValidator() if self.config.enable_compliance else None
        
        # Métricas
        self._operations_count = 0
    
    async def initialize(self) -> None:
        """Inicializa el servicio."""
        logger.info("GovernanceService initialized")
        logger.info(f"  - Audit: {self._audit_service is not None}")
        logger.info(f"  - Policy: {self._policy_engine is not None}")
        logger.info(f"  - Compliance: {self._compliance_validator is not None}")
        logger.info(f"  - Permissions: {self._permission_service is not None}")
    
    async def grant_permission(
        self,
        agent_id: str,
        resource: str,
        permission_type: str,
        granted_by: str,
    ) -> PermissionResult | None:
        """Otorga un permiso."""
        if not self._permission_service:
            return None
        
        try:
            perm_type = PermissionType(permission_type)
        except ValueError:
            perm_type = PermissionType.READ
        
        self._operations_count += 1
        return await self._permission_service.grant_permission(
            agent_id=agent_id,
            resource=resource,
            permission_type=perm_type,
            granted_by=granted_by,
        )
    
    async def create_audit(
        self,
        agent_id: str,
        action: str,
        performed_by: str,
        audit_type: str = "action",
    ) -> AgentAudit | None:
        """Crea una auditoría."""
        if not self._audit_service:
            return None
        
        try:
            a_type = AuditType(audit_type)
        except ValueError:
            a_type = AuditType.ACTION
        
        self._operations_count += 1
        return await self._audit_service.create_audit(
            agent_id=agent_id,
            audit_type=a_type,
            action=action,
            performed_by=performed_by,
        )
    
    async def create_policy(
        self,
        name: str,
        policy_type: str,
        created_by: str,
    ) -> AgentPolicy | None:
        """Crea una política."""
        if not self._policy_engine:
            return None
        
        try:
            p_type = PolicyType(policy_type)
        except ValueError:
            p_type = PolicyType.SECURITY
        
        self._operations_count += 1
        return await self._policy_engine.create_policy(
            name=name,
            policy_type=p_type,
            created_by=created_by,
        )
    
    async def generate_report(self) -> GovernanceReport:
        """Genera reporte de gobierno."""
        report = GovernanceReport(
            report_type=ReportType.SUMMARY,
            title="Governance Summary Report",
        )
        
        # Métricas generales
        report.add_metric("operations_count", self._operations_count)
        report.add_metric("audit_enabled", self._audit_service is not None)
        report.add_metric("policy_enabled", self._policy_engine is not None)
        report.add_metric("compliance_enabled", self._compliance_validator is not None)
        report.add_metric("permissions_enabled", self._permission_service is not None)
        
        return report
    
    def get_metrics(self) -> dict:
        """Obtiene métricas del servicio."""
        return {
            "operations_count": self._operations_count,
            "services_enabled": {
                "audit": self._audit_service is not None,
                "policy": self._policy_engine is not None,
                "compliance": self._compliance_validator is not None,
                "permissions": self._permission_service is not None,
            },
        }


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Result classes
    "PermissionResult",
    "AuditResult",
    "PolicyResult",
    "ComplianceResult",
    # Services
    "GovernanceService",
    "GovernanceServiceConfig",
    "PermissionService",
    "AuditService",
    "PolicyEngine",
    "ComplianceValidator",
]
