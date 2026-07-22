"""Cognitive Runtime — the core of EREN's Cognitive Operating System.

This module provides the complete Cognitive Runtime implementation,
which coordinates the execution of the cognitive cycle through all
existing contracts and components.

Usage:
    from core.PHASE_2.runtime import CognitiveRuntime, RuntimeBuilder

    # Using the builder
    runtime = (
        RuntimeBuilder()
        .with_simulation_mode(True)
        .build()
    )
    runtime.initialize().boot().validate().start()

    # Create and execute a session
    session = runtime.create_session()
    runtime.execute_cognitive_cycle(session, intent={"query": "test"})

    # Get results
    print(f"Events: {len(runtime.events)}")
    print(f"Metrics: {runtime.metrics.get_summary()}")

    # Shutdown
    runtime.shutdown()

Components:
    - CognitiveRuntime: Main runtime coordinator
    - RuntimeBuilder: Fluent builder for runtime configuration
    - RuntimeConfiguration: Configuration options
    - RuntimeContext: Execution context
    - RuntimeExecutor: Cognitive cycle executor
    - RuntimeState: State management
    - RuntimeEvents: Event definitions
    - RuntimeMetrics: Metrics collection
    - RuntimeTrace: Tracing
    - RuntimeHealth: Health checks
    - RuntimeValidator: Validation
    - Exceptions: All runtime exceptions

Architecture:
    The Runtime does NOT think, decide, or use AI.
    It ONLY coordinates the flow through existing contracts.

Example:
    # Simple example
    runtime = (
        CognitiveRuntime()
        .with_simulation_mode(True)
        .build()
    )
    runtime.start()

    session = runtime.create_session()
    runtime.execute_cognitive_cycle(
        session,
        intent={"query": "Diagnose device issue"}
    )

    runtime.shutdown()
"""

from __future__ import annotations

# Exceptions
from .exceptions import (
    CognitiveCycleError,
    ComponentNotAvailableError,
    EngineExecutionError,
    HealthCheckError,
    RuntimeBootError,
    RuntimeException,
    RuntimeExecutionError,
    RuntimeInitializationError,
    RuntimeShutdownError,
    RuntimeStartError,
    RuntimeValidationError,
    SessionCreationError,
)

# Main Runtime
from .runtime import CognitiveRuntime

# Builder
from .runtime_builder import (
    RuntimeBuilder,
    create_default_runtime,
    create_development_runtime,
    create_minimal_runtime,
    create_production_runtime,
    create_testing_runtime,
)

# Configuration
from .runtime_configuration import (
    EngineConfiguration,
    RuntimeConfiguration,
    SessionConfiguration,
)

# Context
from .runtime_context import (
    ComponentReferences,
    CycleContext,
    RuntimeContext,
    SessionContext,
)

# Events
from .runtime_events import (
    EVENT_TYPE_TO_CLASS,
    CognitiveCycleCompleted,
    CognitiveCycleFailed,
    CognitiveCycleStarted,
    ContextSnapshot,
    ContextUpdated,
    DecisionApplied,
    DecisionCreated,
    DecisionFailed,
    KnowledgeFailed,
    KnowledgeRequested,
    KnowledgeRetrieved,
    MemoryFailed,
    MemoryRequested,
    MemoryRetrieved,
    PlanningCompleted,
    PlanningFailed,
    PlanningStarted,
    ReasoningCompleted,
    ReasoningFailed,
    ReasoningStarted,
    RuntimeBootCompleted,
    RuntimeBootStarted,
    RuntimeCompleted,
    RuntimeEvent,
    RuntimeEventType,
    RuntimeFailed,
    RuntimeInitialized,
    RuntimeShutdown,
    RuntimeStarted,
    RuntimeValidationCompleted,
    RuntimeValidationStarted,
    SessionCompleted,
    SessionCreated,
    SessionFailed,
    SessionStarted,
    create_runtime_event,
)

