"""
PHASE 5 - EPIC 6: Planning Agent

Agente dedicado a generar planes de acción.
Convierte decisiones clínicas en planes ejecutables.
"""

from __future__ import annotations

# =============================================================================
# VERSION
# =============================================================================

__version__ = "1.0.0"
__epic__ = "EPIC_6"
__phase__ = "PHASE_5"


# =============================================================================
# IMPORTS FROM SUBMODULES
# =============================================================================

# Domain
from core.PHASE_5.epic6_planning_agent.domain import (
    # Action Plan
    ActionPlan,
    ActionItem,
    ActionPriority,
    ActionStatus,
    # Clinical Plan
    ClinicalPlan,
    ClinicalPhase,
    # Execution Task
    ExecutionTask,
    TaskType,
    TaskStatus,
)

# Engines
from core.PHASE_5.epic6_planning_agent.engines import (
    # Action Planner
    ActionPlanner,
    PlanResult,
    # Schedule Generator
    ScheduleGenerator,
    ScheduleResult,
    # Task Generator
    TaskGenerator,
    TaskResult,
    # Risk Planner
    RiskPlanner,
    RiskAssessment,
)

# Agent
from core.PHASE_5.epic6_planning_agent.agent import (
    PlanningAgent,
    PlanningAgentConfig,
)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Version
    "__version__",
    "__epic__",
    "__phase__",
    # Domain
    "ActionPlan",
    "ActionItem",
    "ActionPriority",
    "ActionStatus",
    "ClinicalPlan",
    "ClinicalPhase",
    "ExecutionTask",
    "TaskType",
    "TaskStatus",
    # Engines
    "ActionPlanner",
    "PlanResult",
    "ScheduleGenerator",
    "ScheduleResult",
    "TaskGenerator",
    "TaskResult",
    "RiskPlanner",
    "RiskAssessment",
    # Agent
    "PlanningAgent",
    "PlanningAgentConfig",
]
