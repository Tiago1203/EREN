"""Planner Engine — re-export and backwards-compatibility alias.

This module exists for **backwards compatibility** and as a **convenience import**.
All public symbols are re-exported from ``planner.py`` and ``engine.py``.

Import from this module when you need the ``PlannerEngine`` (the original stub
class) or when maintaining existing code that imports from
``core.planner.planner_engine``.

New code should prefer importing directly from the appropriate module:

    from core.planner import Planner          # Main capability class
    from core.planner.models import Plan      # Data models
    from core.planner.types import ExecutionContext  # Type definitions

Architecture scaffolding only — see ``engine.py`` and ``planner.py`` for
full documentation.
"""

from __future__ import annotations

# Re-export the original stub class for backwards compatibility
from .engine import PlannerEngine as PlannerEngine

# Re-export the main capability class
from .planner import (
    Planner as Planner,
    EngineSelectionError as EngineSelectionError,
    InvalidIntentionError as InvalidIntentionError,
    PlanCreationError as PlanCreationError,
    PlannerError as PlannerError,
    StepOrderingError as StepOrderingError,
)

# Re-export models
from .models import (
    CognitiveEngineId as CognitiveEngineId,
    EngineSelection as EngineSelection,
    Intention as Intention,
    Plan as Plan,
    PlanStep as PlanStep,
)

# Re-export types
from .types import (
    EngineSelector as EngineSelector,
    ExecutionContext as ExecutionContext,
    GoalType as GoalType,
    PlannerCallback as PlannerCallback,
    PlannerResult as PlannerResult,
    PlanningStrategy as PlanningStrategy,
    ReplanReason as ReplanReason,
    StepOrderer as StepOrderer,
    StepValidator as StepValidator,
    TaskPriority as TaskPriority,
    TaskStatus as TaskStatus,
)

__all__ = [
    # Classes
    "Planner",
    "PlannerEngine",
    # Exceptions
    "PlannerError",
    "InvalidIntentionError",
    "PlanCreationError",
    "EngineSelectionError",
    "StepOrderingError",
    # Models
    "CognitiveEngineId",
    "EngineSelection",
    "Intention",
    "Plan",
    "PlanStep",
    # Types
    "EngineSelector",
    "ExecutionContext",
    "GoalType",
    "PlannerCallback",
    "PlannerResult",
    "PlanningStrategy",
    "ReplanReason",
    "StepOrderer",
    "StepValidator",
    "TaskPriority",
    "TaskStatus",
]
