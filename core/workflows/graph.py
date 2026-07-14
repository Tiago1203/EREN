"""Execution graph for EREN Cognitive Workflow Engine.

Manages the workflow execution graph.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from core.workflows.types import (
    WorkflowDefinition,
    WorkflowNode,
    WorkflowEdge,
    WorkflowExecution,
    NodeExecution,
    NodeType,
    NodeStatus,
)

if TYPE_CHECKING:
    pass


class ExecutionGraph:
    """Manages workflow execution graph.

    The Execution Graph does NOT:
    - Execute tasks
    - Know about implementations

    It ONLY:
    - Tracks graph structure
    - Manages execution state
    - Determines execution order
    """

    def __init__(self, definition: WorkflowDefinition):
        """Initialize execution graph.

        Args:
            definition: Workflow definition.
        """
        self._definition = definition

        # Build adjacency lists
        self._outgoing: dict[str, list[str]] = {}
        self._incoming: dict[str, list[str]] = {}

        for edge in definition.edges:
            if edge.source_id not in self._outgoing:
                self._outgoing[edge.source_id] = []
            self._outgoing[edge.source_id].append(edge.target_id)

            if edge.target_id not in self._incoming:
                self._incoming[edge.target_id] = []
            self._incoming[edge.target_id].append(edge.source_id)

    def get_node(self, node_id: str) -> WorkflowNode | None:
        """Get a node by ID.

        Args:
            node_id: Node ID.

        Returns:
            Node or None.
        """
        return self._definition.get_node(node_id)

    def get_outgoing(self, node_id: str) -> list[str]:
        """Get outgoing node IDs.

        Args:
            node_id: Node ID.

        Returns:
            List of outgoing node IDs.
        """
        return self._outgoing.get(node_id, [])

    def get_incoming(self, node_id: str) -> list[str]:
        """Get incoming node IDs.

        Args:
            node_id: Node ID.

        Returns:
            List of incoming node IDs.
        """
        return self._incoming.get(node_id, [])

    def get_ready_nodes(
        self,
        execution: WorkflowExecution,
    ) -> list[str]:
        """Get nodes ready to execute.

        A node is ready when all its dependencies are complete.

        Args:
            execution: Current execution state.

        Returns:
            List of ready node IDs.
        """
        ready = []

        for node in self._definition.nodes:
            # Skip if already executed or failed
            if node.node_id in execution.completed_node_ids:
                continue
            if node.node_id in execution.failed_node_ids:
                continue

            # Skip if currently running
            if node.node_id in execution.current_node_ids:
                continue

            # Check dependencies
            deps_met = True
            for dep_id in node.depends_on:
                if dep_id not in execution.completed_node_ids:
                    deps_met = False
                    break

            if deps_met:
                ready.append(node.node_id)

        return ready

    def get_entry_nodes(self) -> list[str]:
        """Get entry nodes (no incoming edges).

        Returns:
            List of entry node IDs.
        """
        return [
            node.node_id for node in self._definition.nodes
            if node.node_id not in self._incoming or len(self._incoming[node.node_id]) == 0
        ]

    def get_exit_nodes(self) -> list[str]:
        """Get exit nodes (no outgoing edges).

        Returns:
            List of exit node IDs.
        """
        return [
            node.node_id for node in self._definition.nodes
            if node.node_id not in self._outgoing or len(self._outgoing[node.node_id]) == 0
        ]

    def is_complete(self, execution: WorkflowExecution) -> bool:
        """Check if execution is complete.

        Args:
            execution: Current execution state.

        Returns:
            True if complete.
        """
        exit_nodes = self.get_exit_nodes()

        for node_id in exit_nodes:
            if node_id not in execution.completed_node_ids:
                return False

        return True

    def get_execution_path(
        self,
        execution: WorkflowExecution,
    ) -> list[str]:
        """Get the current execution path.

        Args:
            execution: Current execution state.

        Returns:
            List of node IDs in execution order.
        """
        path = list(execution.completed_node_ids)
        path.extend(execution.current_node_ids)
        return path

    def validate(self) -> tuple[bool, list[str]]:
        """Validate the workflow graph.

        Returns:
            Tuple of (is_valid, error_messages).
        """
        errors = []

        # Check for entry node
        entry_nodes = self.get_entry_nodes()
        if not entry_nodes:
            errors.append("Workflow has no entry node")

        # Check for exit node
        exit_nodes = self.get_exit_nodes()
        if not exit_nodes:
            errors.append("Workflow has no exit node")

        # Check for orphan nodes
        all_node_ids = {node.node_id for node in self._definition.nodes}
        connected_ids = set()

        for edge in self._definition.edges:
            connected_ids.add(edge.source_id)
            connected_ids.add(edge.target_id)

        orphan_ids = all_node_ids - connected_ids
        if orphan_ids:
            errors.append(f"Workflow has orphan nodes: {orphan_ids}")

        # Check dependencies exist
        for node in self._definition.nodes:
            for dep_id in node.depends_on:
                if dep_id not in all_node_ids:
                    errors.append(f"Node {node.node_id} depends on non-existent node {dep_id}")

        # Check for cycles (basic check)
        if self._has_cycle():
            errors.append("Workflow contains a cycle")

        return len(errors) == 0, errors

    def _has_cycle(self) -> bool:
        """Check for cycles using DFS."""
        visited = set()
        rec_stack = set()

        def dfs(node_id: str) -> bool:
            visited.add(node_id)
            rec_stack.add(node_id)

            for neighbor in self.get_outgoing(node_id):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True

            rec_stack.remove(node_id)
            return False

        for node_id in self.get_entry_nodes():
            if node_id not in visited:
                if dfs(node_id):
                    return True

        return False

    def get_parallel_nodes(self) -> list[list[str]]:
        """Get nodes that can execute in parallel.

        Returns:
            List of node ID lists that can run in parallel.
        """
        parallel_groups = []

        # Simple implementation: group nodes by depth
        visited = set()
        queue = [(entry_id, 0) for entry_id in self.get_entry_nodes()]

        while queue:
            node_id, depth = queue.pop(0)

            if node_id in visited:
                continue

            visited.add(node_id)

            # Ensure parallel_groups has enough entries
            while len(parallel_groups) <= depth:
                parallel_groups.append([])

            parallel_groups[depth].append(node_id)

            # Add successors to queue
            for successor in self.get_outgoing(node_id):
                if successor not in visited:
                    queue.append((successor, depth + 1))

        return [group for group in parallel_groups if group]


# Global execution graph cache
_graph_cache: dict[str, ExecutionGraph] = {}


def get_execution_graph(definition: WorkflowDefinition) -> ExecutionGraph:
    """Get or create an execution graph.

    Args:
        definition: Workflow definition.

    Returns:
        ExecutionGraph instance.
    """
    if definition.workflow_id not in _graph_cache:
        _graph_cache[definition.workflow_id] = ExecutionGraph(definition)
    return _graph_cache[definition.workflow_id]


def clear_graph_cache() -> None:
    """Clear the graph cache."""
    _graph_cache.clear()
