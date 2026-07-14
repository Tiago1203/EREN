"""Workflow scheduler for EREN Cognitive Workflow Platform.

Calculates execution order and manages dependencies.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from core.workflows.types import (
    WorkflowExecution,
    WorkflowNode,
)

if TYPE_CHECKING:
    pass


class ScheduledTask:
    """A scheduled task."""

    task_id: str
    workflow_id: str
    execution_id: str
    node_id: str
    scheduled_at: datetime
    status: str
    priority: int

    def __init__(
        self,
        task_id: str,
        workflow_id: str,
        execution_id: str,
        node_id: str,
        scheduled_at: datetime,
        priority: int = 5,
    ):
        self.task_id = task_id
        self.workflow_id = workflow_id
        self.execution_id = execution_id
        self.node_id = node_id
        self.scheduled_at = scheduled_at
        self.status = "pending"
        self.priority = priority


class WorkflowScheduler:
    """Schedules workflow execution.

    The Workflow Scheduler does NOT:
    - Execute tasks
    - Know about implementations

    It ONLY:
    - Calculates order
    - Resolves dependencies
    - Controls parallelism
    - Manages priorities
    - Handles retries
    """

    def __init__(self):
        """Initialize workflow scheduler."""
        self._scheduled_tasks: dict[str, ScheduledTask] = {}
        self._retry_counts: dict[str, int] = {}
        self._max_retries: int = 3

    def calculate_order(
        self,
        ready_nodes: list[str],
        priorities: dict[str, int] | None = None,
    ) -> list[str]:
        """Calculate execution order.

        Args:
            ready_nodes: List of ready node IDs.
            priorities: Optional priority map.

        Returns:
            Ordered list of node IDs.
        """
        if not priorities:
            return ready_nodes

        # Sort by priority (higher = first)
        sorted_nodes = sorted(
            ready_nodes,
            key=lambda n: priorities.get(n, 5),
            reverse=True,
        )

        return sorted_nodes

    def resolve_dependencies(
        self,
        node: WorkflowNode,
        completed_nodes: list[str],
    ) -> bool:
        """Resolve if dependencies are met.

        Args:
            node: Node to check.
            completed_nodes: List of completed node IDs.

        Returns:
            True if dependencies met.
        """
        for dep_id in node.depends_on:
            if dep_id not in completed_nodes:
                return False
        return True

    def should_retry(
        self,
        node_id: str,
        max_retries: int | None = None,
    ) -> bool:
        """Check if a node should be retried.

        Args:
            node_id: Node ID.
            max_retries: Maximum retries.

        Returns:
            True if should retry.
        """
        max_r = max_retries or self._max_retries
        retry_count = self._retry_counts.get(node_id, 0)
        return retry_count < max_r

    def increment_retry(self, node_id: str) -> int:
        """Increment retry count.

        Args:
            node_id: Node ID.

        Returns:
            New retry count.
        """
        self._retry_counts[node_id] = self._retry_counts.get(node_id, 0) + 1
        return self._retry_counts[node_id]

    def reset_retry(self, node_id: str) -> None:
        """Reset retry count.

        Args:
            node_id: Node ID.
        """
        self._retry_counts.pop(node_id, None)

    def schedule_task(
        self,
        workflow_id: str,
        execution_id: str,
        node_id: str,
        delay_seconds: float = 0.0,
        priority: int = 5,
    ) -> ScheduledTask:
        """Schedule a task.

        Args:
            workflow_id: Workflow ID.
            execution_id: Execution ID.
            node_id: Node ID.
            delay_seconds: Delay before execution.
            priority: Task priority.

        Returns:
            Scheduled task.
        """
        task_id = str(uuid.uuid4())

        scheduled_at = datetime.now(timezone.utc)
        if delay_seconds > 0:
            from datetime import timedelta
            scheduled_at = scheduled_at + timedelta(seconds=delay_seconds)

        task = ScheduledTask(
            task_id=task_id,
            workflow_id=workflow_id,
            execution_id=execution_id,
            node_id=node_id,
            scheduled_at=scheduled_at,
            priority=priority,
        )

        self._scheduled_tasks[task_id] = task
        return task

    def get_task(self, task_id: str) -> ScheduledTask | None:
        """Get a scheduled task."""
        return self._scheduled_tasks.get(task_id)

    def get_ready_tasks(self) -> list[ScheduledTask]:
        """Get tasks ready to execute."""
        now = datetime.now(timezone.utc)
        return [
            task for task in self._scheduled_tasks.values()
            if task.status == "pending" and task.scheduled_at <= now
        ]

    def complete_task(self, task_id: str) -> bool:
        """Mark task as complete."""
        task = self._scheduled_tasks.get(task_id)
        if task:
            task.status = "completed"
            return True
        return False

    def cancel_task(self, task_id: str) -> bool:
        """Cancel a task."""
        task = self._scheduled_tasks.get(task_id)
        if task:
            task.status = "cancelled"
            return True
        return False

    def get_parallel_groups(
        self,
        nodes: list[str],
    ) -> list[list[str]]:
        """Group nodes that can run in parallel.

        Args:
            nodes: List of node IDs.

        Returns:
            List of parallel groups.
        """
        if not nodes:
            return []

        # All nodes can run in parallel by default
        return [nodes]


# Global workflow scheduler
_scheduler: WorkflowScheduler | None = None
_scheduler_lock = __import__("threading").Lock()


def get_workflow_scheduler() -> WorkflowScheduler:
    """Get the global workflow scheduler."""
    global _scheduler
    with _scheduler_lock:
        if _scheduler is None:
            _scheduler = WorkflowScheduler()
        return _scheduler


def reset_workflow_scheduler() -> None:
    """Reset the global workflow scheduler."""
    global _scheduler
    with _scheduler_lock:
        _scheduler = None
