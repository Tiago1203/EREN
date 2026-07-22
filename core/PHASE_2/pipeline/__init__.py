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
    >>> from core.PHASE_2.pipeline import ERENPipeline
    >>> pipeline = ERENPipeline.create_default()
    >>> result = pipeline.execute(intent={"query": "..."})
    >>> print(result.status)
"""

from __future__ import annotations

# Builder
from core.PHASE_2.pipeline.builder import (
    DefaultPipelineBuilder,
    PipelineBuilder,
    PipelinePreset,
)
from core.PHASE_2.pipeline.context import PipelineContext

# Observability
from core.PHASE_2.pipeline.events import (
    PipelineEventPublisher,
    PipelineEventType,
    get_pipeline_event_publisher,
    publish_pipeline_event,
)

# Exceptions
from core.PHASE_2.pipeline.exceptions import (
    CancellationRequestedError,
    ContextError,
    ContractNotFoundError,
    DuplicateStageError,
    EmptyPipelineError,
    InvalidStageOrderError,
    InvalidTransitionError,
    MissingDependencyError,
    PauseNotSupportedError,
    PipelineAlreadyRegisteredError,
    PipelineAlreadyRunningError,
    PipelineConfigurationError,
    PipelineException,
    PipelineExecutionError,
    PipelineInitializationError,
    PipelineNotFoundError,
    PipelineNotRunningError,
    PipelineStateError,
    PipelineValidationError,
    PolicyStopOnFailureError,
    PolicyViolationError,
    RegistryError,
    RetryExhaustedError,
    StageCancelledError,
    StageException,
    StageExecutionError,
    StageSkippedError,
    StageTimeoutError,
)
from core.PHASE_2.pipeline.executor import PipelineExecutor, SyncPipelineExecutor
from core.PHASE_2.pipeline.metrics import (
    PipelineMetrics,
    get_pipeline_metrics,
    reset_pipeline_metrics,
)

# Core Pipeline
from core.PHASE_2.pipeline.pipeline import CognitivePipeline

# Policy
from core.PHASE_2.pipeline.policy import (
    ContinueOnFailurePolicy,
    PipelinePolicy,
    PolicyConfig,
    PolicyFactory,
    RetryStagePolicy,
    SkipOptionalPolicy,
    StopOnFailurePolicy,
    StrictExecutionPolicy,
)

# Registry
from core.PHASE_2.pipeline.registry import (
    PipelineRegistry,
    get_pipeline,
    get_pipeline_registry,
    register_pipeline,
    unregister_pipeline,
)
from core.PHASE_2.pipeline.stage import (
    ContextUpdateStage,
    DecisionStage,
    KnowledgeStage,
    MemoryStage,
    PipelineStage,
    PlanningStage,
    ReasoningStage,
    ToolStage,
)
from core.PHASE_2.pipeline.trace import (
    PipelineTrace,
    get_pipeline_trace,
    reset_pipeline_trace,
)

# Types
from core.PHASE_2.pipeline.types import (
    ExecutionPolicy,
    PipelineConfig,
    PipelineIntent,
    PipelineResult,
    PipelineState,
    StageMetadata,
    StageResult,
    StageState,
    StageType,
)

# Validator
from core.PHASE_2.pipeline.validator import PipelineValidator, ValidationResult

# Cognitive Pipeline (PR-048)
from core.PHASE_2.pipeline.cognitive_events import (
    CognitiveEvent,
    CognitiveEventPublisher,
    CognitiveEventType,
    IntentDetectedEvent,
    ContextBuiltEvent,
    MemoryRetrievedEvent,
    KnowledgeRetrievedEvent,
    ReasoningCompletedEvent,
    PlanCreatedEvent,
    DecisionMadeEvent,
    ExecutionCompletedEvent,
    LearningCompletedEvent,
    ResponseGeneratedEvent,
)
from core.PHASE_2.pipeline.cognitive_pipeline import (
    CognitivePipeline,
    CognitivePipelineResult,
    create_cognitive_pipeline,
)
from core.PHASE_2.pipeline.stages import (
    CognitiveStage,
    CognitiveTelemetry,
    IntentDetectionStage,
    ContextBuildingStage,
    MemoryRetrievalStage,
    KnowledgeRetrievalStage,
    CognitiveReasoningStage,
    CognitivePlanningStage,
    CognitiveDecisionStage,
    TaskExecutionStage,
    CognitiveLearningStage,
    ResponseGenerationStage,
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
    # Cognitive Pipeline (PR-048)
    "CognitivePipeline",
    "CognitivePipelineResult",
    "create_cognitive_pipeline",
    # Cognitive Events
    "CognitiveEvent",
    "CognitiveEventPublisher",
    "CognitiveEventType",
    "IntentDetectedEvent",
    "ContextBuiltEvent",
    "MemoryRetrievedEvent",
    "KnowledgeRetrievedEvent",
    "ReasoningCompletedEvent",
    "PlanCreatedEvent",
    "DecisionMadeEvent",
    "ExecutionCompletedEvent",
    "LearningCompletedEvent",
    "ResponseGeneratedEvent",
    # Cognitive Stages
    "CognitiveStage",
    "CognitiveTelemetry",
    "IntentDetectionStage",
    "ContextBuildingStage",
    "MemoryRetrievalStage",
    "KnowledgeRetrievalStage",
    "CognitiveReasoningStage",
    "CognitivePlanningStage",
    "CognitiveDecisionStage",
    "TaskExecutionStage",
    "CognitiveLearningStage",
    "ResponseGenerationStage",
    # Stages (existing)
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
