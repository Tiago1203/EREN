"""Unit tests for router policy module."""

import pytest

from core.PHASE_2.router.policy import (
    RoutingPolicyHandler,
    FirstMatchPolicy,
    HighestScorePolicy,
    PriorityPolicy,
    StrictPolicy,
    WeightedPolicy,
    FallbackPolicy,
    PolicyFactory,
)
from core.PHASE_2.router.context import RouterContext
from core.PHASE_2.router.types import (
    RoutingPolicy,
    PipelineMetadata,
    CandidatePipeline,
    MatchResult,
)


class TestPolicyFactory:
    """Tests for PolicyFactory."""

    def test_create_first_match(self):
        """Test creating first match policy."""
        policy = PolicyFactory.create(RoutingPolicy.FIRST_MATCH)
        assert isinstance(policy, FirstMatchPolicy)

    def test_create_highest_score(self):
        """Test creating highest score policy."""
        policy = PolicyFactory.create(RoutingPolicy.HIGHEST_SCORE)
        assert isinstance(policy, HighestScorePolicy)

    def test_create_priority(self):
        """Test creating priority policy."""
        policy = PolicyFactory.create(RoutingPolicy.PRIORITY)
        assert isinstance(policy, PriorityPolicy)

    def test_create_strict(self):
        """Test creating strict policy."""
        policy = PolicyFactory.create(RoutingPolicy.STRICT)
        assert isinstance(policy, StrictPolicy)

    def test_list_policies(self):
        """Test listing policies."""
        policies = PolicyFactory.list_policies()
        assert RoutingPolicy.FIRST_MATCH in policies
        assert RoutingPolicy.HIGHEST_SCORE in policies


class TestFirstMatchPolicy:
    """Tests for FirstMatchPolicy."""

    def test_select_first_match(self):
        """Test selecting first match."""
        policy = FirstMatchPolicy()
        context = RouterContext(intent_type="diagnostic")

        candidates = [
            CandidatePipeline(
                metadata=PipelineMetadata(pipeline_name="A", pipeline_id="a"),
                score=50.0,
                is_eligible=True,
            ),
            CandidatePipeline(
                metadata=PipelineMetadata(pipeline_name="B", pipeline_id="b"),
                score=100.0,
                is_eligible=True,
            ),
        ]

        selected = policy.select(context, candidates)
        assert selected is not None
        assert selected.pipeline_name == "A"

    def test_can_select(self):
        """Test can select check."""
        policy = FirstMatchPolicy()
        context = RouterContext(intent_type="diagnostic")

        candidates = [
            CandidatePipeline(
                metadata=PipelineMetadata(pipeline_name="A", pipeline_id="a"),
                score=0.0,
                is_eligible=True,
            ),
        ]

        assert policy.can_select(context, candidates) is False


class TestHighestScorePolicy:
    """Tests for HighestScorePolicy."""

    def test_select_highest_score(self):
        """Test selecting highest score."""
        policy = HighestScorePolicy()
        context = RouterContext(intent_type="diagnostic")

        candidates = [
            CandidatePipeline(
                metadata=PipelineMetadata(pipeline_name="A", pipeline_id="a"),
                score=50.0,
                is_eligible=True,
            ),
            CandidatePipeline(
                metadata=PipelineMetadata(pipeline_name="B", pipeline_id="b"),
                score=100.0,
                is_eligible=True,
            ),
        ]

        selected = policy.select(context, candidates)
        assert selected is not None
        assert selected.pipeline_name == "B"


class TestPriorityPolicy:
    """Tests for PriorityPolicy."""

    def test_select_highest_priority(self):
        """Test selecting highest priority."""
        policy = PriorityPolicy()
        context = RouterContext(intent_type="diagnostic")

        candidates = [
            CandidatePipeline(
                metadata=PipelineMetadata(
                    pipeline_name="A",
                    pipeline_id="a",
                    priority=50,
                ),
                score=100.0,
                is_eligible=True,
            ),
            CandidatePipeline(
                metadata=PipelineMetadata(
                    pipeline_name="B",
                    pipeline_id="b",
                    priority=100,
                ),
                score=50.0,
                is_eligible=True,
            ),
        ]

        selected = policy.select(context, candidates)
        assert selected is not None
        assert selected.pipeline_name == "B"


class TestStrictPolicy:
    """Tests for StrictPolicy."""

    def test_select_exact_match_only(self):
        """Test selecting only exact matches."""
        policy = StrictPolicy()
        context = RouterContext(intent_type="diagnostic")

        candidates = [
            CandidatePipeline(
                metadata=PipelineMetadata(pipeline_name="A", pipeline_id="a"),
                score=50.0,
                match_result=MatchResult.PARTIAL,
                is_eligible=True,
            ),
            CandidatePipeline(
                metadata=PipelineMetadata(pipeline_name="B", pipeline_id="b"),
                score=100.0,
                match_result=MatchResult.EXACT,
                is_eligible=True,
            ),
        ]

        selected = policy.select(context, candidates)
        assert selected is not None
        assert selected.pipeline_name == "B"


class TestWeightedPolicy:
    """Tests for WeightedPolicy."""

    def test_weighted_selection(self):
        """Test weighted selection."""
        policy = WeightedPolicy(score_weight=0.5, priority_weight=0.5)
        context = RouterContext(intent_type="diagnostic")

        candidates = [
            CandidatePipeline(
                metadata=PipelineMetadata(
                    pipeline_name="A",
                    pipeline_id="a",
                    priority=50,
                ),
                score=50.0,
                is_eligible=True,
            ),
            CandidatePipeline(
                metadata=PipelineMetadata(
                    pipeline_name="B",
                    pipeline_id="b",
                    priority=100,
                ),
                score=50.0,
                is_eligible=True,
            ),
        ]

        selected = policy.select(context, candidates)
        assert selected is not None
        # B should win due to higher priority (weighted equally)
        assert selected.pipeline_name == "B"


class TestFallbackPolicy:
    """Tests for FallbackPolicy."""

    def test_fallback_to_default(self):
        """Test fallback to default policy."""
        policy = FallbackPolicy(
            policies=[],  # No fallback policies
            default_policy=FirstMatchPolicy(),
        )
        context = RouterContext(intent_type="diagnostic")

        candidates = [
            CandidatePipeline(
                metadata=PipelineMetadata(pipeline_name="A", pipeline_id="a"),
                score=50.0,
                is_eligible=True,
            ),
        ]

        selected = policy.select(context, candidates)
        assert selected is not None
        assert selected.pipeline_name == "A"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