# Executor
from .runtime_executor import CognitiveCycleExecutor, ExecutionResult

# Health
from .runtime_health import (
    ComponentHealth,
    ComponentType,
    HealthStatus,
    RuntimeHealth,
    RuntimeHealthChecker,
)

# Metrics
from .runtime_metrics import (
    CycleMetrics,
    EngineMetrics,
    RuntimeMetrics,
    SessionMetrics,
    StageMetrics,
)

# State
from .runtime_state import (
    CognitiveCycleState,
    CycleStateInfo,
    RuntimeState,
    RuntimeStateInfo,
    RuntimeStateMachine,
    SessionState,
    SessionStateInfo,
    SessionStateMachine,
)

# Trace
from .runtime_trace import (
    EngineExecutionTrace,
    EventPublicationTrace,
    RuntimeTraceCollector,
    TraceEntry,
    TransitionTrace,
)

# Validator
from .runtime_validator import RuntimeValidator, ValidationReport, ValidationResult

__all__ = [
    # Main Runtime
    "CognitiveRuntime",
    # Builder
    "RuntimeBuilder",
    "create_default_runtime",
    "create_development_runtime",
    "create_minimal_runtime",
    "create_production_runtime",
    "create_testing_runtime",
    # Configuration
    "RuntimeConfiguration",
    "SessionConfiguration",
    "EngineConfiguration",
    # Context
    "RuntimeContext",
    "SessionContext",
    "CycleContext",
    "ComponentReferences",
    # State
    "RuntimeState",
    "RuntimeStateInfo",
    "RuntimeStateMachine",
    "SessionState",
    "SessionStateInfo",
    "SessionStateMachine",
    "CognitiveCycleState",
    "CycleStateInfo",
    # Events
    "RuntimeEvent",
    "RuntimeEventType",
    "EVENT_TYPE_TO_CLASS",
    "create_runtime_event",
    "RuntimeStarted",
    "RuntimeInitialized",
    "RuntimeBootStarted",
    "RuntimeBootCompleted",
    "RuntimeValidationStarted",
    "RuntimeValidationCompleted",
    "SessionCreated",
    "SessionStarted",
    "SessionCompleted",
    "SessionFailed",
    "CognitiveCycleStarted",
    "CognitiveCycleCompleted",
    "CognitiveCycleFailed",
    "PlanningStarted",
    "PlanningCompleted",
    "PlanningFailed",
    "KnowledgeRequested",
    "KnowledgeRetrieved",
    "KnowledgeFailed",
    "MemoryRequested",
    "MemoryRetrieved",
    "MemoryFailed",
    "ReasoningStarted",
    "ReasoningCompleted",
    "ReasoningFailed",
    "DecisionCreated",
    "DecisionApplied",
    "DecisionFailed",
    "ContextUpdated",
    "ContextSnapshot",
    "RuntimeCompleted",
    "RuntimeFailed",
    "RuntimeShutdown",
    # Executor
    "CognitiveCycleExecutor",
    "ExecutionResult",
    # Health
    "RuntimeHealth",
    "RuntimeHealthChecker",
    "ComponentHealth",
    "ComponentType",
    "HealthStatus",
    # Metrics
    "RuntimeMetrics",
    "SessionMetrics",
    "CycleMetrics",
    "StageMetrics",
    "EngineMetrics",
    # Trace
    "RuntimeTraceCollector",
    "TraceEntry",
    "TransitionTrace",
    "EngineExecutionTrace",
    "EventPublicationTrace",
    # Validator
    "RuntimeValidator",
    "ValidationReport",
    "ValidationResult",
    # Exceptions
    "RuntimeException",
    "RuntimeInitializationError",
    "RuntimeBootError",
    "RuntimeValidationError",
    "RuntimeStartError",
    "RuntimeExecutionError",
    "RuntimeShutdownError",
    "SessionCreationError",
    "CognitiveCycleError",
    "HealthCheckError",
    "ComponentNotAvailableError",
    "EngineExecutionError",
]
