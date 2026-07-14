"""Cognitive Learning Platform (CLP) for EREN OS.

Main platform for continuous learning.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from core.learning.types import (
    Experience,
    Feedback,
    Pattern,
    Knowledge,
    LearningType,
    LearningStatus,
    LearningMetrics,
    FeedbackType,
)
from core.learning.experience import ExperienceCollector, get_experience_collector
from core.learning.feedback import FeedbackAnalyzer, get_feedback_analyzer
from core.learning.patterns import PatternDiscovery, get_pattern_discovery
from core.learning.consolidation import KnowledgeConsolidator, get_knowledge_consolidator
from core.learning.optimizer import StrategyOptimizer, get_strategy_optimizer

if TYPE_CHECKING:
    pass


class CognitiveLearningPlatform:
    """Cognitive Learning Platform.

    Philosophy:
        Reasoning decides.
        Learning improves.

    The Learning Platform does NOT:
    - Make decisions
    - Generate explanations
    - Execute actions

    It ONLY:
    - Registers experiences
    - Evaluates outcomes
    - Analyzes errors
    - Detects patterns
    - Consolidates knowledge
    - Updates strategies
    - Improves future decisions
    - Optimizes agents
    """

    def __init__(self):
        """Initialize learning platform."""
        self._experience_collector = get_experience_collector()
        self._feedback_analyzer = get_feedback_analyzer()
        self._pattern_discovery = get_pattern_discovery()
        self._knowledge_consolidator = get_knowledge_consolidator()
        self._strategy_optimizer = get_strategy_optimizer()

        self._metrics = LearningMetrics()

    # ========================================================================
    # Experience
    # ========================================================================

    def record_experience(
        self,
        session_id: str,
        context: dict,
        action: str,
        result: Any,
        outcome: str,
        confidence: float = 0.5,
        tags: list[str] | None = None,
    ) -> Experience:
        """Record an experience.

        Args:
            session_id: Session ID.
            context: Context data.
            action: Action taken.
            result: Result of action.
            outcome: Outcome.
            confidence: Confidence.
            tags: Optional tags.

        Returns:
            Recorded experience.
        """
        experience = self._experience_collector.record(
            session_id=session_id,
            context=context,
            action=action,
            result=result,
            outcome=outcome,
            confidence=confidence,
            tags=tags,
        )

        self._metrics.experiences_recorded += 1

        return experience

    def get_experiences(self, session_id: str | None = None) -> list[Experience]:
        """Get experiences.

        Args:
            session_id: Optional session ID filter.

        Returns:
            List of experiences.
        """
        if session_id:
            return self._experience_collector.get_by_session(session_id)
        return self._experience_collector.get_all()

    # ========================================================================
    # Feedback
    # ========================================================================

    def add_feedback(
        self,
        experience_id: str,
        feedback_type: FeedbackType,
        content: str,
        rating: float = 0.5,
        source: str = "user",
    ) -> Feedback:
        """Add feedback.

        Args:
            experience_id: Related experience ID.
            feedback_type: Type of feedback.
            content: Feedback content.
            rating: Rating.
            source: Source.

        Returns:
            Added feedback.
        """
        feedback = self._feedback_analyzer.add(
            experience_id=experience_id,
            feedback_type=feedback_type,
            content=content,
            rating=rating,
            source=source,
        )

        self._metrics.feedback_received += 1

        return feedback

    # ========================================================================
    # Patterns
    # ========================================================================

    def discover_patterns(
        self,
        session_id: str | None = None,
        min_frequency: float = 0.1,
    ) -> list[Pattern]:
        """Discover patterns from experiences.

        Args:
            session_id: Optional session filter.
            min_frequency: Minimum frequency.

        Returns:
            Discovered patterns.
        """
        experiences = self.get_experiences(session_id)

        patterns = self._pattern_discovery.discover(
            experiences=experiences,
            min_frequency=min_frequency,
        )

        self._metrics.patterns_discovered = len(patterns)

        return patterns

    # ========================================================================
    # Knowledge
    # ========================================================================

    def consolidate_knowledge(
        self,
        session_id: str | None = None,
    ) -> list[Knowledge]:
        """Consolidate patterns into knowledge.

        Args:
            session_id: Optional session filter.

        Returns:
            Consolidated knowledge.
        """
        patterns = self.discover_patterns(session_id)
        experiences = self.get_experiences(session_id)

        knowledge = self._knowledge_consolidator.consolidate(
            patterns=patterns,
            experiences=experiences,
        )

        self._metrics.knowledge_consolidated = len(knowledge)

        return knowledge

    def get_knowledge(self, knowledge_type: str | None = None) -> list[Knowledge]:
        """Get consolidated knowledge.

        Args:
            knowledge_type: Optional type filter.

        Returns:
            List of knowledge.
        """
        from core.learning.types import KnowledgeType

        if knowledge_type:
            try:
                kt = KnowledgeType(knowledge_type)
                return self._knowledge_consolidator.get_by_type(kt)
            except ValueError:
                pass

        return self._knowledge_consolidator.get_all()

    # ========================================================================
    # Optimization
    # ========================================================================

    def optimize_strategy(
        self,
        strategy_id: str,
        session_id: str | None = None,
    ) -> dict:
        """Optimize a strategy.

        Args:
            strategy_id: Strategy ID.
            session_id: Optional session filter.

        Returns:
            Optimization recommendations.
        """
        experiences = self.get_experiences(session_id)
        feedback_list = []  # Would need experience_id to get specific feedback

        return self._strategy_optimizer.optimize(
            strategy_id=strategy_id,
            experiences=experiences,
            feedback=feedback_list,
        )

    # ========================================================================
    # Metrics
    # ========================================================================

    def get_metrics(self) -> LearningMetrics:
        """Get learning metrics.

        Returns:
            Learning metrics.
        """
        experiences = self._experience_collector.get_all()

        if experiences:
            outcome_scores = {
                "success": sum(1 for e in experiences if e.outcome == "success"),
                "failure": sum(1 for e in experiences if e.outcome == "failure"),
                "partial": sum(1 for e in experiences if e.outcome == "partial"),
            }
            total = len(experiences)
            self._metrics.avg_outcome_score = (
                outcome_scores["success"] / total
                if total > 0
                else 0.0
            )

        return self._metrics


# Global learning platform
_learning_platform: CognitiveLearningPlatform | None = None
_platform_lock = __import__("threading").Lock()


def get_learning_platform() -> CognitiveLearningPlatform:
    """Get the global learning platform."""
    global _learning_platform
    with _platform_lock:
        if _learning_platform is None:
            _learning_platform = CognitiveLearningPlatform()
        return _learning_platform


def reset_learning_platform() -> None:
    """Reset the global learning platform."""
    global _learning_platform
    with _platform_lock:
        _learning_platform = None
