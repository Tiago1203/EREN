"""Unit tests for pipeline types module."""

import pytest
from datetime import datetime, timezone

from core.pipeline.types import (
    StageState,
    StageType,
    PipelineState,
    StageMetadata,
    StageResult,
    PipelineResult,
    PipelineConfig,
    ExecutionPolicy,
    PipelineIntent,
)


class TestStageState:
    """Tests for StageState."""

    def test_values(self):
        """Test stage state values."""
        assert StageState.PENDING.value == "pending"
        assert StageState.RUNNING.value == "running"
        assert StageState.COMPLETED.value == "completed"

    def test_is_terminal(self):
        """Test terminal state check."""
        assert StageState.is_terminal(StageState.COMPLETED) is True
        assert StageState.is_terminal(StageState.FAILED) is True
        assert StageState.is_terminal(StageState.RUNNING) is False


class TestPipelineState:
    """Tests for PipelineState."""

    def test_values(self):
        """Test pipeline state values."""
        assert PipelineState.CREATED.value == "created"
        assert PipelineState.RUNNING.value == "running"
        assert PipelineState.COMPLETED.value == "completed"

    def test_can_start(self):
        """Test can_start check."""
        assert PipelineState.can_start(PipelineState.READY) is True
        assert PipelineState.can_start(PipelineState.RUNNING) is False

    def test_can_pause(self):
        """Test can_pause check."""
        assert PipelineState.can_pause(PipelineState.RUNNING) is True
        assert PipelineState.can_pause(PipelineState.COMPLETED) is False

    def test_can_cancel(self):
        """Test can_cancel check."""
        assert PipelineState.can_cancel(PipelineState.RUNNING) is True
        assert PipelineState.can_cancel(PipelineState.COMPLETED) is False


class TestStageType:
    """Tests for StageType."""

    def test_values(self):
        """Test stage type values."""
        assert StageType.PLANNING.value == "planning"
        assert StageType.REASONING.value == "reasoning"
        assert StageType.DECISION.value == "decision"


class TestStageMetadata:
    """Tests for StageMetadata."""

    def test_creation(self):
        """Test metadata creation."""
        metadata = StageMetadata(
            stage_name="test",
            stage_type=StageType.PLANNING,
            description="Test stage",
        )
        assert metadata.stage_name == "test"
        assert metadata.stage_type == StageType.PLANNING

    def test_to_dict(self):
        """Test conversion to dict."""
        metadata = StageMetadata(
            stage_name="test",
            stage_type=StageType.PLANNING,
        )
        d = metadata.to_dict()
        assert d["stage_name"] == "test"
        assert d["stage_type"] == "planning"


class TestStageResult:
    """Tests for StageResult."""

    def test_creation(self):
        """Test result creation."""
        result = StageResult(
            stage_name="test",
            stage_type=StageType.PLANNING,
            status=StageState.COMPLETED,
        )
        assert result.stage_name == "test"
        assert result.status == StageState.COMPLETED

    def test_is_success(self):
        """Test success check."""
        result = StageResult(
            stage_name="test",
            stage_type=StageType.PLANNING,
            status=StageState.COMPLETED,
        )
        assert result.is_success is True

    def test_is_failure(self):
        """Test failure check."""
        result = StageResult(
            stage_name="test",
            stage_type=StageType.PLANNING,
            status=StageState.FAILED,
        )
        assert result.is_failure is True


class TestPipelineResult:
    """Tests for PipelineResult."""

    def test_creation(self):
        """Test result creation."""
        result = PipelineResult(
            pipeline_id="test",
            pipeline_name="Test",
            status=PipelineState.COMPLETED,
        )
        assert result.pipeline_id == "test"
        assert result.status == PipelineState.COMPLETED

    def test_is_success(self):
        """Test success check."""
        result = PipelineResult(
            pipeline_id="test",
            pipeline_name="Test",
            status=PipelineState.COMPLETED,
        )
        assert result.is_success is True

    def test_is_failure(self):
        """Test failure check."""
        result = PipelineResult(
            pipeline_id="test",
            pipeline_name="Test",
            status=PipelineState.FAILED,
        )
        assert result.is_failure is True


class TestPipelineConfig:
    """Tests for PipelineConfig."""

    def test_creation(self):
        """Test config creation."""
        config = PipelineConfig(
            pipeline_name="test",
            pipeline_id="test_001",
        )
        assert config.pipeline_name == "test"
        assert config.pipeline_id == "test_001"

    def test_defaults(self):
        """Test default values."""
        config = PipelineConfig(
            pipeline_name="test",
            pipeline_id="test_001",
        )
        assert config.stage_timeout_seconds == 30.0
        assert config.enable_metrics is True


class TestPipelineIntent:
    """Tests for PipelineIntent."""

    def test_creation(self):
        """Test intent creation."""
        intent = PipelineIntent(
            intent_id="intent_001",
            intent_type="diagnostic",
        )
        assert intent.intent_id == "intent_001"
        assert intent.intent_type == "diagnostic"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
