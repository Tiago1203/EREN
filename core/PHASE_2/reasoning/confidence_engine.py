"""Confidence Engine for EREN Cognitive Reasoning Platform.

Calculates confidence and uncertainty.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from core.PHASE_2.reasoning.reasoning_types import (
    ConfidenceLevel,
    ConfidenceScore,
    Evidence,
    Hypothesis,
)

if TYPE_CHECKING:
    pass


class ConfidenceEngine:
    """Calculates confidence and uncertainty.

    The Confidence Engine does NOT:
    - Collect evidence
    - Make decisions
    - Perform inference

    It ONLY:
    - Calculates confidence
    - Calculates uncertainty
    - Detects insufficient information
    """

    def __init__(self):
        """Initialize confidence engine."""
        self._calculation_count: int = 0

    def calculate_confidence(
        self,
        hypothesis: Hypothesis,
        evidence: list[Evidence],
        context: dict | None = None,
    ) -> ConfidenceScore:
        """Calculate confidence for hypothesis.

        Args:
            hypothesis: Hypothesis to evaluate.
            evidence: Related evidence.
            context: Optional context.

        Returns:
            Confidence score.
        """
        self._calculation_count += 1

        # Base confidence from hypothesis
        base = hypothesis.confidence_score

        # Adjust by evidence
        supporting = [e for e in evidence if e.supports()]
        contradicting = [e for e in evidence if e.contradicts()]

        if supporting:
            avg_support = sum(e.confidence * e.weight for e in supporting) / len(supporting)
            base = (base + avg_support) / 2

        if contradicting:
            avg_contradict = sum(e.confidence * e.weight for e in contradicting) / len(contradicting)
            base = base * (1 - avg_contradict)

        # Adjust by evidence count
        evidence_factor = min(1.0, len(evidence) / 5)
        base = base * (0.7 + 0.3 * evidence_factor)

        # Determine level
        level = self._value_to_level(base)

        return ConfidenceScore(
            value=base,
            level=level,
            reasons=(
                f"Based on {len(supporting)} supporting evidence",
                f"Against {len(contradicting)} contradicting evidence",
            ),
            algorithm="evidence_weighted",
        )

    def _value_to_level(self, value: float) -> ConfidenceLevel:
        """Convert value to confidence level.

        Args:
            value: Confidence value.

        Returns:
            Confidence level.
        """
        if value >= 0.9:
            return ConfidenceLevel.VERY_HIGH
        elif value >= 0.75:
            return ConfidenceLevel.HIGH
        elif value >= 0.5:
            return ConfidenceLevel.MODERATE
        elif value >= 0.3:
            return ConfidenceLevel.LOW
        elif value >= 0.15:
            return ConfidenceLevel.VERY_LOW
        else:
            return ConfidenceLevel.NONE

    def calculate_uncertainty(
        self,
        hypothesis: Hypothesis,
        evidence: list[Evidence],
    ) -> dict:
        """Calculate uncertainty.

        Args:
            hypothesis: Hypothesis to evaluate.
            evidence: Related evidence.

        Returns:
            Uncertainty metrics.
        """
        # Epistemic uncertainty (lack of evidence)
        epistemic = 1.0 - min(1.0, len(evidence) / 5)

        # Aleatoric uncertainty (inherent randomness)
        aleatoric = 0.0
        if evidence:
            confidences = [e.confidence for e in evidence]
            variance = sum((c - sum(confidences) / len(confidences)) ** 2 for c in confidences) / len(confidences)
            aleatoric = min(1.0, variance)

        # Total uncertainty
        total = epistemic + aleatoric - (epistemic * aleatoric)

        return {
            "epistemic": epistemic,
            "aleatoric": aleatoric,
            "total": total,
            "is_uncertain": total > 0.5,
        }

    def detect_insufficient_information(
        self,
        evidence: list[Evidence],
        threshold: int = 3,
    ) -> bool:
        """Detect if information is insufficient.

        Args:
            evidence: Evidence to evaluate.
            threshold: Minimum evidence required.

        Returns:
            True if insufficient.
        """
        return len(evidence) < threshold

    def aggregate_confidence(
        self,
        scores: list[ConfidenceScore],
    ) -> ConfidenceScore:
        """Aggregate multiple confidence scores.

        Args:
            scores: Scores to aggregate.

        Returns:
            Aggregated score.
        """
        if not scores:
            return ConfidenceScore(value=0.0, level=ConfidenceLevel.NONE)

        values = [s.value for s in scores]
        avg_value = sum(values) / len(values)

        # Use lowest level among scores
        min_level = min(s.level for s in scores)

        return ConfidenceScore(
            value=avg_value,
            level=min_level,
            reasons=(f"Aggregated from {len(scores)} scores",),
            algorithm="mean_min_level",
        )

    def adjust_confidence(
        self,
        score: ConfidenceScore,
        adjustment: float,
        reason: str,
    ) -> ConfidenceScore:
        """Adjust a confidence score.

        Args:
            score: Score to adjust.
            adjustment: Adjustment amount.
            reason: Reason for adjustment.

        Returns:
            Adjusted score.
        """
        new_value = max(0.0, min(1.0, score.value + adjustment))

        return ConfidenceScore(
            value=new_value,
            level=self._value_to_level(new_value),
            reasons=score.reasons + (reason,),
            supporting_factors=score.supporting_factors,
            contradicting_factors=score.contradicting_factors,
            algorithm=f"{score.algorithm}_adjusted",
        )


# Global confidence engine
_confidence_engine: ConfidenceEngine | None = None
_confidence_lock = __import__("threading").Lock()


def get_confidence_engine() -> ConfidenceEngine:
    """Get the global confidence engine."""
    global _confidence_engine
    with _confidence_lock:
        if _confidence_engine is None:
            _confidence_engine = ConfidenceEngine()
        return _confidence_engine


def reset_confidence_engine() -> None:
    """Reset the global confidence engine."""
    global _confidence_engine
    with _confidence_lock:
        _confidence_engine = None
