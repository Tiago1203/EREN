"""Strategy Selector for EREN Cognitive Decision Engine.

Selects the best strategy for achieving a goal.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from core.decision.types import (
    Goal,
    GoalAnalysis,
    DecisionStrategy,
    DecisionTask,
    StrategySelection,
    RiskLevel,
)

if TYPE_CHECKING:
    pass


class StrategySelector:
    """Selects the best decision strategy.

    The Strategy Selector does NOT:
    - Execute tasks
    - Query providers

    It ONLY:
    - Analyzes goal characteristics
    - Selects optimal strategy
    - Evaluates alternatives
    """

    def __init__(self):
        """Initialize strategy selector."""
        self._strategy_rules = self._load_strategy_rules()

    def select(
        self,
        goal: Goal,
        analysis: GoalAnalysis,
        tasks: list[DecisionTask],
    ) -> StrategySelection:
        """Select optimal strategy.

        Args:
            goal: Goal to achieve.
            analysis: Goal analysis.
            tasks: Decomposed tasks.

        Returns:
            Strategy selection.
        """
        # Analyze task characteristics
        has_dependencies = any(len(t.depends_on) > 0 for t in tasks)
        has_parallel_potential = self._has_parallel_potential(tasks)
        is_high_risk = self._is_high_risk(goal, analysis)

        # Score strategies
        scores = self._score_strategies(
            goal=goal,
            analysis=analysis,
            tasks=tasks,
            has_dependencies=has_dependencies,
            has_parallel_potential=has_parallel_potential,
            is_high_risk=is_high_risk,
        )

        # Select best
        best_strategy = max(scores, key=scores.get)
        alternatives = [s for s, _ in sorted(scores.items(), key=lambda x: x[1], reverse=True) if s != best_strategy][:2]

        # Generate reasoning
        reasoning = self._generate_reasoning(
            best_strategy,
            goal,
            analysis,
            has_dependencies,
            has_parallel_potential,
        )

        return StrategySelection(
            selected_strategy=best_strategy,
            alternatives=alternatives,
            reasoning=reasoning,
            confidence=scores[best_strategy],
            estimated_outcome={
                "parallel_tasks": sum(1 for t in tasks if not t.depends_on),
                "sequential_tasks": sum(1 for t in tasks if t.depends_on),
                "estimated_time_reduction": self._estimate_time_reduction(best_strategy, tasks),
            },
        )

    def _has_parallel_potential(self, tasks: list[DecisionTask]) -> bool:
        """Check if tasks have parallel execution potential."""
        if len(tasks) < 2:
            return False

        # Count tasks with no dependencies
        no_deps = sum(1 for t in tasks if not t.depends_on)
        return no_deps >= 2

    def _is_high_risk(self, goal: Goal, analysis: GoalAnalysis) -> bool:
        """Check if goal is high risk."""
        high_risk_keywords = [
            "surgery", "procedure", "treatment", "medication",
            "critical", "emergency", "urgent",
        ]

        text = (goal.description + " " + analysis.primary_objective).lower()

        return any(kw in text for kw in high_risk_keywords) or analysis.risk_tolerance == RiskLevel.HIGH

    def _score_strategies(
        self,
        goal: Goal,
        analysis: GoalAnalysis,
        tasks: list[DecisionTask],
        has_dependencies: bool,
        has_parallel_potential: bool,
        is_high_risk: bool,
    ) -> dict[DecisionStrategy, float]:
        """Score each strategy."""
        scores = {}

        # SEQUENTIAL: Best for linear workflows
        scores[DecisionStrategy.SEQUENTIAL] = 0.5
        if not has_parallel_potential:
            scores[DecisionStrategy.SEQUENTIAL] += 0.3
        if is_high_risk:
            scores[DecisionStrategy.SEQUENTIAL] += 0.2

        # PARALLEL: Best when tasks can run concurrently
        scores[DecisionStrategy.PARALLEL] = 0.3
        if has_parallel_potential:
            scores[DecisionStrategy.PARALLEL] += 0.4
        if not is_high_risk:
            scores[DecisionStrategy.PARALLEL] += 0.1

        # HYBRID: Default choice
        scores[DecisionStrategy.HYBRID] = 0.6
        if has_dependencies and has_parallel_potential:
            scores[DecisionStrategy.HYBRID] += 0.2

        # CONDITIONAL: Best for complex logic
        scores[DecisionStrategy.CONDITIONAL] = 0.4
        conditional_keywords = ["if", "when", "condition", "based on"]
        if any(kw in goal.description.lower() for kw in conditional_keywords):
            scores[DecisionStrategy.CONDITIONAL] += 0.3

        # EXPLORATORY: Best for research
        scores[DecisionStrategy.EXPLORATORY] = 0.3
        if goal.goal_type.value in ["research", "analysis"]:
            scores[DecisionStrategy.EXPLORATORY] += 0.4

        # CONSERVATIVE: Best for high risk
        scores[DecisionStrategy.CONSERVATIVE] = 0.3
        if is_high_risk:
            scores[DecisionStrategy.CONSERVATIVE] += 0.4
        if analysis.risk_tolerance == RiskLevel.LOW:
            scores[DecisionStrategy.CONSERVATIVE] += 0.2

        # AGGRESSIVE: Best for speed
        scores[DecisionStrategy.AGGRESSIVE] = 0.4
        if not is_high_risk:
            scores[DecisionStrategy.AGGRESSIVE] += 0.2
        urgent_keywords = ["quick", "fast", "urgent", "asap"]
        if any(kw in goal.description.lower() for kw in urgent_keywords):
            scores[DecisionStrategy.AGGRESSIVE] += 0.2

        return scores

    def _generate_reasoning(
        self,
        strategy: DecisionStrategy,
        goal: Goal,
        analysis: GoalAnalysis,
        has_dependencies: bool,
        has_parallel_potential: bool,
    ) -> str:
        """Generate reasoning for strategy selection."""
        reasons = []

        reasons.append(f"Selected {strategy.value} strategy for {goal.goal_type.value} goal.")

        if strategy == DecisionStrategy.SEQUENTIAL:
            reasons.append("Tasks require strict ordering.")
        elif strategy == DecisionStrategy.PARALLEL:
            reasons.append("Independent tasks can execute concurrently.")
        elif strategy == DecisionStrategy.HYBRID:
            reasons.append("Combining sequential and parallel execution for efficiency.")
        elif strategy == DecisionStrategy.CONSERVATIVE:
            reasons.append("Conservative approach due to risk tolerance.")
        elif strategy == DecisionStrategy.AGGRESSIVE:
            reasons.append("Optimizing for speed over caution.")

        return " ".join(reasons)

    def _estimate_time_reduction(
        self,
        strategy: DecisionStrategy,
        tasks: list[DecisionTask],
    ) -> float:
        """Estimate time reduction percentage."""
        if strategy == DecisionStrategy.PARALLEL:
            no_deps = sum(1 for t in tasks if not t.depends_on)
            if no_deps > 1:
                return 0.3  # 30% reduction
        elif strategy == DecisionStrategy.HYBRID:
            return 0.2  # 20% reduction

        return 0.0

    def _load_strategy_rules(self) -> dict:
        """Load strategy selection rules."""
        return {}
