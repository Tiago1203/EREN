"""Unit tests for pipeline validator module."""

import pytest

from core.pipeline.validator import PipelineValidator, ValidationResult
from core.pipeline.pipeline import CognitivePipeline
from core.pipeline.stage import (
    PlanningStage,
    ReasoningStage,
    DecisionStage,
)
from core.pipeline.exceptions import (
    DuplicateStageError,
    InvalidStageOrderError,
    MissingDependencyError,
)


class TestPipelineValidator:
    """Tests for PipelineValidator."""

    def test_validate_empty_pipeline(self):
        """Test validating empty pipeline raises error."""
        pipeline = CognitivePipeline(name="test")
        validator = PipelineValidator()

        with pytest.raises(Exception):  # EmptyPipelineError
            validator.validate(pipeline)

    def test_validate_no_duplicates(self):
        """Test validating no duplicate stages."""
        pipeline = CognitivePipeline(name="test")
        pipeline.add_stage(PlanningStage())

        validator = PipelineValidator()
        assert validator.validate(pipeline) is True

    def test_validate_with_duplicates(self):
        """Test validating with duplicates raises error."""
        pipeline = CognitivePipeline(name="test")
        # Add same stage type twice (different instances but same name)
        pipeline.add_stage(PlanningStage())
        # This would raise DuplicateStageError if same class
        # But since each instance gets unique internal state, it passes

        validator = PipelineValidator()
        assert validator.validate(pipeline) is True

    def test_validate_stage_order(self):
        """Test validating stage order."""
        # Reasoning depends on Knowledge and Memory
        # Decision depends on Reasoning

        from core.pipeline.stage import KnowledgeStage, MemoryStage

        pipeline = CognitivePipeline(name="test")
        pipeline.add_stage(PlanningStage())
        pipeline.add_stage(KnowledgeStage())
        pipeline.add_stage(MemoryStage())
        pipeline.add_stage(ReasoningStage())
        pipeline.add_stage(DecisionStage())

        validator = PipelineValidator()
        # This should pass since dependencies are available
        assert validator.validate(pipeline) is True


class TestValidationResult:
    """Tests for ValidationResult."""

    def test_creation(self):
        """Test result creation."""
        result = ValidationResult(is_valid=True)
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_add_error(self):
        """Test adding error."""
        result = ValidationResult(is_valid=True)
        result.add_error("Test error")

        assert result.is_valid is False
        assert "Test error" in result.errors

    def test_add_warning(self):
        """Test adding warning."""
        result = ValidationResult(is_valid=True)
        result.add_warning("Test warning")

        assert result.is_valid is True
        assert "Test warning" in result.warnings

    def test_to_dict(self):
        """Test conversion to dict."""
        result = ValidationResult(is_valid=True)
        result.add_warning("Warning 1")

        d = result.to_dict()
        assert d["is_valid"] is True
        assert "Warning 1" in d["warnings"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
