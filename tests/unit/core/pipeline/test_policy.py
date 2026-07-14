"""Unit tests for pipeline policy module."""

import pytest

from core.pipeline.policy import (
    PipelinePolicy,
    StopOnFailurePolicy,
    ContinueOnFailurePolicy,
    StrictExecutionPolicy,
    SkipOptionalPolicy,
    RetryStagePolicy,
    PolicyFactory,
)
from core.pipeline.stage import PlanningStage, ToolStage
from core.pipeline.context import PipelineContext
from core.pipeline.types import StageState


class TestPolicyFactory:
    """Tests for PolicyFactory."""

    def test_create_stop_on_failure(self):
        """Test creating stop on failure policy."""
        policy = PolicyFactory.create("stop_on_failure")
        assert isinstance(policy, StopOnFailurePolicy)

    def test_create_continue_on_failure(self):
        """Test creating continue on failure policy."""
        policy = PolicyFactory.create("continue_on_failure")
        assert isinstance(policy, ContinueOnFailurePolicy)

    def test_create_strict_execution(self):
        """Test creating strict execution policy."""
        policy = PolicyFactory.create("strict_execution")
        assert isinstance(policy, StrictExecutionPolicy)

    def test_create_skip_optional(self):
        """Test creating skip optional policy."""
        policy = PolicyFactory.create("skip_optional")
        assert isinstance(policy, SkipOptionalPolicy)

    def test_create_retry_stage(self):
        """Test creating retry stage policy."""
        policy = PolicyFactory.create("retry_stage", max_retries=5)
        assert isinstance(policy, RetryStagePolicy)

    def test_list_policies(self):
        """Test listing available policies."""
        policies = PolicyFactory.list_policies()
        assert "stop_on_failure" in policies
        assert "continue_on_failure" in policies


class TestStopOnFailurePolicy:
    """Tests for StopOnFailurePolicy."""

    def test_should_stop_on_required_failure(self):
        """Test stopping on required stage failure."""
        policy = StopOnFailurePolicy()
        stage = PlanningStage()
        context = PipelineContext()

        result = type('obj', (object,), {
            'is_success': False,
            'stage_name': 'PlanningStage',
        })()

        assert policy.should_stop_on_failure(stage, result, context) is True

    def test_should_retry(self):
        """Test retry behavior."""
        policy = StopOnFailurePolicy()
        stage = PlanningStage()
        stage._retry_count = 3  # Set retry count

        result = type('obj', (object,), {'is_success': False})()

        # With retry_count=3, should retry up to 3 times
        assert policy.should_retry(stage, result, 0) is True
        assert policy.should_retry(stage, result, 2) is True
        assert policy.should_retry(stage, result, 3) is False


class TestContinueOnFailurePolicy:
    """Tests for ContinueOnFailurePolicy."""

    def test_should_not_stop_on_failure(self):
        """Test not stopping on failure."""
        policy = ContinueOnFailurePolicy()
        stage = PlanningStage()
        context = PipelineContext()

        result = type('obj', (object,), {'is_success': False})()

        assert policy.should_stop_on_failure(stage, result, context) is False


class TestRetryStagePolicy:
    """Tests for RetryStagePolicy."""

    def test_max_retries(self):
        """Test max retries configuration."""
        policy = RetryStagePolicy(max_retries=3)

        stage = PlanningStage()
        result = type('obj', (object,), {'is_success': False, 'retry_attempts': 0})()

        assert policy.should_retry(stage, result, 0) is True
        assert policy.should_retry(stage, result, 2) is True
        assert policy.should_retry(stage, result, 3) is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
