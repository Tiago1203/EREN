"""Domain models for the Planner engine.

Architecture scaffolding only. These are **data structure declarations** for the
shapes the planner operates on — no logic, AI, or agents live here. Fields are
intentionally minimal and may evolve as responsibilities are formalized.

The planner pipeline moves through four shapes:

``Intention`` → (create plan) → ``PlanStep`` → (select engines) →
``EngineSelection`` → (order execution) → ``Plan``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class CognitiveEngineId(str, Enum):
    """Identifiers of the cognitive engines the planner may schedule.

    Mirrors the engines under ``core/``. Used to reference a target engine
    without importing its concrete class (keeps the planner decoupled).
    """

    ORCHESTRATOR = "orchestrator"
    PLANNER = "planner"
    REASONING = "reasoning"
    MEMORY = "memory"
    KNOWLEDGE = "knowledge"
    DIAGNOSTIC = "diagnostic"
    WORKFLOW = "workflow"
    TOOLS = "tools"


@dataclass(frozen=True, slots=True)
class Intention:
    """A normalized statement of what the caller wants to achieve.

    The planner's entry shape (result of "receive intention"). Concrete fields
    for goal, constraints and context will be refined later.
    """

    goal: str = ""


@dataclass(frozen=True, slots=True)
class EngineSelection:
    """The engine chosen to carry out a single step, and why.

    Produced by the "select engines" responsibility. ``engine`` references a
    cognitive engine by id; ``rationale`` documents the (future) selection
    justification for explainability.
    """

    engine: CognitiveEngineId
    rationale: str = ""


@dataclass(frozen=True, slots=True)
class PlanStep:
    """A single, discrete unit of work within a plan.

    Carries its position (``order``), the engine assigned to it
    (``selection``), and the ids of steps it depends on (``depends_on``).
    """

    order: int
    selection: EngineSelection
    description: str = ""
    depends_on: tuple[int, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class Plan:
    """An ordered, executable plan derived from an ``Intention``.

    The planner's output shape: the intention it addresses plus the ordered
    steps the orchestrator will execute.
    """

    intention: Intention
    steps: tuple[PlanStep, ...] = field(default_factory=tuple)
