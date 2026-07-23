"""
PHASE 5 - EPIC 10: Agent Learning & Optimization

Motor de aprendizaje y optimización para agentes.
Optimiza continuamente el comportamiento de los agentes.
"""

from __future__ import annotations

# =============================================================================
# VERSION
# =============================================================================

__version__ = "1.0.0"
__epic__ = "EPIC_10"
__phase__ = "PHASE_5"


# =============================================================================
# IMPORTS FROM SUBMODULES
# =============================================================================

# Domain
from core.PHASE_5.epic10_learning.domain import (
    # Agent Metric
    AgentMetric,
    MetricType,
    MetricValue,
    # Learning Session
    LearningSession,
    SessionStatus,
    # Optimization Report
    OptimizationReport,
    OptimizationType,
    Recommendation,
)

# Engines
from core.PHASE_5.epic10_learning.engines import (
    # Performance Analyzer
    PerformanceAnalyzer,
    AnalysisResult,
    # Strategy Optimizer
    StrategyOptimizer,
    OptimizationResult,
    # Agent Evaluator
    AgentEvaluator,
    EvaluationResult,
    # Collaboration Optimizer
    CollaborationOptimizer,
    CollabOptimizationResult,
)

# Agent
from core.PHASE_5.epic10_learning.agent import (
    AgentLearningEngine,
    AgentLearningConfig,
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
    "AgentMetric",
    "MetricType",
    "MetricValue",
    "LearningSession",
    "SessionStatus",
    "OptimizationReport",
    "OptimizationType",
    "Recommendation",
    # Engines
    "PerformanceAnalyzer",
    "AnalysisResult",
    "StrategyOptimizer",
    "OptimizationResult",
    "AgentEvaluator",
    "EvaluationResult",
    "CollaborationOptimizer",
    "CollabOptimizationResult",
    # Agent
    "AgentLearningEngine",
    "AgentLearningConfig",
]
