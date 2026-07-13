"""Decision evaluators for the Cognitive Decision Engine.

Provides evaluation components for risk, priority, and decision scoring.

Architecture only -- no AI, no business logic.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .decision_metrics import DecisionMetricsCollector
from .decision_strategy import DecisionStrategy
from .decision_types import (
    DecisionCandidate,
    DecisionContext,
    DecisionPriority,
    DecisionStrategyType,
    RiskLevel,
)

if TYPE_CHECKING:
    pass


# =============================================================================
# Risk Evaluator
# =============================================================================


class RiskEvaluatorComponent:
    """Evaluates risk of decision candidates."""

    def evaluate(
        self,
        candidate: DecisionCandidate,
        context: DecisionContext,
    ) -> float:
        """Evaluate risk score for a candidate.

        Args:
            candidate: The candidate to evaluate.
            context: Decision context.

        Returns:
            Risk score between 0.0 (no risk) and 1.0 (critical risk).
        """
        # Base risk from candidate risk level
        risk_scores = {
            RiskLevel.MINIMAL: 0.1,
            RiskLevel.LOW: 0.25,
            RiskLevel.MEDIUM: 0.5,
            RiskLevel.HIGH: 0.75,
            RiskLevel.CRITICAL: 1.0,
        }
        base_risk = risk_scores.get(candidate.risk_level, 0.5)

        # Adjust based on confidence (lower confidence = higher risk)
        confidence_adjustment = (1 - candidate.confidence) * 0.2

        # Safety requirements increase risk
        safety_adjustment = 0.0
        if candidate.metadata.get("affects_patient_safety"):
            safety_adjustment = 0.3
        if candidate.metadata.get("requires_invasive_action"):
            safety_adjustment += 0.2

        # Calculate final risk
        final_risk = min(1.0, base_risk + confidence_adjustment + safety_adjustment)

        return final_risk


# =============================================================================
# Priority Evaluator
# =============================================================================


class PriorityEvaluatorComponent:
    """Evaluates priority of decision candidates."""

    PRIORITY_SCORES = {
        DecisionPriority.CRITICAL: 100,
        DecisionPriority.HIGH: 75,
        DecisionPriority.MEDIUM: 50,
        DecisionPriority.LOW: 25,
    }

    def evaluate(
        self,
        candidate: DecisionCandidate,
        context: DecisionContext,
    ) -> int:
        """Evaluate priority score for a candidate.

        Args:
            candidate: The candidate to evaluate.
            context: Decision context.

        Returns:
            Priority score (higher = more important).
        """
        base_priority = self.PRIORITY_SCORES.get(candidate.priority, 50)

        # Adjust based on confidence
        confidence_bonus = int(candidate.confidence * 20)

        # Adjust based on hypothesis confidence
        hypothesis_bonus = 0
        if candidate.based_on_hypothesis:
            if context.best_hypothesis_id == candidate.based_on_hypothesis:
                hypothesis_bonus = 20

        # Time constraints
        time_bonus = 0
        if context.time_constraints.get("urgent"):
            time_bonus = 15

        return base_priority + confidence_bonus + hypothesis_bonus + time_bonus


# =============================================================================
# Decision Evaluator
# =============================================================================


class DecisionEvaluatorComponent:
    """Evaluates and ranks decision candidates."""

    def __init__(self) -> None:
        """Initialize the evaluator."""
        self._risk_evaluator = RiskEvaluatorComponent()
        self._priority_evaluator = PriorityEvaluatorComponent()

    def evaluate(
        self,
        candidates: list[DecisionCandidate],
        context: DecisionContext,
        strategy: DecisionStrategy,
    ) -> list[DecisionCandidate]:
        """Evaluate and rank candidates.

        Args:
            candidates: Candidates to evaluate.
            context: Decision context.
            strategy: Decision strategy to use.

        Returns:
            Evaluated candidates ranked by score.
        """
        if not candidates:
            return []

        evaluated = []

        for candidate in candidates:
            # Calculate risk score
            risk_score = self._risk_evaluator.evaluate(candidate, context)

            # Calculate priority score
            priority_score = self._priority_evaluator.evaluate(candidate, context)

            # Calculate combined score using strategy
            score = strategy.calculate_score(
                candidate=candidate,
                risk_score=risk_score,
                priority_score=priority_score,
                context=context,
            )

            # Create evaluated candidate (immutable)
            from dataclasses import replace
            from .decision_types import DECISION_RISK_MAP

            evaluated_candidate = replace(
                candidate,
                risk_score=risk_score,
            )

            evaluated.append((score, evaluated_candidate))

        # Sort by score (strategy-dependent)
        ranked = strategy.rank(evaluated)

        return [c for _, c in ranked]


# =============================================================================
# Action Selector
# =============================================================================


class ActionSelectorComponent:
    """Selects the best action from candidates."""

    def __init__(self) -> None:
        """Initialize the selector."""
        self._evaluator = DecisionEvaluatorComponent()

    def select(
        self,
        candidates: list[DecisionCandidate],
        context: DecisionContext,
        strategy: DecisionStrategy,
    ) -> DecisionCandidate | None:
        """Select the best candidate.

        Args:
            candidates: Candidates to select from.
            context: Decision context.
            strategy: Decision strategy.

        Returns:
            The best candidate or None.
        """
        if not candidates:
            return None

        evaluated = self._evaluator.evaluate(candidates, context, strategy)

        if not evaluated:
            return None

        # Return best (first after ranking)
        return evaluated[0]
