"""EREN Cognitive Workflow Engine (CWE).

The official system for cognitive workflow execution in EREN.
Allows executing long-running, persistent, and resumable processes.

Philosophy:
    An agent executes tasks.
    A Workflow executes complete processes.

Architecture:
    Execution Coordinator
            │
            ▼
    Decision Engine
            │
            ▼
    Workflow Engine
            │
            ├── Workflow Planner
            ├── Workflow Runtime
            ├── State Manager
            ├── Checkpoint Manager
            ├── Execution Graph
            └── Agent Platform

Responsibilities:
- Create workflows
- Persist state
- Resume execution
- Cancel
- Pause
- Checkpointing
- Rollback
- Versioning
- Observability
- Fault recovery
"""

from __future__ import annotations

# Types
from core.workflows.types import (
    # Enums
    WorkflowType,
    WorkflowStatus,
    NodeType,
    NodeStatus,
    ExecutionStrategy,
    # Classes
    WorkflowNode,
    WorkflowEdge,
    WorkflowDefinition,
    NodeExecution,
    WorkflowExecution,
    Checkpoint,
    CompensationRecord,
    WorkflowMetrics,
)

# Components
from core.workflows.graph import (
    ExecutionGraph,
    get_execution_graph,
    clear_graph_cache,
)
from core.workflows.state import (
    StateManager,
    get_state_manager,
    reset_state_manager,
)
from core.workflows.checkpoint import (
    CheckpointManager,
    get_checkpoint_manager,
    reset_checkpoint_manager,
)
from core.workflows.planner import (
    WorkflowPlanner,
    get_workflow_planner,
    reset_workflow_planner,
)
from core.workflows.runtime import (
    WorkflowRuntime,
    get_workflow_runtime,
    reset_workflow_runtime,
)
from core.workflows.executor import (
    TaskExecutor,
    get_task_executor,
    reset_task_executor,
)
from core.workflows.scheduler import (
    WorkflowScheduler,
    get_workflow_scheduler,
    reset_workflow_scheduler,
)
from core.workflows.events import (
    WorkflowEventType,
    WorkflowEvent,
    WorkflowEventBus,
    get_event_bus,
    reset_event_bus,
)
from core.workflows.metrics import (
    MetricsCollector,
    get_metrics_collector,
    reset_metrics_collector,
)

# Main engine
from core.workflows.engine import (
    WorkflowEngine,
    get_workflow_engine,
    reset_workflow_engine,
)

__all__ = [
    # Types
    "WorkflowType",
    "WorkflowStatus",
    "NodeType",
    "NodeStatus",
    "ExecutionStrategy",
    "WorkflowNode",
    "WorkflowEdge",
    "WorkflowDefinition",
    "NodeExecution",
    "WorkflowExecution",
    "Checkpoint",
    "CompensationRecord",
    "WorkflowMetrics",
    # Components
    "ExecutionGraph",
    "get_execution_graph",
    "clear_graph_cache",
    "StateManager",
    "get_state_manager",
    "reset_state_manager",
    "CheckpointManager",
    "get_checkpoint_manager",
    "reset_checkpoint_manager",
    "WorkflowPlanner",
    "get_workflow_planner",
    "reset_workflow_planner",
    "WorkflowRuntime",
    "get_workflow_runtime",
    "reset_workflow_runtime",
    "TaskExecutor",
    "get_task_executor",
    "reset_task_executor",
    "WorkflowScheduler",
    "get_workflow_scheduler",
    "reset_workflow_scheduler",
    "WorkflowEventType",
    "WorkflowEvent",
    "WorkflowEventBus",
    "get_event_bus",
    "reset_event_bus",
    "MetricsCollector",
    "get_metrics_collector",
    "reset_metrics_collector",
    # Main engine
    "WorkflowEngine",
    "get_workflow_engine",
    "reset_workflow_engine",
]
