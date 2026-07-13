"""EREN core — Orchestrator engine. Scaffolding only; no functionality yet."""

from .engine import OrchestratorEngine
from .exceptions import (
    ContextError,
    EngineInvocationError,
    EngineNotRegisteredError,
    OrchestratorError,
    PlanExecutionError,
    ResponseMergeError,
)
from .interfaces import EngineRegistry, OrchestratorPort
from .models import (
    CognitiveContext,
    EngineResponse,
    ExecutionState,
    OrchestrationResult,
)

__all__ = [
    "OrchestratorEngine",
    "OrchestratorPort",
    "EngineRegistry",
    "OrchestratorError",
    "ContextError",
    "PlanExecutionError",
    "EngineInvocationError",
    "EngineNotRegisteredError",
    "ResponseMergeError",
    "CognitiveContext",
    "EngineResponse",
    "ExecutionState",
    "OrchestrationResult",
]
