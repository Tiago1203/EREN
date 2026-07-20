"""Pipeline Validator for EREN OS Cognitive Capability Pipeline.

Validates pipeline configuration and structure.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from core.pipeline.exceptions import (
    DuplicateStageError,
    EmptyPipelineError,
    InvalidStageOrderError,
    MissingDependencyError,
)

if TYPE_CHECKING:
    from core.pipeline.pipeline import CognitivePipeline


class PipelineValidator:
    """Validates pipeline configuration and structure.

    Checks for:
    - Empty pipeline
    - Duplicate stages
    - Invalid stage order
    - Missing dependencies
    - Contract existence
    """

    def validate(self, pipeline: CognitivePipeline) -> bool:
        """Validate a pipeline.

        Args:
            pipeline: Pipeline to validate.

        Returns:
            True if valid.

        Raises:
            PipelineValidationError: If validation fails.
        """
        # Check for empty pipeline
        if pipeline.stage_count == 0:
            raise EmptyPipelineError()

        # Check for duplicates
        self._validate_no_duplicates(pipeline)

        # Check stage order
        self._validate_stage_order(pipeline)

        # Check dependencies
        self._validate_dependencies(pipeline)

        return True

    def _validate_no_duplicates(self, pipeline: CognitivePipeline) -> None:
        """Validate no duplicate stages.

        Args:
            pipeline: Pipeline to validate.

        Raises:
            DuplicateStageError: If duplicates found.
        """
        stage_names = [s.name for s in pipeline.stages]
        seen = set()

        for name in stage_names:
            if name in seen:
                raise DuplicateStageError(name)
            seen.add(name)

    def _validate_stage_order(self, pipeline: CognitivePipeline) -> None:
        """Validate stage execution order.

        Args:
            pipeline: Pipeline to validate.

        Raises:
            InvalidStageOrderError: If order is invalid.
        """
        # Define valid stage types that must come early
        early_stages = {"PlanningStage", "KnowledgeStage"}
        late_stages = {"ToolStage", "ContextUpdateStage"}

        stage_names = [s.__class__.__name__ for s in pipeline.stages]

        # Check that late stages don't come before early stages
        late_indices = []
        early_indices = []

        for i, name in enumerate(stage_names):
            if name in late_stages:
                late_indices.append(i)
            if name in early_stages:
                early_indices.append(i)

        # If we have both, ensure early comes before late
        if late_indices and early_indices:
            if max(early_indices) > min(late_indices):
                raise InvalidStageOrderError(
                    "Late stages (Tool, ContextUpdate) must come after "
                    "early stages (Planning, Knowledge)",
                    stage_name=stage_names[min(late_indices)],
                )

    def _validate_dependencies(self, pipeline: CognitivePipeline) -> None:
        """Validate stage dependencies.

        Args:
            pipeline: Pipeline to validate.

        Raises:
            MissingDependencyError: If dependency is missing.
        """
        # Define expected dependencies
        dependencies = {
            "ReasoningStage": ["KnowledgeStage", "MemoryStage"],
            "DecisionStage": ["ReasoningStage"],
            "MemoryStage": ["PlanningStage"],
        }

        stage_map = {s.__class__.__name__: s for s in pipeline.stages}

        for stage_name, required_deps in dependencies.items():
            if stage_name in stage_map:
                for dep in required_deps:
                    if dep not in stage_map:
                        raise MissingDependencyError(
                            stage_name,
                            dep,
                        )

    def validate_stage_dependencies(self, stage_names: list[str]) -> bool:
        """Validate dependencies for a list of stage names.

        Args:
            stage_names: List of stage class names.

        Returns:
            True if valid.
        """
        # Similar validation for stage name list
        dependencies = {
            "ReasoningStage": ["KnowledgeStage", "MemoryStage"],
            "DecisionStage": ["ReasoningStage"],
        }

        for stage_name, required_deps in dependencies.items():
            if stage_name in stage_names:
                for dep in required_deps:
                    if dep not in stage_names:
                        raise MissingDependencyError(stage_name, dep)

        return True


class ValidationResult:
    """Result of pipeline validation."""

    def __init__(self, is_valid: bool):
        """Initialize result.

        Args:
            is_valid: Whether validation passed.
        """
        self.is_valid = is_valid
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def add_error(self, error: str) -> None:
        """Add an error.

        Args:
            error: Error message.
        """
        self.errors.append(error)
        self.is_valid = False

    def add_warning(self, warning: str) -> None:
        """Add a warning.

        Args:
            warning: Warning message.
        """
        self.warnings.append(warning)

    def to_dict(self) -> dict:
        """Convert to dictionary.

        Returns:
            Dictionary representation.
        """
        return {
            "is_valid": self.is_valid,
            "errors": self.errors,
            "warnings": self.warnings,
        }
