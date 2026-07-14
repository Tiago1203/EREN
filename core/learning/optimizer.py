"""Strategy Optimizer for EREN Cognitive Learning Platform.

Optimizes strategies based on learning.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from core.learning.types import Experience, Feedback

if TYPE_CHECKING:
    pass


class StrategyOptimizer:
    """Optimizes strategies based on learning.

    The Strategy Optimizer does NOT:
    - Record experiences
    - Discover patterns
    - Consolidate knowledge

    It ONLY:
    - Optimizes strategies
    - Adapts parameters
    - Improves performance
    """

    def __init__(self):
        """Initialize strategy optimizer."""
        self._optimizations: dict[str, dict] = {}

    def optimize(
        self,
        strategy_id: str,
        experiences: list[Experience],
        feedback: list[Feedback],
    ) -> dict:
        """Optimize a strategy.

        Args:
            strategy_id: Strategy ID.
            experiences: Experiences to learn from.
            feedback: Feedback to consider.

        Returns:
            Optimization recommendations.
        """
        # Calculate outcome scores
        outcome_scores = self._calculate_outcome_scores(experiences)

        # Calculate feedback impact
        feedback_impact = self._calculate_feedback_impact(feedback)

        # Generate recommendations
        recommendations = self._generate_recommendations(
            strategy_id,
            outcome_scores,
            feedback_impact,
        )

        self._optimizations[strategy_id] = {
            "outcomes": outcome_scores,
            "feedback_impact": feedback_impact,
            "recommendations": recommendations,
        }

        return recommendations

    def _calculate_outcome_scores(self, experiences: list[Experience]) -> dict:
        """Calculate outcome scores."""
        scores = {
            "success": 0.0,
            "failure": 0.0,
            "partial": 0.0,
            "avg_confidence": 0.0,
        }

        if not experiences:
            return scores

        outcome_counts = {"success": 0, "failure": 0, "partial": 0}
        for exp in experiences:
            if exp.outcome in outcome_counts:
                outcome_counts[exp.outcome] += 1

        total = len(experiences)
        scores["success"] = outcome_counts["success"] / total
        scores["failure"] = outcome_counts["failure"] / total
        scores["partial"] = outcome_counts["partial"] / total
        scores["avg_confidence"] = sum(e.confidence for e in experiences) / total

        return scores

    def _calculate_feedback_impact(self, feedback: list[Feedback]) -> dict:
        """Calculate feedback impact."""
        if not feedback:
            return {"positive": 0.0, "negative": 0.0, "neutral": 0.0, "avg_rating": 0.5}

        positive = sum(1 for f in feedback if f.feedback_type.value == "positive")
        negative = sum(1 for f in feedback if f.feedback_type.value == "negative")
        neutral = sum(1 for f in feedback if f.feedback_type.value == "neutral")

        total = len(feedback)

        return {
            "positive": positive / total,
            "negative": negative / total,
            "neutral": neutral / total,
            "avg_rating": sum(f.rating for f in feedback) / total,
        }

    def _generate_recommendations(
        self,
        strategy_id: str,
        outcome_scores: dict,
        feedback_impact: dict,
    ) -> list[dict]:
        """Generate optimization recommendations."""
        recommendations = []

        # Success rate recommendation
        if outcome_scores["success"] < 0.5:
            recommendations.append({
                "type": "success_rate",
                "priority": "high",
                "message": "Success rate below 50%. Consider reviewing strategy.",
                "action": "review_strategy",
            })

        # Failure rate recommendation
        if outcome_scores["failure"] > 0.3:
            recommendations.append({
                "type": "failure_rate",
                "priority": "high",
                "message": "High failure rate. Analyze failure patterns.",
                "action": "analyze_failures",
            })

        # Confidence recommendation
        if outcome_scores["avg_confidence"] < 0.4:
            recommendations.append({
                "type": "confidence",
                "priority": "medium",
                "message": "Low average confidence. Improve evidence gathering.",
                "action": "improve_evidence",
            })

        # Feedback recommendation
        if feedback_impact["negative"] > 0.3:
            recommendations.append({
                "type": "feedback",
                "priority": "high",
                "message": "High negative feedback. Review decision criteria.",
                "action": "review_criteria",
            })

        return recommendations

    def get_optimization(self, strategy_id: str) -> dict | None:
        """Get optimization data for strategy."""
        return self._optimizations.get(strategy_id)


# Global strategy optimizer
_strategy_optimizer: StrategyOptimizer | None = None
_optimizer_lock = __import__("threading").Lock()


def get_strategy_optimizer() -> StrategyOptimizer:
    """Get the global strategy optimizer."""
    global _strategy_optimizer
    with _optimizer_lock:
        if _strategy_optimizer is None:
            _strategy_optimizer = StrategyOptimizer()
        return _strategy_optimizer


def reset_strategy_optimizer() -> None:
    """Reset the global strategy optimizer."""
    global _strategy_optimizer
    with _optimizer_lock:
        _strategy_optimizer = None
