"""Dependency Graph for the Cognitive Dependency Injection Container.

Manages and analyzes the dependency graph.

Architecture only -- no implementations.
"""

import threading
from dataclasses import dataclass, field

from .service_descriptor import ServiceDescriptor


@dataclass
class DependencyNode:
    """A node in the dependency graph."""

    contract: str
    implementation: str
    dependencies: list = field(default_factory=list)
    depth: int = 0
    is_root: bool = False


@dataclass
class DependencyEdge:
    """An edge in the dependency graph."""

    from_contract: str
    to_contract: str
    is_required: bool = True


class DependencyGraph:
    """Graph representation of service dependencies.

    Allows analysis of dependency relationships.
    """

    def __init__(self):
        """Initialize the dependency graph."""
        self._nodes: dict[str, DependencyNode] = {}
        self._edges: list[DependencyEdge] = []
        self._lock = threading.RLock()

    def add_node(
        self,
        contract: str,
        implementation: str,
        dependencies: list = None,
        is_root: bool = False,
    ) -> None:
        """Add a node to the graph.

        Args:
            contract: Contract name.
            implementation: Implementation name.
            dependencies: List of dependency contracts.
            is_root: Whether this is a root service.
        """
        with self._lock:
            self._nodes[contract] = DependencyNode(
                contract=contract,
                implementation=implementation,
                dependencies=dependencies or [],
                is_root=is_root,
            )

            # Add edges for dependencies
            for dep in (dependencies or []):
                self._edges.append(
                    DependencyEdge(
                        from_contract=contract,
                        to_contract=dep,
                    )
                )

    def add_descriptor(self, descriptor: ServiceDescriptor, is_root: bool = False) -> None:
        """Add a service descriptor to the graph.

        Args:
            descriptor: Service descriptor.
            is_root: Whether this is a root service.
        """
        impl_name = (
            descriptor.implementation.__name__
            if callable(descriptor.implementation)
            else str(descriptor.implementation)
        )
        self.add_node(
            contract=descriptor.contract,
            implementation=impl_name,
            dependencies=descriptor.dependencies,
            is_root=is_root,
        )

    def get_node(self, contract: str) -> DependencyNode | None:
        """Get a node by contract.

        Args:
            contract: Contract name.

        Returns:
            Dependency node or None.
        """
        with self._lock:
            return self._nodes.get(contract)

    def get_dependencies(self, contract: str) -> list[str]:
        """Get direct dependencies of a contract.

        Args:
            contract: Contract name.

        Returns:
            List of dependency contracts.
        """
        with self._lock:
            node = self._nodes.get(contract)
            return list(node.dependencies) if node else []

    def get_dependents(self, contract: str) -> list[str]:
        """Get contracts that depend on this contract.

        Args:
            contract: Contract name.

        Returns:
            List of dependent contracts.
        """
        with self._lock:
            dependents = []
            for edge in self._edges:
                if edge.to_contract == contract:
                    dependents.append(edge.from_contract)
            return dependents

    def calculate_depth(self, contract: str) -> int:
        """Calculate the depth of a contract in the dependency tree.

        Args:
            contract: Contract name.

        Returns:
            Depth (0 = no dependencies).
        """
        with self._lock:
            visited = set()
            return self._calculate_depth_recursive(contract, visited)

    def _calculate_depth_recursive(
        self,
        contract: str,
        visited: set,
    ) -> int:
        """Recursively calculate depth.

        Args:
            contract: Contract name.
            visited: Set of visited nodes.

        Returns:
            Depth.
        """
        if contract in visited:
            return 0

        visited.add(contract)
        node = self._nodes.get(contract)

        if not node or not node.dependencies:
            return 0

        max_depth = 0
        for dep in node.dependencies:
            dep_depth = self._calculate_depth_recursive(dep, visited.copy())
            max_depth = max(max_depth, dep_depth)

        return max_depth + 1

    def find_cycles(self) -> list[list[str]]:
        """Find all cycles in the dependency graph.

        Returns:
            List of cycles (each cycle is a list of contracts).
        """
        with self._lock:
            cycles = []
            visited = set()

            for contract in self._nodes:
                if contract not in visited:
                    self._find_cycles_recursive(
                        contract,
                        [],
                        visited,
                        cycles,
                    )

            return cycles

    def _find_cycles_recursive(
        self,
        contract: str,
        path: list,
        visited: set,
        cycles: list,
    ) -> None:
        """Recursively find cycles.

        Args:
            contract: Current contract.
            path: Current path.
            visited: Set of visited nodes.
            cycles: List to collect cycles.
        """
        if contract in path:
            cycle_start = path.index(contract)
            cycle = path[cycle_start:] + [contract]
            cycles.append(cycle)
            return

        if contract in visited:
            return

        visited.add(contract)
        path.append(contract)

        node = self._nodes.get(contract)
        if node:
            for dep in node.dependencies:
                self._find_cycles_recursive(
                    dep,
                    path.copy(),
                    visited.copy(),
                    cycles,
                )

    def find_orphans(self) -> list[str]:
        """Find orphan dependencies (no implementation registered).

        Returns:
            List of orphan contract names.
        """
        with self._lock:
            orphans = set()

            for node in self._nodes.values():
                for dep in node.dependencies:
                    if dep not in self._nodes:
                        orphans.add(dep)

            return list(orphans)

    def find_roots(self) -> list[str]:
        """Find root services (no dependencies on other services).

        Returns:
            List of root contract names.
        """
        with self._lock:
            roots = []
            for node in self._nodes.values():
                if not node.dependencies or len(node.dependencies) == 0:
                    roots.append(node.contract)
            return roots

    def find_leaves(self) -> list[str]:
        """Find leaf services (not depended upon by others).

        Returns:
            List of leaf contract names.
        """
        with self._lock:
            dependents_count = {}
            for node in self._nodes.values():
                for dep in node.dependencies:
                    dependents_count[dep] = dependents_count.get(dep, 0) + 1

            leaves = [
                contract
                for contract in self._nodes
                if dependents_count.get(contract, 0) == 0
            ]
            return leaves

    def get_all_contracts(self) -> list[str]:
        """Get all contract names.

        Returns:
            List of contracts.
        """
        with self._lock:
            return list(self._nodes.keys())

    def get_statistics(self) -> dict:
        """Get graph statistics.

        Returns:
            Dictionary of statistics.
        """
        with self._lock:
            return {
                "node_count": len(self._nodes),
                "edge_count": len(self._edges),
                "root_count": len(self.find_roots()),
                "leaf_count": len(self.find_leaves()),
                "orphan_count": len(self.find_orphans()),
                "cycle_count": len(self.find_cycles()),
            }

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        with self._lock:
            return {
                "nodes": {
                    contract: {
                        "implementation": node.implementation,
                        "dependencies": node.dependencies,
                        "depth": self.calculate_depth(contract),
                        "is_root": node.is_root,
                    }
                    for contract, node in self._nodes.items()
                },
                "edges": [
                    {"from": e.from_contract, "to": e.to_contract}
                    for e in self._edges
                ],
                "statistics": self.get_statistics(),
            }
