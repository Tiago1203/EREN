"""Reflection Engine for EREN Cognitive Reasoning Platform.

Handles self-evaluation, error detection, and revision.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from core.PHASE_2.reasoning.reasoning_types import (
    Evidence,
    Hypothesis,
)

if TYPE_CHECKING:
    pass


class ReflectionEngine:
    """Performs self-reflection on reasoning.

    The Reflection Engine does NOT:
    - Collect evidence
    - Make decisions
    - Generate hypotheses

    It ONLY:
    - Performs self-evaluation
    - Detects errors
    - Revises conclusions
    - Performs second passes
    """

    def __init__(self):
        """Initialize reflection engine."""
        self._reflection_count: int = 0
        self._errors_detected: list[dict] = []
        self._revisions: list[dict] = []

    def reflect(
        self,
        hypothesis: Hypothesis,
        evidence: list[Evidence],
        context: dict | None = None,
    ) -> dict:
        """Perform reflection on hypothesis.

        Args:
            hypothesis: Hypothesis to reflect on.
            evidence: Related evidence.
            context: Optional context.

        Returns:
            Reflection result.
        """
        self._reflection_count += 1

        issues = self._detect_issues(hypothesis, evidence)
        suggestions = self._generate_suggestions(issues, hypothesis, evidence)

        return {
            "reflection_id": f"ref_{self._reflection_count}",
            "hypothesis_id": hypothesis.hypothesis_id,
            "issues_detected": issues,
            "suggestions": suggestions,
            "confidence_impact": self._calculate_confidence_impact(issues),
        }

    def _detect_issues(
        self,
        hypothesis: Hypothesis,
        evidence: list[Evidence],
    ) -> list[dict]:
        """Detect issues with hypothesis.

        Args:
            hypothesis: Hypothesis to check.
            evidence: Related evidence.

        Returns:
            List of detected issues.
        """
        issues = []

        # Check evidence sufficiency
        if len(evidence) < 2:
            issues.append({
                "type": "insufficient_evidence",
                "severity": "high",
                "message": "Insufficient evidence for reliable conclusion",
            })

        # Check confidence
        if hypothesis.confidence_score < 0.5:
            issues.append({
                "type": "low_confidence",
                "severity": "medium",
                "message": "Confidence below threshold",
            })

        # Check conflicting evidence
        supporting = sum(1 for e in evidence if e.supports())
        contradicting = sum(1 for e in evidence if e.contradicts())

        if contradicting > supporting:
            issues.append({
                "type": "conflicting_evidence",
                "severity": "high",
                "message": "More contradicting than supporting evidence",
            })

        # Check temporal consistency
        old_evidence = [e for e in evidence if e.is_temporary]
        if old_evidence:
            issues.append({
                "type": "temporary_assumptions",
                "severity": "low",
                "message": "Contains temporary assumptions",
            })

        return issues

    def _generate_suggestions(
        self,
        issues: list[dict],
        hypothesis: Hypothesis,
        evidence: list[Evidence],
    ) -> list[str]:
        """Generate suggestions for improvement.

        Args:
            issues: Detected issues.
            hypothesis: Related hypothesis.
            evidence: Related evidence.

        Returns:
            List of suggestions.
        """
        suggestions = []

        for issue in issues:
            if issue["type"] == "insufficient_evidence":
                suggestions.append("Collect more evidence before concluding")
            elif issue["type"] == "low_confidence":
                suggestions.append("Seek additional supporting evidence")
            elif issue["type"] == "conflicting_evidence":
                suggestions.append("Investigate source of conflicting evidence")
            elif issue["type"] == "temporary_assumptions":
                suggestions.append("Verify temporary assumptions")

        return suggestions

    def _calculate_confidence_impact(self, issues: list[dict]) -> float:
        """Calculate confidence impact.

        Args:
            issues: Detected issues.

        Returns:
            Confidence adjustment (-1.0 to 1.0).
        """
        impact = 0.0

        for issue in issues:
            if issue["severity"] == "high":
                impact -= 0.2
            elif issue["severity"] == "medium":
                impact -= 0.1
            elif issue["severity"] == "low":
                impact -= 0.05

        return impact

    def second_pass(
        self,
        conclusions: list[dict],
        context: dict | None = None,
    ) -> list[dict]:
        """Perform second pass analysis.

        Args:
            conclusions: Initial conclusions.
            context: Optional context.

        Returns:
            Revised conclusions.
        """
        revised = []

        for conclusion in conclusions:
            issues = self._detect_second_pass_issues(conclusion)
            if issues:
                revised_conclusion = self._revise_conclusion(conclusion, issues)
                self._revisions.append({
                    "original": conclusion,
                    "revised": revised_conclusion,
                    "issues": issues,
                })
                revised.append(revised_conclusion)
            else:
                revised.append(conclusion)

        return revised

    def _detect_second_pass_issues(self, conclusion: dict) -> list[dict]:
        """Detect issues in second pass.

        Args:
            conclusion: Conclusion to check.

        Returns:
            List of issues.
        """
        issues = []

        if conclusion.get("confidence", 1.0) < 0.3:
            issues.append({
                "type": "very_low_confidence",
                "severity": "high",
            })

        return issues

    def _revise_conclusion(
        self,
        conclusion: dict,
        issues: list[dict],
    ) -> dict:
        """Revise a conclusion.

        Args:
            conclusion: Conclusion to revise.
            issues: Issues to address.

        Returns:
            Revised conclusion.
        """
        revised = conclusion.copy()
        revised["revised"] = True
        revised["revisions_applied"] = len(issues)
        return revised

    def detect_error(self, data: dict) -> list[dict]:
        """Detect errors in data.

        Args:
            data: Data to check.

        Returns:
            List of detected errors.
        """
        errors = []

        if "confidence" in data and data["confidence"] > 1.0:
            errors.append({"type": "confidence_overflow", "data": data})

        if "probability" in data and not 0.0 <= data["probability"] <= 1.0:
            errors.append({"type": "probability_out_of_range", "data": data})

        return errors


# Global reflection engine
_reflection_engine: ReflectionEngine | None = None
_reflection_lock = __import__("threading").Lock()


def get_reflection_engine() -> ReflectionEngine:
    """Get the global reflection engine."""
    global _reflection_engine
    with _reflection_lock:
        if _reflection_engine is None:
            _reflection_engine = ReflectionEngine()
        return _reflection_engine


def reset_reflection_engine() -> None:
    """Reset the global reflection engine."""
    global _reflection_engine
    with _reflection_lock:
        _reflection_engine = None
