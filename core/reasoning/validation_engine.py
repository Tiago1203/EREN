"""Validation Engine for EREN Cognitive Reasoning Platform.

Verifies decisions, contrasts with rules and guidelines.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from core.reasoning.reasoning_types import (
    Decision,
    Evidence,
    Hypothesis,
)

if TYPE_CHECKING:
    pass


class ValidationEngine:
    """Validates decisions and reasoning.

    The Validation Engine does NOT:
    - Collect evidence
    - Make decisions
    - Generate explanations

    It ONLY:
    - Verifies decisions
    - Contrasts with rules
    - Contrasts with guidelines
    - Detects inconsistencies
    """

    def __init__(self):
        """Initialize validation engine."""
        self._rules: list[Callable] = []
        self._guidelines: list[Callable] = []
        self._validation_count: int = 0

    def add_rule(self, rule: Callable) -> None:
        """Add a validation rule.

        Args:
            rule: Rule function.
        """
        self._rules.append(rule)

    def add_guideline(self, guideline: Callable) -> None:
        """Add a guideline.

        Args:
            guideline: Guideline function.
        """
        self._guidelines.append(guideline)

    def validate_decision(
        self,
        decision: Decision,
        hypothesis: Hypothesis,
        evidence: list[Evidence],
    ) -> dict:
        """Validate a decision.

        Args:
            decision: Decision to validate.
            hypothesis: Related hypothesis.
            evidence: Related evidence.

        Returns:
            Validation result.
        """
        self._validation_count += 1

        issues = []

        # Check confidence threshold
        if decision.confidence.value < 0.5:
            issues.append({
                "type": "low_confidence",
                "severity": "high",
                "message": "Confidence below validation threshold",
            })

        # Check evidence sufficiency
        if len(evidence) < 2:
            issues.append({
                "type": "insufficient_evidence",
                "severity": "medium",
                "message": "Insufficient evidence for validation",
            })

        # Apply rules
        for rule in self._rules:
            try:
                result = rule(decision, hypothesis, evidence)
                if result:
                    issues.append(result)
            except Exception:
                pass

        # Apply guidelines
        guideline_violations = self._check_guidelines(decision, hypothesis)

        return {
            "validation_id": f"val_{self._validation_count}",
            "decision_id": decision.decision_id,
            "is_valid": len(issues) == 0 and len(guideline_violations) == 0,
            "issues": issues,
            "guideline_violations": guideline_violations,
        }

    def _check_guidelines(
        self,
        decision: Decision,
        hypothesis: Hypothesis,
    ) -> list[dict]:
        """Check guideline violations.

        Args:
            decision: Decision to check.
            hypothesis: Related hypothesis.

        Returns:
            List of violations.
        """
        violations = []

        for guideline in self._guidelines:
            try:
                result = guideline(decision, hypothesis)
                if result:
                    violations.append(result)
            except Exception:
                pass

        return violations

    def detect_inconsistencies(
        self,
        hypotheses: list[Hypothesis],
        evidence: list[Evidence],
    ) -> list[dict]:
        """Detect inconsistencies.

        Args:
            hypotheses: Hypotheses to check.
            evidence: Evidence to check.

        Returns:
            List of inconsistencies.
        """
        inconsistencies = []

        # Check for contradicting hypotheses
        for i, h1 in enumerate(hypotheses):
            for h2 in hypotheses[i + 1:]:
                if self._contradict_each_other(h1, h2):
                    inconsistencies.append({
                        "type": "contradicting_hypotheses",
                        "hypothesis_1": h1.hypothesis_id,
                        "hypothesis_2": h2.hypothesis_id,
                    })

        # Check evidence alignment
        for h in hypotheses:
            h_evidence = [e for e in evidence if h.hypothesis_id in e.related_hypotheses]
            supporting = sum(1 for e in h_evidence if e.supports())
            contradicting = sum(1 for e in h_evidence if e.contradicts())

            if contradicting > supporting * 2:
                inconsistencies.append({
                    "type": "misaligned_evidence",
                    "hypothesis": h.hypothesis_id,
                    "supporting": supporting,
                    "contradicting": contradicting,
                })

        return inconsistencies

    def _contradict_each_other(self, h1: Hypothesis, h1_ref: Hypothesis) -> bool:
        """Check if two hypotheses contradict each other.

        Args:
            h1: First hypothesis.
            h1_ref: Second hypothesis.

        Returns:
            True if contradictions.
        """
        # Simple heuristic based on probability
        if h1.probability > 0.7 and h1_ref.probability < 0.3:
            return True
        if h1_ref.probability > 0.7 and h1.probability < 0.3:
            return True
        return False

    def verify_evidence_quality(
        self,
        evidence: list[Evidence],
        min_confidence: float = 0.3,
    ) -> list[dict]:
        """Verify evidence quality.

        Args:
            evidence: Evidence to verify.
            min_confidence: Minimum confidence threshold.

        Returns:
            List of quality issues.
        """
        issues = []

        for e in evidence:
            if e.confidence < min_confidence:
                issues.append({
                    "evidence_id": e.evidence_id,
                    "issue": "low_confidence",
                    "confidence": e.confidence,
                })

            if e.is_temporary and not e.is_verified:
                issues.append({
                    "evidence_id": e.evidence_id,
                    "issue": "unverified_temporary",
                })

        return issues


# Global validation engine
_validation_engine: ValidationEngine | None = None
_validation_lock = __import__("threading").Lock()


def get_validation_engine() -> ValidationEngine:
    """Get the global validation engine."""
    global _validation_engine
    with _validation_lock:
        if _validation_engine is None:
            _validation_engine = ValidationEngine()
        return _validation_engine


def reset_validation_engine() -> None:
    """Reset the global validation engine."""
    global _validation_engine
    with _validation_lock:
        _validation_engine = None
