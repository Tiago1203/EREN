"""Unit tests for pipeline core module."""

import pytest

from core.PHASE_2.pipeline.pipeline import CognitivePipeline
from core.PHASE_2.pipeline.context import PipelineContext
from core.PHASE_2.pipeline.stage import (
    PipelineStage,
    PlanningStage,
    KnowledgeStage,
    ReasoningStage,
    StageState,
    StageType,
)
from core.PHASE_2.pipeline.types import (
    PipelineState,
    StageResult,
    PipelineResult,
    PipelineConfig,
)
from core.PHASE_2.pipeline.exceptions import (
    DuplicateStageError,
    EmptyPipelineError,
    PipelineValidationError,
)


class TestPipelineContext:
    """Tests for PipelineContext."""

    def test_creation(self):
        """Test context creation."""
        ctx = PipelineContext(
            pipeline_id="test_pipeline",
            pipeline_name="Test",
        )
        assert ctx.pipeline_id == "test_pipeline"
        assert ctx.pipeline_name == "Test"

    def test_shared_data_operations(self):
        """Test shared data get/set operations."""
        ctx = PipelineContext()

        ctx.set("key1", "value1")
        assert ctx.get("key1") == "value1"
        assert ctx.has("key1") is True
        assert ctx.has("nonexistent") is False

        ctx.delete("key1")
        assert ctx.has("key1") is False

    def test_stage_result_operations(self):
        """Test stage result operations."""
        ctx = PipelineContext()

        from core.PHASE_2.pipeline.types import StageResult
        result = StageResult(
            stage_name="test_stage",
            stage_type=StageType.CUSTOM,
            status=StageState.COMPLETED,
        )

        ctx.add_stage_result("test_stage", result)
        assert ctx.get_stage_result("test_stage") is not None
        assert "test_stage" in ctx.get_successful_stages()

    def test_cancellation(self):
        """Test cancellation operations."""
        ctx = PipelineContext()

        ctx.request_cancellation("User requested")
        assert ctx.is_cancellation_requested() is True
        assert ctx.cancellation_reason == "User requested"


class TestPipelineStage:
    """Tests for PipelineStage."""

    def test_stage_metadata(self):
        """Test stage metadata."""
        stage = PlanningStage()
        assert stage.name == "PlanningStage"
        assert stage.stage_type == StageType.PLANNING
        assert stage.is_required is True

    def test_stage_describe(self):
        """Test stage describe method."""
        stage = PlanningStage()
        assert len(stage.describe()) > 0

    def test_stage_state(self):
        """Test stage state management."""
        stage = PlanningStage()
        assert stage.state == StageState.PENDING

        stage.reset()
        assert stage.state == StageState.PENDING


class TestCognitivePipeline:
    """Tests for CognitivePipeline."""

    def test_creation(self):
        """Test pipeline creation."""
        pipeline = CognitivePipeline(name="test")
        assert pipeline.name == "test"
        assert pipeline.state == PipelineState.CREATED

    def test_add_stage(self):
        """Test adding stages."""
        pipeline = CognitivePipeline(name="test")
        pipeline.add_stage(PlanningStage())

        assert pipeline.stage_count == 1
        assert pipeline.stages[0].name == "PlanningStage"

    def test_add_duplicate_stage(self):
        """Test adding duplicate stage raises error."""
        pipeline = CognitivePipeline(name="test")
        pipeline.add_stage(PlanningStage())

        with pytest.raises(DuplicateStageError):
            pipeline.add_stage(PlanningStage())

    def test_remove_stage(self):
        """Test removing stages."""
        pipeline = CognitivePipeline(name="test")
        pipeline.add_stage(PlanningStage())

        assert pipeline.remove_stage("PlanningStage") is True
        assert pipeline.stage_count == 0

    def test_validate_empty_pipeline(self):
        """Test validating empty pipeline raises error."""
        pipeline = CognitivePipeline(name="test")

        with pytest.raises(EmptyPipelineError):
            pipeline.validate()

    def test_validate_with_stages(self):
        """Test validating pipeline with stages."""
        pipeline = CognitivePipeline(name="test")
        pipeline.add_stage(PlanningStage())

        assert pipeline.validate() is True

    def test_prepare_pipeline(self):
        """Test preparing pipeline."""
        pipeline = CognitivePipeline(name="test")
        pipeline.add_stage(PlanningStage())

        pipeline.prepare()
        assert pipeline.state == PipelineState.READY

    def test_get_stage(self):
        """Test getting stage by name."""
        pipeline = CognitivePipeline(name="test")
        pipeline.add_stage(PlanningStage())

        stage = pipeline.get_stage("PlanningStage")
        assert stage is not None
        assert stage.name == "PlanningStage"

    def test_clear_stages(self):
        """Test clearing all stages."""
        pipeline = CognitivePipeline(name="test")
        pipeline.add_stage(PlanningStage())
        pipeline.add_stage(KnowledgeStage())

        pipeline.clear_stages()
        assert pipeline.stage_count == 0


class TestPipelineStates:
    """Tests for pipeline states."""

    def test_state_transitions(self):
        """Test valid state transitions."""
        assert PipelineState.can_start(PipelineState.READY) is True
        assert PipelineState.can_pause(PipelineState.RUNNING) is True
        assert PipelineState.can_resume(PipelineState.PAUSED) is True
        assert PipelineState.can_cancel(PipelineState.RUNNING) is True

    def test_terminal_states(self):
        """Test terminal states."""
        assert PipelineState.is_terminal(PipelineState.COMPLETED) is True
        assert PipelineState.is_terminal(PipelineState.FAILED) is True
        assert PipelineState.is_terminal(PipelineState.CANCELLED) is True
        assert PipelineState.is_terminal(PipelineState.RUNNING) is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
