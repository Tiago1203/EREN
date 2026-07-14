"""EREN core — Workflow (DEPRECATED)

This module is DEPRECATED and will be removed in version 2.0.0.

All functionality has been moved to `core.workflows`.

Migration:
    from core.workflow import WorkflowEngine
    # BECOMES
    from core.workflows import WorkflowEngine

For more information, see:
- docs/architecture/MIGRATION_GUIDE.md
- docs/adr/ADR-001-duplicate-modules.md

---

Deprecated: 2026-07-14
Removal: Version 2.0.0 (planned)
"""

from __future__ import annotations

import warnings

# Emit deprecation warning on import
warnings.warn(
    "core.workflow is DEPRECATED and will be removed in version 2.0.0. "
    "Please use core.workflows instead. "
    "See: docs/architecture/MIGRATION_GUIDE.md",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export everything from the canonical location
from core.workflows import (
    # Main engine
    WorkflowPlatform,
    WorkflowEngine,
    get_workflow_platform,
    get_workflow_engine,
    reset_workflow_platform,
    reset_workflow_engine,
    # Types
    WorkflowType,
    WorkflowStatus,
    NodeType,
    NodeStatus,
    ExecutionStrategy,
    WorkflowNode,
    WorkflowEdge,
    WorkflowDefinition,
    NodeExecution,
    WorkflowExecution,
    Checkpoint,
    CompensationRecord,
    WorkflowMetrics,
    # Components
    ExecutionGraph,
    get_execution_graph,
    clear_graph_cache,
    StateStore,
    get_state_store,
    reset_state_store,
    StateManager,
    get_state_manager,
    reset_state_manager,
    CheckpointManager,
    get_checkpoint_manager,
    reset_checkpoint_manager,
    RecoveryManager,
    get_recovery_manager,
    reset_recovery_manager,
    WorkflowPlanner,
    get_workflow_planner,
    reset_workflow_planner,
    WorkflowRuntime,
    get_workflow_runtime,
    reset_workflow_runtime,
    WorkflowExecutor,
    TaskExecutor,
    get_task_executor,
    reset_task_executor,
    WorkflowScheduler,
    get_workflow_scheduler,
    reset_workflow_scheduler,
    WorkflowEventType,
    WorkflowEvent,
    WorkflowEventBus,
    get_event_bus,
    reset_event_bus,
    MetricsCollector,
    get_metrics_collector,
    reset_metrics_collector,
)

__all__ = [
    # Main engine
    "WorkflowPlatform",
    "WorkflowEngine",
    "get_workflow_platform",
    "get_workflow_engine",
    "reset_workflow_platform",
    "reset_workflow_engine",
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
    "StateStore",
    "get_state_store",
    "reset_state_store",
    "StateManager",
    "get_state_manager",
    "reset_state_manager",
    "CheckpointManager",
    "get_checkpoint_manager",
    "reset_checkpoint_manager",
    "RecoveryManager",
    "get_recovery_manager",
    "reset_recovery_manager",
    "WorkflowPlanner",
    "get_workflow_planner",
    "reset_workflow_planner",
    "WorkflowRuntime",
    "get_workflow_runtime",
    "reset_workflow_runtime",
    "WorkflowExecutor",
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
]

# Deprecation metadata
__deprecated__ = True
__deprecated_since__ = "2026-07-14"
__deprecated_remove__ = "2.0.0"
__deprecated_replacement__ = "core.workflows"
