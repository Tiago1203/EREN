"""
Standards Repository Module

Complete implementation for biomedical engineering standards
including IEC, ISO, AAMI, NFPA, FDA, and other regulations.
"""

from enum import Enum
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional, Protocol
from collections import defaultdict


class StandardOrganization(Enum):
    """Standards organizations."""
    IEC = "iec"                    # International Electrotechnical Commission
    ISO = "iso"                   # International Organization for Standardization
    AAMI = "aami"                # Association for the Advancement of Medical Instrumentation
    NFPA = "nfpa"                # National Fire Protection Association
    IEEE = "ieee"                # Institute of Electrical and Electronics Engineers
    WHO = "who"                  # World Health Organization
    FDA = "fda"                  # US Food and Drug Administration
    EPA = "epa"                  # US Environmental Protection Agency
    EU = "eu"                    # European Union
    TGA = "tga"                  # Therapeutic Goods Administration (Australia)
    HealthCanada = "healthcanada"  # Health Canada
    ANVISA = "anvisa"            # Brazil ANVISA
    CUSTOM = "custom"             # Institutional standards


class StandardCategory(Enum):
    """Categories of standards."""
    SAFETY = "safety"
    QUALITY = "quality"
    PERFORMANCE = "performance"
    TESTING = "testing"
    LABELING = "labeling"
    BIOCOMPATIBILITY = "biocompatibility"
    ELECTRICAL = "electrical"
    SOFTWARE = "software"
    STERILIZATION = "sterilization"
    PACKAGING = "packaging"
    ENVIRONMENTAL = "environmental"
   cybersecurity = "cybersecurity"


class VerificationMethod(Enum):
    """Methods for verifying compliance."""
    INSPECTION = "inspection"
    TESTING = "testing"
    ANALYSIS = "analysis"
    REVIEW = "review"
    DEMONSTRATION = "demonstration"
    AUDIT = "audit"


class ComplianceStatus(Enum):
    """Compliance status."""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    NOT_APPLICABLE = "not_applicable"
    PENDING = "pending"
    EXEMPT = "exempt"
    UNDER_REVIEW = "under_review"


class RiskClassification(Enum):
    """Risk classification per standard."""
    CLASS_A = "class_a"  # No or minimal public health impact
    CLASS_B = "class_b"  # Non-serious injury
    CLASS_C = "class_c"  # Serious injury
    CLASS_D = "class_d"  # Death or irreversible injury


@dataclass(frozen=True)
class Standard:
    """
    Engineering standard with full metadata.
    """
    standard_id: str
    code: str                          # e.g., "IEC 60601-1"
    title: str
    version: str
    publication_date: date
    organization: StandardOrganization
    category: StandardCategory
    scope: str
    description: str
    key_requirements: list[str] = field(default_factory=list)
    related_standards: list[str] = field(default_factory=list)
    replaces: Optional[str] = None
    replaced_by: Optional[str] = None
    url: Optional[str] = None
    is_mandatory: bool = False
    applicable_risk_classes: list[RiskClassification] = field(default_factory=list)
    effective_date: Optional[date] = None
    withdrawal_date: Optional[date] = None
    keywords: list[str] = field(default_factory=list)
    
    def __post_init__(self):
        if isinstance(self.organization, str):
            object.__setattr__(self, 'organization', StandardOrganization(self.organization))
        if isinstance(self.category, str):
            object.__setattr__(self, 'category', StandardCategory(self.category))


@dataclass(frozen=True)
class StandardRequirement:
    """
    Specific requirement clause within a standard.
    """
    requirement_id: str
    standard_id: str
    clause: str                        # e.g., "4.2.1"
    section_title: str
    description: str
    requirement_text: str
    verification_method: VerificationMethod
    acceptance_criteria: str
    documentation_required: list[str] = field(default_factory=list)
    test_methods: list[str] = field(default_factory=list)
    related_requirements: list[str] = field(default_factory=list)
    severity: str = "major"           # critical, major, minor
    is_mandatory: bool = True
    
    def __post_init__(self):
        if isinstance(self.verification_method, str):
            object.__setattr__(self, 'verification_method', VerificationMethod(self.verification_method))


@dataclass(frozen=True)
class ComplianceCheck:
    """
    Compliance verification for a specific requirement.
    """
    check_id: str
    device_id: str
    standard_id: str
    requirement_id: Optional[str] = None
    status: ComplianceStatus = ComplianceStatus.PENDING
    evidence: Optional[str] = None
    evidence_url: Optional[str] = None
    verified_at: Optional[datetime] = None
    verified_by: Optional[str] = None
    notes: Optional[str] = None
    findings: list[str] = field(default_factory=list)
    corrective_actions: list[str] = field(default_factory=list)
    next_review_date: Optional[date] = None


