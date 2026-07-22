"""Dependency Resolver for EREN Cognitive Decision Engine.

Resolves task dependencies and execution order.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from core.PHASE_2.decision.types import (
    DecisionTask,
)

if TYPE_CHECKING:
    pass


class DependencyResolver:
    """Resolves task dependencies and execution order.

    The Dependency Resolver does NOT:
    - Execute tasks
    - Make decisions

    It ONLY:
    - Analyzes dependencies
    - Calculates execution order
    - Detects circular dependencies
    """

    def __init__(self):
        """Initialize dependency resolver."""
        pass

    def resolve(self, tasks: list[DecisionTask]) -> list[DecisionTask]:
        """Resolve dependencies and return ordered tasks.

        Args:
            tasks: Tasks to resolve.

        Returns:
            Tasks in execution order.
        """
        if not tasks:
            return []

        # Create a copy to avoid modifying original
        tasks = [DecisionTask(**t.__dict__) for t in tasks]

        # Build dependency graph
        graph = self._build_graph(tasks)

        # Check for cycles
        if self._has_cycle(graph):
            raise ValueError("Circular dependency detected")

        # Topological sort
        ordered = self._topological_sort(tasks, graph)

        return ordered

    def _build_graph(self, tasks: list[DecisionTask]) -> dict[str, list[str]]:
        """Build dependency graph.

        Args:
            tasks: Tasks to analyze.

        Returns:
            Dictionary mapping task_id to list of dependent task_ids.
        """
        graph: dict[str, list[str]] = {t.task_id: [] for t in tasks}

        for task in tasks:
            for dep_id in task.depends_on:
                if dep_id in graph:
                    graph[dep_id].append(task.task_id)

        return graph

    def _has_cycle(self, graph: dict[str, list[str]]) -> bool:
        """Check for circular dependencies.

        Args:
            graph: Dependency graph.

        Returns:
            True if cycle detected.
        """
        visited = set()
        rec_stack = set()

        def dfs(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)

            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True

            rec_stack.remove(node)
            return False

        for node in graph:
            if node not in visited:
                if dfs(node):
                    return True

        return False

    def _topological_sort(
        self,
        tasks: list[DecisionTask],
        graph: dict[str, list[str]],
    ) -> list[DecisionTask]:
        """Perform topological sort on tasks.

        Args:
            tasks: Tasks to sort.
            graph: Dependency graph.

        Returns:
            Tasks in topological order.
        """
        # Calculate in-degree for each task
        in_degree: dict[str, int] = {t.task_id: 0 for t in tasks}
        for task in tasks:
            for dep_id in task.depends_on:
                if dep_id in in_degree:
                    in_degree[task.task_id] += 1

        # Tasks with no dependencies (or all deps outside)
        queue = [t for t in tasks if in_degree[t.task_id] == 0]
        result = []

        while queue:
            # Sort by priority (critical first)
            queue.sort(key=lambda t: t.priority.value)
            task = queue.pop(0)
            result.append(task)

            # Decrease in-degree for dependent tasks
            for dependent_id in graph[task.task_id]:
                in_degree[dependent_id] -= 1
                if in_degree[dependent_id] == 0:
                    dependent = next(
                        (t for t in tasks if t.task_id == dependent_id),
                        None
                    )
                    if dependent:
                        queue.append(dependent)

        return result

    def validate_dependencies(self, tasks: list[DecisionTask]) -> tuple[bool, list[str]]:
        """Validate task dependencies.

        Args:
            tasks: Tasks to validate.

        Returns:
            Tuple of (is_valid, error_messages).
        """
        errors = []

        task_ids = {t.task_id for t in tasks}

        for task in tasks:
            if task.task_id in task.depends_on:
                errors.append(
                    f"Task {task.task_id} depends on itself"
                )

            for dep_id in task.depends_on:
                if dep_id not in task_ids:
                    errors.append(
                        f"Task {task.task_id} depends on unknown task {dep_id}"
                    )

        graph = self._build_graph(tasks)
        if self._has_cycle(graph):
            errors.append("Circular dependency detected")

        return len(errors) == 0, errors

    def calculate_execution_order(
        self,
        tasks: list[DecisionTask],
    ) -> list[list[DecisionTask]]:
        """Calculate parallelizable execution groups.

        Args:
            tasks: Tasks to analyze.

        Returns:
            List of task groups that can run in parallel.
        """
        if not tasks:
            return []

        tasks = [DecisionTask(**t.__dict__) for t in tasks]
        groups: list[list[DecisionTask]] = []

        while tasks:
            ready = []
            remaining = []

            for task in tasks:
                deps_met = all(
                    dep_id not in [t.task_id for t in remaining]
                    for dep_id in task.depends_on
                )
                if deps_met:
                    ready.append(task)
                else:
                    remaining.append(task)

            if not ready:
                break

            groups.append(ready)
            tasks = remaining

        return groups

    def estimate_parallelism(
        self,
        tasks: list[DecisionTask],
    ) -> tuple[int, float]:
        """Estimate potential parallelism.

        Args:
            tasks: Tasks to analyze.

        Returns:
            Tuple of (max_parallel, speedup_ratio).
        """
        groups = self.calculate_execution_order(tasks)

        if not groups:
            return 0, 0.0

        max_parallel = max(len(g) for g in groups)
        sequential_time = sum(t.estimated_time_seconds for t in tasks)

        parallel_time = sum(
            max(t.estimated_time_seconds for t in group)
            for group in groups
        )

        speedup = sequential_time / parallel_time if parallel_time > 0 else 1.0

        return max_parallel, speedup
