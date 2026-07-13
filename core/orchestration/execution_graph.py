"""Execution graph for cognitive orchestration.

Defines dependencies between engines and their execution.

Architecture only -- no implementations, no business logic.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass


# =============================================================================
# Node Types
# =============================================================================


class NodeType(str, Enum):
    """Types of nodes in execution graph."""

    ENGINE = "engine"  # Cognitive engine
    PHASE = "phase"  # Processing phase
    DATA = "data"  # Data node


# =============================================================================
# Edge Types
# =============================================================================


class EdgeType(str, Enum):
    """Types of edges in execution graph."""

    EXECUTES = "executes"  # Engine executes phase
    DEPENDS_ON = "depends_on"  # Node depends on another
    PRODUCES = "produces"  # Node produces data
    CONSUMES = "consumes"  # Node consumes data


# =============================================================================
# Graph Node
# =============================================================================


@dataclass(frozen=True)
class GraphNode:
    """A node in the execution graph."""

    node_id: str
    node_type: NodeType
    label: str
    metadata: dict = field(default_factory=dict)

    def __hash__(self) -> int:
        """Make hashable."""
        return hash(self.node_id)


# =============================================================================
# Graph Edge
# =============================================================================


@dataclass(frozen=True)
class GraphEdge:
    """An edge in the execution graph."""

    edge_id: str
    from_node: str
    to_node: str
    edge_type: EdgeType
    weight: float = 1.0
    metadata: dict = field(default_factory=dict)

    def __hash__(self) -> int:
        """Make hashable."""
        return hash(self.edge_id)


# =============================================================================
# Execution Graph
# =============================================================================


class ExecutionGraph:
    """Graph representing engine execution dependencies.

    Used to visualize and validate the orchestration flow.
    """

    def __init__(self) -> None:
        """Initialize the execution graph."""
        self._nodes: dict[str, GraphNode] = {}
        self._edges: dict[str, GraphEdge] = {}
        self._adjacency: dict[str, list[str]] = {}  # node -> [nodes]
        self._reverse_adjacency: dict[str, list[str]] = {}  # node -> [nodes]

    # =========================================================================
    # Node Operations
    # =========================================================================

    def add_node(self, node: GraphNode) -> None:
        """Add a node to the graph.

        Args:
            node: The node to add.
        """
        self._nodes[node.node_id] = node
        self._adjacency.setdefault(node.node_id, [])
        self._reverse_adjacency.setdefault(node.node_id, [])

    def remove_node(self, node_id: str) -> bool:
        """Remove a node from the graph.

        Args:
            node_id: The node ID.

        Returns:
            True if removed.
        """
        if node_id not in self._nodes:
            return False

        # Remove node
        del self._nodes[node_id]

        # Remove edges
        edges_to_remove = [
            eid for eid, edge in self._edges.items()
            if edge.from_node == node_id or edge.to_node == node_id
        ]
        for eid in edges_to_remove:
            del self._edges[eid]

        # Update adjacency
        self._adjacency.pop(node_id, None)
        self._reverse_adjacency.pop(node_id, None)

        return True

    def get_node(self, node_id: str) -> GraphNode | None:
        """Get a node by ID.

        Args:
            node_id: The node ID.

        Returns:
            The node or None.
        """
        return self._nodes.get(node_id)

    def get_all_nodes(self) -> list[GraphNode]:
        """Get all nodes.

        Returns:
            All nodes in the graph.
        """
        return list(self._nodes.values())

    # =========================================================================
    # Edge Operations
    # =========================================================================

    def add_edge(self, edge: GraphEdge) -> None:
        """Add an edge to the graph.

        Args:
            edge: The edge to add.
        """
        self._edges[edge.edge_id] = edge
        self._adjacency.setdefault(edge.from_node, []).append(edge.to_node)
        self._reverse_adjacency.setdefault(edge.to_node, []).append(edge.from_node)

    def remove_edge(self, edge_id: str) -> bool:
        """Remove an edge from the graph.

        Args:
            edge_id: The edge ID.

        Returns:
            True if removed.
        """
        if edge_id not in self._edges:
            return False

        edge = self._edges[edge_id]
        del self._edges[edge_id]

        # Update adjacency
        if edge.from_node in self._adjacency:
            self._adjacency[edge.from_node] = [
                n for n in self._adjacency[edge.from_node] if n != edge.to_node
            ]
        if edge.to_node in self._reverse_adjacency:
            self._reverse_adjacency[edge.to_node] = [
                n for n in self._reverse_adjacency[edge.to_node] if n != edge.from_node
            ]

        return True

    def get_edge(self, edge_id: str) -> GraphEdge | None:
        """Get an edge by ID.

        Args:
            edge_id: The edge ID.

        Returns:
            The edge or None.
        """
        return self._edges.get(edge_id)

    def get_all_edges(self) -> list[GraphEdge]:
        """Get all edges.

        Returns:
            All edges in the graph.
        """
        return list(self._edges.values())

    # =========================================================================
    # Graph Queries
    # =========================================================================

    def get_successors(self, node_id: str) -> list[GraphNode]:
        """Get successor nodes.

        Args:
            node_id: The node ID.

        Returns:
            Successor nodes.
        """
        successor_ids = self._adjacency.get(node_id, [])
        return [self._nodes[nid] for nid in successor_ids if nid in self._nodes]

    def get_predecessors(self, node_id: str) -> list[GraphNode]:
        """Get predecessor nodes.

        Args:
            node_id: The node ID.

        Returns:
            Predecessor nodes.
        """
        predecessor_ids = self._reverse_adjacency.get(node_id, [])
        return [self._nodes[nid] for nid in predecessor_ids if nid in self._nodes]

    def topological_sort(self) -> list[GraphNode] | None:
        """Get topological order of nodes.

        Returns:
            Nodes in topological order, or None if cycle exists.
        """
        in_degree: dict[str, int] = {}
        for node_id in self._nodes:
            in_degree[node_id] = len(self._reverse_adjacency.get(node_id, []))

        queue = [node_id for node_id, degree in in_degree.items() if degree == 0]
        result = []

        while queue:
            node_id = queue.pop(0)
            result.append(self._nodes[node_id])

            for successor_id in self._adjacency.get(node_id, []):
                in_degree[successor_id] -= 1
                if in_degree[successor_id] == 0:
                    queue.append(successor_id)

        if len(result) != len(self._nodes):
            return None  # Cycle detected

        return result

    def has_cycle(self) -> bool:
        """Check if graph has a cycle.

        Returns:
            True if graph has a cycle.
        """
        return self.topological_sort() is None

    def get_execution_order(self) -> list[list[GraphNode]]:
        """Get execution order in stages.

        Nodes that can execute in parallel are in the same stage.

        Returns:
            List of execution stages.
        """
        stages: list[list[GraphNode]] = []
        remaining = set(self._nodes.keys())
        completed = set()

        while remaining:
            # Find nodes with all dependencies completed
            ready = []
            for node_id in remaining:
                predecessors = self._reverse_adjacency.get(node_id, [])
                if all(pred in completed for pred in predecessors):
                    ready.append(node_id)

            if not ready:
                break  # Shouldn't happen if no cycles

            stage = [self._nodes[nid] for nid in ready]
            stages.append(stage)

            for node_id in ready:
                remaining.remove(node_id)
                completed.add(node_id)

        return stages


# =============================================================================
# Graph Factory
# =============================================================================


class ExecutionGraphFactory:
    """Factory for creating execution graphs."""

    @staticmethod
    def create_cognitive_graph() -> ExecutionGraph:
        """Create the default cognitive execution graph.

        Returns:
            Default execution graph.
        """
        graph = ExecutionGraph()

        # Add phase nodes
        phases = [
            ("intake", "User Input Processing"),
            ("planning", "Planning"),
            ("knowledge", "Knowledge Query"),
            ("memory", "Memory Query"),
            ("reasoning", "Reasoning"),
            ("decision", "Decision Making"),
            ("action", "Action Execution"),
            ("output", "Response Generation"),
        ]

        for phase_id, label in phases:
            graph.add_node(GraphNode(
                node_id=f"phase_{phase_id}",
                node_type=NodeType.PHASE,
                label=label,
            ))

        # Add engine nodes
        engines = [
            ("orchestrator", "Orchestrator"),
            ("planner", "Planner Engine"),
            ("knowledge", "Knowledge Engine"),
            ("memory", "Memory Engine"),
            ("reasoning", "Reasoning Engine"),
            ("decision", "Decision Engine"),
            ("tool", "Tool Engine"),
            ("voice", "Voice Engine"),
        ]

        for engine_id, label in engines:
            graph.add_node(GraphNode(
                node_id=f"engine_{engine_id}",
                node_type=NodeType.ENGINE,
                label=label,
            ))

        # Add execution edges (engine executes phase)
        execution_edges = [
            ("orchestrator", "intake"),
            ("planner", "planning"),
            ("knowledge", "knowledge"),
            ("memory", "memory"),
            ("reasoning", "reasoning"),
            ("decision", "decision"),
            ("tool", "action"),
            ("voice", "output"),
        ]

        for idx, (engine_id, phase_id) in enumerate(execution_edges):
            graph.add_edge(GraphEdge(
                edge_id=f"exec_{idx}",
                from_node=f"engine_{engine_id}",
                to_node=f"phase_{phase_id}",
                edge_type=EdgeType.EXECUTES,
            ))

        # Add dependency edges (phase depends on previous)
        dependencies = [
            ("intake", "planning"),
            ("planning", "knowledge"),
            ("planning", "memory"),
            ("knowledge", "reasoning"),
            ("memory", "reasoning"),
            ("reasoning", "decision"),
            ("decision", "action"),
            ("action", "output"),
        ]

        for idx, (from_phase, to_phase) in enumerate(dependencies):
            graph.add_edge(GraphEdge(
                edge_id=f"dep_{idx}",
                from_node=f"phase_{from_phase}",
                to_node=f"phase_{to_phase}",
                edge_type=EdgeType.DEPENDS_ON,
                weight=1.0,
            ))

        return graph
