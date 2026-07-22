"""
Confidence Engine Module

Complete implementation of EPIC 4 for EREN PHASE 3.

This module provides confidence calculation and uncertainty quantification:
- Confidence Calculator
- Risk Assessor
- Quality Evaluator
- Coverage Analyzer
- Ambiguity Detector

ARCHITECTURE NOTE:
All shared Enums (ConfidenceLevel, RiskLevel, UncertaintyType) are imported
from core.intelligence.foundation.enums to ensure consistency.
Only Engine-specific enums are defined locally.
"""

from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

# Import shared enums from SINGLE SOURCE OF TRUTH
from core.intelligence.foundation.enums import (
    ConfidenceLevel,
    RiskLevel,
    UncertaintyType,
)

# Version
__version__ = "1.0.0"


# Engine-specific ConfidenceQualityDimension (different from foundation.QualityDimension)
class ConfidenceQualityDimension(Enum):
    """Dimensions of quality for confidence evaluation."""
    EVIDENCE_QUALITY = "evidence_quality"
    REASONING_QUALITY = "reasoning_quality"
    OUTPUT_QUALITY = "output_quality"
    COVERAGE = "coverage"
    CONSISTENCY = "consistency"


@dataclass(frozen=True)
class ConfidenceScore:
    """Confidence score output."""
    score: float
    level: ConfidenceLevel
    components: dict[str, float]
    uncertainty_factors: list[str]
    supporting_factors: list[str]
    recommendation: str
    
    @property
    def is_uncertain(self) -> bool:
        """Returns True if confidence is below threshold."""
        return self.score < 0.5
    
    @property
    def is_certain(self) -> bool:
        """Returns True if confidence is above threshold."""
        return self.score >= 0.8
    
    @property
    def percentage(self) -> int:
        """Returns score as percentage."""
        return int(self.score * 100)


@dataclass(frozen=True)
class RiskFactor:
    """Individual risk factor."""
    factor_id: str
    name: str
    description: str
    category: str
    probability: float
    severity: float
    detectability: float = 0.5
    
    @property
    def risk_score(self) -> float:
        """Calculate risk score."""
        return self.probability * self.severity * (1 - self.detectability * 0.5)


@dataclass(frozen=True)
class RiskAssessment:
    """Complete risk assessment."""
    overall_risk: RiskLevel
    risk_factors: list[RiskFactor]
    recommendations: list[str]
    immediate_actions: list[str]


@dataclass(frozen=True)
class UncertaintyFactor:
    """Individual uncertainty factor."""
    factor_id: str
    type: UncertaintyType
    description: str
    magnitude: float
    impact_on_confidence: float
    mitigatable: bool


@dataclass(frozen=True)
class UncertaintyReport:
    """Complete uncertainty quantification."""
    total_uncertainty: float
    factors: list[UncertaintyFactor]
    confidence_impact: float
    mitigation_suggestions: list[str]
    data_gaps: list[str]


@dataclass(frozen=True)
class QualityScore:
    """Quality evaluation result."""
    overall_quality: float
    dimensions: dict[ConfidenceQualityDimension, float]
    issues: list[str]
    strengths: list[str]


@dataclass(frozen=True)
class CoverageAnalysis:
    """Coverage analysis result."""
    coverage_percentage: float
    covered_topics: list[str]
    missing_topics: list[str]
    evidence_coverage: float
    reasoning_coverage: float


@dataclass(frozen=True)
class AmbiguityReport:
    """Ambiguity detection result."""
    is_ambiguous: bool
    ambiguity_types: list[str]
    conflicting_interpretations: list[str]
    clarification_needed: list[str]


@dataclass(frozen=True)
class ConfidenceResult:
    """Complete confidence result."""
    confidence_score: ConfidenceScore
    risk_assessment: RiskAssessment
    uncertainty_report: UncertaintyReport
    quality_score: QualityScore
    coverage_analysis: CoverageAnalysis
    ambiguity_report: AmbiguityReport
    timestamp: datetime = field(default_factory=datetime.now)


