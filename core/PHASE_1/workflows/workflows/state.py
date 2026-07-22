"""State management for EREN Cognitive Workflow Engine.

Manages workflow execution state.
"""

from __future__ import annotations

from datetime import UTC
from typing import TYPE_CHECKING, Any

from core.workflows.types import (
    NodeExecution,
    NodeStatus,
    WorkflowExecution,
    WorkflowStatus,
)

if TYPE_CHECKING:
    pass


class StateManager:
    """Manages workflow execution state.

    The State Manager does NOT:
    - Execute tasks
    - Know about implementations

    It ONLY:
    - Tracks execution state
    - Manages state transitions
    - Stores state data
    """

    def __init__(self):
        """Initialize state manager."""
        self._executions: dict[str, WorkflowExecution] = {}

    def create_execution(
        self,
        execution_id: str,
        workflow_id: str,
        workflow_name: str,
        input_data: dict | None = None,
    ) -> WorkflowExecution:
        """Create a new workflow execution.

        Args:
            execution_id: Execution ID.
            workflow_id: Workflow ID.
            workflow_name: Workflow name.
            input_data: Initial input data.

        Returns:
            Created execution.
        """
        execution = WorkflowExecution(
            execution_id=execution_id,
            workflow_id=workflow_id,
            workflow_name=workflow_name,
            input_data=input_data or {},
        )

        self._executions[execution_id] = execution
        return execution

    def get_execution(self, execution_id: str) -> WorkflowExecution | None:
        """Get an execution.

        Args:
            execution_id: Execution ID.

        Returns:
            Execution or None.
        """
        return self._executions.get(execution_id)

    def get_all_executions(self) -> list[WorkflowExecution]:
        """Get all executions.

        Returns:
            List of executions.
        """
        return list(self._executions.values())

    def get_executions_by_workflow(
        self,
        workflow_id: str,
    ) -> list[WorkflowExecution]:
        """Get executions for a workflow.

        Args:
            workflow_id: Workflow ID.

        Returns:
            List of executions.
        """
        return [
            e for e in self._executions.values()
            if e.workflow_id == workflow_id
        ]

    def get_running_executions(self) -> list[WorkflowExecution]:
        """Get all running executions.

        Returns:
            List of running executions.
        """
        return [
            e for e in self._executions.values()
            if e.status == WorkflowStatus.RUNNING
        ]

    def update_status(
        self,
        execution_id: str,
        status: WorkflowStatus,
    ) -> bool:
        """Update workflow status.

        Args:
            execution_id: Execution ID.
            status: New status.

        Returns:
            True if updated.
        """
        execution = self._executions.get(execution_id)
        if not execution:
            return False

        from datetime import datetime

        execution.status = status

        if status == WorkflowStatus.RUNNING and not execution.started_at:
            execution.started_at = datetime.now(UTC)
        elif status in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED, WorkflowStatus.CANCELLED]:
            execution.completed_at = datetime.now(UTC)

        return True

    def start_node(
        self,
        execution_id: str,
        node_id: str,
        execution: NodeExecution,
    ) -> bool:
        """Mark a node as started.

        Args:
            execution_id: Execution ID.
            node_id: Node ID.
            execution: Node execution.

        Returns:
            True if started.
        """
        workflow_exec = self._executions.get(execution_id)
        if not workflow_exec:
            return False

        workflow_exec.node_executions[node_id] = execution
        workflow_exec.current_node_ids.append(node_id)
        workflow_exec.status = WorkflowStatus.RUNNING

        if not workflow_exec.started_at:
            from datetime import datetime
            workflow_exec.started_at = datetime.now(UTC)

        return True

    def complete_node(
        self,
        execution_id: str,
        node_id: str,
        result: Any = None,
    ) -> bool:
        """Mark a node as completed.

        Args:
            execution_id: Execution ID.
            node_id: Node ID.
            result: Node result.

        Returns:
            True if completed.
        """
        workflow_exec = self._executions.get(execution_id)
        if not workflow_exec:
            return False

        node_exec = workflow_exec.node_executions.get(node_id)
        if node_exec:
            node_exec.status = NodeStatus.COMPLETED
            node_exec.result = result
            from datetime import datetime
            node_exec.completed_at = datetime.now(UTC)

        if node_id in workflow_exec.current_node_ids:
            workflow_exec.current_node_ids.remove(node_id)
        workflow_exec.completed_node_ids.append(node_id)

        return True

    def fail_node(
        self,
        execution_id: str,
        node_id: str,
        error: str,
    ) -> bool:
        """Mark a node as failed.

        Args:
            execution_id: Execution ID.
            node_id: Node ID.
            error: Error message.

        Returns:
            True if marked as failed.
        """
        workflow_exec = self._executions.get(execution_id)
        if not workflow_exec:
            return False

        node_exec = workflow_exec.node_executions.get(node_id)
        if node_exec:
            node_exec.status = NodeStatus.FAILED
            node_exec.error = error
            from datetime import datetime
            node_exec.completed_at = datetime.now(UTC)

        if node_id in workflow_exec.current_node_ids:
            workflow_exec.current_node_ids.remove(node_id)
        workflow_exec.failed_node_ids.append(node_id)
        workflow_exec.error_message = error
        workflow_exec.error_node_id = node_id

        return True

    def skip_node(
        self,
        execution_id: str,
        node_id: str,
    ) -> bool:
        """Mark a node as skipped.

        Args:
            execution_id: Execution ID.
            node_id: Node ID.

        Returns:
            True if skipped.
        """
        workflow_exec = self._executions.get(execution_id)
        if not workflow_exec:
            return False

        node_exec = workflow_exec.node_executions.get(node_id)
        if node_exec:
            node_exec.status = NodeStatus.SKIPPED

        workflow_exec.completed_node_ids.append(node_id)

        return True

    def set_current_nodes(
        self,
        execution_id: str,
        node_ids: list[str],
    ) -> bool:
        """Set current executing nodes.

        Args:
            execution_id: Execution ID.
            node_ids: Node IDs.

        Returns:
            True if set.
        """
        workflow_exec = self._executions.get(execution_id)
        if not workflow_exec:
            return False

        workflow_exec.current_node_ids = node_ids
        return True

    def update_state(
        self,
        execution_id: str,
        state: dict,
    ) -> bool:
        """Update workflow state.

        Args:
            execution_id: Execution ID.
            state: New state.

        Returns:
            True if updated.
        """
        workflow_exec = self._executions.get(execution_id)
        if not workflow_exec:
            return False

        workflow_exec.state.update(state)
        return True

    def set_output(
        self,
        execution_id: str,
        output_data: dict,
    ) -> bool:
        """Set workflow output.

        Args:
            execution_id: Execution ID.
            output_data: Output data.

        Returns:
            True if set.
        """
        workflow_exec = self._executions.get(execution_id)
        if not workflow_exec:
            return False

        workflow_exec.output_data.update(output_data)
        return True

    def get_node_execution(
        self,
        execution_id: str,
        node_id: str,
    ) -> NodeExecution | None:
        """Get node execution.

        Args:
            execution_id: Execution ID.
            node_id: Node ID.

        Returns:
            NodeExecution or None.
        """
        workflow_exec = self._executions.get(execution_id)
        if not workflow_exec:
            return None

        return workflow_exec.node_executions.get(node_id)

    def delete_execution(self, execution_id: str) -> bool:
        """Delete an execution.

        Args:
            execution_id: Execution ID.

        Returns:
            True if deleted.
        """
        if execution_id in self._executions:
            del self._executions[execution_id]
            return True
        return False


# Global state manager
_state_manager: StateManager | None = None
_state_lock = __import__("threading").Lock()


def get_state_manager() -> StateManager:
    """Get the global state manager.

    Returns:
        Global StateManager instance.
    """
    global _state_manager
    with _state_lock:
        if _state_manager is None:
            _state_manager = StateManager()
        return _state_manager


def reset_state_manager() -> None:
    """Reset the global state manager."""
    global _state_manager
    with _state_lock:
        _state_manager = None
