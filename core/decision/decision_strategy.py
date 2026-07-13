"""Decision strategies for the Cognitive Decision Engine.

Provides different strategies for decision making.

Architecture only -- no AI, no business logic.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from .decision_types import DecisionCandidate, DecisionContext, DecisionStrategyType, RiskLevel

if TYPE_CHECKING:
    pass


# =============================================================================
# Base Strategy
# =============================================================================


class DecisionStrategy(ABC):
    """Base class for decision strategies."""

    @abstractmethod
    def calculate_score(
        self,
        candidate: DecisionCandidate,
        risk_score: float,
        priority_score: int,
        context: DecisionContext,
    ) -> float:
        """Calculate decision score.

        Args:
            candidate: The candidate.
            risk_score: Risk score (0.0-1.0).
            priority_score: Priority score (0-100).
            context: Decision context.

        Returns:
            Combined score (higher = better).
        """
        ...

    @abstractmethod
    def rank(
        self,
        scored: list[tuple[float, DecisionCandidate]],
    ) -> list[tuple[float, DecisionCandidate]]:
        """Rank scored candidates.

        Args:
            scored: List of (score, candidate) tuples.

        Returns:
            Sorted list of (score, candidate) tuples.
        """
        ...

    @abstractmethod
    def name(self) -> str:
        """Get strategy name."""
        ...

    @abstractmethod
    def strategy_type(self) -> DecisionStrategyType:
        """Get strategy type."""
        ...


# =============================================================================
# Conservative Strategy
# =============================================================================


class ConservativeStrategy(DecisionStrategy):
    """Conservative strategy - minimizes risk above all.

    Prefer decisions with:
    - Low risk
    - High confidence
    - Human approval for uncertain decisions
    """

    def calculate_score(
        self,
        candidate: DecisionCandidate,
        risk_score: float,
        priority_score: int,
        context: DecisionContext,
    ) -> float:
        """Calculate score favoring safety."""
        # Risk is dominant factor (inverted - lower risk = higher score)
        risk_factor = (1 - risk_score) * 2

        # Confidence bonus
        confidence_factor = candidate.confidence

        # Priority bonus (small)
        priority_factor = priority_score / 100

        # Safety requirement override
        if candidate.risk_level in (RiskLevel.HIGH, RiskLevel.CRITICAL):
            # Require very high confidence
            if candidate.confidence < 0.9:
                return 0.0

        return risk_factor + confidence_factor + priority_factor

    def rank(
        self,
        scored: list[tuple[float, DecisionCandidate]],
    ) -> list[tuple[float, DecisionCandidate]]:
        """Rank by safety first."""
        # Sort descending by score
        return sorted(scored, key=lambda x: x[0], reverse=True)

    def name(self) -> str:
        return "Conservative"

    def strategy_type(self) -> DecisionStrategyType:
        return DecisionStrategyType.CONSERVATIVE


# =============================================================================
# Balanced Strategy
# =============================================================================


class BalancedStrategy(DecisionStrategy):
    """Balanced strategy - balances risk and benefit.

    Consider:
    - Risk (40%)
    - Confidence (30%)
    - Priority (30%)
    """

    def calculate_score(
        self,
        candidate: DecisionCandidate,
        risk_score: float,
        priority_score: int,
        context: DecisionContext,
    ) -> float:
        """Calculate balanced score."""
        # Risk factor (40%) - inverted
        risk_factor = (1 - risk_score) * 0.4

        # Confidence factor (30%)
        confidence_factor = candidate.confidence * 0.3

        # Priority factor (30%)
        priority_factor = (priority_score / 100) * 0.3

        return risk_factor + confidence_factor + priority_factor

    def rank(
        self,
        scored: list[tuple[float, DecisionCandidate]],
    ) -> list[tuple[float, DecisionCandidate]]:
        """Rank by balanced score."""
        return sorted(scored, key=lambda x: x[0], reverse=True)

    def name(self) -> str:
        return "Balanced"

    def strategy_type(self) -> DecisionStrategyType:
        return DecisionStrategyType.BALANCED


# =============================================================================
# Speed Strategy
# =============================================================================


class SpeedStrategy(DecisionStrategy):
    """Speed strategy - prioritizes quick decisions.

    Consider:
    - Execution time (if available)
    - Low complexity
    - Existing evidence
    """

    def calculate_score(
        self,
        candidate: DecisionCandidate,
        risk_score: float,
        priority_score: int,
        context: DecisionContext,
    ) -> float:
        """Calculate score favoring speed."""
        # Base score from priority
        base = priority_score / 100

        # Evidence bonus
        evidence_bonus = 0.0
        if candidate.based_on_evidence:
            evidence_bonus = min(0.3, len(candidate.based_on_evidence) * 0.05)

        # Speed bonus (faster = better)
        speed_bonus = 0.0
        if candidate.estimated_duration_ms > 0:
            # Normalize: faster = higher bonus
            speed_bonus = max(0, 1 - candidate.estimated_duration_ms / 60000) * 0.3

        # Risk penalty (moderate)
        risk_penalty = risk_score * 0.2

        return base + evidence_bonus + speed_bonus - risk_penalty

    def rank(
        self,
        scored: list[tuple[float, DecisionCandidate]],
    ) -> list[tuple[float, DecisionCandidate]]:
        """Rank by speed score."""
        return sorted(scored, key=lambda x: x[0], reverse=True)

    def name(self) -> str:
        return "Speed"

    def strategy_type(self) -> DecisionStrategyType:
        return DecisionStrategyType.SPEED


# =============================================================================
# Confidence-Based Strategy
# =============================================================================


class ConfidenceBasedStrategy(DecisionStrategy):
    """Confidence-based strategy - follows the data.

    Consider:
    - Hypothesis confidence
    - Evidence strength
    - Risk-adjusted returns
    """

    def calculate_score(
        self,
        candidate: DecisionCandidate,
        risk_score: float,
        priority_score: int,
        context: DecisionContext,
    ) -> float:
        """Calculate score based on confidence."""
        # Confidence is dominant
        confidence_factor = candidate.confidence * 2

        # Evidence bonus
        evidence_bonus = 0.0
        if candidate.based_on_evidence:
            evidence_bonus = len(candidate.based_on_evidence) * 0.05

        # Risk penalty (smaller than other strategies)
        risk_penalty = risk_score * 0.1

        return confidence_factor + evidence_bonus - risk_penalty

    def rank(
        self,
        scored: list[tuple[float, DecisionCandidate]],
    ) -> list[tuple[float, DecisionCandidate]]:
        """Rank by confidence."""
        return sorted(scored, key=lambda x: x[0], reverse=True)

    def name(self) -> str:
        return "ConfidenceBased"

    def strategy_type(self) -> DecisionStrategyType:
        return DecisionStrategyType.CONFIDENCE_BASED


# =============================================================================
# Strategy Factory
# =============================================================================


class DecisionStrategyFactory:
    """Factory for creating decision strategies."""

    _strategies: dict[DecisionStrategyType, type[DecisionStrategy]] = {
        DecisionStrategyType.CONSERVATIVE: ConservativeStrategy,
        DecisionStrategyType.SAFETY_FIRST: ConservativeStrategy,
        DecisionStrategyType.BALANCED: BalancedStrategy,
        DecisionStrategyType.SPEED: SpeedStrategy,
        DecisionStrategyType.CONFIDENCE_BASED: ConfidenceBasedStrategy,
        DecisionStrategyType.EFFICIENCY: BalancedStrategy,
        DecisionStrategyType.HUMAN_IN_LOOP: BalancedStrategy,
        DecisionStrategyType.FULLY_AUTOMATED: SpeedStrategy,
    }

    @classmethod
    def create(cls, strategy_type: DecisionStrategyType) -> DecisionStrategy:
        """Create a strategy by type."""
        strategy_cls = cls._strategies.get(strategy_type, BalancedStrategy)
        return strategy_cls()

    @classmethod
    def register(cls, strategy_type: DecisionStrategyType, strategy_cls: type[DecisionStrategy]) -> None:
        """Register a new strategy."""
        cls._strategies[strategy_type] = strategy_cls
