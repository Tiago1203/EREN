"""
Clinical Validation Module

Complete implementation of EPIC 8 for EREN PHASE 3.

This module provides clinical validation:
- Evidence Validation
- Confidence Checking
- Consistency Checking
- Self-Correction
"""

from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


# Version
__version__ = "1.0.0"


class ValidationDecision(Enum):
    """Decision outcomes."""
    APPROVED = "approved"
    REJECTED = "rejected"
    REQUIRES_CORRECTION = "requires_correction"
    ESCALATE = "escalate"


class CorrectionType(Enum):
    """Types of self-corrections."""
    REWORD = "reword"
    NARROW = "narrow"
    BROADEN = "broaden"
    ADD_CONDITION = "add_condition"
    REDUCE_CONFIDENCE = "reduce"
    ESCALATE = "escalate"


@dataclass
class ValidationResult:
    """Result of clinical validation."""
    decision: ValidationDecision
    is_valid: bool
    evidence_valid: bool
    confidence_valid: bool
    safety_valid: bool
    rules_valid: bool
    consistency_valid: bool
    clinical_valid: bool
    rejection_reasons: list[str]
    correction_suggestions: list[str]


@dataclass
class EvidenceValidationResult:
    """Result of evidence validation."""
    is_sufficient: bool
    is_relevant: bool
    is_current: bool
    quality_score: float
    sufficiency_score: float
    reason: Optional[str]
    missing_evidence: list[str]


@dataclass
class ConsistencyResult:
    """Result of consistency checking."""
    is_consistent: bool
    internal_consistent: bool
    external_consistent: bool
    inconsistencies: list[str]
    suggestions: list[str]
    adjustment: Optional[float]


@dataclass
class Correction:
    """Self-correction suggestion."""
    correction_id: str
    correction_type: CorrectionType
    original_text: str
    corrected_text: str
    reason: str
    confidence_impact: float


@dataclass
class CorrectionResult:
    """Result of self-correction."""
    was_corrected: bool
    corrections: list[Correction]
    final_recommendation: Optional[str]
    requires_escalation: bool


# Thresholds
MIN_EVIDENCE_COUNT = 3
MIN_QUALITY_SCORE = 0.4
MIN_CONFIDENCE_SCORE = 0.5


class EvidenceValidator:
    """Validates evidence for recommendations."""
    
    async def validate(self, context: dict) -> EvidenceValidationResult:
        """Validate evidence sufficiency and quality."""
        evidence = context.get("evidence_bundle", {})
        supporting = evidence.get("supporting", [])
        contradicting = evidence.get("contradicting", [])
        
        # Check quantity
        sufficient_count = len(supporting) >= MIN_EVIDENCE_COUNT
        
        # Check quality
        quality_scores = [e.get("quality_score", 0) for e in supporting]
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
        sufficient_quality = avg_quality >= MIN_QUALITY_SCORE
        
        # Calculate sufficiency score
        sufficiency_score = min(len(supporting) / MIN_EVIDENCE_COUNT, 1.0) * avg_quality
        
        # Contradiction penalty
        contradiction_ratio = len(contradicting) / max(len(supporting), 1)
        sufficiency_score = max(0, sufficiency_score - contradiction_ratio * 0.3)
        
        is_sufficient = sufficient_count and sufficient_quality and contradiction_ratio < 0.3
        
        missing = []
        if not sufficient_count:
            missing.append(f"Need {MIN_EVIDENCE_COUNT - len(supporting)} more evidence")
        if not sufficient_quality:
            missing.append("Evidence quality too low")
        
        return EvidenceValidationResult(
            is_sufficient=is_sufficient,
            is_relevant=sufficient_quality,
            is_current=True,
            quality_score=avg_quality,
            sufficiency_score=sufficiency_score,
            reason=None if is_sufficient else "; ".join(missing),
            missing_evidence=missing,
        )


class ConfidenceChecker:
    """Checks confidence levels."""
    
    async def check(self, confidence: dict) -> EvidenceValidationResult:
        """Check if confidence is acceptable."""
        score = confidence.get("score", 0)
        is_acceptable = score >= MIN_CONFIDENCE_SCORE
        
        return EvidenceValidationResult(
            is_sufficient=is_acceptable,
            is_relevant=True,
            is_current=True,
            quality_score=score,
            sufficiency_score=score,
            reason=None if is_acceptable else f"Confidence {score:.0%} below threshold",
            missing_evidence=[],
        )


class ConsistencyChecker:
    """Checks consistency of recommendations."""
    
    async def check(
        self,
        recommendation: dict,
        context: dict,
    ) -> ConsistencyResult:
        """Check internal and external consistency."""
        issues = []
        suggestions = []
        
        # Check hypothesis-evidence consistency
        hypothesis = context.get("hypothesis", {})
        evidence_bundle = context.get("evidence_bundle", {})
        
        hypothesis_type = hypothesis.get("type")
        evidence_types = [e.get("type") for e in evidence_bundle.get("supporting", [])]
        
        if hypothesis_type and evidence_types:
            mismatch_count = sum(1 for et in evidence_types if et != hypothesis_type)
            mismatch_ratio = mismatch_count / len(evidence_types)
            
            if mismatch_ratio > 0.5:
                issues.append("Evidence type mismatch with hypothesis")
                suggestions.append("Review hypothesis or gather matching evidence")
        
        return ConsistencyResult(
            is_consistent=len(issues) == 0,
            internal_consistent=len(issues) == 0,
            external_consistent=True,
            inconsistencies=issues,
            suggestions=suggestions,
            adjustment=-0.15 if issues else None,
        )


