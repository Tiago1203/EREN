"""Domain models for the Orchestrator engine.

Architecture scaffolding only. These are **data structure declarations** for the
shapes the orchestrator moves through — no logic, AI, or agents live here.
Fields are intentionally minimal and may evolve.

Lifecycle shapes:

``CognitiveContext`` (in) → (execute plan / invoke engines) → ``EngineResponse``
accumulated in ``ExecutionState`` → (merge) → ``OrchestrationResult`` (out).
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class CognitiveContext:
    """Everything the orchestrator needs to serve one cognitive request.

    The orchestrator's input shape ("receive a context"). Carries the request
    plus the ambient information required for multi-tenant isolation and
    auditability. Concrete fields will be refined later.
    """

    request: str = ""
    tenant_id: str = ""
    correlation_id: str = ""
    metadata: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class EngineResponse:
    """A single engine's contribution to the request.

    Produced by "invoke engines". ``engine`` is the id of the engine that ran;
    ``payload`` is its opaque output (typed later); ``confidence`` supports the
    future explainability/confidence requirements.
    """

    engine: str
    payload: object = None
    confidence: float = 0.0


@dataclass(frozen=True, slots=True)
class ExecutionState:
    """Intermediate state accumulated while executing a plan.

    Holds the originating context and the engine responses gathered so far, so
    the orchestrator can pass evolving state between steps without globals.
    """

    context: CognitiveContext
    responses: tuple[EngineResponse, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class OrchestrationResult:
    """The final, explainable result returned to the caller.

    Produced by "merge responses". Bundles the merged ``output`` with the
    context it answered and the per-engine responses that support it (evidence
    trail for auditability).
    """

    context: CognitiveContext
    responses: tuple[EngineResponse, ...] = field(default_factory=tuple)
    output: object = None
