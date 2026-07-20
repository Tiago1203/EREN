"""Domain models for the Orchestrator engine.

Domain models for orchestration including context, responses, and plan steps.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True, slots=True)
class CognitiveContext:
    """Everything the orchestrator needs to serve one cognitive request.

    The orchestrator's input shape ("receive a context"). Carries the request
    plus the ambient information required for multi-tenant isolation and
    auditability.
    """

    request: str = ""
    tenant_id: str = ""
    correlation_id: str = ""
    metadata: Mapping[str, str] = field(default_factory=dict)


@dataclass
class PlanStep:
    """A single step in an execution plan."""
    step_id: str
    engine: str
    action: str
    input_data: dict[str, Any] = field(default_factory=dict)
    depends_on: list[str] = field(default_factory=list)


@dataclass
class EngineResponse:
    """A single engine's contribution to the request.

    Produced by "invoke engines". ``engine`` is the id of the engine that ran;
    ``output`` is its opaque output; ``confidence`` supports explainability.
    """

    engine: str
    success: bool = True
    output: Any = None
    error: str | None = None
    confidence: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ExecutionState:
    """Intermediate state accumulated while executing a plan.

    Holds the originating context and the engine responses gathered so far, so
    the orchestrator can pass evolving state between steps without globals.
    """

    context: CognitiveContext
    responses: tuple[EngineResponse, ...] = field(default_factory=tuple)


@dataclass
class OrchestrationResult:
    """The final, explainable result returned to the caller.

    Produced by "merge responses". Bundles the merged ``output`` with the
    context it answered and the per-engine responses that support it (evidence
    trail for auditability).
    """

    context: CognitiveContext
    responses: Sequence[EngineResponse] = field(default_factory=tuple)
    output: Any = None
    success: bool = True
    confidence: float = 0.0
    execution_summary: dict[str, Any] = field(default_factory=dict)
