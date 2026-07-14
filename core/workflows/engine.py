"""Cognitive Workflow Engine (CWE) for EREN OS.

Main engine for cognitive workflow execution.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from core.workflows.types import (
    WorkflowDefinition,
    WorkflowExecution,
    WorkflowNode,
    WorkflowEdge,
    WorkflowType,
    NodeType,
    WorkflowStatus,
    WorkflowMetrics,
)
from core.workflows.graph import get_execution_graph
from core.workflows.state import get_state_manager, StateManager
from core.workflows.checkpoint import get_checkpoint_manager, CheckpointManager
from core.workflows.planner import get_workflow_planner, WorkflowPlanner
from core.workflows.runtime import get_workflow_runtime, WorkflowRuntime

if TYPE_CHECKING:
    pass


class WorkflowEngine:
    """Cognitive Workflow Engine.

    An agent executes tasks.
    A Workflow executes complete processes.

    The Workflow Engine does NOT:
    - Know about AI/LLM/RAG
    - Know about specific implementations

    It ONLY:
    - Creates workflows
    - Persists state
    - Resumes execution
    - Handles checkpoints
    - Manages rollback
    - Provides observability
    """

    def __init__(self):
        """Initialize workflow engine."""
        self._state_manager = get_state_manager()
        self._checkpoint_manager = get_checkpoint_manager()
        self._planner = get_workflow_planner()
        self._runtime = get_workflow_runtime()

        # Workflow definitions
        self._definitions: dict[str, WorkflowDefinition] = {}

        # Metrics
        self._metrics = WorkflowMetrics()

    # ========================================================================
    # Workflow Definition
    # ========================================================================

    def create_definition(
        self,
        name: str,
        description: str,
        workflow_type: WorkflowType = WorkflowType.LINEAR,
        config: dict | None = None,
    ) -> WorkflowDefinition:
        """Create a workflow definition.

        Args:
            name: Workflow name.
            description: Workflow description.
            workflow_type: Type of workflow.
            config: Configuration.

        Returns:
            Created workflow definition.
        """
        workflow_id = str(uuid.uuid4())

        definition = WorkflowDefinition(
            workflow_id=workflow_id,
            name=name,
            description=description,
            workflow_type=workflow_type,
            config=config or {},
        )

        self._definitions[workflow_id] = definition
        self._metrics.workflows_created += 1

        if workflow_type.value not in self._metrics.by_type:
            self._metrics.by_type[workflow_type.value] = 0
        self._metrics.by_type[workflow_type.value] += 1

        return definition

    def add_node(
        self,
        workflow_id: str,
        name: str,
        node_type: NodeType,
        config: dict | None = None,
        depends_on: list[str] | None = None,
        max_retries: int = 0,
        timeout_seconds: float = 0.0,
    ) -> WorkflowNode | None:
        """Add a node to a workflow.

        Args:
            workflow_id: Workflow ID.
            name: Node name.
            node_type: Node type.
            config: Node configuration.
            depends_on: Dependency node IDs.
            max_retries: Max retries.
            timeout_seconds: Timeout.

        Returns:
            Created node or None.
        """
        definition = self._definitions.get(workflow_id)
        if not definition:
            return None

        node = WorkflowNode.create(
            name=name,
            node_type=node_type,
            config=config,
            depends_on=depends_on,
            max_retries=max_retries,
            timeout_seconds=timeout_seconds,
        )

        definition.nodes.append(node)

        # Set entry node if first node
        if not definition.entry_node_id:
            definition.entry_node_id = node.node_id

        return node

    def add_edge(
        self,
        workflow_id: str,
        source_id: str,
        target_id: str,
        condition: str = "",
        priority: int = 0,
    ) -> WorkflowEdge | None:
        """Add an edge to a workflow.

        Args:
            workflow_id: Workflow ID.
            source_id: Source node ID.
            target_id: Target node ID.
            condition: Edge condition.
            priority: Edge priority.

        Returns:
            Created edge or None.
        """
        definition = self._definitions.get(workflow_id)
        if not definition:
            return None

        edge = WorkflowEdge.create(
            source_id=source_id,
            target_id=target_id,
            condition=condition,
            priority=priority,
        )

        definition.edges.append(edge)
        return edge

    def get_definition(self, workflow_id: str) -> WorkflowDefinition | None:
        """Get a workflow definition.

        Args:
            workflow_id: Workflow ID.

        Returns:
            Definition or None.
        """
        return self._definitions.get(workflow_id)

    def get_all_definitions(self) -> list[WorkflowDefinition]:
        """Get all workflow definitions.

        Returns:
            List of definitions.
        """
        return list(self._definitions.values())

    # ========================================================================
    # Workflow Execution
    # ========================================================================

    def start(
        self,
        workflow_id: str,
        input_data: dict | None = None,
    ) -> WorkflowExecution | None:
        """Start a workflow execution.

        Args:
            workflow_id: Workflow ID.
            input_data: Input data.

        Returns:
            Started execution or None.
        """
        definition = self._definitions.get(workflow_id)
        if not definition:
            return None

        # Set planner definition
        self._planner.set_definition(definition)

        # Execute workflow
        execution = self._runtime.execute_workflow(
            definition=definition,
            input_data=input_data,
        )

        self._metrics.total_executions += 1

        if execution.status == WorkflowStatus.COMPLETED:
            self._metrics.workflows_completed += 1
        elif execution.status == WorkflowStatus.FAILED:
            self._metrics.workflows_failed += 1
        elif execution.status == WorkflowStatus.CANCELLED:
            self._metrics.workflows_cancelled += 1

        return execution

    def get_execution(self, execution_id: str) -> WorkflowExecution | None:
        """Get an execution.

        Args:
            execution_id: Execution ID.

        Returns:
            Execution or None.
        """
        return self._state_manager.get_execution(execution_id)

    def get_running_executions(self) -> list[WorkflowExecution]:
        """Get all running executions.

        Returns:
            List of running executions.
        """
        return self._state_manager.get_running_executions()

    def pause(self, execution_id: str) -> bool:
        """Pause an execution.

        Args:
            execution_id: Execution ID.

        Returns:
            True if paused.
        """
        return self._runtime.pause_workflow(execution_id)

    def resume(self, execution_id: str) -> WorkflowExecution | None:
        """Resume a paused execution.

        Args:
            execution_id: Execution ID.

        Returns:
            Updated execution or None.
        """
        return self._runtime.resume_workflow(execution_id)

    def cancel(self, execution_id: str) -> bool:
        """Cancel an execution.

        Args:
            execution_id: Execution ID.

        Returns:
            True if cancelled.
        """
        return self._runtime.cancel_workflow(execution_id)

    # ========================================================================
    # Checkpoint & Recovery
    # ========================================================================

    def create_checkpoint(
        self,
        execution_id: str,
        metadata: dict | None = None,
    ) -> bool:
        """Create a checkpoint.

        Args:
            execution_id: Execution ID.
            metadata: Checkpoint metadata.

        Returns:
            True if created.
        """
        execution = self._state_manager.get_execution(execution_id)
        if not execution:
            return False

        self._checkpoint_manager.create_checkpoint(execution, metadata)
        return True

    def restore(
        self,
        checkpoint_id: str,
    ) -> WorkflowExecution | None:
        """Restore from a checkpoint.

        Args:
            checkpoint_id: Checkpoint ID.

        Returns:
            Restored execution or None.
        """
        return self._checkpoint_manager.restore_from_checkpoint(checkpoint_id)

    # ========================================================================
    # Metrics
    # ========================================================================

    def get_metrics(self) -> WorkflowMetrics:
        """Get workflow metrics.

        Returns:
            Metrics.
        """
        return self._metrics


# Global workflow engine
_engine: WorkflowEngine | None = None
_engine_lock = __import__("threading").Lock()


def get_workflow_engine() -> WorkflowEngine:
    """Get the global workflow engine.

    Returns:
        Global WorkflowEngine instance.
    """
    global _engine
    with _engine_lock:
        if _engine is None:
            _engine = WorkflowEngine()
        return _engine


def reset_workflow_engine() -> None:
    """Reset the global workflow engine."""
    global _engine
    with _engine_lock:
        _engine = None
