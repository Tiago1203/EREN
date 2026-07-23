"""
PHASE 5 - EPIC 1: Agent Orchestrator

Sistema de orquestación de agentes especializados.
Coordina qué agentes participan, en qué orden, y cómo combinar sus resultados.

MEJORA: Incluye OrchestratorAgent que conecta todos los EPICs en un flujo unificado.
"""

from __future__ import annotations

# =============================================================================
# VERSION
# =============================================================================

__version__ = "1.0.0"
__epic__ = "EPIC_1"
__phase__ = "PHASE_5"


# =============================================================================
# IMPORTS FROM SUBMODULES
# =============================================================================

# Domain
from core.PHASE_5.epic1_orchestrator.domain import (
    # Workflow
    Workflow,
    WorkflowStatus,
    WorkflowStep,
    # AgentExecution
    AgentExecution,
    ExecutionStatus,
    ExecutionResult,
    # OrchestrationPlan
    OrchestrationPlan,
    PlanStatus,
    PlanStep,
    # Enums
    OrchestrationStrategy,
    ExecutionMode,
    AggregationMethod,
)

# Engine
from core.PHASE_5.epic1_orchestrator.engine import (
    OrchestratorEngine,
    OrchestratorConfig,
)

# Dispatcher
from core.PHASE_5.epic1_orchestrator.dispatcher import (
    TaskDispatcher,
    DispatchStrategy,
)

# Scheduler
from core.PHASE_5.epic1_orchestrator.scheduler import (
    TaskScheduler,
    ScheduleStrategy,
)

# Aggregator
from core.PHASE_5.epic1_orchestrator.aggregator import (
    ResponseAggregator,
    AggregationConfig,
)

# Orchestrator Agent (NUEVO - Conecta todos los EPICs)
from core.PHASE_5.epic1_orchestrator.orchestrator_agent import (
    OrchestratorAgent,
    EpicRegistry,
    EpicConnection,
)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Version
    "__version__",
    "__epic__",
    "__phase__",
    # Domain - Workflow
    "Workflow",
    "WorkflowStatus",
    "WorkflowStep",
    # Domain - AgentExecution
    "AgentExecution",
    "ExecutionStatus",
    "ExecutionResult",
    # Domain - OrchestrationPlan
    "OrchestrationPlan",
    "PlanStatus",
    "PlanStep",
    # Domain - Enums
    "OrchestrationStrategy",
    "ExecutionMode",
    "AggregationMethod",
    # Engine
    "OrchestratorEngine",
    "OrchestratorConfig",
    # Dispatcher
    "TaskDispatcher",
    "DispatchStrategy",
    # Scheduler
    "TaskScheduler",
    "ScheduleStrategy",
    # Aggregator
    "ResponseAggregator",
    "AggregationConfig",
    # Orchestrator Agent (NUEVO)
    "OrchestratorAgent",
    "EpicRegistry",
    "EpicConnection",
]
