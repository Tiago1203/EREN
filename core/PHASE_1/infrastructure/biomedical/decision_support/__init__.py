"""Clinical Decision Support System for EREN OS.

PR-064: Clinical Decision Support System

Provides evidence-based clinical recommendations, risk assessment,
and drug interaction checking.
"""

from __future__ import annotations

from core.PHASE_1.infrastructure.biomedical.decision_support.engine import (
    ClinicalDecisionSupport,
    Contraindication,
    get_clinical_decision_support,
    reset_clinical_decision_support,
)
from core.PHASE_1.infrastructure.biomedical.decision_support.types import (
    CDSDecision,
    ClinicalGuideline,
    DrugInteraction,
    EvidenceLevel,
    EvidenceSource,
    Recommendation,
    RecommendationType,
    RiskAssessment,
    RiskFactor,
)

__all__ = [
    # Engine
    "ClinicalDecisionSupport",
    "Contraindication",
    "get_clinical_decision_support",
    "reset_clinical_decision_support",
    # Types
    "EvidenceLevel",
    "RecommendationType",
    "ClinicalGuideline",
    "EvidenceSource",
    "Recommendation",
    "RiskFactor",
    "RiskAssessment",
    "DrugInteraction",
    "CDSDecision",
]