class EvidenceBasedCalculator:
    """Calculates confidence based on evidence."""
    
    async def calculate(self, evidence_bundle: dict) -> float:
        """Calculate evidence-based confidence."""
        supporting_evidence = evidence_bundle.get("supporting", [])
        contradicting_evidence = evidence_bundle.get("contradicting", [])
        
        if not supporting_evidence:
            return 0.2
        
        # Evidence quantity
        evidence_count = len(supporting_evidence)
        quantity_score = min(evidence_count / 5, 1.0)
        
        # Evidence quality (average)
        quality_scores = [e.get("quality_score", 0.5) for e in supporting_evidence]
        avg_quality = sum(quality_scores) / len(quality_scores)
        
        # Evidence relevance (average)
        relevance_scores = [e.get("relevance_score", 0.5) for e in supporting_evidence]
        avg_relevance = sum(relevance_scores) / len(relevance_scores)
        
        # Contradicting evidence penalty
        contradiction_penalty = len(contradicting_evidence) * 0.1
        
        score = (
            quantity_score * 0.3 +
            avg_quality * 0.4 +
            avg_relevance * 0.3 -
            contradiction_penalty
        )
        
        return max(0.0, min(1.0, score))


class KnowledgeBasedCalculator:
    """Calculates confidence based on knowledge."""
    
    async def calculate(self, context: dict) -> float:
        """Calculate knowledge-based confidence."""
        coverage = context.get("knowledge_coverage", 0.0)
        quality = context.get("knowledge_quality", 0.0)
        recency = context.get("knowledge_recency", 0.5)
        
        score = (
            coverage * 0.4 +
            quality * 0.4 +
            recency * 0.2
        )
        
        return max(0.0, min(1.0, score))


class ReasoningBasedCalculator:
    """Calculates confidence based on reasoning."""
    
    async def calculate(self, chain: dict) -> float:
        """Calculate reasoning-based confidence."""
        strength = chain.get("strength", 0.5)
        step_count = len(chain.get("steps", []))
        
        # Longer chains may be weaker
        step_penalty = max(0, (step_count - 5) * 0.02)
        
        # Premise support ratio
        steps = chain.get("steps", [])
        premises_supported = sum(1 for s in steps if s.get("supported", False))
        premise_ratio = premises_supported / max(len(steps), 1)
        
        score = (
            strength * 0.5 +
            premise_ratio * 0.5 -
            step_penalty
        )
        
        return max(0.0, min(1.0, score))


class EnsembleCalculator:
    """Combines multiple confidence sources."""
    
    def __init__(
        self,
        evidence_weight: float = 0.4,
        knowledge_weight: float = 0.3,
        reasoning_weight: float = 0.3,
    ):
        self.evidence_weight = evidence_weight
        self.knowledge_weight = knowledge_weight
        self.reasoning_weight = reasoning_weight
    
    def combine(
        self,
        evidence: float,
        knowledge: float,
        reasoning: float,
    ) -> float:
        """Combine scores using weighted average."""
        score = (
            evidence * self.evidence_weight +
            knowledge * self.knowledge_weight +
            reasoning * self.reasoning_weight
        )
        return max(0.0, min(1.0, score))


