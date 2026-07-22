"""Explanation Engine for EREN Cognitive Reasoning Platform.

Generates explanations, justifications, and traceable reasoning.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from core.PHASE_2.reasoning.reasoning_types import (
    ConfidenceScore,
    Decision,
    Evidence,
    Hypothesis,
)

if TYPE_CHECKING:
    pass


class ExplanationEngine:
    """Generates explanations for reasoning.

    The Explanation Engine does NOT:
    - Collect evidence
    - Make decisions
    - Calculate confidence

    It ONLY:
    - Generates explanations
    - Provides justifications
    - Includes references
    - Creates traceable reasoning
    """

    def __init__(self):
        """Initialize explanation engine."""
        self._explanations_generated: int = 0

    def explain_hypothesis(
        self,
        hypothesis: Hypothesis,
        evidence: list[Evidence],
        confidence: ConfidenceScore,
    ) -> dict:
        """Generate explanation for hypothesis.

        Args:
            hypothesis: Hypothesis to explain.
            evidence: Supporting evidence.
            confidence: Confidence score.

        Returns:
            Explanation dictionary.
        """
        self._explanations_generated += 1

        supporting = [e for e in evidence if e.supports()]
        contradicting = [e for e in evidence if e.contradicts()]

        return {
            "explanation_id": f"exp_{self._explanations_generated}",
            "hypothesis_id": hypothesis.hypothesis_id,
            "summary": self._generate_summary(hypothesis, confidence),
            "evidence_summary": self._summarize_evidence(supporting, contradicting),
            "reasoning_chain": self._build_reasoning_chain(hypothesis, evidence),
            "confidence_explanation": self._explain_confidence(confidence),
            "references": self._collect_references(evidence),
        }

    def _generate_summary(
        self,
        hypothesis: Hypothesis,
        confidence: ConfidenceScore,
    ) -> str:
        """Generate summary text.

        Args:
            hypothesis: Hypothesis.
            confidence: Confidence score.

        Returns:
            Summary text.
        """
        return (
            f"Based on analysis, {hypothesis.description} "
            f"with confidence {confidence.value:.1%}. "
            f"Status: {hypothesis.status.name}"
        )

    def _summarize_evidence(
        self,
        supporting: list[Evidence],
        contradicting: list[Evidence],
    ) -> str:
        """Summarize evidence.

        Args:
            supporting: Supporting evidence.
            contradicting: Contradicting evidence.

        Returns:
            Evidence summary.
        """
        parts = []

        if supporting:
            parts.append(f"{len(supporting)} supporting evidence")
        if contradicting:
            parts.append(f"{len(contradicting)} contradicting evidence")

        if not parts:
            return "No evidence evaluated"

        return " and ".join(parts)

    def _build_reasoning_chain(
        self,
        hypothesis: Hypothesis,
        evidence: list[Evidence],
    ) -> list[str]:
        """Build reasoning chain.

        Args:
            hypothesis: Hypothesis.
            evidence: Evidence.

        Returns:
            List of reasoning steps.
        """
        chain = []

        chain.append("1. Initial observation recorded")

        for i, e in enumerate(evidence[:5], 2):
            relation = "supports" if e.supports() else "contradicts"
            chain.append(f"{i}. Evidence {i-1} {relation}: {e.content}")

        chain.append(f"{len(chain) + 1}. Hypothesis evaluated: {hypothesis.description}")
        chain.append(f"{len(chain) + 1}. Confidence calculated: {hypothesis.confidence_score:.2f}")

        return chain

    def _explain_confidence(self, confidence: ConfidenceScore) -> str:
        """Explain confidence score.

        Args:
            confidence: Confidence score.

        Returns:
            Explanation text.
        """
        parts = [f"Confidence level: {confidence.level.name} ({confidence.value:.1%})"]

        if confidence.reasons:
            parts.append("Reasons:")
            for reason in confidence.reasons:
                parts.append(f"  - {reason}")

        return "\n".join(parts)

    def _collect_references(self, evidence: list[Evidence]) -> list[dict]:
        """Collect references from evidence.

        Args:
            evidence: Evidence to extract references from.

        Returns:
            List of references.
        """
        refs = []

        for e in evidence:
            if isinstance(e.content, dict) and "reference" in e.content:
                refs.append(e.content["reference"])

            refs.append({
                "source": e.source.value,
                "type": e.evidence_type.value,
                "id": e.evidence_id,
            })

        return refs

    def explain_decision(
        self,
        decision: Decision,
        hypothesis: Hypothesis,
        alternatives: list[Hypothesis],
    ) -> dict:
        """Generate explanation for decision.

        Args:
            decision: Decision to explain.
            hypothesis: Selected hypothesis.
            alternatives: Alternative hypotheses.

        Returns:
            Decision explanation.
        """
        return {
            "decision_id": decision.decision_id,
            "selected": hypothesis.description,
            "justification": list(decision.justification),
            "confidence": decision.confidence.value,
            "alternatives_considered": [h.description for h in alternatives],
            "selection_reason": decision.selected_reason,
        }

    def create_justification(
        self,
        conclusion: str,
        evidence_ids: list[str],
        reasoning_chain: list[str],
    ) -> str:
        """Create justification text.

        Args:
            conclusion: Conclusion.
            evidence_ids: Evidence IDs used.
            reasoning_chain: Reasoning steps.

        Returns:
            Justification text.
        """
        lines = [f"Conclusion: {conclusion}", "", "Evidence:"]
        for eid in evidence_ids:
            lines.append(f"  - {eid}")

        lines.append("", "Reasoning:")
        for step in reasoning_chain:
            lines.append(f"  {step}")

        return "\n".join(lines)


# Global explanation engine
_explanation_engine: ExplanationEngine | None = None
_explanation_lock = __import__("threading").Lock()


def get_explanation_engine() -> ExplanationEngine:
    """Get the global explanation engine."""
    global _explanation_engine
    with _explanation_lock:
        if _explanation_engine is None:
            _explanation_engine = ExplanationEngine()
        return _explanation_engine


def reset_explanation_engine() -> None:
    """Reset the global explanation engine."""
    global _explanation_engine
    with _explanation_lock:
        _explanation_engine = None
