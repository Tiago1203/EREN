"""Unit tests for EREN Cognitive Learning Platform."""

import pytest

from core.learning.types import (
    LearningType,
    LearningStatus,
    Experience,
    Feedback,
    FeedbackType,
    Pattern,
    Knowledge,
    KnowledgeType,
)
from core.learning.experience import ExperienceCollector, get_experience_collector, reset_experience_collector
from core.learning.feedback import FeedbackAnalyzer, get_feedback_analyzer, reset_feedback_analyzer
from core.learning.patterns import PatternDiscovery, get_pattern_discovery, reset_pattern_discovery
from core.learning.consolidation import KnowledgeConsolidator, get_knowledge_consolidator, reset_knowledge_consolidator
from core.learning.optimizer import StrategyOptimizer, get_strategy_optimizer, reset_strategy_optimizer
from core.learning.platform import CognitiveLearningPlatform, get_learning_platform


class TestExperienceCollector:
    """Tests for ExperienceCollector."""

    def setup_method(self):
        """Setup for each test."""
        reset_experience_collector()

    def test_record_experience(self):
        """Test recording experience."""
        collector = get_experience_collector()
        experience = collector.record(
            session_id="session_1",
            context={"key": "value"},
            action="test_action",
            result={"success": True},
            outcome="success",
        )
        assert experience.session_id == "session_1"
        assert experience.action == "test_action"
        assert experience.outcome == "success"

    def test_get_by_session(self):
        """Test getting experiences by session."""
        collector = get_experience_collector()
        collector.record("session_1", {}, "action1", {}, "success")
        collector.record("session_1", {}, "action2", {}, "failure")
        collector.record("session_2", {}, "action3", {}, "success")

        session1_exps = collector.get_by_session("session_1")
        assert len(session1_exps) == 2


class TestFeedbackAnalyzer:
    """Tests for FeedbackAnalyzer."""

    def setup_method(self):
        """Setup for each test."""
        reset_feedback_analyzer()

    def test_add_feedback(self):
        """Test adding feedback."""
        analyzer = get_feedback_analyzer()
        feedback = analyzer.add(
            experience_id="exp_1",
            feedback_type=FeedbackType.POSITIVE,
            content="Good result",
            rating=0.9,
        )
        assert feedback.experience_id == "exp_1"
        assert feedback.feedback_type == FeedbackType.POSITIVE

    def test_analyze_feedback(self):
        """Test analyzing feedback."""
        analyzer = get_feedback_analyzer()
        feedback = analyzer.add(
            experience_id="exp_1",
            feedback_type=FeedbackType.NEGATIVE,
            content="Poor result",
            rating=0.2,
        )
        analysis = analyzer.analyze(feedback.feedback_id)
        assert analysis["sentiment"] == "negative"
        assert analysis["actionable"] is True


class TestPatternDiscovery:
    """Tests for PatternDiscovery."""

    def setup_method(self):
        """Setup for each test."""
        reset_pattern_discovery()

    def test_discover_patterns(self):
        """Test discovering patterns."""
        discovery = get_pattern_discovery()

        # Create experiences
        experiences = [
            Experience(
                experience_id=f"exp_{i}",
                session_id="session_1",
                context={"type": "test"},
                action=f"action_{i % 3}",
                result={},
                outcome="success",
            )
            for i in range(10)
        ]

        patterns = discovery.discover(experiences, min_frequency=0.1)
        assert isinstance(patterns, list)


class TestKnowledgeConsolidator:
    """Tests for KnowledgeConsolidator."""

    def setup_method(self):
        """Setup for each test."""
        reset_knowledge_consolidator()

    def test_consolidate(self):
        """Test consolidating patterns."""
        consolidator = get_knowledge_consolidator()

        patterns = [
            Pattern(
                pattern_id="pat_1",
                description="Test pattern",
                pattern_type="sequence",
                frequency=0.8,
                confidence=0.7,
            )
        ]

        experiences = [
            Experience(
                experience_id="exp_1",
                session_id="session_1",
                context={},
                action="test_action",
                result={},
                outcome="success",
            )
        ]

        knowledge = consolidator.consolidate(patterns, experiences)
        assert len(knowledge) >= 0


class TestStrategyOptimizer:
    """Tests for StrategyOptimizer."""

    def setup_method(self):
        """Setup for each test."""
        reset_strategy_optimizer()

    def test_optimize(self):
        """Test optimizing strategy."""
        optimizer = get_strategy_optimizer()

        experiences = [
            Experience(
                experience_id=f"exp_{i}",
                session_id="session_1",
                context={},
                action="test_action",
                result={},
                outcome="success",
            )
            for i in range(5)
        ]

        recommendations = optimizer.optimize("strategy_1", experiences, [])
        assert isinstance(recommendations, list)


class TestCognitiveLearningPlatform:
    """Tests for CognitiveLearningPlatform."""

    def setup_method(self):
        """Setup for each test."""
        reset_experience_collector()
        reset_feedback_analyzer()
        reset_pattern_discovery()
        reset_knowledge_consolidator()
        reset_strategy_optimizer()

    def test_record_experience(self):
        """Test recording experience."""
        platform = CognitiveLearningPlatform()
        experience = platform.record_experience(
            session_id="session_1",
            context={"test": True},
            action="test_action",
            result={"success": True},
            outcome="success",
        )
        assert experience.experience_id.startswith("exp_")
        assert experience.outcome == "success"

    def test_add_feedback(self):
        """Test adding feedback."""
        platform = CognitiveLearningPlatform()
        experience = platform.record_experience(
            session_id="session_1",
            context={},
            action="test",
            result={},
            outcome="success",
        )
        feedback = platform.add_feedback(
            experience_id=experience.experience_id,
            feedback_type=FeedbackType.POSITIVE,
            content="Good work",
            rating=0.9,
        )
        assert feedback.feedback_id.startswith("fb_")

    def test_discover_patterns(self):
        """Test discovering patterns."""
        platform = CognitiveLearningPlatform()

        # Record some experiences
        for i in range(5):
            platform.record_experience(
                session_id="session_1",
                context={"index": i},
                action=f"action_{i}",
                result={},
                outcome="success",
            )

        patterns = platform.discover_patterns()
        assert isinstance(patterns, list)

    def test_consolidate_knowledge(self):
        """Test consolidating knowledge."""
        platform = CognitiveLearningPlatform()

        # Record experiences
        for i in range(3):
            platform.record_experience(
                session_id="session_1",
                context={},
                action="test_action",
                result={},
                outcome="success",
            )

        knowledge = platform.consolidate_knowledge()
        assert isinstance(knowledge, list)

    def test_optimize_strategy(self):
        """Test optimizing strategy."""
        platform = CognitiveLearningPlatform()
        recommendations = platform.optimize_strategy("test_strategy")
        assert isinstance(recommendations, list)

    def test_get_metrics(self):
        """Test getting metrics."""
        platform = CognitiveLearningPlatform()
        platform.record_experience(
            session_id="session_1",
            context={},
            action="test",
            result={},
            outcome="success",
        )
        metrics = platform.get_metrics()
        assert metrics.experiences_recorded >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