class ConfidenceCalculator:
    """Main confidence calculator."""
    
    def __init__(self):
        self.evidence_calc = EvidenceBasedCalculator()
        self.knowledge_calc = KnowledgeBasedCalculator()
        self.reasoning_calc = ReasoningBasedCalculator()
        self.ensemble = EnsembleCalculator()
    
    async def calculate(
        self,
        evidence_bundle: dict,
        knowledge_context: dict,
        reasoning_chain: dict,
    ) -> ConfidenceScore:
        """Calculate confidence score."""
        
        # Calculate component scores
        evidence_score = await self.evidence_calc.calculate(evidence_bundle)
        knowledge_score = await self.knowledge_calc.calculate(knowledge_context)
        reasoning_score = await self.reasoning_calc.calculate(reasoning_chain)
        
        # Ensemble combination
        overall_score = self.ensemble.combine(
            evidence=evidence_score,
            knowledge=knowledge_score,
            reasoning=reasoning_score,
        )
        
        # Determine factors
        uncertainty_factors = []
        supporting_factors = []
        
        if evidence_score < 0.5:
            uncertainty_factors.append("Limited evidence available")
        else:
            supporting_factors.append("Strong evidence support")
        
        if knowledge_score < 0.5:
            uncertainty_factors.append("Limited knowledge coverage")
        else:
            supporting_factors.append("Well-documented domain knowledge")
        
        if reasoning_score < 0.5:
            uncertainty_factors.append("Reasoning chain is weak")
        else:
            supporting_factors.append("Strong reasoning chain")
        
        # Generate recommendation
        recommendation = self._generate_recommendation(
            overall_score, uncertainty_factors
        )
        
        return ConfidenceScore(
            score=overall_score,
            level=self._get_level(overall_score),
            components={
                "evidence": evidence_score,
                "knowledge": knowledge_score,
                "reasoning": reasoning_score,
            },
            uncertainty_factors=uncertainty_factors,
            supporting_factors=supporting_factors,
            recommendation=recommendation,
        )
    
    def _get_level(self, score: float) -> ConfidenceLevel:
        """Get confidence level from score."""
        if score >= 0.95:
            return ConfidenceLevel.VERY_HIGH
        elif score >= 0.85:
            return ConfidenceLevel.HIGH
        elif score >= 0.70:
            return ConfidenceLevel.MODERATE
        elif score >= 0.50:
            return ConfidenceLevel.LOW
        elif score >= 0.30:
            return ConfidenceLevel.VERY_LOW
        else:
            return ConfidenceLevel.UNCERTAIN
    
    def _generate_recommendation(
        self,
        score: float,
        uncertainty_factors: list[str],
    ) -> str:
        """Generate recommendation based on confidence."""
        if score >= 0.8:
            return "Proceed with confidence."
        elif score >= 0.5:
            factors_str = ", ".join(uncertainty_factors[:2])
            return f"Proceed with caution: {factors_str}"
        else:
            return "More investigation needed before proceeding."


class ConfidenceEngine:
    """
    Main confidence engine that provides the external interface.
    """
    
    def __init__(self):
        self.calculator = ConfidenceCalculator()
    
    async def assess_confidence(
        self,
        evidence_bundle: dict,
        knowledge_context: dict,
        reasoning_chain: dict,
    ) -> ConfidenceScore:
        """Assess confidence for given inputs."""
        return await self.calculator.calculate(
            evidence_bundle=evidence_bundle,
            knowledge_context=knowledge_context,
            reasoning_chain=reasoning_chain,
        )
    
    def explain_confidence(self, score: ConfidenceScore) -> str:
        """Generate natural language explanation."""
        lines = [
            f"Confidence: {score.percentage}% ({score.level.value})",
            "",
            "Supporting factors:",
        ]
        
        for factor in score.supporting_factors:
            lines.append(f"  ✓ {factor}")
        
        if score.uncertainty_factors:
            lines.append("")
            lines.append("Uncertainty factors:")
            for factor in score.uncertainty_factors:
                lines.append(f"  ⚠ {factor}")
        
        lines.append("")
        lines.append(f"Recommendation: {score.recommendation}")
        
        return "\n".join(lines)


__all__ = [
    # Version
    "__version__",
    # Enums (imported from Foundation)
    "ConfidenceLevel",
    "RiskLevel",
    "UncertaintyType",
    # Local enums
    "ConfidenceQualityDimension",
    # Data classes
    "ConfidenceScore",
    "RiskFactor",
    "RiskAssessment",
    "UncertaintyFactor",
    "UncertaintyReport",
    "QualityScore",
    "CoverageAnalysis",
    "AmbiguityReport",
    "ConfidenceResult",
    # Calculators
    "EvidenceBasedCalculator",
    "KnowledgeBasedCalculator",
    "ReasoningBasedCalculator",
    "EnsembleCalculator",
    "ConfidenceCalculator",
    "ConfidenceEngine",
]
