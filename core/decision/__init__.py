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

# Types
from core.decision.types import (
    # Enums
    DecisionStrategy,
    ExecutionPolicy,
    RiskLevel,
    TaskStatus,
    TaskPriority,
    DependencyType,
    GoalType,
    DecisionStatus,
    # Classes
    DecisionTask,
    Goal,
    GoalAnalysis,
    DecisionPlan,
    StrategySelection,
    RiskAssessment,
    ExecutionDecision,
    ReplanningReason,
    DecisionMetrics,
)

# Components
from core.decision.goal_analyzer import GoalAnalyzer
from core.decision.task_decomposer import TaskDecomposer
from core.decision.dependency_resolver import DependencyResolver
from core.decision.strategy_selector import StrategySelector
from core.decision.risk_evaluator import RiskEvaluator
from core.decision.execution_policy import ExecutionPolicyManager
from core.decision.replanner import Replanner
from core.decision.decision_builder import DecisionBuilder

# Events and metrics
from core.decision.events import (
    DecisionEventType,
    DecisionEvent,
    DecisionEventBus,
    get_event_bus,
    reset_event_bus,
)
from core.decision.metrics import DecisionMetricsCollector

# Main engine
from core.decision.engine import (
    CognitiveDecisionEngine,
    get_decision_engine,
    reset_decision_engine,
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
