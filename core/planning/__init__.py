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

# Types
from core.planning.types import (
    TaskStatus,
    TaskPriority,
    DependencyType,
    GoalType,
    PlanStatus,
    Task,
    Goal,
    GoalAnalysis,
    ExecutionPlan,
    PlanningMetrics,
)

# Components
from core.planning.goal_analyzer import GoalAnalyzer
from core.planning.task_decomposer import TaskDecomposer
from core.planning.dependency_resolver import DependencyResolver
from core.planning.plan_builder import PlanBuilder

# Events and metrics
from core.planning.events import (
    PlanningEventType,
    PlanningEvent,
    PlanningEventBus,
    get_event_bus,
    reset_event_bus,
)
from core.planning.metrics import PlanningMetricsCollector

# Main engine
from core.planning.planner import (
    CognitivePlanningEngine,
    get_planning_engine,
    reset_planning_engine,
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
