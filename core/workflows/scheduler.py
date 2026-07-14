"""Task scheduler for EREN Cognitive Workflow Engine.

Schedules workflow task execution.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

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

    def __init__(
        self,
        task_id: str,
        workflow_id: str,
        execution_id: str,
        node_id: str,
        scheduled_at: datetime,
    ):
        self.task_id = task_id
        self.workflow_id = workflow_id
        self.execution_id = execution_id
        self.node_id = node_id
        self.scheduled_at = scheduled_at
        self.status = "pending"


class WorkflowScheduler:
    """Schedules workflow task execution.

    The Workflow Scheduler does NOT:
    - Execute tasks
    - Know about implementations

    It ONLY:
    - Schedules tasks
    - Tracks scheduled tasks
    - Manages execution order
    """

    def __init__(self):
        """Initialize workflow scheduler."""
        self._scheduled_tasks: dict[str, ScheduledTask] = {}
        self._execution_queue: list[str] = []

    def schedule_task(
        self,
        workflow_id: str,
        execution_id: str,
        node_id: str,
        delay_seconds: float = 0.0,
    ) -> ScheduledTask:
        """Schedule a task.

        Args:
            workflow_id: Workflow ID.
            execution_id: Execution ID.
            node_id: Node ID.
            delay_seconds: Delay before execution.

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
        )

        self._scheduled_tasks[task_id] = task
        self._execution_queue.append(task_id)

        return task

    def get_task(self, task_id: str) -> ScheduledTask | None:
        """Get a scheduled task.

        Args:
            task_id: Task ID.

        Returns:
            Scheduled task or None.
        """
        return self._scheduled_tasks.get(task_id)

    def get_pending_tasks(self) -> list[ScheduledTask]:
        """Get pending tasks.

        Returns:
            List of pending tasks.
        """
        now = datetime.now(timezone.utc)
        pending = []

        for task in self._scheduled_tasks.values():
            if task.status == "pending" and task.scheduled_at <= now:
                pending.append(task)

        return pending

    def get_task_count(self) -> int:
        """Get total task count.

        Returns:
            Number of tasks.
        """
        return len(self._scheduled_tasks)

    def complete_task(self, task_id: str) -> bool:
        """Mark a task as complete.

        Args:
            task_id: Task ID.

        Returns:
            True if completed.
        """
        task = self._scheduled_tasks.get(task_id)
        if not task:
            return False

        task.status = "completed"
        return True

    def cancel_task(self, task_id: str) -> bool:
        """Cancel a scheduled task.

        Args:
            task_id: Task ID.

        Returns:
            True if cancelled.
        """
        task = self._scheduled_tasks.get(task_id)
        if not task:
            return False

        task.status = "cancelled"
        return True

    def clear_completed(self) -> int:
        """Clear completed tasks.

        Returns:
            Number of tasks cleared.
        """
        completed_ids = [
            tid for tid, task in self._scheduled_tasks.items()
            if task.status == "completed"
        ]

        for tid in completed_ids:
            del self._scheduled_tasks[tid]

        return len(completed_ids)


# Global workflow scheduler
_scheduler: WorkflowScheduler | None = None
_scheduler_lock = __import__("threading").Lock()


def get_workflow_scheduler() -> WorkflowScheduler:
    """Get the global workflow scheduler.

    Returns:
        Global WorkflowScheduler instance.
    """
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
