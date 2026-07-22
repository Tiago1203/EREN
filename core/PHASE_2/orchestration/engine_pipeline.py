"""Engine pipeline for cognitive orchestration.

Defines the execution order of cognitive engines.

Architecture only -- no implementations, no business logic.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass


# =============================================================================
# Pipeline Stage
# =============================================================================


@dataclass(frozen=True)
class PipelineStage:
    """A single stage in the engine pipeline."""

    stage_id: str
    phase: str  # CyclePhase value
    engine_type: str  # EngineType value
    engine_id: str
    position: int  # Order in pipeline
    dependencies: tuple[str, ...] = field(default_factory=tuple)  # Dependent stage IDs
    optional: bool = False  # Can be skipped
    timeout_ms: int = 30000  # Stage timeout

    def __hash__(self) -> int:
        """Make hashable."""
        return hash(self.stage_id)


# =============================================================================
# Pipeline Definition
# =============================================================================


class PipelineDefinition:
    """Definition of an engine pipeline.

    Describes the stages and their ordering.
    """

    def __init__(self) -> None:
        """Initialize the pipeline definition."""
        self._stages: dict[str, PipelineStage] = {}
        self._ordered: list[str] = []  # Stage IDs in order

    def add_stage(
        self,
        stage: PipelineStage,
    ) -> PipelineDefinition:
        """Add a stage to the pipeline.

        Args:
            stage: The stage to add.

        Returns:
            Self for chaining.
        """
        self._stages[stage.stage_id] = stage
        self._ordered.append(stage.stage_id)
        return self

    def remove_stage(self, stage_id: str) -> bool:
        """Remove a stage from the pipeline.

        Args:
            stage_id: The stage ID.

        Returns:
            True if removed.
        """
        if stage_id in self._stages:
            del self._stages[stage_id]
            self._ordered.remove(stage_id)
            return True
        return False

    def get_stage(self, stage_id: str) -> PipelineStage | None:
        """Get a stage by ID.

        Args:
            stage_id: The stage ID.

        Returns:
            The stage or None.
        """
        return self._stages.get(stage_id)

    def get_stages_in_order(self) -> list[PipelineStage]:
        """Get all stages in execution order.

        Returns:
            Stages in order.
        """
        return [self._stages[sid] for sid in self._ordered if sid in self._stages]

    def get_stages_by_phase(self, phase: str) -> list[PipelineStage]:
        """Get stages for a specific phase.

        Args:
            phase: The phase.

        Returns:
            Stages for the phase.
        """
        return [s for s in self._stages.values() if s.phase == phase]

    def can_execute(self, stage_id: str, completed: set[str]) -> bool:
        """Check if a stage can be executed.

        Args:
            stage_id: The stage ID.
            completed: Set of completed stage IDs.

        Returns:
            True if stage dependencies are met.
        """
        stage = self._stages.get(stage_id)
        if not stage:
            return False

        return all(dep in completed for dep in stage.dependencies)


# =============================================================================
# Default Pipeline
# =============================================================================


def get_default_pipeline() -> PipelineDefinition:
    """Get the default cognitive pipeline.

    Returns:
        Default pipeline definition.
    """
    pipeline = PipelineDefinition()

    # Intake (always first)
    pipeline.add_stage(PipelineStage(
        stage_id="stage_intake",
        phase="intake",
        engine_type="orchestrator",
        engine_id="orchestrator_main",
        position=0,
    ))

    # Planning
    pipeline.add_stage(PipelineStage(
        stage_id="stage_planning",
        phase="planning",
        engine_type="planner",
        engine_id="planner_main",
        position=1,
        dependencies=("stage_intake",),
    ))

    # Knowledge and Memory (can run in parallel after planning)
    pipeline.add_stage(PipelineStage(
        stage_id="stage_knowledge",
        phase="knowledge",
        engine_type="knowledge",
        engine_id="knowledge_main",
        position=2,
        dependencies=("stage_planning",),
    ))

    pipeline.add_stage(PipelineStage(
        stage_id="stage_memory",
        phase="memory",
        engine_type="memory",
        engine_id="memory_main",
        position=2,
        dependencies=("stage_planning",),
    ))

    # Reasoning (after knowledge and memory)
    pipeline.add_stage(PipelineStage(
        stage_id="stage_reasoning",
        phase="reasoning",
        engine_type="reasoning",
        engine_id="reasoning_main",
        position=3,
        dependencies=("stage_knowledge", "stage_memory"),
    ))

    # Decision (after reasoning)
    pipeline.add_stage(PipelineStage(
        stage_id="stage_decision",
        phase="decision",
        engine_type="decision",
        engine_id="decision_main",
        position=4,
        dependencies=("stage_reasoning",),
    ))

    # Action (after decision)
    pipeline.add_stage(PipelineStage(
        stage_id="stage_action",
        phase="action",
        engine_type="tool",
        engine_id="tool_main",
        position=5,
        dependencies=("stage_decision",),
    ))

    # Output (always last)
    pipeline.add_stage(PipelineStage(
        stage_id="stage_output",
        phase="output",
        engine_type="voice",
        engine_id="voice_main",
        position=6,
        dependencies=("stage_action",),
    ))

    return pipeline


# =============================================================================
# Pipeline Executor (Contract)
# =============================================================================


class PipelineExecutor:
    """Executes engines according to pipeline.

    This is a contract - actual execution is handled
    by the Orchestrator.
    """

    def __init__(
        self,
        pipeline: PipelineDefinition,
        engine_registry: Any | None = None,
    ) -> None:
        """Initialize the pipeline executor.

        Args:
            pipeline: The pipeline to execute.
            engine_registry: Registry to get engines from.
        """
        self._pipeline = pipeline
        self._engine_registry = engine_registry
        self._completed_stages: set[str] = set()
        self._stage_results: dict[str, Any] = {}

    def reset(self) -> None:
        """Reset the executor state."""
        self._completed_stages.clear()
        self._stage_results.clear()

    def get_next_stages(self) -> list[PipelineStage]:
        """Get stages that can be executed next.

        Returns:
            List of executable stages.
        """
        next_stages = []

        for stage in self._pipeline.get_stages_in_order():
            if stage.stage_id not in self._completed_stages:
                if self._pipeline.can_execute(stage.stage_id, self._completed_stages):
                    next_stages.append(stage)

        return next_stages

    def mark_completed(self, stage_id: str, result: Any) -> None:
        """Mark a stage as completed.

        Args:
            stage_id: The stage ID.
            result: The stage result.
        """
        self._completed_stages.add(stage_id)
        self._stage_results[stage_id] = result

    def is_complete(self) -> bool:
        """Check if pipeline is complete.

        Returns:
            True if all required stages are completed.
        """
        for stage in self._pipeline.get_stages_in_order():
            if not stage.optional and stage.stage_id not in self._completed_stages:
                return False
        return True

    def get_results(self) -> dict[str, Any]:
        """Get all stage results.

        Returns:
            Dictionary of stage results.
        """
        return dict(self._stage_results)


# =============================================================================
# Pipeline Builder
# =============================================================================


class PipelineBuilder:
    """Builder for creating custom pipelines."""

    def __init__(self) -> None:
        """Initialize the builder."""
        self._stages: list[PipelineStage] = []
        self._position = 0

    def add_stage(
        self,
        stage_id: str,
        phase: str,
        engine_type: str,
        engine_id: str,
        dependencies: list[str] | None = None,
        optional: bool = False,
        timeout_ms: int = 30000,
    ) -> PipelineBuilder:
        """Add a stage to the pipeline.

        Args:
            stage_id: Unique stage ID.
            phase: Cycle phase.
            engine_type: Engine type.
            engine_id: Engine ID.
            dependencies: Dependent stage IDs.
            optional: Whether stage is optional.
            timeout_ms: Stage timeout.

        Returns:
            Self for chaining.
        """
        stage = PipelineStage(
            stage_id=stage_id,
            phase=phase,
            engine_type=engine_type,
            engine_id=engine_id,
            position=self._position,
            dependencies=tuple(dependencies or []),
            optional=optional,
            timeout_ms=timeout_ms,
        )
        self._stages.append(stage)
        self._position += 1
        return self

    def build(self) -> PipelineDefinition:
        """Build the pipeline.

        Returns:
            The pipeline definition.
        """
        pipeline = PipelineDefinition()
        for stage in self._stages:
            pipeline.add_stage(stage)
        return pipeline
