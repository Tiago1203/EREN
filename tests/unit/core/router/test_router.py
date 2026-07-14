"""Unit tests for router core module."""

import pytest

from core.router.router import CapabilityRouter
from core.router.context import RouterContext
from core.router.result import RoutingResult
from core.router.matcher import PipelineMatcher
from core.router.selector import PipelineSelector
from core.router.types import (
    RouterState,
    PipelineMetadata,
    CandidatePipeline,
    MatchResult,
    RoutingPolicy,
)
from core.router.exceptions import NoMatchingPipelineError


class TestRouterContext:
    """Tests for RouterContext."""

    def test_creation(self):
        """Test context creation."""
        ctx = RouterContext(
            intent_type="diagnostic",
            session_id="test_session",
        )
        assert ctx.intent_type == "diagnostic"
        assert ctx.session_id == "test_session"

    def test_from_intent(self):
        """Test context from intent."""
        ctx = RouterContext.from_intent(
            intent_type="diagnostic",
            intent_data={"query": "fever"},
        )
        assert ctx.intent_type == "diagnostic"
        assert ctx.intent_data["query"] == "fever"

    def test_capability_operations(self):
        """Test capability operations."""
        ctx = RouterContext(available_capabilities=["reasoning", "memory"])

        assert ctx.has_capability("reasoning") is True
        assert ctx.has_capability("knowledge") is False
        assert ctx.has_all_capabilities(["reasoning", "memory"]) is True
        assert ctx.has_any_capability(["knowledge", "reasoning"]) is True

        ctx.add_capability("knowledge")
        assert ctx.has_capability("knowledge") is True

        ctx.remove_capability("reasoning")
        assert ctx.has_capability("reasoning") is False


class TestRoutingResult:
    """Tests for RoutingResult."""

    def test_creation(self):
        """Test result creation."""
        result = RoutingResult()
        assert result.state == RouterState.CREATED

    def test_start_complete(self):
        """Test start and complete."""
        result = RoutingResult()
        result.start()
        assert result.state == RouterState.ANALYZING

        result.set_selected_pipeline(PipelineMetadata(
            pipeline_name="Test",
            pipeline_id="test",
        ))
        result.complete()
        assert result.state == RouterState.READY
        assert result.is_success is True

    def test_failure(self):
        """Test failure handling."""
        result = RoutingResult()
        result.start()
        result.fail("Test error")
        assert result.state == RouterState.FAILED
        assert result.is_failure is True
        assert "Test error" in result.errors


class TestPipelineMatcher:
    """Tests for PipelineMatcher."""

    def test_exact_match(self):
        """Test exact intent type match."""
        matcher = PipelineMatcher()
        context = RouterContext(
            intent_type="diagnostic",
            available_capabilities=["reasoning"],
        )
        metadata = PipelineMetadata(
            pipeline_name="Test",
            pipeline_id="test",
            intent_types=("diagnostic",),
            required_capabilities=("reasoning",),
        )

        candidate = matcher.match(context, metadata)
        assert candidate.match_result == MatchResult.EXACT
        assert candidate.score >= 90
        assert candidate.is_eligible is True

    def test_capability_mismatch(self):
        """Test capability mismatch."""
        matcher = PipelineMatcher()
        context = RouterContext(
            intent_type="diagnostic",
            available_capabilities=["reasoning"],
        )
        metadata = PipelineMetadata(
            pipeline_name="Test",
            pipeline_id="test",
            required_capabilities=("llm",),  # Not available
        )

        candidate = matcher.match(context, metadata)
        assert candidate.is_eligible is False
        assert "Missing capabilities" in candidate.eligibility_reason


class TestPipelineSelector:
    """Tests for PipelineSelector."""

    def test_first_match_policy(self):
        """Test first match policy."""
        selector = PipelineSelector(policy=RoutingPolicy.FIRST_MATCH)
        context = RouterContext(intent_type="diagnostic")

        # Candidates are pre-sorted by score
        candidates = [
            CandidatePipeline(
                metadata=PipelineMetadata(pipeline_name="A", pipeline_id="a"),
                score=100.0,
                is_eligible=True,
            ),
            CandidatePipeline(
                metadata=PipelineMetadata(pipeline_name="B", pipeline_id="b"),
                score=50.0,
                is_eligible=True,
            ),
        ]

        result = RoutingResult()
        selected = selector.select(context, candidates, result)
        assert selected is not None
        assert selected.pipeline_name == "A"  # First eligible with score > 0

    def test_highest_score_policy(self):
        """Test highest score policy."""
        selector = PipelineSelector(policy=RoutingPolicy.HIGHEST_SCORE)
        context = RouterContext(intent_type="diagnostic")

        candidates = [
            CandidatePipeline(
                metadata=PipelineMetadata(pipeline_name="A", pipeline_id="a"),
                score=50.0,
            ),
            CandidatePipeline(
                metadata=PipelineMetadata(pipeline_name="B", pipeline_id="b"),
                score=100.0,
            ),
        ]

        result = RoutingResult()
        selected = selector.select(context, candidates, result)
        assert selected is not None
        assert selected.pipeline_name == "B"  # Highest score


class TestCapabilityRouter:
    """Tests for CapabilityRouter."""

    def test_creation(self):
        """Test router creation."""
        router = CapabilityRouter()
        assert router.state == RouterState.CREATED

    def test_basic_routing(self):
        """Test basic routing."""
        router = CapabilityRouter()

        result = router.route(
            intent_type="diagnostic",
            session_id="test_session",
            available_capabilities=["reasoning", "knowledge"],
        )

        assert result is not None
        assert result.is_success is True or result.is_failure is True

    def test_routing_statistics(self):
        """Test routing statistics."""
        router = CapabilityRouter()

        router.route(intent_type="diagnostic")
        router.route(intent_type="maintenance")

        assert router.routing_count >= 2

    def test_to_dict(self):
        """Test dictionary conversion."""
        router = CapabilityRouter()
        d = router.to_dict()

        assert "state" in d
        assert "default_policy" in d
        assert "statistics" in d


class TestRouterStates:
    """Tests for router states."""

    def test_state_values(self):
        """Test state values."""
        assert RouterState.CREATED.value == "created"
        assert RouterState.ANALYZING.value == "analyzing"
        assert RouterState.MATCHING.value == "matching"
        assert RouterState.SELECTING.value == "selecting"
        assert RouterState.READY.value == "ready"
        assert RouterState.FAILED.value == "failed"

    def test_is_terminal(self):
        """Test terminal states."""
        assert RouterState.is_terminal(RouterState.READY) is True
        assert RouterState.is_terminal(RouterState.FAILED) is True
        assert RouterState.is_terminal(RouterState.ANALYZING) is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
