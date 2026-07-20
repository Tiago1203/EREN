"""Abstract interfaces (ports) for the Orchestrator engine.

Defines the contract the orchestrator exposes to callers (e.g. ``apps/*`` via
the SDK) and the shape it expects from the engines it coordinates. Pure
``typing.Protocol`` — method signatures only, no logic, AI, or agents.

The orchestrator's lifecycle, as declared here:

1. **receive a context** — the entry point ``orchestrate`` takes a
   ``CognitiveContext``.
2. **execute a plan** — ``execute_plan`` walks a plan's ordered steps.
3. **invoke engines** — ``invoke_engine`` delegates a step to a cognitive engine.
4. **merge responses** — ``merge_responses`` fuses engine outputs.
5. **return a result** — ``orchestrate`` returns an ``OrchestrationResult``.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Protocol, runtime_checkable

from core.contracts.base import CognitiveEngine

from .models import CognitiveContext, EngineResponse, OrchestrationResult

# Registry the orchestrator coordinates: engine id -> engine implementation.
# Consumers wire concrete engines in; the orchestrator depends only on the
# ``CognitiveEngine`` abstraction (Dependency Inversion).
type EngineRegistry = Mapping[str, CognitiveEngine]


@runtime_checkable
class OrchestratorPort(Protocol):
    """Contract callers use to run a cognitive request end-to-end.

    This is EREN's primary cognitive entry point. Callers depend on this
    abstraction, not on ``OrchestratorEngine`` (Dependency Inversion), so the
    orchestrator is substitutable and testable.
    """

    def orchestrate(self, context: CognitiveContext) -> OrchestrationResult:
        """Receive a *context*, run it to completion, and return the result."""
        ...

    def execute_plan(
        self, context: CognitiveContext, plan: object
    ) -> Sequence[EngineResponse]:
        """Execute *plan* (the planner's ``Plan``) against *context*.

        ``plan`` is typed opaquely to keep the orchestrator decoupled from the
        planner's concrete representation.
        """
        ...

    def invoke_engine(self, engine: str, context: CognitiveContext) -> EngineResponse:
        """Delegate one unit of work to the cognitive engine identified by *engine*."""
        ...

    def merge_responses(
        self, context: CognitiveContext, responses: Sequence[EngineResponse]
    ) -> OrchestrationResult:
        """Fuse per-engine *responses* into a single explainable result."""
        ...
