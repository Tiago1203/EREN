"""EREN Cognitive Planning Engine (CPE).

The first cognitive planning system of EREN.
Transforms user intent into execution plans.

Philosophy:
    LLM responds.
    Planning Engine decides what to do.
    
    Never executes tasks.
    Never queries providers.
    Never uses OpenAI directly.
    
    Only generates plans.

Example:
    User: "The Philips MX450 monitor won't turn on. Analyze the problem."
    
    Planning Engine:
    
    Plan:
        1. Consult device history
        2. Search technical manual
        3. Retrieve similar incidents
        4. Consult maintenance protocols
        5. Execute technical reasoning
        6. Generate diagnosis
    
    Execution Coordinator executes each step via existing capabilities.
"""

from __future__ import annotations

from core.PHASE_2.planning.dependency_resolver import DependencyResolver

# Events and metrics
from core.PHASE_2.planning.events import (
    PlanningEvent,
    PlanningEventBus,
    PlanningEventType,
    get_event_bus,
    reset_event_bus,
)

# Components
from core.PHASE_2.planning.goal_analyzer import GoalAnalyzer
from core.PHASE_2.planning.metrics import PlanningMetricsCollector
from core.PHASE_2.planning.plan_builder import PlanBuilder

# Main engine
from core.PHASE_2.planning.planner import (
    CognitivePlanningEngine,
    get_planning_engine,
    reset_planning_engine,
)
from core.PHASE_2.planning.task_decomposer import TaskDecomposer

# Types
from core.PHASE_2.planning.types import (
    DependencyType,
    ExecutionPlan,
    Goal,
    GoalAnalysis,
    GoalType,
    PlanningMetrics,
    PlanStatus,
    Task,
    TaskPriority,
    TaskStatus,
)

__all__ = [
    # Types
    "TaskStatus",
    "TaskPriority",
    "DependencyType",
    "GoalType",
    "PlanStatus",
    "Task",
    "Goal",
    "GoalAnalysis",
    "ExecutionPlan",
    "PlanningMetrics",
    # Components
    "GoalAnalyzer",
    "TaskDecomposer",
    "DependencyResolver",
    "PlanBuilder",
    # Events
    "PlanningEventType",
    "PlanningEvent",
    "PlanningEventBus",
    "get_event_bus",
    "reset_event_bus",
    # Metrics
    "PlanningMetricsCollector",
    # Main engine
    "CognitivePlanningEngine",
    "get_planning_engine",
    "reset_planning_engine",
]
