"""EREN core — Planner engine.

Architecture scaffolding. Exports the primary ``Planner`` capability class,
all data models, types, and exceptions.

For backwards compatibility, the original ``PlannerEngine`` stub class is also
re-exported via ``planner_engine`` submodule.
"""

from .engine import PlannerEngine
from .exceptions import (
    EngineSelectionError,
    ExecutionOrderError,
    IntentionError,
    InvalidIntentionError,
    PlanCreationError,
    PlannerError,
    StepOrderingError,
)
from .interfaces import PlannerPort
from .models import (
    CognitiveEngineId,
    EngineSelection,
    Intention,
    Plan,
    PlanStep,
)
from .planner import Planner
from .types import (
    EngineSelector,
    ExecutionContext,
    GoalType,
    PlannerCallback,
    PlannerResult,
    PlanningStrategy,
    ReplanReason,
    StepOrderer,
    StepValidator,
    TaskPriority,
    TaskStatus,
)

__all__ = [
    # Primary capability
    "Planner",
    # Legacy stub (for backwards compatibility)
    "PlannerEngine",
    # Contract
    "PlannerPort",
    # Exceptions
    "PlannerError",
    "InvalidIntentionError",
    "IntentionError",
    "PlanCreationError",
    "EngineSelectionError",
    "StepOrderingError",
    "ExecutionOrderError",
    # Models
    "CognitiveEngineId",
    "Intention",
    "EngineSelection",
    "PlanStep",
    "Plan",
    # Types
    "TaskPriority",
    "TaskStatus",
    "GoalType",
    "ExecutionContext",
    "PlannerResult",
    "PlanningStrategy",
    "EngineSelector",
    "StepOrderer",
    "ReplanReason",
    "PlannerCallback",
    "StepValidator",
]
