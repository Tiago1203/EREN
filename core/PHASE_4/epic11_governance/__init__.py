"""
PHASE 4 - EPIC 11: Knowledge Governance & Lifecycle

Gobernanza y ciclo de vida del conocimiento:
- Auditoría completa
- Versionado
- Retención
- Rollback
- Compliance
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Optional, Protocol
import uuid


class AuditAction(str, Enum):
    """Acciones de auditoría."""
    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    SUPERSEDED = "superseded"
    VIEWED = "viewed"
    EXPORTED = "exported"
    ROLLED_BACK = "rolled_back"
    STATUS_CHANGED = "status_changed"


class RetentionPolicy(str, Enum):
    """Políticas de retención."""
    PERMANENT = "permanent"       # Nunca eliminar
    STANDARD = "standard"         # 7 años
    SHORT_TERM = "short_term"     # 2 años
    REVIEW_REQUIRED = "review"    # Requiere revisión periódica


@dataclass
class AuditEntry:
    """Entrada de auditoría."""
    entry_id: str
    asset_id: str
    action: AuditAction
    user_id: str
    timestamp: datetime
    
    # Changes
    previous_value: str = ""
    new_value: str = ""
    change_summary: str = ""
    
    # Context
    ip_address: str = ""
    user_agent: str = ""
    session_id: str = ""
    
    # Metadata
    reason: str = ""
    approval_id: str = ""


@dataclass
class ComplianceReport:
    """Reporte de compliance."""
    report_id: str
    generated_at: datetime
    period_start: datetime
    period_end: datetime
    
    # Metrics
    total_assets: int = 0
    compliant_assets: int = 0
    non_compliant_assets: int = 0
    
    # Details
    violations: list[dict] = field(default_factory=list)
    expiring_assets: list[dict] = field(default_factory=list)


@dataclass
class RollbackPlan:
    """Plan de rollback."""
    plan_id: str
    asset_id: str
    target_version: str
    created_at: datetime
    created_by: str
    steps: list[str] = field(default_factory=list)


class AuditLogger:
    """Logger de auditoría."""
    
    def __init__(self):
        self._entries: list[AuditEntry] = []
    
    def log(
        self,
        asset_id: str,
        action: AuditAction,
        user_id: str,
        **kwargs,
    ) -> AuditEntry:
        """Registra acción de auditoría."""
        entry = AuditEntry(
            entry_id=str(uuid.uuid4()),
            asset_id=asset_id,
            action=action,
            user_id=user_id,
            timestamp=datetime.now(UTC),
            previous_value=kwargs.get("previous_value", ""),
            new_value=kwargs.get("new_value", ""),
            change_summary=kwargs.get("change_summary", ""),
            reason=kwargs.get("reason", ""),
        )
        
        self._entries.append(entry)
        return entry
    
    def get_entries(
        self,
        asset_id: str | None = None,
        user_id: str | None = None,
        action: AuditAction | None = None,
        since: datetime | None = None,
        limit: int = 100,
    ) -> list[AuditEntry]:
        """Obtiene entradas de auditoría."""
        entries = self._entries
        
        if asset_id:
            entries = [e for e in entries if e.asset_id == asset_id]
        if user_id:
            entries = [e for e in entries if e.user_id == user_id]
        if action:
            entries = [e for e in entries if e.action == action]
        if since:
            entries = [e for e in entries if e.timestamp >= since]
        
        # Sort by timestamp descending
        entries.sort(key=lambda e: e.timestamp, reverse=True)
        
        return entries[:limit]
    
    def get_asset_history(self, asset_id: str) -> list[AuditEntry]:
        """Obtiene historial completo de asset."""
        return self.get_entries(asset_id=asset_id, limit=1000)
    
    def generate_compliance_report(
        self,
        period_start: datetime,
        period_end: datetime,
    ) -> ComplianceReport:
        """Genera reporte de compliance."""
        entries = [
            e for e in self._entries
            if period_start <= e.timestamp <= period_end
        ]
        
        # Count actions
        actions_count = {}
        for entry in entries:
            action_key = entry.action.value
            actions_count[action_key] = actions_count.get(action_key, 0) + 1
        
        return ComplianceReport(
            report_id=str(uuid.uuid4()),
            generated_at=datetime.now(UTC),
            period_start=period_start,
            period_end=period_end,
            total_assets=len(set(e.asset_id for e in entries)),
            compliant_assets=len(set(e.asset_id for e in entries if e.action in [AuditAction.CREATED, AuditAction.UPDATED, AuditAction.PUBLISHED])),
            violations=[],
        )


class RetentionManager:
    """Gestor de retención."""
    
    def __init__(self):
        self._policies: dict[str, RetentionPolicy] = {}
        self._expiry_dates: dict[str, datetime] = {}
    
    def set_policy(
        self,
        asset_id: str,
        policy: RetentionPolicy,
        custom_expiry: datetime | None = None,
    ) -> None:
        """Establece política de retención."""
        self._policies[asset_id] = policy
        self._expiry_dates[asset_id] = custom_expiry or self._calculate_expiry(policy)
    
    def _calculate_expiry(self, policy: RetentionPolicy) -> datetime:
        """Calcula fecha de expiración según política."""
        from datetime import timedelta
        
        days = {
            RetentionPolicy.PERMANENT: 365 * 100,  # 100 years
            RetentionPolicy.STANDARD: 365 * 7,     # 7 years
            RetentionPolicy.SHORT_TERM: 365 * 2,  # 2 years
            RetentionPolicy.REVIEW_REQUIRED: 365, # 1 year
        }
        
        return datetime.now(UTC) + timedelta(days=days.get(policy, 365))
    
    def get_expiry(self, asset_id: str) -> datetime | None:
        """Obtiene fecha de expiración."""
        return self._expiry_dates.get(asset_id)
    
    def get_expired_assets(self) -> list[str]:
        """Obtiene IDs de assets expirados."""
        now = datetime.now(UTC)
        return [
            asset_id for asset_id, expiry in self._expiry_dates.items()
            if expiry < now
        ]
    
    def needs_review(self, asset_id: str) -> bool:
        """Verifica si asset necesita revisión."""
        return self._policies.get(asset_id) == RetentionPolicy.REVIEW_REQUIRED


class RollbackManager:
    """Gestor de rollback."""
    
    def __init__(self):
        self._versions: dict[str, dict] = {}  # asset_id -> {version: content}
    
    async def create_snapshot(
        self,
        asset_id: str,
        version: str,
        content: str,
    ) -> bool:
        """Crea snapshot para rollback."""
        if asset_id not in self._versions:
            self._versions[asset_id] = {}
        
        self._versions[asset_id][version] = content
        return True
    
    async def get_version(
        self,
        asset_id: str,
        version: str,
    ) -> str | None:
        """Obtiene contenido de versión específica."""
        if asset_id not in self._versions:
            return None
        
        return self._versions[asset_id].get(version)
    
    async def create_rollback_plan(
        self,
        asset_id: str,
        target_version: str,
        current_version: str,
        created_by: str,
    ) -> RollbackPlan:
        """Crea plan de rollback."""
        steps = [
            f"1. Backup current version {current_version}",
            f"2. Create snapshot of current state",
            f"3. Restore to version {target_version}",
            "4. Verify restored content",
            "5. Update metadata and timestamps",
            "6. Notify stakeholders",
        ]
        
        return RollbackPlan(
            plan_id=str(uuid.uuid4()),
            asset_id=asset_id,
            target_version=target_version,
            steps=steps,
            created_at=datetime.now(UTC),
            created_by=created_by,
        )
    
    async def execute_rollback(
        self,
        plan: RollbackPlan,
        content_getter: callable,
        content_setter: callable,
    ) -> bool:
        """Ejecuta rollback."""
        try:
            # Get target content
            content = await content_getter(plan.asset_id, plan.target_version)
            if content is None:
                return False
            
            # Apply rollback
            await content_setter(plan.asset_id, content)
            
            return True
        except Exception:
            return False


class GovernanceEngine:
    """Motor de gobernanza."""
    
    def __init__(
        self,
        audit_logger: AuditLogger | None = None,
        retention_manager: RetentionManager | None = None,
        rollback_manager: RollbackManager | None = None,
    ):
        self.audit = audit_logger or AuditLogger()
        self.retention = retention_manager or RetentionManager()
        self.rollback = rollback_manager or RollbackManager()
    
    async def initialize_governance(
        self,
        asset_id: str,
        user_id: str,
        policy: RetentionPolicy = RetentionPolicy.STANDARD,
    ) -> None:
        """Inicializa gobernanza para asset."""
        # Set retention policy
        self.retention.set_policy(asset_id, policy)
        
        # Log creation
        self.audit.log(
            asset_id=asset_id,
            action=AuditAction.CREATED,
            user_id=user_id,
        )
    
    async def change_status(
        self,
        asset_id: str,
        old_status: str,
        new_status: str,
        user_id: str,
        reason: str = "",
    ) -> None:
        """Cambia estado de gobernanza."""
        self.audit.log(
            asset_id=asset_id,
            action=AuditAction.STATUS_CHANGED,
            user_id=user_id,
            previous_value=old_status,
            new_value=new_status,
            reason=reason,
        )
    
    async def archive_asset(
        self,
        asset_id: str,
        user_id: str,
        reason: str = "",
    ) -> None:
        """Archiva asset."""
        self.audit.log(
            asset_id=asset_id,
            action=AuditAction.ARCHIVED,
            user_id=user_id,
            reason=reason,
        )
    
    async def get_compliance_status(
        self,
        asset_id: str,
    ) -> dict:
        """Obtiene estado de compliance."""
        expiry = self.retention.get_expiry(asset_id)
        needs_review = self.retention.needs_review(asset_id)
        
        # Get recent audit entries
        history = self.audit.get_asset_history(asset_id)
        
        return {
            "asset_id": asset_id,
            "retention_policy": self.retention._policies.get(asset_id),
            "expiry_date": expiry.isoformat() if expiry else None,
            "needs_review": needs_review,
            "audit_entries_count": len(history),
            "last_modified": history[0].timestamp.isoformat() if history else None,
        }


# =============================================================================
# IMPORTS FROM SUBMODULES
# =============================================================================

# Lifecycle
from core.PHASE_4.epic11_governance.lifecycle import (
    LifecycleStage,
    ArchiveReason,
    KnowledgeSnapshot,
    RollbackPlan,
    BaseLifecycleManager,
    InMemoryLifecycleManager,
    RollbackManager,
)

# Compliance
from core.PHASE_4.epic11_governance.compliance import (
    RetentionPolicy,
    ComplianceStatus,
    GovernancePolicy,
    ComplianceReport,
    BaseComplianceManager,
    InMemoryComplianceManager,
    RetentionEnforcer,
)

# Audit
from core.PHASE_4.epic11_governance.audit import (
    AuditAction,
    AuditSeverity,
    AuditEntry,
    AuditQuery,
    BaseAuditManager,
    InMemoryAuditManager,
    AuditReporter,
)


__all__ = [
    # Version
    "__version__",
    # Enums
    "AuditAction",
    "RetentionPolicy",
    "LifecycleStage",
    "ArchiveReason",
    "ComplianceStatus",
    "AuditSeverity",
    # Data Classes
    "AuditEntry",
    "KnowledgeSnapshot",
    "GovernancePolicy",
    "ComplianceReport",
    "RollbackPlan",
    "AuditQuery",
    # Managers
    "AuditLogger",
    "RetentionManager",
    "RollbackManager",
    "GovernanceEngine",
    # New from submodules
    "BaseLifecycleManager",
    "InMemoryLifecycleManager",
    "BaseComplianceManager",
    "InMemoryComplianceManager",
    "RetentionEnforcer",
    "BaseAuditManager",
    "InMemoryAuditManager",
    "AuditReporter",
]
