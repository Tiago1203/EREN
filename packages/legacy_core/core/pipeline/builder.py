"""Pipeline Builder for EREN OS Cognitive Capability Pipeline.

Fluent builder for constructing pipeline instances.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from core.pipeline.pipeline import CognitivePipeline
from core.pipeline.policy import PipelinePolicy, PolicyConfig, PolicyFactory
from core.pipeline.stage import PipelineStage
from core.pipeline.types import PipelineConfig

if TYPE_CHECKING:
    pass


class PipelineBuilder:
    """Fluent builder for creating CognitivePipeline instances.

    Example:
        pipeline = (
            PipelineBuilder()
                .named("my_pipeline")
                .with_stage(PlanningStage)
                .with_stage(KnowledgeStage)
                .with_stage(ReasoningStage)
                .with_policy("continue_on_failure")
                .build()
        )
    """

    def __init__(self):
        """Initialize the builder."""
        self._name: str = "default_pipeline"
        self._pipeline_id: str | None = None
        self._stages: list[PipelineStage] = []
        self._policy: PipelinePolicy | None = None
        self._config: PipelineConfig | None = None
        self._event_publisher = None
        self._metrics = None
        self._trace = None

    def named(self, name: str) -> PipelineBuilder:
        """Set the pipeline name.

        Args:
            name: Pipeline name.

        Returns:
            Self for chaining.
        """
        self._name = name
        return self

    def with_id(self, pipeline_id: str) -> PipelineBuilder:
        """Set the pipeline ID.

        Args:
            pipeline_id: Unique pipeline ID.

        Returns:
            Self for chaining.
        """
        self._pipeline_id = pipeline_id
        return self

    def with_stage(self, stage: PipelineStage | type[PipelineStage]) -> PipelineBuilder:
        """Add a stage to the pipeline.

        Args:
            stage: Stage instance or stage class to instantiate.

        Returns:
            Self for chaining.
        """
        if isinstance(stage, type):
            # Instantiate the class
            stage_instance = stage()
        else:
            stage_instance = stage

        self._stages.append(stage_instance)
        return self

    def with_stages(self, stages: list[PipelineStage | type[PipelineStage]]) -> PipelineBuilder:
        """Add multiple stages.

        Args:
            stages: List of stage instances or classes.

        Returns:
            Self for chaining.
        """
        for stage in stages:
            self.with_stage(stage)
        return self

    def with_policy(self, policy: PipelinePolicy | str | type[PipelinePolicy]) -> PipelineBuilder:
        """Set the execution policy.

        Args:
            policy: Policy instance, name, or class.

        Returns:
            Self for chaining.
        """
        if isinstance(policy, str):
            self._policy = PolicyFactory.create(policy)
        elif isinstance(policy, type) and issubclass(policy, PipelinePolicy):
            self._policy = policy()
        else:
            self._policy = policy
        return self

    def with_policy_config(self, config: PolicyConfig) -> PipelineBuilder:
        """Set policy configuration.

        Args:
            config: Policy configuration.

        Returns:
            Self for chaining.
        """
        self._policy = config.create_policy()
        return self

    def with_config(self, config: PipelineConfig) -> PipelineBuilder:
        """Set pipeline configuration.

        Args:
            config: Pipeline configuration.

        Returns:
            Self for chaining.
        """
        self._config = config
        return self

    def with_timeout(self, stage_timeout: float, pipeline_timeout: float) -> PipelineBuilder:
        """Set timeout configuration.

        Args:
            stage_timeout: Stage timeout in seconds.
            pipeline_timeout: Pipeline timeout in seconds.

        Returns:
            Self for chaining.
        """
        if self._config is None:
            self._config = PipelineConfig(
                pipeline_name=self._name,
                pipeline_id=self._pipeline_id or "",
            )
        self._config = PipelineConfig(
            pipeline_name=self._name,
            pipeline_id=self._config.pipeline_id,
            stage_timeout_seconds=stage_timeout,
            pipeline_timeout_seconds=pipeline_timeout,
            enable_metrics=self._config.enable_metrics if self._config else True,
            enable_tracing=self._config.enable_tracing if self._config else True,
            enable_events=self._config.enable_events if self._config else True,
        )
        return self

    def with_observability(
        self,
        event_publisher=None,
        metrics=None,
        trace=None,
    ) -> PipelineBuilder:
        """Set observability components.

        Args:
            event_publisher: Event publisher.
            metrics: Metrics collector.
            trace: Trace collector.

        Returns:
            Self for chaining.
        """
        self._event_publisher = event_publisher
        self._metrics = metrics
        self._trace = trace
        return self

    def build(self) -> CognitivePipeline:
        """Build the pipeline instance.

        Returns:
            Configured CognitivePipeline instance.

        Raises:
            PipelineConfigurationError: If configuration is invalid.
        """
        # Create config if not provided
        if self._config is None:
            self._config = PipelineConfig(
                pipeline_name=self._name,
                pipeline_id=self._pipeline_id or "",
            )

        # Create pipeline
        pipeline = CognitivePipeline(
            name=self._name,
            pipeline_id=self._pipeline_id,
            stages=self._stages if self._stages else None,
            policy=self._policy,
            config=self._config,
        )

        # Set observability
        if self._event_publisher:
            pipeline.set_event_publisher(self._event_publisher)
        if self._metrics:
            pipeline.set_metrics(self._metrics)
        if self._trace:
            pipeline.set_trace(self._trace)

        return pipeline


class DefaultPipelineBuilder:
    """Builder for creating the default EREN pipeline.

    Creates a standard pipeline with all cognitive stages.
    """

    @staticmethod
    def create_default() -> CognitivePipeline:
        """Create the default pipeline.

        Returns:
            Default cognitive pipeline.
        """
        from core.pipeline.stage import (
            ContextUpdateStage,
            DecisionStage,
            KnowledgeStage,
            MemoryStage,
            PlanningStage,
            ReasoningStage,
            ToolStage,
        )

        return (
            PipelineBuilder()
            .named("default_pipeline")
            .with_stage(PlanningStage)
            .with_stage(KnowledgeStage)
            .with_stage(MemoryStage)
            .with_stage(ReasoningStage)
            .with_stage(DecisionStage)
            .with_stage(ToolStage)
            .with_stage(ContextUpdateStage)
            .with_policy("stop_on_failure")
            .build()
        )

    @staticmethod
    def create_minimal() -> CognitivePipeline:
        """Create a minimal pipeline with essential stages.

        Returns:
            Minimal cognitive pipeline.
        """
        from core.pipeline.stage import (
            DecisionStage,
            PlanningStage,
            ReasoningStage,
        )

        return (
            PipelineBuilder()
            .named("minimal_pipeline")
            .with_stage(PlanningStage)
            .with_stage(ReasoningStage)
            .with_stage(DecisionStage)
            .with_policy("stop_on_failure")
            .build()
        )

    @staticmethod
    def create_research() -> CognitivePipeline:
        """Create a pipeline optimized for research.

        Returns:
            Research-focused pipeline.
        """
        from core.pipeline.stage import (
            KnowledgeStage,
            MemoryStage,
            PlanningStage,
            ReasoningStage,
        )

        return (
            PipelineBuilder()
            .named("research_pipeline")
            .with_stage(PlanningStage)
            .with_stage(KnowledgeStage)
            .with_stage(MemoryStage)
            .with_stage(ReasoningStage)
            .with_policy("continue_on_failure")
            .build()
        )


class PipelinePreset:
    """Presets for common pipeline configurations."""

    PRESETS: dict[str, dict] = {
        "default": {
            "name": "default_pipeline",
            "stages": [
                "PlanningStage",
                "KnowledgeStage",
                "MemoryStage",
                "ReasoningStage",
                "DecisionStage",
                "ToolStage",
                "ContextUpdateStage",
            ],
            "policy": "stop_on_failure",
        },
        "minimal": {
            "name": "minimal_pipeline",
            "stages": ["PlanningStage", "ReasoningStage", "DecisionStage"],
            "policy": "stop_on_failure",
        },
        "research": {
            "name": "research_pipeline",
            "stages": ["PlanningStage", "KnowledgeStage", "MemoryStage", "ReasoningStage"],
            "policy": "continue_on_failure",
        },
        "emergency": {
            "name": "emergency_pipeline",
            "stages": ["ReasoningStage", "DecisionStage", "ToolStage"],
            "policy": "strict_execution",
        },
        "maintenance": {
            "name": "maintenance_pipeline",
            "stages": ["PlanningStage", "KnowledgeStage", "ToolStage", "ContextUpdateStage"],
            "policy": "continue_on_failure",
        },
    }

    @classmethod
    def get_preset(cls, name: str) -> dict | None:
        """Get a preset by name.

        Args:
            name: Preset name.

        Returns:
            Preset configuration or None.
        """
        return cls.PRESETS.get(name.lower())

    @classmethod
    def list_presets(cls) -> list[str]:
        """List all available presets.

        Returns:
            List of preset names.
        """
        return list(cls.PRESETS.keys())

    @classmethod
    def build_preset(cls, name: str) -> CognitivePipeline:
        """Build a pipeline from a preset.

        Args:
            name: Preset name.

        Returns:
            Configured CognitivePipeline.

        Raises:
            ValueError: If preset not found.
        """
        preset = cls.get_preset(name)
        if preset is None:
            raise ValueError(f"Unknown preset: {name}")

        from core.pipeline.stage import (
            ContextUpdateStage,
            DecisionStage,
            KnowledgeStage,
            MemoryStage,
            PlanningStage,
            ReasoningStage,
            ToolStage,
        )

        stage_map = {
            "PlanningStage": PlanningStage,
            "KnowledgeStage": KnowledgeStage,
            "MemoryStage": MemoryStage,
            "ReasoningStage": ReasoningStage,
            "DecisionStage": DecisionStage,
            "ToolStage": ToolStage,
            "ContextUpdateStage": ContextUpdateStage,
        }

        builder = PipelineBuilder().named(preset["name"])

        for stage_name in preset["stages"]:
            stage_class = stage_map.get(stage_name)
            if stage_class:
                builder.with_stage(stage_class)

        builder.with_policy(preset["policy"])

        return builder.build()