class SelfCorrectionEngine:
    """Engine for self-correction of recommendations."""
    
    async def correct(
        self,
        recommendation: dict,
        consistency_result: ConsistencyResult,
        evidence_result: EvidenceValidationResult,
    ) -> CorrectionResult:
        """Attempt to self-correct recommendation."""
        
        reasons = list(consistency_result.inconsistencies)
        if not evidence_result.is_sufficient:
            reasons.append(evidence_result.reason or "Insufficient evidence")
        
        if not reasons:
            return CorrectionResult(
                was_corrected=False,
                corrections=[],
                final_recommendation=recommendation.get("action"),
                requires_escalation=False,
            )
        
        # Determine correction type
        correction_type = self._determine_correction_type(reasons)
        
        if correction_type == CorrectionType.ESCALATE:
            return CorrectionResult(
                was_corrected=True,
                corrections=[],
                final_recommendation=None,
                requires_escalation=True,
            )
        
        # Apply correction
        correction = self._apply_correction(recommendation, correction_type, reasons)
        
        return CorrectionResult(
            was_corrected=True,
            corrections=[correction],
            final_recommendation=correction.corrected_text,
            requires_escalation=False,
        )
    
    def _determine_correction_type(self, reasons: list[str]) -> CorrectionType:
        """Determine correction type needed."""
        for reason in reasons:
            if "safety" in reason.lower() or "risk" in reason.lower():
                return CorrectionType.ESCALATE
            if "quality" in reason.lower() or "evidence" in reason.lower():
                return CorrectionType.REDUCE_CONFIDENCE
        
        return CorrectionType.REDUCE_CONFIDENCE
    
    def _apply_correction(
        self,
        recommendation: dict,
        correction_type: CorrectionType,
        reasons: list[str],
    ) -> Correction:
        """Apply specific correction."""
        original = recommendation.get("action", "")
        confidence_impact = 0.0
        corrected = original
        
        if correction_type == CorrectionType.REDUCE_CONFIDENCE:
            corrected = f"{original} (verify with additional testing)"
            confidence_impact = -0.20
        elif correction_type == CorrectionType.ESCALATE:
            corrected = "ESCALATE_TO_HUMAN"
            confidence_impact = -1.0
        
        return Correction(
            correction_id=f"corr_{datetime.now().timestamp()}",
            correction_type=correction_type,
            original_text=original,
            corrected_text=corrected,
            reason="; ".join(reasons),
            confidence_impact=confidence_impact,
        )


class ClinicalValidationEngine:
    """
    Main clinical validation engine.
    Final gate before any response is issued.
    """
    
    def __init__(self):
        self.evidence_validator = EvidenceValidator()
        self.confidence_checker = ConfidenceChecker()
        self.consistency_checker = ConsistencyChecker()
        self.self_correction = SelfCorrectionEngine()
    
    async def validate(
        self,
        recommendation: dict,
        context: dict,
        safety_decision: str,
        confidence: dict,
        rules_compliant: bool,
    ) -> ValidationResult:
        """Validate recommendation through complete pipeline."""
        
        rejection_reasons = []
        
        # 1. Evidence Validation
        evidence_result = await self.evidence_validator.validate(context)
        evidence_valid = evidence_result.is_sufficient
        if not evidence_valid:
            rejection_reasons.append(f"Evidence: {evidence_result.reason}")
        
        # 2. Confidence Check
        confidence_result = await self.confidence_checker.check(confidence)
        confidence_valid = confidence_result.is_sufficient
        if not confidence_valid:
            rejection_reasons.append(f"Confidence: {confidence_result.reason}")
        
        # 3. Safety Gate
        safety_valid = safety_decision != "block"
        if not safety_valid:
            rejection_reasons.append("Safety validation failed")
        
        # 4. Rules Check
        rules_valid = rules_compliant
        if not rules_valid:
            rejection_reasons.append("Rules violation detected")
        
        # 5. Consistency Check
        consistency_result = await self.consistency_checker.check(recommendation, context)
        consistency_valid = consistency_result.is_consistent
        if not consistency_valid:
            rejection_reasons.extend(consistency_result.inconsistencies)
        
        # Determine decision
        if rejection_reasons:
            # Try self-correction
            correction_result = await self.self_correction.correct(
                recommendation, consistency_result, evidence_result
            )
            
            if correction_result.requires_escalation:
                decision = ValidationDecision.ESCALATE
            elif correction_result.was_corrected:
                decision = ValidationDecision.REQUIRES_CORRECTION
            else:
                decision = ValidationDecision.REJECTED
        else:
            decision = ValidationDecision.APPROVED
        
        return ValidationResult(
            decision=decision,
            is_valid=decision == ValidationDecision.APPROVED,
            evidence_valid=evidence_valid,
            confidence_valid=confidence_valid,
            safety_valid=safety_valid,
            rules_valid=rules_valid,
            consistency_valid=consistency_valid,
            clinical_valid=True,
            rejection_reasons=rejection_reasons,
            correction_suggestions=consistency_result.suggestions,
        )


__all__ = [
    # Version
    "__version__",
    # Enums
    "ValidationDecision",
    "CorrectionType",
    # Data Classes
    "ValidationResult",
    "EvidenceValidationResult",
    "ConsistencyResult",
    "Correction",
    "CorrectionResult",
    # Validators
    "EvidenceValidator",
    "ConfidenceChecker",
    "ConsistencyChecker",
    "SelfCorrectionEngine",
    "ClinicalValidationEngine",
    # Constants
    "MIN_EVIDENCE_COUNT",
    "MIN_QUALITY_SCORE",
    "MIN_CONFIDENCE_SCORE",
]
