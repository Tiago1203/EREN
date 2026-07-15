"""Clinical Decision Support Engine for EREN OS.

Provides evidence-based clinical decision support.
"""

from __future__ import annotations

import threading
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from core.biomedical.decision_support.types import (
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


@dataclass
class Contraindication:
    """A contraindication for a medication."""

    contraindication_id: str
    medication: str = ""
    conditions: list[str] = field(default_factory=list)
    allergies: list[str] = field(default_factory=list)
    severity: str = "major"
    description: str = ""
    recommendation: str = ""


class ClinicalDecisionSupport:
    """Clinical decision support engine.

    Features:
    - Evidence-based recommendations
    - Risk assessment
    - Drug interaction checking
    - Contraindication detection
    - Explanation generation
    """

    def __init__(self):
        """Initialize CDS engine."""
        self._guidelines: dict[str, ClinicalGuideline] = {}
        self._drug_interactions: dict[str, DrugInteraction] = {}
        self._contraindications: dict[str, Contraindication] = {}
        self._evidence_sources: dict[str, EvidenceSource] = {}
        self._lock = threading.RLock()

    # =========================================================================
    # Guidelines
    # =========================================================================

    def add_guideline(self, guideline: ClinicalGuideline) -> None:
        """Add a clinical guideline."""
        with self._lock:
            self._guidelines[guideline.guideline_id] = guideline

    def get_guideline(self, guideline_id: str) -> ClinicalGuideline | None:
        """Get guideline by ID."""
        return self._guidelines.get(guideline_id)

    def find_guidelines(self, topic: str) -> list[ClinicalGuideline]:
        """Find guidelines by topic."""
        with self._lock:
            return [
                g for g in self._guidelines.values()
                if topic.lower() in g.name.lower()
            ]

    # =========================================================================
    # Drug Interactions
    # =========================================================================

    def add_drug_interaction(self, interaction: DrugInteraction) -> None:
        """Add drug interaction."""
        with self._lock:
            key = f"{interaction.drug1}:{interaction.drug2}"
            self._drug_interactions[key] = interaction

    def check_drug_interactions(
        self,
        drug1: str,
        drug2: str,
    ) -> DrugInteraction | None:
        """Check for interaction between two drugs."""
        key = f"{drug1}:{drug2}"
        reverse_key = f"{drug2}:{drug1}"

        return self._drug_interactions.get(key) or self._drug_interactions.get(reverse_key)

    def check_all_interactions(
        self,
        medications: list[str],
    ) -> list[DrugInteraction]:
        """Check all interactions in a medication list."""
        interactions = []
        n = len(medications)

        for i in range(n):
            for j in range(i + 1, n):
                interaction = self.check_drug_interactions(
                    medications[i], medications[j]
                )
                if interaction:
                    interactions.append(interaction)

        return interactions

    # =========================================================================
    # Contraindications
    # =========================================================================

    def add_contraindication(self, contra: Contraindication) -> None:
        """Add contraindication."""
        with self._lock:
            self._contraindications[contra.contraindication_id] = contra

    def check_contraindications(
        self,
        medication: str,
        conditions: list[str],
        allergies: list[str],
    ) -> list[Contraindication]:
        """Check contraindications."""
        results = []

        with self._lock:
            for contra in self._contraindications.values():
                if contra.medication.lower() == medication.lower():
                    # Check conditions
                    for condition in contra.conditions:
                        if any(c.lower() in condition.lower() for c in conditions):
                            results.append(contra)
                            break
                    # Check allergies
                    for allergy in contra.allergies:
                        if any(a.lower() in allergy.lower() for a in allergies):
                            results.append(contra)
                            break

        return results

    # =========================================================================
    # Risk Assessment
    # =========================================================================

    def assess_risk(
        self,
        patient_id: str,
        factors: list[RiskFactor],
    ) -> RiskAssessment:
        """Assess patient risk."""
        total_risk = 0.0

        for factor in factors:
            if factor.value is not None:
                # Simple risk calculation
                risk_contrib = factor.risk_contribution
                if isinstance(factor.value, (int, float)):
                    # Check if exceeds threshold
                    if factor.value > factor.threshold:
                        total_risk += risk_contrib

        # Normalize to 0-100
        risk_score = min(total_risk * 100, 100)

        # Classify risk level
        if risk_score < 20:
            overall = "low"
        elif risk_score < 50:
            overall = "moderate"
        elif risk_score < 75:
            overall = "high"
        else:
            overall = "very_high"

        return RiskAssessment(
            assessment_id=str(uuid.uuid4()),
            patient_id=patient_id,
            overall_risk=overall,
            risk_score=risk_score,
            factors=factors,
            recommendations=self._generate_risk_recommendations(overall),
        )

    def _generate_risk_recommendations(self, risk_level: str) -> list[str]:
        """Generate recommendations based on risk level."""
        recommendations = {
            "low": ["Continue routine monitoring"],
            "moderate": ["Consider lifestyle modifications", "Schedule follow-up in 3 months"],
            "high": ["Initiate risk reduction measures", "Consider specialist referral"],
            "very_high": ["Urgent intervention required", "Immediate specialist consultation"],
        }
        return recommendations.get(risk_level, [])

    # =========================================================================
    # Decision Generation
    # =========================================================================

    def generate_decision(
        self,
        patient_id: str,
        medications: list[str],
        conditions: list[str],
        allergies: list[str],
        risk_factors: list[RiskFactor] | None = None,
    ) -> CDSDecision:
        """Generate clinical decision support."""
        recommendations = []
        alerts = []

        # Check drug interactions
        interactions = self.check_all_interactions(medications)
        for interaction in interactions:
            if interaction.severity in ("major", "contraindicated"):
                alerts.append(f"⚠️ {interaction.severity.upper()}: {interaction.description}")
                recommendations.append(Recommendation(
                    recommendation_id=str(uuid.uuid4()),
                    type=RecommendationType.ALERT,
                    content=f"Review {interaction.drug1} and {interaction.drug2} combination",
                    evidence_level=EvidenceLevel.A,
                    confidence=0.95,
                ))

        # Check contraindications
        for med in medications:
            contra = self.check_contraindications(med, conditions, allergies)
            for c in contra:
                alerts.append(f"⚠️ Contraindication: {c.description}")
                recommendations.append(Recommendation(
                    recommendation_id=str(uuid.uuid4()),
                    type=RecommendationType.TREATMENT,
                    content=f"Consider alternative to {c.medication}",
                    evidence_level=EvidenceLevel.B,
                    confidence=0.85,
                ))

        # Risk assessment
        risk_assessment = None
        if risk_factors:
            risk_assessment = self.assess_risk(patient_id, risk_factors)
            if risk_assessment.overall_risk in ("high", "very_high"):
                recommendations.append(Recommendation(
                    recommendation_id=str(uuid.uuid4()),
                    type=RecommendationType.MONITORING,
                    content="Enhanced monitoring recommended due to risk profile",
                    evidence_level=EvidenceLevel.B,
                    confidence=risk_assessment.risk_score / 100,
                ))

        # Calculate confidence
        confidence = 0.5
        if recommendations:
            confidence = sum(r.confidence for r in recommendations) / len(recommendations)

        return CDSDecision(
            decision_id=str(uuid.uuid4()),
            patient_id=patient_id,
            recommendations=recommendations,
            alerts=alerts,
            risk_assessment=risk_assessment,
            drug_interactions=interactions,
            confidence=confidence,
            explanation=self._generate_explanation(recommendations, risk_assessment),
            citations=self._collect_citations(recommendations),
        )

    def _generate_explanation(
        self,
        recommendations: list[Recommendation],
        risk: RiskAssessment | None,
    ) -> str:
        """Generate human-readable explanation."""
        parts = []

        if recommendations:
            parts.append(f"Based on {len(recommendations)} recommendations:")
            for rec in recommendations[:3]:
                parts.append(f"- {rec.content} (Evidence: {rec.evidence_level.value})")

        if risk:
            parts.append(f"Risk Assessment: {risk.overall_risk.upper()} (Score: {risk.risk_score:.0f}/100)")

        return "\n".join(parts) if parts else "No specific recommendations at this time."

    def _collect_citations(self, recommendations: list[Recommendation]) -> list[str]:
        """Collect citations from recommendations."""
        citations = []
        for rec in recommendations:
            citations.extend(rec.sources)
        return list(set(citations))


# =============================================================================
# Contraindication Type
# =============================================================================


@dataclass
class Contraindication:
    """A contraindication for a medication."""

    contraindication_id: str
    medication: str
    conditions: list[str] = field(default_factory=list)
    allergies: list[str] = field(default_factory=list)
    severity: str = "major"
    description: str = ""
    recommendation: str = ""


# =============================================================================
# Singleton
# =============================================================================

_global_cds: ClinicalDecisionSupport | None = None
_cds_lock = threading.Lock()


def get_clinical_decision_support() -> ClinicalDecisionSupport:
    """Get global CDS engine."""
    global _global_cds
    with _cds_lock:
        if _global_cds is None:
            _global_cds = ClinicalDecisionSupport()
        return _global_cds


def reset_clinical_decision_support() -> None:
    """Reset global CDS engine."""
    global _global_cds
    with _cds_lock:
        _global_cds = None
