"""Agent scheduler for EREN Cognitive Agent Runtime.

Schedules and executes agent tasks.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Callable

from core.agents.types import AgentTask, TaskStatus

if TYPE_CHECKING:
    pass


class AgentScheduler:
    """Schedules and executes agent tasks.

    The Scheduler does NOT:
    - Execute tasks itself
    - Know about implementations

    It ONLY:
    - Queues tasks
    - Assigns tasks to agents
    - Manages task dependencies
    - Handles timeouts
    """

    def __init__(self):
        """Initialize scheduler."""
        self._tasks: dict[str, AgentTask] = {}
        self._queue: list[str] = []  # Task IDs
        self._running: dict[str, str] = {}  # task_id -> agent_id
        self._callbacks: dict[str, list] = {}  # event_type -> callbacks

    def submit_task(
        self,
        agent_id: str,
        capability: str,
        description: str,
        input_data: dict | None = None,
        priority: int = 5,
        depends_on: list[str] | None = None,
        max_retries: int = 3,
    ) -> AgentTask:
        """Submit a task for execution.

        Args:
            agent_id: Agent ID to execute task.
            capability: Required capability.
            description: Task description.
            input_data: Task input.
            priority: Task priority (1-10).
            depends_on: Task dependencies.
            max_retries: Maximum retries.

        Returns:
            Submitted task.
        """
        task_id = str(uuid.uuid4())

        task = AgentTask(
            task_id=task_id,
            agent_id=agent_id,
            capability=capability,
            description=description,
            input_data=input_data or {},
            priority=priority,
            depends_on=depends_on or [],
            max_retries=max_retries,
            created_at=datetime.now(timezone.utc),
        )

        self._tasks[task_id] = task
        self._queue.append(task_id)

        # Sort queue by priority
        self._queue.sort(
            key=lambda t: self._tasks[t].priority
        )

        return task

    def get_task(self, task_id: str) -> AgentTask | None:
        """Get task by ID.

        Args:
            task_id: Task ID.

        Returns:
            Task or None.
        """
        return self._tasks.get(task_id)

    def get_all_tasks(self) -> list[AgentTask]:
        """Get all tasks.

        Returns:
            List of tasks.
        """
        return list(self._tasks.values())

    def get_pending_tasks(self) -> list[AgentTask]:
        """Get pending tasks.

        Returns:
            List of pending tasks.
        """
        return [
            task for task in self._tasks.values()
            if task.status == TaskStatus.PENDING
        ]

    def get_ready_tasks(
        self,
        completed_tasks: dict[str, Any] | None = None,
    ) -> list[AgentTask]:
        """Get tasks ready to execute (dependencies met).

        Args:
            completed_tasks: Dict of completed task IDs.

        Returns:
            List of ready tasks.
        """
        completed = completed_tasks or {}

        ready = []
        for task in self._tasks.values():
            if task.status != TaskStatus.PENDING:
                continue

            # Check dependencies
            deps_met = all(
                dep_id in completed or
                self._tasks.get(dep_id, AgentTask(task_id="", agent_id="", capability="", description="")).status == TaskStatus.COMPLETED
                for dep_id in task.depends_on
            )

            if deps_met:
                ready.append(task)

        return ready

    def start_task(
        self,
        task_id: str,
        agent_id: str,
    ) -> AgentTask | None:
        """Start a task.

        Args:
            task_id: Task ID.
            agent_id: Agent executing.

        Returns:
            Started task or None.
        """
        task = self._tasks.get(task_id)
        if not task or task.status != TaskStatus.PENDING:
            return None

        task.status = TaskStatus.RUNNING
        task.agent_id = agent_id
        task.started_at = datetime.now(timezone.utc)
        task.assigned_at = datetime.now(timezone.utc)

        self._running[task_id] = agent_id

        return task

    def complete_task(
        self,
        task_id: str,
        output_data: Any,
    ) -> AgentTask | None:
        """Mark task as completed.

        Args:
            task_id: Task ID.
            output_data: Task output.

        Returns:
            Completed task or None.
        """
        task = self._tasks.get(task_id)
        if not task or task.status != TaskStatus.RUNNING:
            return None

        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.now(timezone.utc)
        task.output_data = output_data

        self._running.pop(task_id, None)

        return task

    def fail_task(
        self,
        task_id: str,
        error: str,
    ) -> AgentTask | None:
        """Mark task as failed.

        Args:
            task_id: Task ID.
            error: Error message.

        Returns:
            Failed task or None.
        """
        task = self._tasks.get(task_id)
        if not task or task.status != TaskStatus.RUNNING:
            return None

        task.retries += 1
        task.error = error

        if task.retries >= task.max_retries:
            task.status = TaskStatus.FAILED
            task.completed_at = datetime.now(timezone.utc)
        else:
            # Reset for retry
            task.status = TaskStatus.PENDING
            task.started_at = None

        self._running.pop(task_id, None)

        return task

    def cancel_task(self, task_id: str) -> bool:
        """Cancel a task.

        Args:
            task_id: Task ID.

        Returns:
            True if cancelled.
        """
        task = self._tasks.get(task_id)
        if not task:
            return False

        task.status = TaskStatus.CANCELLED
        task.completed_at = datetime.now(timezone.utc)

        self._running.pop(task_id, None)
        if task_id in self._queue:
            self._queue.remove(task_id)

        return True

    def get_running_tasks(self) -> list[AgentTask]:
        """Get running tasks.

        Returns:
            List of running tasks.
        """
        return [
            task for task in self._tasks.values()
            if task.status == TaskStatus.RUNNING
        ]

    def get_task_stats(self) -> dict:
        """Get task statistics.

        Returns:
            Statistics dictionary.
        """
        counts = {
            "pending": 0,
            "running": 0,
            "completed": 0,
            "failed": 0,
            "cancelled": 0,
        }

        for task in self._tasks.values():
            counts[task.status.value] = counts.get(task.status.value, 0) + 1

        return {
            "total_tasks": len(self._tasks),
            "by_status": counts,
            "running_count": len(self._running),
            "queue_size": len(self._queue),
        }

    def clear_completed(self, before_hours: int = 24) -> int:
        """Clear completed tasks.

        Args:
            before_hours: Clear tasks completed before this many hours ago.

        Returns:
            Number of tasks cleared.
        """
        cutoff = datetime.now(timezone.utc).timestamp() - (before_hours * 3600)
        cleared = 0

        to_remove = []
        for task_id, task in self._tasks.items():
            if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
                if task.completed_at and task.completed_at.timestamp() < cutoff:
                    to_remove.append(task_id)
                    cleared += 1

        for task_id in to_remove:
            self._tasks.pop(task_id, None)

        return cleared


# Global scheduler
_global_scheduler: AgentScheduler | None = None
_scheduler_lock = __import__("threading").Lock()


def get_scheduler() -> AgentScheduler:
    """Get the global agent scheduler.

    Returns:
        Global AgentScheduler instance.
    """
    global _global_scheduler
    with _scheduler_lock:
        if _global_scheduler is None:
            _global_scheduler = AgentScheduler()
        return _global_scheduler


def reset_scheduler() -> None:
    """Reset the global agent scheduler."""
    global _global_scheduler
    with _scheduler_lock:
        _global_scheduler = None