@dataclass(frozen=True)
class ComplianceReport:
    """
    Complete compliance report for a device.
    """
    report_id: str
    device_id: str
    device_name: str
    device_category: str
    standards_checked: list[str]
    checks: list[ComplianceCheck]
    overall_status: ComplianceStatus
    compliant_count: int = 0
    non_compliant_count: int = 0
    pending_count: int = 0
    exempt_count: int = 0
    not_applicable_count: int = 0
    generated_at: datetime = field(default_factory=datetime.now)
    generated_by: str = "System"
    summary: Optional[str] = None
    recommendations: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class StandardComparison:
    """Comparison between standards."""
    comparison_id: str
    standard_a: str
    standard_b: str
    common_requirements: list[str] = field(default_factory=list)
    differences: list[str] = field(default_factory=list)
    compatibility: str = "compatible"


class IStandardsRepository(Protocol):
    """Repository interface for standards persistence."""
    
    async def get_standard(self, standard_id: str) -> Standard | None: ...
    async def search_standards(self, query: str) -> list[Standard]: ...
    async def get_requirements(self, standard_id: str) -> list[StandardRequirement]: ...


class StandardsRepository:
    """
    Repository for biomedical engineering standards.
    
    Manages:
    - Standard documents and metadata
    - Requirements and clauses
    - Compliance checking
    - Report generation
    """
    
    def __init__(
        self,
        repository: Optional[IStandardsRepository] = None,
    ):
        self._repository = repository
        self._standards: dict[str, Standard] = {}
        self._requirements: dict[str, list[StandardRequirement]] = defaultdict(list)
        self._code_index: dict[str, str] = {}
        self._device_compliance: dict[str, dict[str, ComplianceCheck]] = defaultdict(dict)
    
    async def get_standard(
        self,
        standard_id: str,
    ) -> Standard | None:
        """Get standard by ID."""
        if self._repository:
            return await self._repository.get_standard(standard_id)
        return self._standards.get(standard_id)
    
    async def get_standard_by_code(
        self,
        code: str,
    ) -> Standard | None:
        """Get standard by code (e.g., 'IEC 60601-1')."""
        standard_id = self._code_index.get(code.upper())
        if standard_id:
            return await self.get_standard(standard_id)
        
        for standard in self._standards.values():
            if standard.code.upper() == code.upper():
                return standard
        
        return None
    
    async def add_standard(
        self,
        standard: Standard,
    ) -> None:
        """Add a standard to the repository."""
        self._standards[standard.standard_id] = standard
        self._code_index[standard.code.upper()] = standard.standard_id
    
    async def search_standards(
        self,
        query: str,
        organization: StandardOrganization | None = None,
        category: StandardCategory | None = None,
    ) -> list[Standard]:
        """Search standards by query."""
        query_lower = query.lower()
        results = []
        
        for standard in self._standards.values():
            if organization and standard.organization != organization:
                continue
            if category and standard.category != category:
                continue
            
            if query_lower in standard.code.lower():
                results.append(standard)
            elif query_lower in standard.title.lower():
                results.append(standard)
            elif query_lower in standard.description.lower():
                results.append(standard)
            elif any(query_lower in kw.lower() for kw in standard.keywords):
                results.append(standard)
        
        return results
    
    async def get_standards_by_organization(
        self,
        organization: StandardOrganization,
    ) -> list[Standard]:
        """Get all standards from an organization."""
        return [
            s for s in self._standards.values()
            if s.organization == organization
        ]
    
    async def get_standards_by_category(
        self,
        category: StandardCategory,
    ) -> list[Standard]:
        """Get all standards in a category."""
        return [
            s for s in self._standards.values()
            if s.category == category
        ]
    
    async def get_requirements(
        self,
        standard_id: str,
    ) -> list[StandardRequirement]:
        """Get requirements for a standard."""
        if self._repository:
            return await self._repository.get_requirements(standard_id)
        return self._requirements.get(standard_id, [])
    
    async def add_requirement(
        self,
        requirement: StandardRequirement,
    ) -> None:
        """Add a requirement to a standard."""
        self._requirements[requirement.standard_id].append(requirement)
    
    async def get_related_standards(
        self,
        standard_id: str,
    ) -> list[Standard]:
        """Get standards related to this one."""
        standard = await self.get_standard(standard_id)
        if not standard:
            return []
        
        related = []
        for code in standard.related_standards:
            related_std = await self.get_standard_by_code(code)
            if related_std:
                related.append(related_std)
        
        return related
    
    async def get_applicable_standards(
        self,
        device_category: str,
        risk_class: RiskClassification,
    ) -> list[Standard]:
        """Get standards applicable to a device."""
        applicable = []
        
        for standard in self._standards.values():
            if standard.applicable_risk_classes:
                if risk_class in standard.applicable_risk_classes:
                    applicable.append(standard)
            else:
                applicable.append(standard)
        
        return applicable
    
    async def check_compliance(
        self,
        device_id: str,
        standard_id: str,
        requirement_id: str | None = None,
        status: ComplianceStatus = ComplianceStatus.PENDING,
        evidence: str | None = None,
        verified_by: str | None = None,
        notes: str | None = None,
    ) -> ComplianceCheck:
        """Record compliance check for a requirement."""
        check = ComplianceCheck(
            check_id=f"check_{device_id}_{standard_id}_{requirement_id or 'all'}_{datetime.now().timestamp()}",
            device_id=device_id,
            standard_id=standard_id,
            requirement_id=requirement_id,
            status=status,
            evidence=evidence,
            verified_at=datetime.now(),
            verified_by=verified_by,
            notes=notes,
        )
        
        self._device_compliance[device_id][standard_id] = check
        return check
    
    async def get_compliance_status(
        self,
        device_id: str,
        standard_id: str,
    ) -> ComplianceCheck | None:
        """Get compliance status for a device/standard."""
        return self._device_compliance.get(device_id, {}).get(standard_id)
    
    async def generate_compliance_report(
        self,
        device_id: str,
        device_name: str,
        device_category: str,
        standard_ids: list[str],
    ) -> ComplianceReport:
        """Generate complete compliance report."""
        checks = []
        compliant = 0
        non_compliant = 0
        pending = 0
        exempt = 0
        not_applicable = 0
        
        for std_id in standard_ids:
            check = self._device_compliance.get(device_id, {}).get(std_id)
            if check:
                checks.append(check)
                
                if check.status == ComplianceStatus.COMPLIANT:
                    compliant += 1
                elif check.status == ComplianceStatus.NON_COMPLIANT:
                    non_compliant += 1
                elif check.status == ComplianceStatus.PENDING:
                    pending += 1
                elif check.status == ComplianceStatus.EXEMPT:
                    exempt += 1
                elif check.status == ComplianceStatus.NOT_APPLICABLE:
                    not_applicable += 1
        
        if non_compliant > 0:
            overall = ComplianceStatus.NON_COMPLIANT
        elif pending > 0:
            overall = ComplianceStatus.UNDER_REVIEW
        elif compliant > 0 and non_compliant == 0:
            overall = ComplianceStatus.COMPLIANT
        else:
            overall = ComplianceStatus.PENDING
        
        recommendations = []
        for check in checks:
            if check.status == ComplianceStatus.NON_COMPLIANT:
                recommendations.extend(check.corrective_actions)
        
        return ComplianceReport(
            report_id=f"report_{device_id}_{datetime.now().timestamp()}",
            device_id=device_id,
            device_name=device_name,
            device_category=device_category,
            standards_checked=standard_ids,
            checks=checks,
            overall_status=overall,
            compliant_count=compliant,
            non_compliant_count=non_compliant,
            pending_count=pending,
            exempt_count=exempt,
            not_applicable_count=not_applicable,
            recommendations=list(set(recommendations)),
        )
    
    async def compare_standards(
        self,
        standard_id_a: str,
        standard_id_b: str,
    ) -> StandardComparison:
        """Compare two standards."""
        std_a = await self.get_standard(standard_id_a)
        std_b = await self.get_standard(standard_id_b)
        
        if not std_a or not std_b:
            raise ValueError("One or both standards not found")
        
        reqs_a = {r.requirement_id for r in await self.get_requirements(standard_id_a)}
        reqs_b = {r.requirement_id for r in await self.get_requirements(standard_id_b)}
        
        common = list(reqs_a & reqs_b)
        only_a = list(reqs_a - reqs_b)
        only_b = list(reqs_b - reqs_a)
        
        return StandardComparison(
            comparison_id=f"compare_{standard_id_a}_{standard_id_b}",
            standard_a=standard_id_a,
            standard_b=standard_id_b,
            common_requirements=common,
            differences=[f"Only in {std_a.code}: {only_a}", f"Only in {std_b.code}: {only_b}"],
        )
    
    async def get_overdue_standards(
        self,
        reference_date: date | None = None,
    ) -> list[Standard]:
        """Get standards that have been withdrawn or superseded."""
        ref_date = reference_date or date.today()
        overdue = []
        
        for standard in self._standards.values():
            if standard.withdrawal_date and standard.withdrawal_date < ref_date:
                overdue.append(standard)
        
        return overdue


# Standard definitions for common biomedical standards
IEC_STANDARDS = {
    "IEC 60601-1": {
        "title": "Medical Electrical Equipment - General Requirements",
        "description": "General requirements for basic safety and essential performance",
    },
    "IEC 60601-1-8": {
        "title": "Alarm Requirements",
        "description": "General requirements, tests and guidance for alarm systems",
    },
    "IEC 62304": {
        "title": "Software Life Cycle Processes",
        "description": "Software life cycle processes for medical devices",
    },
}

ISO_STANDARDS = {
    "ISO 13485": {
        "title": "Quality Management Systems",
        "description": "Requirements for regulatory purposes",
    },
    "ISO 14971": {
        "title": "Risk Management",
        "description": "Application of risk management to medical devices",
    },
    "ISO 15288": {
        "title": "System Life Cycle Processes",
        "description": "System life cycle processes",
    },
}


__all__ = [
    "StandardOrganization",
    "StandardCategory",
    "VerificationMethod",
    "ComplianceStatus",
    "RiskClassification",
    "Standard",
    "StandardRequirement",
    "ComplianceCheck",
    "ComplianceReport",
    "StandardComparison",
    "IStandardsRepository",
    "StandardsRepository",
]
