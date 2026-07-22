"""EREN Cognitive Decision Engine (CDE).

Refactored from Planning Engine to be a complete decision-making system.

Philosophy:
    Planning is only part of decision-making.
    The Decision Engine decides the best strategy to achieve a cognitive goal.

    LLM responds.
    Decision Engine decides what to do.

    Never executes tasks.
    Never queries providers.
    Never uses OpenAI directly.

    Only takes decisions.

Architecture:
    Decision Engine
        ├── Goal Analyzer
        ├── Planning Module
        │        ├── Task Decomposer
        │        └── Dependency Resolver
        ├── Strategy Selector
        ├── Risk Evaluator
        ├── Execution Policy
        ├── Replanner
        ├── Decision Builder
        └── Metrics
"""

from __future__ import annotations

from core.PHASE_2.decision.decision_builder import DecisionBuilder
from core.PHASE_2.decision.dependency_resolver import DependencyResolver

# Main engine
from core.PHASE_2.decision.engine import (
    CognitiveDecisionEngine,
    get_decision_engine,
    reset_decision_engine,
)

# Events and metrics
from core.PHASE_2.decision.events import (
    DecisionEvent,
    DecisionEventBus,
    DecisionEventType,
    get_event_bus,
    reset_event_bus,
)
from core.PHASE_2.decision.execution_policy import ExecutionPolicyManager

# Components
from core.PHASE_2.decision.goal_analyzer import GoalAnalyzer
from core.PHASE_2.decision.metrics import DecisionMetricsCollector
from core.PHASE_2.decision.replanner import Replanner
from core.PHASE_2.decision.risk_evaluator import RiskEvaluator
from core.PHASE_2.decision.strategy_selector import StrategySelector
from core.PHASE_2.decision.task_decomposer import TaskDecomposer

# Types
from core.PHASE_2.decision.types import (
    DecisionMetrics,
    DecisionPlan,
    DecisionStatus,
    # Enums
    DecisionStrategy,
    # Classes
    DecisionTask,
    DependencyType,
    ExecutionDecision,
    ExecutionPolicy,
    Goal,
    GoalAnalysis,
    GoalType,
    ReplanningReason,
    RiskAssessment,
    RiskLevel,
    StrategySelection,
    TaskPriority,
    TaskStatus,
)

__all__ = [
    # Enums
    "DecisionStrategy",
    "ExecutionPolicy",
    "RiskLevel",
    "TaskStatus",
    "TaskPriority",
    "DependencyType",
    "GoalType",
    "DecisionStatus",
    # Classes
    "DecisionTask",
    "Goal",
    "GoalAnalysis",
    "DecisionPlan",
    "StrategySelection",
    "RiskAssessment",
    "ExecutionDecision",
    "ReplanningReason",
    "DecisionMetrics",
    # Components
    "GoalAnalyzer",
    "TaskDecomposer",
    "DependencyResolver",
    "StrategySelector",
    "RiskEvaluator",
    "ExecutionPolicyManager",
    "Replanner",
    "DecisionBuilder",
    # Events
    "DecisionEventType",
    "DecisionEvent",
    "DecisionEventBus",
    "get_event_bus",
    "reset_event_bus",
    # Metrics
    "DecisionMetricsCollector",
    # Main engine
    "CognitiveDecisionEngine",
    "get_decision_engine",
    "reset_decision_engine",
]
