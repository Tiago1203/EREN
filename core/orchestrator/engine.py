"""Orchestrator engine for EREN core — the heart of EREN.

Architecture scaffolding only. The class fixes the **shape** of the
orchestration capability — the lifecycle of a cognitive request — but contains
no logic, AI, or agents. Method bodies raise ``NotImplementedError`` until
behavior is designed.
"""

from __future__ import annotations

from collections.abc import Sequence

from .exceptions import OrchestratorError
from .interfaces import EngineRegistry
from .models import CognitiveContext, EngineResponse, OrchestrationResult


class OrchestratorEngine:
    """Coordinates EREN's cognitive engines across a request lifecycle.

    The central nervous system: it **receives a context**, **executes a plan**,
    **invokes engines**, **merges their responses**, and **returns a result**.
    It is the only engine that knows about the others; each other engine stays
    independent and is composed *by* the orchestrator. It delegates — it does
    not plan, reason, or implement domain logic itself.

    Satisfies :class:`~core.contracts.base.CognitiveEngine` and, structurally,
    :class:`core.orchestrator.interfaces.OrchestratorPort`.

    Engines are injected as a registry (Dependency Inversion): the orchestrator
    depends only on the ``CognitiveEngine`` abstraction, never on concrete
    engine classes.
    """

    def __init__(self, engines: EngineRegistry | None = None) -> None:
        self._engines: EngineRegistry = engines if engines is not None else {}

    @property
    def name(self) -> str:
        """Stable identifier of this engine."""
        return "orchestrator"

    def describe(self) -> str:
        """Human-readable description of the orchestrator capability."""
        return "Coordinates cognitive engines across a request lifecycle."

    def orchestrate(self, context: CognitiveContext) -> OrchestrationResult:
        """Receive a *context*, run it to completion, and return the result."""
        raise NotImplementedError

    def execute_plan(
        self, context: CognitiveContext, plan: object
    ) -> Sequence[EngineResponse]:
        """Execute *plan* (the planner's ``Plan``) against *context*."""
        raise NotImplementedError

    def invoke_engine(self, engine: str, context: CognitiveContext) -> EngineResponse:
        """Delegate one unit of work to the cognitive engine identified by *engine*."""
        raise NotImplementedError

    def merge_responses(
        self, context: CognitiveContext, responses: Sequence[EngineResponse]
    ) -> OrchestrationResult:
        """Fuse per-engine *responses* into a single explainable result."""
        raise NotImplementedError


__all__ = ["OrchestratorEngine", "OrchestratorError"]
