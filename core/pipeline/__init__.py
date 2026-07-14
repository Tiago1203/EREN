"""EREN OS Cognitive Capability Pipeline.

This module implements the Cognitive Capability Pipeline (CCP), the component
responsible for dynamically executing cognitive capabilities of EREN.

Philosophy:
    The Runtime does not decide which motors to execute.
    The Pipeline decides which cognitive capabilities participate in a cycle.

Key Concepts:
    - Pipeline: Orchestrates stage execution
    - Stage: Individual processing unit (Planning, Knowledge, Memory, etc.)
    - Context: Shared data flowing through stages
    - Policy: Execution policies (StopOnFailure, ContinueOnFailure, etc.)

Example:
    >>> from core.pipeline import ERENPipeline
    >>> pipeline = ERENPipeline.create_default()
    >>> result = pipeline.execute(intent={"query": "..."})
    >>> print(result.status)
"""

from __future__ import annotations

# Core Pipeline
from core.pipeline.pipeline import CognitivePipeline
from core.pipeline.context import PipelineContext
from core.pipeline.stage import (
    PipelineStage,
    PlanningStage,
    KnowledgeStage,
    MemoryStage,
    ReasoningStage,
    DecisionStage,
    ToolStage,
    ContextUpdateStage,
)
from core.pipeline.executor import PipelineExecutor, SyncPipelineExecutor

# Types
from core.pipeline.types import (
    PipelineState,
    StageState,
    StageType,
    StageMetadata,
    StageResult,
    PipelineResult,
    PipelineConfig,
    ExecutionPolicy,
    PipelineIntent,
)

# Builder
from core.pipeline.builder import (
    PipelineBuilder,
    DefaultPipelineBuilder,
    PipelinePreset,
)

# Registry
from core.pipeline.registry import (
    PipelineRegistry,
    get_pipeline_registry,
    register_pipeline,
    get_pipeline,
    unregister_pipeline,
)

# Policy
from core.pipeline.policy import (
    PipelinePolicy,
    StopOnFailurePolicy,
    ContinueOnFailurePolicy,
    StrictExecutionPolicy,
    SkipOptionalPolicy,
    RetryStagePolicy,
    PolicyFactory,
    PolicyConfig,
)

# Validator
from core.pipeline.validator import PipelineValidator, ValidationResult

# Observability
from core.pipeline.events import (
    PipelineEventPublisher,
    PipelineEventType,
    get_pipeline_event_publisher,
    publish_pipeline_event,
)
from core.pipeline.metrics import (
    PipelineMetrics,
    get_pipeline_metrics,
    reset_pipeline_metrics,
)
from core.pipeline.trace import (
    PipelineTrace,
    get_pipeline_trace,
    reset_pipeline_trace,
)

# Exceptions
from core.pipeline.exceptions import (
    PipelineException,
    PipelineInitializationError,
    PipelineConfigurationError,
    PipelineValidationError,
    DuplicateStageError,
    InvalidStageOrderError,
    MissingDependencyError,
    EmptyPipelineError,
    ContractNotFoundError,
    StageException,
    StageExecutionError,
    StageTimeoutError,
    StageSkippedError,
    StageCancelledError,
    PipelineExecutionError,
    PolicyViolationError,
    PolicyStopOnFailureError,
    RetryExhaustedError,
    PipelineStateError,
    InvalidTransitionError,
    PipelineNotRunningError,
    PipelineAlreadyRunningError,
    CancellationRequestedError,
    PauseNotSupportedError,
    ContextError,
    RegistryError,
    PipelineNotFoundError,
    PipelineAlreadyRegisteredError,
)


# Aliases for backwards compatibility
ERENPipeline = CognitivePipeline
ERENPipelineBuilder = PipelineBuilder
ERENPipelineRegistry = PipelineRegistry


__all__ = [
    # Core
    "CognitivePipeline",
    "PipelineContext",
    "PipelineStage",
    "PipelineExecutor",
    "SyncPipelineExecutor",
    # Stages
    "PlanningStage",
    "KnowledgeStage",
    "MemoryStage",
    "ReasoningStage",
    "DecisionStage",
    "ToolStage",
    "ContextUpdateStage",
    # Types
    "PipelineState",
    "StageState",
    "StageType",
    "StageMetadata",
    "StageResult",
    "PipelineResult",
    "PipelineConfig",
    "ExecutionPolicy",
    "PipelineIntent",
    # Builder
    "PipelineBuilder",
    "DefaultPipelineBuilder",
    "PipelinePreset",
    # Registry
    "PipelineRegistry",
    "get_pipeline_registry",
    "register_pipeline",
    "get_pipeline",
    "unregister_pipeline",
    # Policy
    "PipelinePolicy",
    "StopOnFailurePolicy",
    "ContinueOnFailurePolicy",
    "StrictExecutionPolicy",
    "SkipOptionalPolicy",
    "RetryStagePolicy",
    "PolicyFactory",
    "PolicyConfig",
    # Validator
    "PipelineValidator",
    "ValidationResult",
    # Events
    "PipelineEventPublisher",
    "PipelineEventType",
    "get_pipeline_event_publisher",
    "publish_pipeline_event",
    # Metrics
    "PipelineMetrics",
    "get_pipeline_metrics",
    "reset_pipeline_metrics",
    # Trace
    "PipelineTrace",
    "get_pipeline_trace",
    "reset_pipeline_trace",
    # Exceptions
    "PipelineException",
    "PipelineInitializationError",
    "PipelineConfigurationError",
    "PipelineValidationError",
    "DuplicateStageError",
    "InvalidStageOrderError",
    "MissingDependencyError",
    "EmptyPipelineError",
    "ContractNotFoundError",
    "StageException",
    "StageExecutionError",
    "StageTimeoutError",
    "StageSkippedError",
    "StageCancelledError",
    "PipelineExecutionError",
    "PolicyViolationError",
    "PolicyStopOnFailureError",
    "RetryExhaustedError",
    "PipelineStateError",
    "InvalidTransitionError",
    "PipelineNotRunningError",
    "PipelineAlreadyRunningError",
    "CancellationRequestedError",
    "PauseNotSupportedError",
    "ContextError",
    "RegistryError",
    "PipelineNotFoundError",
    "PipelineAlreadyRegisteredError",
    # Aliases
    "ERENPipeline",
    "ERENPipelineBuilder",
    "ERENPipelineRegistry",
]
