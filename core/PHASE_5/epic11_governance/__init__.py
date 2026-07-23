"""
PHASE 5 - EPIC 11: Multi-Agent Governance

Gobierno del ecosistema multiagente.
Administra permisos, auditoría, seguridad, versiones y políticas.
"""

from __future__ import annotations

# =============================================================================
# VERSION
# =============================================================================

__version__ = "1.0.0"
__epic__ = "EPIC_11"
__phase__ = "PHASE_5"


# =============================================================================
# IMPORTS FROM SUBMODULES
# =============================================================================

# Domain
from core.PHASE_5.epic11_governance.domain import (
    # Agent Policy
    AgentPolicy,
    PolicyType,
    PolicyStatus,
    # Agent Permission
    AgentPermission,
    PermissionType,
    # Agent Audit
    AgentAudit,
    AuditType,
    AuditStatus,
    # Governance Rule
    GovernanceRule,
    RuleType,
    # Agent Version
    AgentVersion,
    VersionStatus,
    # Governance Report
    GovernanceReport,
    ReportType,
)

# Services
from core.PHASE_5.epic11_governance.services import (
    # Governance Service
    GovernanceService,
    GovernanceServiceConfig,
    # Permission Service
    PermissionService,
    PermissionResult,
    # Audit Service
    AuditService,
    AuditResult,
    # Policy Engine
    PolicyEngine,
    PolicyResult,
    # Compliance Validator
    ComplianceValidator,
    ComplianceResult,
)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Version
    "__version__",
    "__epic__",
    "__phase__",
    # Domain
    "AgentPolicy",
    "PolicyType",
    "PolicyStatus",
    "AgentPermission",
    "PermissionType",
    "AgentAudit",
    "AuditType",
    "AuditStatus",
    "GovernanceRule",
    "RuleType",
    "AgentVersion",
    "VersionStatus",
    "GovernanceReport",
    "ReportType",
    # Services
    "GovernanceService",
    "GovernanceServiceConfig",
    "PermissionService",
    "PermissionResult",
    "AuditService",
    "AuditResult",
    "PolicyEngine",
    "PolicyResult",
    "ComplianceValidator",
    "ComplianceResult",
]
