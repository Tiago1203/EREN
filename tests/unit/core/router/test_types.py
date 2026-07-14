"""Unit tests for router types module."""

import pytest
from datetime import datetime, timezone

from core.router.types import (
    RouterState,
    RoutingPolicy,
    MatchResult,
    PipelineMetadata,
    CandidatePipeline,
    RoutingRule,
    RoutingContext,
)


class TestRouterState:
    """Tests for RouterState."""

    def test_values(self):
        """Test state values."""
        assert RouterState.CREATED.value == "created"
        assert RouterState.ANALYZING.value == "analyzing"
        assert RouterState.MATCHING.value == "matching"
        assert RouterState.SELECTING.value == "selecting"
        assert RouterState.READY.value == "ready"
        assert RouterState.FAILED.value == "failed"

    def test_is_terminal(self):
        """Test terminal state check."""
        assert RouterState.is_terminal(RouterState.READY) is True
        assert RouterState.is_terminal(RouterState.FAILED) is True
        assert RouterState.is_terminal(RouterState.ANALYZING) is False

    def test_can_route(self):
        """Test can route check."""
        assert RouterState.can_route(RouterState.READY) is True
        assert RouterState.can_route(RouterState.CREATED) is True
        assert RouterState.can_route(RouterState.FAILED) is False


class TestRoutingPolicy:
    """Tests for RoutingPolicy."""

    def test_values(self):
        """Test policy values."""
        assert RoutingPolicy.FIRST_MATCH.value == "first_match"
        assert RoutingPolicy.HIGHEST_SCORE.value == "highest_score"
        assert RoutingPolicy.PRIORITY.value == "priority"


class TestMatchResult:
    """Tests for MatchResult."""

    def test_values(self):
        """Test match result values."""
        assert MatchResult.EXACT.value == "exact"
        assert MatchResult.PARTIAL.value == "partial"
        assert MatchResult.POTENTIAL.value == "potential"
        assert MatchResult.NO_MATCH.value == "no_match"


class TestPipelineMetadata:
    """Tests for PipelineMetadata."""

    def test_creation(self):
        """Test metadata creation."""
        metadata = PipelineMetadata(
            pipeline_name="TestPipeline",
            pipeline_id="test_pipeline",
            tags=("test", "medical"),
            priority=100,
        )
        assert metadata.pipeline_name == "TestPipeline"
        assert "test" in metadata.tags

    def test_to_dict(self):
        """Test conversion to dict."""
        metadata = PipelineMetadata(
            pipeline_name="Test",
            pipeline_id="test",
        )
        d = metadata.to_dict()
        assert d["pipeline_name"] == "Test"
        assert "tags" in d


class TestCandidatePipeline:
    """Tests for CandidatePipeline."""

    def test_creation(self):
        """Test candidate creation."""
        metadata = PipelineMetadata(
            pipeline_name="Test",
            pipeline_id="test",
        )
        candidate = CandidatePipeline(
            metadata=metadata,
            score=85.0,
            match_result=MatchResult.EXACT,
        )
        assert candidate.score == 85.0
        assert candidate.match_result == MatchResult.EXACT
        assert candidate.is_eligible is True

    def test_to_dict(self):
        """Test conversion to dict."""
        metadata = PipelineMetadata(pipeline_name="Test", pipeline_id="test")
        candidate = CandidatePipeline(metadata=metadata)
        d = candidate.to_dict()
        assert d["pipeline_name"] == "Test"
        assert d["score"] == 0.0


class TestRoutingRule:
    """Tests for RoutingRule."""

    def test_creation(self):
        """Test rule creation."""
        rule = RoutingRule(
            rule_id="rule_001",
            name="Test Rule",
            intent_type="diagnostic",
            pipeline_name="DiagnosticPipeline",
        )
        assert rule.rule_id == "rule_001"
        assert rule.intent_type == "diagnostic"

    def test_to_dict(self):
        """Test conversion to dict."""
        rule = RoutingRule(
            rule_id="rule_001",
            name="Test Rule",
        )
        d = rule.to_dict()
        assert d["rule_id"] == "rule_001"
        assert d["name"] == "Test Rule"


class TestRoutingContext:
    """Tests for RoutingContext."""

    def test_creation(self):
        """Test context creation."""
        context = RoutingContext(
            intent_type="diagnostic",
            session_id="test_session",
        )
        assert context.intent_type == "diagnostic"
        assert context.session_id == "test_session"

    def test_to_dict(self):
        """Test conversion to dict."""
        context = RoutingContext(intent_type="diagnostic")
        d = context.to_dict()
        assert d["intent_type"] == "diagnostic"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
