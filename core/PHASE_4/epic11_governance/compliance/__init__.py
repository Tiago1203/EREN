"""
PHASE 4 - EPIC 11: Compliance Module

Gestión de compliance:
- Compliance Manager
- Retention Policies
- Policy Enforcement
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional


class RetentionPolicy(str, Enum):
    """Políticas de retención."""
    PERMANENT = "permanent"       # Nunca eliminar
    STANDARD = "standard"         # 7 años (clínico)
    SHORT_TERM = "short_term"     # 2 años
    REVIEW_REQUIRED = "review"   # Requiere revisión periódica


class ComplianceStatus(str, Enum):
    """Estados de compliance."""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PENDING_REVIEW = "pending_review"
    EXEMPT = "exempt"


@dataclass
class GovernancePolicy:
    """Política de gobernanza."""
    policy_id: str
    name: str
    description: str
    
    # Policy details
    retention_policy: RetentionPolicy = RetentionPolicy.STANDARD
    review_frequency_days: int = 365
    
    # Requirements
    requires_approval: bool = False
    approval_roles: list[str] = field(default_factory=list)
    
    # Status
    is_active: bool = True
    created_at: str = ""
    updated_at: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()


@dataclass
class ComplianceReport:
    """Reporte de compliance."""
    report_id: str
    generated_at: str = ""
    
    # Status
    overall_status: ComplianceStatus = ComplianceStatus.COMPLIANT
    
    # Counts
    total_documents: int = 0
    compliant_count: int = 0
    non_compliant_count: int = 0
    pending_review_count: int = 0
    
    # Issues
    issues: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    
    def __post_init__(self):
        if not self.generated_at:
            self.generated_at = datetime.now().isoformat()


class BaseComplianceManager(ABC):
    """Clase base para gestión de compliance."""
    
    @abstractmethod
    async def check_compliance(self, document_id: str) -> ComplianceStatus:
        """Verifica compliance."""
        ...
    
    @abstractmethod
    async def generate_report(self) -> ComplianceReport:
        """Genera reporte."""
        ...


class InMemoryComplianceManager(BaseComplianceManager):
    """Gestor de compliance en memoria."""
    
    def __init__(self):
        self._policies: dict[str, GovernancePolicy] = {}
        self._document_policies: dict[str, str] = {}  # doc_id -> policy_id
    
    async def add_policy(self, policy: GovernancePolicy) -> GovernancePolicy:
        """Añade política."""
        self._policies[policy.policy_id] = policy
        return policy
    
    async def get_policy(self, policy_id: str) -> GovernancePolicy | None:
        """Obtiene política."""
        return self._policies.get(policy_id)
    
    async def apply_policy(
        self,
        document_id: str,
        policy_id: str,
    ) -> None:
        """Aplica política a documento."""
        self._document_policies[document_id] = policy_id
    
    async def check_compliance(self, document_id: str) -> ComplianceStatus:
        """Verifica compliance."""
        policy_id = self._document_policies.get(document_id)
        
        if not policy_id:
            return ComplianceStatus.PENDING_REVIEW
        
        policy = self._policies.get(policy_id)
        if not policy:
            return ComplianceStatus.NON_COMPLIANT
        
        if not policy.is_active:
            return ComplianceStatus.NON_COMPLIANT
        
        return ComplianceStatus.COMPLIANT
    
    async def generate_report(self) -> ComplianceReport:
        """Genera reporte."""
        report = ComplianceReport(report_id="auto")
        
        report.total_documents = len(self._document_policies)
        
        for doc_id in self._document_policies:
            status = await self.check_compliance(doc_id)
            
            if status == ComplianceStatus.COMPLIANT:
                report.compliant_count += 1
            elif status == ComplianceStatus.NON_COMPLIANT:
                report.non_compliant_count += 1
            else:
                report.pending_review_count += 1
        
        if report.non_compliant_count > 0:
            report.overall_status = ComplianceStatus.NON_COMPLIANT
            report.issues.append(f"{report.non_compliant_count} documents are non-compliant")
        
        if report.pending_review_count > 0:
            if report.overall_status == ComplianceStatus.COMPLIANT:
                report.overall_status = ComplianceStatus.PENDING_REVIEW
        
        return report


class RetentionEnforcer:
    """Aplicador de políticas de retención."""
    
    def __init__(self, compliance_manager: BaseComplianceManager):
        self._compliance = compliance_manager
    
    def get_retention_period(self, policy: RetentionPolicy) -> timedelta:
        """Obtiene período de retención."""
        periods = {
            RetentionPolicy.PERMANENT: timedelta(days=365*100),
            RetentionPolicy.STANDARD: timedelta(days=365*7),
            RetentionPolicy.SHORT_TERM: timedelta(days=365*2),
            RetentionPolicy.REVIEW_REQUIRED: timedelta(days=365),
        }
        return periods.get(policy, timedelta(days=365*7))
    
    def should_retain(
        self,
        created_at: str,
        policy: RetentionPolicy,
    ) -> bool:
        """Determina si debe retener."""
        created = datetime.fromisoformat(created_at)
        period = self.get_retention_period(policy)
        
        return datetime.now() - created < period
    
    def needs_review(
        self,
        last_reviewed: str | None,
        review_frequency_days: int,
    ) -> bool:
        """Determina si necesita revisión."""
        if not last_reviewed:
            return True
        
        reviewed = datetime.fromisoformat(last_reviewed)
        return datetime.now() - reviewed > timedelta(days=review_frequency_days)


__all__ = [
    "RetentionPolicy",
    "ComplianceStatus",
    "GovernancePolicy",
    "ComplianceReport",
    "BaseComplianceManager",
    "InMemoryComplianceManager",
    "RetentionEnforcer",
]
