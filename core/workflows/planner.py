"""Workflow planner for EREN Cognitive Workflow Engine.

Plans workflow execution.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from core.workflows.types import (
    WorkflowDefinition,
    WorkflowNode,
    WorkflowExecution,
    NodeExecution,
    NodeType,
    NodeStatus,
    WorkflowStatus,
)
from core.workflows.graph import ExecutionGraph

if TYPE_CHECKING:
    pass


class WorkflowPlanner:
    """Plans workflow execution.

    The Workflow Planner does NOT:
    - Execute tasks
    - Know about implementations

    It ONLY:
    - Creates execution plans
    - Determines execution order
    - Plans parallel execution
    """

    def __init__(self):
        """Initialize workflow planner."""
        self._graph: ExecutionGraph | None = None
        self._definition: WorkflowDefinition | None = None

    def set_definition(self, definition: WorkflowDefinition) -> None:
        """Set the workflow definition.

        Args:
            definition: Workflow definition.
        """
        self._definition = definition
        self._graph = ExecutionGraph(definition)

    def create_execution_plan(
        self,
        execution_id: str,
        input_data: dict | None = None,
    ) -> WorkflowExecution | None:
        """Create an execution plan.

        Args:
            execution_id: Execution ID.
            input_data: Initial input data.

        Returns:
            Created execution or None.
        """
        if not self._definition or not self._graph:
            return None

        from core.workflows.state import get_state_manager

        state_manager = get_state_manager()

        execution = state_manager.create_execution(
            execution_id=execution_id,
            workflow_id=self._definition.workflow_id,
            workflow_name=self._definition.name,
            input_data=input_data,
        )

        # Initialize node executions
        for node in self._definition.nodes:
            node_exec = NodeExecution(
                node_id=node.node_id,
                execution_id=execution_id,
            )
            execution.node_executions[node.node_id] = node_exec

        return execution

    def get_next_nodes(
        self,
        execution: WorkflowExecution,
    ) -> list[str]:
        """Get the next nodes to execute.

        Args:
            execution: Current execution.

        Returns:
            List of node IDs to execute next.
        """
        if not self._graph:
            return []

        # Get ready nodes (dependencies met)
        ready = self._graph.get_ready_nodes(execution)

        # Filter based on workflow type
        if self._definition and self._definition.workflow_type.value == "parallel":
            return ready
        else:
            # For sequential, return only first ready node
            return ready[:1] if ready else []

    def should_skip_node(
        self,
        execution: WorkflowExecution,
        node_id: str,
        result: Any = None,
    ) -> bool:
        """Check if a node should be skipped.

        Args:
            execution: Current execution.
            node_id: Node ID.
            result: Node result.

        Returns:
            True if should skip.
        """
        if not self._graph:
            return False

        node = self._graph.get_node(node_id)
        if not node:
            return False

        # Check condition for decision nodes
        if node.node_type == NodeType.DECISION:
            if result is not None and isinstance(result, dict):
                condition = node.config.get("condition", "")
                skip_value = node.config.get("skip_value", False)

                if condition and condition in result:
                    return result[condition] == skip_value

        return False

    def get_parallel_nodes(
        self,
        execution: WorkflowExecution,
    ) -> list[list[str]]:
        """Get nodes that can execute in parallel.

        Args:
            execution: Current execution.

        Returns:
            List of node ID lists.
        """
        if not self._graph:
            return []

        return self._graph.get_parallel_nodes()

    def is_workflow_complete(
        self,
        execution: WorkflowExecution,
    ) -> bool:
        """Check if workflow is complete.

        Args:
            execution: Current execution.

        Returns:
            True if complete.
        """
        if not self._graph:
            return False

        return self._graph.is_complete(execution)

    def get_failed_nodes(
        self,
        execution: WorkflowExecution,
    ) -> list[str]:
        """Get failed nodes.

        Args:
            execution: Current execution.

        Returns:
            List of failed node IDs.
        """
        return execution.failed_node_ids.copy()

    def should_retry(
        self,
        execution: WorkflowExecution,
        node_id: str,
    ) -> bool:
        """Check if a node should be retried.

        Args:
            execution: Current execution.
            node_id: Node ID.

        Returns:
            True if should retry.
        """
        if not self._graph:
            return False

        node = self._graph.get_node(node_id)
        if not node:
            return False

        node_exec = execution.node_executions.get(node_id)
        if not node_exec:
            return False

        return node_exec.retry_count < node.max_retries

    def get_exit_nodes(self) -> list[str]:
        """Get exit nodes.

        Returns:
            List of exit node IDs.
        """
        if not self._graph:
            return []

        return self._graph.get_exit_nodes()

    def get_entry_nodes(self) -> list[str]:
        """Get entry nodes.

        Returns:
            List of entry node IDs.
        """
        if not self._graph:
            return []

        return self._graph.get_entry_nodes()


# Global workflow planner
_planner: WorkflowPlanner | None = None
_planner_lock = __import__("threading").Lock()


def get_workflow_planner() -> WorkflowPlanner:
    """Get the global workflow planner.

    Returns:
        Global WorkflowPlanner instance.
    """
    global _planner
    with _planner_lock:
        if _planner is None:
            _planner = WorkflowPlanner()
        return _planner


def reset_workflow_planner() -> None:
    """Reset the global workflow planner."""
    global _planner
    with _planner_lock:
        _planner = None
