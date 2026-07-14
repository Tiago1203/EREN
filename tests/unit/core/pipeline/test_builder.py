"""Unit tests for pipeline builder module."""

import pytest

from core.pipeline.builder import (
    PipelineBuilder,
    DefaultPipelineBuilder,
    PipelinePreset,
)
from core.pipeline.stage import (
    PlanningStage,
    KnowledgeStage,
    ReasoningStage,
)
from core.pipeline.policy import StopOnFailurePolicy


class TestPipelineBuilder:
    """Tests for PipelineBuilder."""

    def test_named(self):
        """Test naming pipeline."""
        builder = PipelineBuilder().named("my_pipeline")
        assert builder._name == "my_pipeline"

    def test_with_id(self):
        """Test setting pipeline ID."""
        builder = PipelineBuilder().with_id("pipeline_001")
        assert builder._pipeline_id == "pipeline_001"

    def test_with_stage(self):
        """Test adding stage."""
        builder = PipelineBuilder()
        builder.with_stage(PlanningStage)
        assert len(builder._stages) == 1

    def test_with_stages(self):
        """Test adding multiple stages."""
        builder = PipelineBuilder()
        builder.with_stages([PlanningStage, KnowledgeStage])
        assert len(builder._stages) == 2

    def test_with_policy(self):
        """Test setting policy."""
        builder = PipelineBuilder()
        builder.with_policy("continue_on_failure")
        assert builder._policy is not None

    def test_build(self):
        """Test building pipeline."""
        pipeline = (
            PipelineBuilder()
            .named("test_pipeline")
            .with_stage(PlanningStage)
            .with_stage(ReasoningStage)
            .with_policy(StopOnFailurePolicy())
            .build()
        )

        assert pipeline.name == "test_pipeline"
        assert pipeline.stage_count == 2


class TestDefaultPipelineBuilder:
    """Tests for DefaultPipelineBuilder."""

    def test_create_default(self):
        """Test creating default pipeline."""
        pipeline = DefaultPipelineBuilder.create_default()
        assert pipeline.name == "default_pipeline"
        assert pipeline.stage_count > 0

    def test_create_minimal(self):
        """Test creating minimal pipeline."""
        pipeline = DefaultPipelineBuilder.create_minimal()
        assert pipeline.name == "minimal_pipeline"


class TestPipelinePreset:
    """Tests for PipelinePreset."""

    def test_get_preset(self):
        """Test getting preset."""
        preset = PipelinePreset.get_preset("default")
        assert preset is not None
        assert "name" in preset

    def test_list_presets(self):
        """Test listing presets."""
        presets = PipelinePreset.list_presets()
        assert "default" in presets
        assert "minimal" in presets

    def test_build_preset(self):
        """Test building from preset."""
        pipeline = PipelinePreset.build_preset("minimal")
        assert pipeline.name == "minimal_pipeline"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
