"""Confidence calculation models.

Provides pluggable confidence calculation algorithms.

Architecture only — no AI, no business logic.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Protocol

from .reasoning_types import ConfidenceLevel, ConfidenceScore, Evidence, Hypothesis

if TYPE_CHECKING:
    pass


# =============================================================================
# Confidence Calculator Protocol
# =============================================================================


class ConfidenceCalculator(Protocol):
    """Protocol for confidence calculation algorithms."""

    def calculate(
        self,
        hypothesis: Hypothesis,
        supporting_evidence: list[Evidence],
        contradicting_evidence: list[Evidence],
    ) -> ConfidenceScore:
        """Calculate confidence score for a hypothesis."""
        ...


# =============================================================================
# Default Calculator
# =============================================================================


class DefaultConfidenceCalculator:
    """Default confidence calculation using weighted evidence.

    Formula: P(H|E) = P(H) * (1 + sum(supporting) - sum(contradicting))
    """

    def calculate(
        self,
        hypothesis: Hypothesis,
        supporting_evidence: list[Evidence],
        contradicting_evidence: list[Evidence],
    ) -> ConfidenceScore:
        """Calculate confidence using weighted evidence."""
        reasons: list[str] = []
        supporting_factors: list[str] = []
        contradicting_factors: list[str] = []

        # Base probability
        prob = hypothesis.probability

        # Process supporting evidence
        supporting_weight = 0.0
        for ev in supporting_evidence:
            weight = ev.confidence * ev.weight
            supporting_weight += weight
            supporting_factors.append(f"{ev.evidence_id}: +{weight:.2f}")

        # Process contradicting evidence
        contradicting_weight = 0.0
        for ev in contradicting_evidence:
            weight = ev.confidence * ev.weight
            contradicting_weight += weight
            contradicting_factors.append(f"{ev.evidence_id}: -{weight:.2f}")

        # Calculate final probability
        # Bayesian-inspired: P(H|E) = P(H) * (1 + Ws - Wc)
        adjustment = supporting_weight - contradicting_weight
        final_prob = max(0.0, min(1.0, prob * (1 + adjustment)))

        # Determine reasons
        if supporting_evidence:
            reasons.append(f"Supported by {len(supporting_evidence)} evidence")
        if contradicting_evidence:
            reasons.append(f"Contradicted by {len(contradicting_evidence)} evidence")
        if abs(adjustment) > 0.5:
            reasons.append(f"Strong adjustment: {adjustment:+.2f}")

        # Determine level
        level = self._prob_to_level(final_prob)

        return ConfidenceScore(
            value=final_prob,
            level=level,
            reasons=tuple(reasons),
            supporting_factors=tuple(supporting_factors),
            contradicting_factors=tuple(contradicting_factors),
            algorithm="default_weighted",
        )

    @staticmethod
    def _prob_to_level(prob: float) -> ConfidenceLevel:
        """Convert probability to confidence level."""
        if prob >= 0.95:
            return ConfidenceLevel.CERTAIN
        elif prob >= 0.8:
            return ConfidenceLevel.VERY_HIGH
        elif prob >= 0.6:
            return ConfidenceLevel.HIGH
        elif prob >= 0.4:
            return ConfidenceLevel.MODERATE
        elif prob >= 0.2:
            return ConfidenceLevel.LOW
        elif prob >= 0.1:
            return ConfidenceLevel.VERY_LOW
        else:
            return ConfidenceLevel.NONE


# =============================================================================
# Bayesian Calculator
# =============================================================================


class BayesianConfidenceCalculator:
    """Bayesian-inspired confidence calculation.

    Uses Bayes' theorem: P(H|E) = P(E|H) * P(H) / P(E)
    """

    def calculate(
        self,
        hypothesis: Hypothesis,
        supporting_evidence: list[Evidence],
        contradicting_evidence: list[Evidence],
    ) -> ConfidenceScore:
        """Calculate confidence using Bayesian inference."""
        reasons: list[str] = []
        supporting_factors: list[str] = []
        contradicting_factors: list[str] = []

        # Prior probability
        prior = hypothesis.probability

        # Likelihood from supporting evidence
        for ev in supporting_evidence:
            # P(E|H) = evidence confidence
            likelihood = ev.confidence * ev.weight
            supporting_factors.append(f"{ev.evidence_id}: P(E|H)={likelihood:.2f}")

        # Likelihood from contradicting evidence
        for ev in contradicting_evidence:
            # P(E|not H) approximation
            likelihood = ev.confidence * ev.weight
            contradicting_factors.append(f"{ev.evidence_id}: P(E|not H)={likelihood:.2f}")

        # Calculate posterior (simplified)
        # P(H|E) = P(E|H) * P(H) / P(E)
        supporting_prod = 1.0
        for ev in supporting_evidence:
            supporting_prod *= (1 - ev.confidence * ev.weight)

        contradicting_prod = 1.0
        for ev in contradicting_evidence:
            contradicting_prod *= (1 - ev.confidence * ev.weight)

        # Posterior approximation
        posterior = prior * supporting_prod / (prior * supporting_prod + (1 - prior) * contradicting_prod)
        posterior = max(0.0, min(1.0, posterior))

        # Reasons
        reasons.append(f"Bayesian posterior: {posterior:.2f}")
        if supporting_evidence:
            reasons.append(f"Based on {len(supporting_evidence)} supporting, {len(contradicting_evidence)} contradicting")

        level = self._prob_to_level(posterior)

        return ConfidenceScore(
            value=posterior,
            level=level,
            reasons=tuple(reasons),
            supporting_factors=tuple(supporting_factors),
            contradicting_factors=tuple(contradicting_factors),
            algorithm="bayesian",
        )

    @staticmethod
    def _prob_to_level(prob: float) -> ConfidenceLevel:
        """Convert probability to confidence level."""
        if prob >= 0.95:
            return ConfidenceLevel.CERTAIN
        elif prob >= 0.8:
            return ConfidenceLevel.VERY_HIGH
        elif prob >= 0.6:
            return ConfidenceLevel.HIGH
        elif prob >= 0.4:
            return ConfidenceLevel.MODERATE
        elif prob >= 0.2:
            return ConfidenceLevel.LOW
        elif prob >= 0.1:
            return ConfidenceLevel.VERY_LOW
        else:
            return ConfidenceLevel.NONE


# =============================================================================
# Dempster-Shafer Calculator
# =============================================================================


class DempsterShaferCalculator:
    """Dempster-Shafer theory-based confidence calculation.

    Uses mass functions and Dempster's rule for combination.
    """

    def calculate(
        self,
        hypothesis: Hypothesis,
        supporting_evidence: list[Evidence],
        contradicting_evidence: list[Evidence],
    ) -> ConfidenceScore:
        """Calculate confidence using Dempster-Shafer theory."""
        reasons: list[str] = []
        supporting_factors: list[str] = []
        contradicting_factors: []

        # Mass for hypothesis
        m_h = 0.0
        for ev in supporting_evidence:
            mass = ev.confidence * ev.weight
            m_h += mass * (1 - m_h)  # Dempster's rule
            supporting_factors.append(f"{ev.evidence_id}: m(H)={mass:.2f}")

        # Mass against hypothesis
        m_not_h = 0.0
        for ev in contradicting_evidence:
            mass = ev.confidence * ev.weight
            m_not_h += mass * (1 - m_not_h)
            contradicting_factors.append(f"{ev.evidence_id}: m(~H)={mass:.2f}")

        # Belief function: Bel(H) = sum of masses for subsets
        bel_h = m_h

        # Plausibility: Pl(H) = 1 - m(~H)
        pl_h = 1 - m_not_h

        # Belief interval
        lower = bel_h
        upper = pl_h

        # Use midpoint as confidence
        final_prob = (lower + upper) / 2

        reasons.append(f"DS interval: [{lower:.2f}, {upper:.2f}]")
        if supporting_evidence:
            reasons.append(f"Combined {len(supporting_evidence)} supporting evidence")
        if contradicting_evidence:
            reasons.append(f"Combined {len(contradicting_evidence)} contradicting evidence")

        level = self._prob_to_level(final_prob)

        return ConfidenceScore(
            value=final_prob,
            level=level,
            reasons=tuple(reasons),
            supporting_factors=tuple(supporting_factors),
            contradicting_factors=tuple(contradicting_factors),
            algorithm="dempster_shafer",
        )

    @staticmethod
    def _prob_to_level(prob: float) -> ConfidenceLevel:
        """Convert probability to confidence level."""
        if prob >= 0.95:
            return ConfidenceLevel.CERTAIN
        elif prob >= 0.8:
            return ConfidenceLevel.VERY_HIGH
        elif prob >= 0.6:
            return ConfidenceLevel.HIGH
        elif prob >= 0.4:
            return ConfidenceLevel.MODERATE
        elif prob >= 0.2:
            return ConfidenceLevel.LOW
        elif prob >= 0.1:
            return ConfidenceLevel.VERY_LOW
        else:
            return ConfidenceLevel.NONE


# =============================================================================
# Calculator Factory
# =============================================================================


class ConfidenceCalculatorFactory:
    """Factory for creating confidence calculators."""

    _calculators: dict[str, type[ConfidenceCalculator]] = {
        "default": DefaultConfidenceCalculator,
        "bayesian": BayesianConfidenceCalculator,
        "dempster_shafer": DempsterShaferCalculator,
    }

    @classmethod
    def create(cls, algorithm: str = "default") -> ConfidenceCalculator:
        """Create a confidence calculator.

        Args:
            algorithm: The algorithm name.

        Returns:
            A confidence calculator instance.
        """
        calculator_cls = cls._calculators.get(algorithm, DefaultConfidenceCalculator)
        return calculator_cls()

    @classmethod
    def register(cls, name: str, calculator_cls: type[ConfidenceCalculator]) -> None:
        """Register a new confidence calculator.

        Args:
            name: The algorithm name.
            calculator_cls: The calculator class.
        """
        cls._calculators[name] = calculator_cls

    @classmethod
    def available_algorithms(cls) -> list[str]:
        """Get list of available algorithms."""
        return list(cls._calculators.keys())
