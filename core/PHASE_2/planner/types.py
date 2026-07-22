"""Type definitions for the Planner engine.

Architecture scaffolding only. These are **type aliases** and **protocols**
that define the shapes the planner operates on — no logic, AI, or agents live here.

This module provides domain-specific types that complement the models in
``models.py``, focusing on higher-level type relationships and constraints.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from enum import IntEnum
from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:
    from .models import Intention, Plan, PlanStep


# --------------------------------------------------------------------------
# Priority levels for tasks and plans
# --------------------------------------------------------------------------


class TaskPriority(IntEnum):
    """Priority levels for plan steps and execution tasks.

    Lower values indicate higher priority. Used by the planner to resolve
    conflicts and by the orchestrator to allocate resources.
    """

    CRITICAL = 1  # Patient safety, emergency protocols
    HIGH = 2  # Time-sensitive clinical operations
    NORMAL = 3  # Standard diagnostic/maintenance workflows
    LOW = 4  # Documentation, reporting, cleanup
    BACKGROUND = 5  # Long-running analysis, learning updates


class TaskStatus(IntEnum):
    """Lifecycle states for plan steps and tasks.

    Mirrors a simplified state machine: PENDING → IN_PROGRESS → COMPLETED,
    with failure states and cancellation paths.
    """

    PENDING = 0
    IN_PROGRESS = 1
    COMPLETED = 2
    FAILED = 3
    CANCELLED = 4
    BLOCKED = 5  # Waiting on dependency


# --------------------------------------------------------------------------
# Goal types
# --------------------------------------------------------------------------


class GoalType(str):
    """Discriminators for the class of goal being planned.

    Allows the planner to apply different strategies based on whether the
    request is a diagnostic query, a maintenance task, a regulatory check,
    etc.
    """

    DIAGNOSTIC = "diagnostic"
    MAINTENANCE = "maintenance"
    REGULATORY = "regulatory"
    CONSULTATION = "consultation"
    RESEARCH = "research"
    REPORT = "report"
    EMERGENCY = "emergency"
    UNKNOWN = "unknown"


# --------------------------------------------------------------------------
# Execution context
# --------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class ExecutionContext:
    """Ambient information available during planning.

    Populated by the Orchestrator before calling the Planner. The planner
    reads (never writes) this object to inform its decisions.
    """

    request_id: str = ""
    session_id: str = ""
    hospital_id: str = ""
    department: str = ""
    device_id: str = ""
    device_type: str = ""
    user_id: str = ""
    user_role: str = ""
    urgency: TaskPriority = TaskPriority.NORMAL
    metadata: dict[str, Any] = field(default_factory=dict)

    def get(self, key: str, default: Any = None) -> Any:
        """Read a metadata key with a default."""
        return self.metadata.get(key, default)


# ------------------------------------------------------------------------------------------------------------------------------------------
# Result types
# --------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class PlannerResult:
    """The complete output of the planner pipeline.

    Wraps the primary output (``Plan``) together with metadata that downstream
    components (Orchestrator, Workflow) need to execute it.
    """

    plan: Plan
    priority: TaskPriority = TaskPriority.NORMAL
    estimated_steps: int = 0
    requires_confirmation: bool = False
    warnings: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)


# ------------------------------------------------------------------------------------------------------------------------------------------
# Strategy protocols
# --------------------------------------------------------------------------


class PlanningStrategy(Protocol):
    """Protocol for pluggable planning strategies.

    A ``PlanningStrategy`` takes an ``Intention`` and produces a raw list of
    ``PlanStep`` (un-ordered, no engine assigned). The planner applies this
    strategy and then post-processes the output through ``select_engines`` and
    ``order_execution``.

    Implementors are free to use any algorithm (rule-based, tree-search,
    LLM-assisted, …) as long as they satisfy this interface.
    """

    def decompose(self, intention: Intention, context: ExecutionContext) -> list[PlanStep]:
        """Break *intention* into candidate steps.

        Steps are returned in discovery order; the planner may reorder them.
        """
        ...


class EngineSelector(Protocol):
    """Protocol for pluggable engine selection strategies.

    Takes a list of ``PlanStep`` and returns the same steps with their
    ``selection`` field populated.
    """

    def select(self, steps: list[PlanStep], context: ExecutionContext) -> list[PlanStep]:
        """Assign an engine to each step."""
        ...


class StepOrderer(Protocol):
    """Protocol for pluggable dependency resolvers.

    Takes a list of ``PlanStep`` (with ``depends_on`` populated) and returns
    them in topologically-sorted execution order.
    """

    def order(self, steps: list[PlanStep]) -> list[PlanStep]:
        """Return steps in execution order."""
        ...


# ------------------------------------------------------------------------------------------------------------------------------------------
# Replanning reasons
# --------------------------------------------------------------------------


class ReplanReason(str):
    """Why the planner is being asked to revise a plan.

    Used by the Orchestrator to communicate the cause of replanning so the
    planner can apply an appropriate strategy.
    """

    STEP_FAILED = "step_failed"
    NEW_INFORMATION = "new_information"
    USER_FEEDBACK = "user_feedback"
    CONTEXT_CHANGED = "context_changed"
    OPTIMIZATION = "optimization"
    TIMEOUT = "timeout"


# ------------------------------------------------------------------------------------------------------------------------------------------
# Callback types for the planning pipeline
# --------------------------------------------------------------------------


PlannerCallback = Callable[[str, dict[str, Any]], Awaitable[None]]
"""Async callback invoked at pipeline milestones.

Called with (event_name, event_data). Used by the Orchestrator to log,
telemetry-instrument, or audit the planning process.
"""

StepValidator = Callable[["PlanStep", "ExecutionContext"], bool]
"""Validator called before a step is added to the plan.

Should return ``True`` to accept the step, ``False`` to reject it.
Used for safety checks, policy enforcement, or permission gates.
"""


# ------------------------------------------------------------------------------------------------------------------------------------------
# Re-exports for convenience
# --------------------------------------------------------------------------


__all__ = [
    # Priority / Status
    "TaskPriority",
    "TaskStatus",
    # Goal types
    "GoalType",
    # Context
    "ExecutionContext",
    # Result
    "PlannerResult",
    # Strategies (protocols)
    "PlanningStrategy",
    "EngineSelector",
    "StepOrderer",
    # Replanning
    "ReplanReason",
    # Callbacks
    "PlannerCallback",
    "StepValidator",
]
