"""Exception types for the Orchestrator engine.

Scaffolding only — type declarations, no logic. One base error plus a subclass
per lifecycle stage so callers can handle orchestration failures granularly.
"""

from __future__ import annotations


class OrchestratorError(Exception):
    """Base class for all orchestrator-related errors."""


class ContextError(OrchestratorError):
    """Raised when the incoming ``CognitiveContext`` is missing or invalid."""


class PlanExecutionError(OrchestratorError):
    """Raised when a plan cannot be executed to completion."""


class EngineInvocationError(OrchestratorError):
    """Raised when an invoked cognitive engine fails."""


class EngineNotRegisteredError(OrchestratorError):
    """Raised when a step targets an engine that is not in the registry."""


class ResponseMergeError(OrchestratorError):
    """Raised when engine responses cannot be merged into a result."""
