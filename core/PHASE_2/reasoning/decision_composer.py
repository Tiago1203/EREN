"""Decision Composer for EREN Cognitive Reasoning Platform.

Composes the final decision with evidence, explanations, and confidence.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from core.PHASE_2.reasoning.reasoning_types import (
    ConfidenceScore,
    Decision,
    DecisionStatus,
    DecisionType,
    Evidence,
    Hypothesis,
)

if TYPE_CHECKING:
    pass


class DecisionComposer:
    """Composes final decisions.

    The Decision Composer does NOT:
    - Collect evidence
    - Generate hypotheses
    - Calculate confidence

    It ONLY:
    - Builds final decision
    - Aggregates evidence
    - Adds explanations
    - Adds confidence
    """

    def __init__(self):
        """Initialize decision composer."""
        self._decisions_composed: int = 0

    def compose(
        self,
        hypothesis: Hypothesis,
        evidence: list[Evidence],
        explanation: dict,
        confidence: ConfidenceScore,
        alternatives: list[Hypothesis] | None = None,
    ) -> Decision:
        """Compose a decision.

        Args:
            hypothesis: Selected hypothesis.
            evidence: Related evidence.
            explanation: Explanation dictionary.
            confidence: Confidence score.
            alternatives: Alternative hypotheses.

        Returns:
            Composed decision.
        """
        self._decisions_composed += 1

        decision_id = f"dec_{uuid.uuid4().hex[:16]}"

        # Determine decision type based on hypothesis
        decision_type = self._infer_decision_type(hypothesis)

        # Build justification
        justification = self._build_justification(
            hypothesis, evidence, explanation
        )

        # Collect alternatives
        alternative_ids = []
        if alternatives:
            for alt in alternatives[:5]:  # Limit to 5 alternatives
                alternative_ids.append(alt.description)

        # Select reason
        selected_reason = self._build_selected_reason(
            hypothesis, confidence
        )

        return Decision(
            decision_id=decision_id,
            decision_type=decision_type,
            description=hypothesis.description,
            status=DecisionStatus.PROPOSED,
            based_on_hypothesis=hypothesis.hypothesis_id,
            confidence=confidence,
            justification=tuple(justification),
            alternatives=tuple(alternative_ids),
            selected_reason=selected_reason,
        )

    def _infer_decision_type(self, hypothesis: Hypothesis) -> DecisionType:
        """Infer decision type from hypothesis.

        Args:
            hypothesis: Hypothesis to analyze.

        Returns:
            Inferred decision type.
        """
        desc = hypothesis.description.lower()

        if any(word in desc for word in ["diagnos", "detect", "identif"]):
            return DecisionType.DIAGNOSTIC
        elif any(word in desc for word in ["treat", "therap", "interven"]):
            return DecisionType.THERAPEUTIC
        elif any(word in desc for word in ["operat", "action", "proces"]):
            return DecisionType.OPERATIONAL
        else:
            return DecisionType.RECOMMENDATION

    def _build_justification(
        self,
        hypothesis: Hypothesis,
        evidence: list[Evidence],
        explanation: dict,
    ) -> list[str]:
        """Build justification list.

        Args:
            hypothesis: Hypothesis.
            evidence: Evidence.
            explanation: Explanation.

        Returns:
            List of justification strings.
        """
        justification = []

        justification.append(f"Based on analysis of {len(evidence)} evidence items")

        supporting = [e for e in evidence if e.supports()]
        if supporting:
            justification.append(f"Supported by {len(supporting)} supporting evidence")

        contradicting = [e for e in evidence if e.contradicts()]
        if contradicting:
            justification.append(f"Considered {len(contradicting)} contradicting evidence")

        if explanation.get("reasoning_chain"):
            chain = explanation["reasoning_chain"]
            if chain:
                justification.append(f"Derived from {len(chain)} reasoning steps")

        return justification

    def _build_selected_reason(
        self,
        hypothesis: Hypothesis,
        confidence: ConfidenceScore,
    ) -> str:
        """Build selection reason.

        Args:
            hypothesis: Selected hypothesis.
            confidence: Confidence score.

        Returns:
            Selection reason.
        """
        parts = [
            f"Highest ranked hypothesis (rank: {hypothesis.rank})",
            f"Confidence: {confidence.value:.1%}",
        ]

        if hypothesis.priority.name != "MEDIUM":
            parts.append(f"Priority: {hypothesis.priority.name}")

        return "; ".join(parts)

    def compose_alternative(
        self,
        hypothesis: Hypothesis,
        confidence: ConfidenceScore,
        reason_not_selected: str,
    ) -> dict:
        """Compose an alternative decision.

        Args:
            hypothesis: Alternative hypothesis.
            confidence: Confidence score.
            reason_not_selected: Why not selected.

        Returns:
            Alternative decision info.
        """
        return {
            "hypothesis_id": hypothesis.hypothesis_id,
            "description": hypothesis.description,
            "confidence": confidence.value,
            "reason_not_selected": reason_not_selected,
            "rank": hypothesis.rank,
        }


# Global decision composer
_decision_composer: DecisionComposer | None = None
_composer_lock = __import__("threading").Lock()


def get_decision_composer() -> DecisionComposer:
    """Get the global decision composer."""
    global _decision_composer
    with _composer_lock:
        if _decision_composer is None:
            _decision_composer = DecisionComposer()
        return _decision_composer


def reset_decision_composer() -> None:
    """Reset the global decision composer."""
    global _decision_composer
    with _composer_lock:
        _decision_composer = None
