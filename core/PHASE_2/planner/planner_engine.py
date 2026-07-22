"""Planner Engine — re-export and backwards-compatibility alias.

This module exists for **backwards compatibility** and as a **convenience import**.
All public symbols are re-exported from ``planner.py`` and ``engine.py``.

Import from this module when you need the ``PlannerEngine`` (the original stub
class) or when maintaining existing code that imports from
``core.planner.planner_engine``.

New code should prefer importing directly from the appropriate module:

    from core.PHASE_2.planner import Planner          # Main capability class
    from core.PHASE_2.planner.models import Plan      # Data models
    from core.PHASE_2.planner.types import ExecutionContext  # Type definitions

Architecture scaffolding only — see ``engine.py`` and ``planner.py`` for
full documentation.
"""

from __future__ import annotations

# Re-export the original stub class for backwards compatibility
from .engine import PlannerEngine as PlannerEngine

# Re-export models
from .models import (
    CognitiveEngineId as CognitiveEngineId,
)
from .models import (
    EngineSelection as EngineSelection,
)
from .models import (
    Intention as Intention,
)
from .models import (
    Plan as Plan,
)
from .models import (
    PlanStep as PlanStep,
)
from .planner import (
    EngineSelectionError as EngineSelectionError,
)
from .planner import (
    InvalidIntentionError as InvalidIntentionError,
)
from .planner import (
    PlanCreationError as PlanCreationError,
)

# Re-export the main capability class
from .planner import (
    Planner as Planner,
)
from .planner import (
    PlannerError as PlannerError,
)
from .planner import (
    StepOrderingError as StepOrderingError,
)

# Re-export types
from .types import (
    EngineSelector as EngineSelector,
)
from .types import (
    ExecutionContext as ExecutionContext,
)
from .types import (
    GoalType as GoalType,
)
from .types import (
    PlannerCallback as PlannerCallback,
)
from .types import (
    PlannerResult as PlannerResult,
)
from .types import (
    PlanningStrategy as PlanningStrategy,
)
from .types import (
    ReplanReason as ReplanReason,
)
from .types import (
    StepOrderer as StepOrderer,
)
from .types import (
    StepValidator as StepValidator,
)
from .types import (
    TaskPriority as TaskPriority,
)
from .types import (
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
