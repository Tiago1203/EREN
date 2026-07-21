"""
Standards Repository Module

Provides repository for biomedical engineering standards:
- IEC 60601, 62304
- ISO 13485, 14971
- AAMI guidelines
- NFPA 99
- FDA regulations
"""

from enum import Enum
from dataclasses import dataclass, field
from datetime import date
from typing import Optional


class StandardOrganization(Enum):
    """Standards organizations."""
    IEC = "iec"
    ISO = "iso"
    AAMI = "aami"
    NFPA = "nfpa"
    IEEE = "ieee"
    WHO = "who"
    FDA = "fda"
    EU = "eu"
    CUSTOM = "custom"


class VerificationMethod(Enum):
    """Methods for verifying compliance."""
    INSPECTION = "inspection"
    TESTING = "testing"
    ANALYSIS = "analysis"
    REVIEW = "review"
    DEMONSTRATION = "demonstration"


class ComplianceStatus(Enum):
    """Compliance status."""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    NOT_APPLICABLE = "not_applicable"
    PENDING = "pending"
    EXEMPT = "exempt"


@dataclass(frozen=True)
class Standard:
    """Engineering standard."""
    standard_id: str
    code: str
    title: str
    version: str
    publication_date: date
    organization: StandardOrganization
    scope: str
    description: str
    key_requirements: list[str] = field(default_factory=list)
    related_standards: list[str] = field(default_factory=list)
    url: str | None = None
    is_mandatory: bool = False


@dataclass(frozen=True)
class StandardRequirement:
    """Specific requirement of a standard."""
    requirement_id: str
    standard_id: str
    clause: str
    title: str
    description: str
    requirement_text: str
    verification_method: VerificationMethod
    acceptance_criteria: str
    documentation_required: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ComplianceCheck:
    """Compliance verification."""
    check_id: str
    device_id: str
    standard_id: str
    requirement_id: str | None = None
    status: ComplianceStatus = ComplianceStatus.PENDING
    evidence: str | None = None
    verified_at: date | None = None
    verified_by: str | None = None
    notes: str | None = None


@dataclass(frozen=True)
class ComplianceReport:
    """Compliance report for a device."""
    report_id: str
    device_id: str
    checks: list[ComplianceCheck]
    overall_status: ComplianceStatus
    compliant_count: int = 0
    non_compliant_count: int = 0
    pending_count: int = 0
    exempt_count: int = 0


class StandardsRepository:
    """
    Repository for biomedical engineering standards.
    """
    
    def __init__(self):
        self._standards: dict[str, Standard] = {}
        self._requirements: dict[str, list[StandardRequirement]] = {}
    
    async def get_standard(
        self,
        standard_id: str,
    ) -> Standard | None:
        """Get standard by ID."""
        return self._standards.get(standard_id)
    
    async def search_standards(
        self,
        query: str,
        organization: StandardOrganization | None = None,
    ) -> list[Standard]:
        """Search standards."""
        query_lower = query.lower()
        results = []
        
        for standard in self._standards.values():
            if organization and standard.organization != organization:
                continue
            
            if (query_lower in standard.code.lower() or
                query_lower in standard.title.lower()):
                results.append(standard)
        
        return results
    
    async def get_requirements(
        self,
        standard_id: str,
    ) -> list[StandardRequirement]:
        """Get requirements for a standard."""
        return self._requirements.get(standard_id, [])
    
    async def get_standards_by_organization(
        self,
        organization: StandardOrganization,
    ) -> list[Standard]:
        """Get all standards from an organization."""
        return [
            s for s in self._standards.values()
            if s.organization == organization
        ]
    
    async def get_related_standards(
        self,
        standard_id: str,
    ) -> list[Standard]:
        """Get related standards."""
        standard = self._standards.get(standard_id)
        if not standard:
            return []
        
        related = []
        for related_code in standard.related_standards:
            for s in self._standards.values():
                if s.code == related_code:
                    related.append(s)
        
        return related
    
    async def check_compliance(
        self,
        device_id: str,
        standard_id: str,
    ) -> ComplianceReport:
        """Generate compliance report for a device."""
        standard = self._standards.get(standard_id)
        if not standard:
            return ComplianceReport(
                report_id=f"report_{device_id}_{standard_id}",
                device_id=device_id,
                checks=[],
                overall_status=ComplianceStatus.NOT_APPLICABLE,
            )
        
        checks = []
        compliant_count = 0
        non_compliant_count = 0
        pending_count = 0
        exempt_count = 0
        
        for req in self._requirements.get(standard_id, []):
            check = ComplianceCheck(
                check_id=f"check_{device_id}_{req.requirement_id}",
                device_id=device_id,
                standard_id=standard_id,
                requirement_id=req.requirement_id,
                status=ComplianceStatus.PENDING,
            )
            checks.append(check)
            pending_count += 1
        
        if pending_count == 0:
            overall = ComplianceStatus.NOT_APPLICABLE
        else:
            overall = ComplianceStatus.PENDING
        
        return ComplianceReport(
            report_id=f"report_{device_id}_{standard_id}",
            device_id=device_id,
            checks=checks,
            overall_status=overall,
            compliant_count=compliant_count,
            non_compliant_count=non_compliant_count,
            pending_count=pending_count,
            exempt_count=exempt_count,
        )


__all__ = [
    "StandardOrganization",
    "VerificationMethod",
    "ComplianceStatus",
    "Standard",
    "StandardRequirement",
    "ComplianceCheck",
    "ComplianceReport",
    "StandardsRepository",
]
