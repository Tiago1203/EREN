"""Cognitive Orchestration Contracts for EREN.

Provides the infrastructure for coordinating all cognitive engines.

Architecture only -- no implementations, no business logic.

The orchestration contracts define:
- Common interface for all cognitive engines
- Cognitive cycle states and phases
- Engine state management
- Pipeline execution order
- Shared orchestration context
"""

from __future__ import annotations

from core.orchestration.cognitive_cycle import (
    DEFAULT_CYCLE_CONFIG,
    PHASE_DEPENDENCIES,
    PHASE_ENGINE_MAP,
    CognitiveCycle,
    CycleConfiguration,
    CycleMetadata,
    CyclePhase,
    CycleState,
    PhaseResult,
    PhaseTransition,
)
from core.orchestration.engine_pipeline import (
    PipelineBuilder,
    PipelineDefinition,
    PipelineExecutor,
    PipelineStage,
    get_default_pipeline,
)
from core.orchestration.engine_result import (
    EngineResult,
    ResultFactory,
    ResultStatus,
    ResultType,
)
from core.orchestration.engine_state import (
    EngineState,
    EngineStateManager,
    StateTransition,
    get_state_manager,
)
from core.orchestration.execution_graph import (
    EdgeType,
    ExecutionGraph,
    ExecutionGraphFactory,
    GraphEdge,
    GraphNode,
    NodeType,
)
from core.orchestration.orchestration_context import (
    ContextFactory,
    ContextKey,
    OrchestrationContext,
)
from core.orchestration.orchestration_contracts import (
    CognitiveEngine,
    ContractViolationError,
    EngineRegistry,
    EngineType,
    Plannable,
    Stateful,
)
from core.orchestration.transition_manager import (
    TransitionHandler,
    TransitionManager,
    get_transition_manager,
)

__all__ = [
    # Contracts
    "CognitiveEngine",
    "EngineRegistry",
    "EngineType",
    "Plannable",
    "Stateful",
    "ContractViolationError",
    # Cycle
    "CognitiveCycle",
    "CycleState",
    "CyclePhase",
    "CycleMetadata",
    "CycleConfiguration",
    "PhaseTransition",
    "PhaseResult",
    "PHASE_DEPENDENCIES",
    "PHASE_ENGINE_MAP",
    "DEFAULT_CYCLE_CONFIG",
    # Engine State
    "EngineState",
    "EngineStateManager",
    "StateTransition",
    "get_state_manager",
    # Engine Result
    "EngineResult",
    "ResultStatus",
    "ResultType",
    "ResultFactory",
    # Pipeline
    "PipelineDefinition",
    "PipelineExecutor",
    "PipelineBuilder",
    "PipelineStage",
    "get_default_pipeline",
    # Execution Graph
    "ExecutionGraph",
    "ExecutionGraphFactory",
    "GraphNode",
    "GraphEdge",
    "NodeType",
    "EdgeType",
    # Context
    "OrchestrationContext",
    "ContextKey",
    "ContextFactory",
    # Transition
    "TransitionManager",
    "TransitionHandler",
    "get_transition_manager",
]
