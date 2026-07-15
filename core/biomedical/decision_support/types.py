"""Clinical Decision Support Types for EREN OS.

Type definitions for clinical decision support system.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass


# =============================================================================
# Evidence & Guidelines
# =============================================================================


class EvidenceLevel(str, Enum):
    """Evidence levels for recommendations."""

    A = "a"  # High certainty
    B = "b"  # Moderate certainty
    C = "c"  # Low certainty
    D = "d"  # Expert opinion


class RecommendationType(str, Enum):
    """Types of recommendations."""

    DIAGNOSIS = "diagnosis"
    TREATMENT = "treatment"
    MONITORING = "monitoring"
    REFERRAL = "referral"
    PREVENTION = "prevention"
    ALERT = "alert"


@dataclass
class ClinicalGuideline:
    """Clinical guideline."""

    guideline_id: str
    name: str
    organization: str = ""
    version: str = "1.0"
    publication_date: datetime = field(default_factory=lambda: datetime.now(UTC))
    url: str = ""
    recommendations: list[dict] = field(default_factory=list)


@dataclass
class EvidenceSource:
    """Source of clinical evidence."""

    source_id: str
    title: str = ""
    authors: list[str] = field(default_factory=list)
    journal: str = ""
    year: int = 0
    doi: str = ""
    url: str = ""
    evidence_level: EvidenceLevel = EvidenceLevel.C


# =============================================================================
# Recommendations
# =============================================================================


@dataclass
class Recommendation:
    """Clinical recommendation."""

    recommendation_id: str
    type: RecommendationType
    content: str
    evidence_level: EvidenceLevel = EvidenceLevel.C
    confidence: float = 0.5  # 0-1
    sources: list[str] = field(default_factory=list)
    contraindications: list[str] = field(default_factory=list)
    caveats: list[str] = field(default_factory=list)
    patient_specific: bool = False

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "recommendation_id": self.recommendation_id,
            "type": self.type.value,
            "content": self.content,
            "evidence_level": self.evidence_level.value,
            "confidence": self.confidence,
            "sources": self.sources,
            "contraindications": self.contraindications,
            "caveats": self.caveats,
        }


# =============================================================================
# Risk Analysis
# =============================================================================


@dataclass
class RiskFactor:
    """A risk factor."""

    factor_id: str
    name: str
    category: str = ""  # cardiac, respiratory, etc.
    value: Any = None
    threshold: float = 0.0
    unit: str = ""
    risk_contribution: float = 0.0  # 0-1


@dataclass
class RiskAssessment:
    """Risk assessment result."""

    assessment_id: str
    patient_id: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    overall_risk: str = "low"  # low, moderate, high, very_high
    risk_score: float = 0.0  # 0-100
    factors: list[RiskFactor] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)


# =============================================================================
# Drug Interactions
# =============================================================================


@dataclass
class DrugInteraction:
    """Drug-drug interaction."""

    interaction_id: str
    drug1: str
    drug2: str
    severity: str = "moderate"  # minor, moderate, major, contraindicated
    description: str = ""
    mechanism: str = ""
    recommendation: str = ""


# =============================================================================
# CDS Output
# =============================================================================


@dataclass
class CDSDecision:
    """Clinical decision support output."""

    decision_id: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    patient_id: str = ""
    recommendations: list[Recommendation] = field(default_factory=list)
    alerts: list[str] = field(default_factory=list)
    risk_assessment: RiskAssessment | None = None
    drug_interactions: list[DrugInteraction] = field(default_factory=list)
    confidence: float = 0.0
    explanation: str = ""
    citations: list[str] = field(default_factory=list)
    disclaimer: str = "This is a clinical decision support suggestion only. Always consult with a qualified healthcare professional."
