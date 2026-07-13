"""Scheduling queue implementation.

Provides queue management for cognitive tasks.

Architecture only -- no implementations, no business logic.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable

from .scheduling_types import (
    CognitiveTask,
    QueueStatistics,
    TaskPriority,
    TaskState,
)

if TYPE_CHECKING:
    pass


# =============================================================================
# Queue Entry
# =============================================================================


@dataclass
class QueueEntry:
    """An entry in the scheduling queue."""

    task: CognitiveTask
    enqueued_at: str = ""
    priority_override: int | None = None

    def __post_init__(self) -> None:
        """Set enqueue time."""
        from datetime import datetime, timezone
        if not self.enqueued_at:
            self.enqueued_at = datetime.now(timezone.utc).isoformat()

    @property
    def effective_priority(self) -> int:
        """Get effective priority (considering override)."""
        if self.priority_override is not None:
            return self.priority_override
        return self.task.priority.value


# =============================================================================
# Scheduling Queue
# =============================================================================


class SchedulingQueue:
    """Queue for scheduling cognitive tasks.

    Manages task queuing with different strategies.
    """

    def __init__(self, name: str = "default") -> None:
        """Initialize the queue.

        Args:
            name: Queue name.
        """
        self._name = name
        self._entries: list[QueueEntry] = []
        self._by_task_id: dict[str, QueueEntry] = {}
        self._lock = threading.RLock()

    @property
    def name(self) -> str:
        """Get queue name."""
        return self._name

    @property
    def size(self) -> int:
        """Get queue size."""
        with self._lock:
            return len(self._entries)

    def enqueue(self, task: CognitiveTask) -> None:
        """Enqueue a task.

        Args:
            task: Task to enqueue.
        """
        with self._lock:
            entry = QueueEntry(task=task)
            self._entries.append(entry)
            self._by_task_id[task.metadata.task_id] = entry

    def dequeue(self) -> CognitiveTask | None:
        """Dequeue the next task.

        Returns:
            Next task or None if queue is empty.
        """
        with self._lock:
            if not self._entries:
                return None
            entry = self._entries.pop(0)
            self._by_task_id.pop(entry.task.metadata.task_id, None)
            return entry.task

    def peek(self) -> CognitiveTask | None:
        """Peek at the next task without removing.

        Returns:
            Next task or None.
        """
        with self._lock:
            if not self._entries:
                return None
            return self._entries[0].task

    def get(self, task_id: str) -> CognitiveTask | None:
        """Get a task by ID.

        Args:
            task_id: Task ID.

        Returns:
            Task or None.
        """
        with self._lock:
            entry = self._by_task_id.get(task_id)
            return entry.task if entry else None

    def remove(self, task_id: str) -> bool:
        """Remove a task from queue.

        Args:
            task_id: Task ID.

        Returns:
            True if removed.
        """
        with self._lock:
            entry = self._by_task_id.get(task_id)
            if not entry:
                return False
            self._entries.remove(entry)
            del self._by_task_id[task_id]
            return True

    def get_by_state(self, state: TaskState) -> list[CognitiveTask]:
        """Get tasks by state.

        Args:
            state: Task state.

        Returns:
            List of tasks.
        """
        with self._lock:
            return [e.task for e in self._entries if e.task.state == state]

    def get_by_capability(self, capability: str) -> list[CognitiveTask]:
        """Get tasks by required capability.

        Args:
            capability: Capability name.

        Returns:
            List of tasks.
        """
        with self._lock:
            return [
                e.task for e in self._entries
                if e.task.capability == capability
            ]

    def get_pending(self) -> list[CognitiveTask]:
        """Get all pending tasks.

        Returns:
            List of pending tasks.
        """
        return self.get_by_state(TaskState.PENDING)

    def get_ready(self) -> list[CognitiveTask]:
        """Get all ready tasks.

        Returns:
            List of ready tasks.
        """
        return self.get_by_state(TaskState.READY)

    def clear(self) -> None:
        """Clear the queue."""
        with self._lock:
            self._entries.clear()
            self._by_task_id.clear()

    def get_statistics(self) -> QueueStatistics:
        """Get queue statistics.

        Returns:
            Queue statistics.
        """
        with self._lock:
            stats = QueueStatistics(total_tasks=len(self._entries))

            for entry in self._entries:
                task = entry.task
                if task.state == TaskState.PENDING:
                    stats.pending_tasks += 1
                elif task.state == TaskState.READY:
                    stats.ready_tasks += 1
                elif task.state == TaskState.RUNNING:
                    stats.running_tasks += 1
                elif task.state == TaskState.COMPLETED:
                    stats.completed_tasks += 1
                elif task.state == TaskState.FAILED:
                    stats.failed_tasks += 1

            return stats


# =============================================================================
# Multi-Queue Manager
# =============================================================================


class MultiQueueManager:
    """Manages multiple scheduling queues."""

    def __init__(self) -> None:
        """Initialize the manager."""
        self._queues: dict[str, SchedulingQueue] = {}
        self._lock = threading.RLock()

    def create_queue(self, name: str) -> SchedulingQueue:
        """Create a new queue.

        Args:
            name: Queue name.

        Returns:
            New queue.
        """
        with self._lock:
            if name in self._queues:
                return self._queues[name]
            queue = SchedulingQueue(name=name)
            self._queues[name] = queue
            return queue

    def get_queue(self, name: str) -> SchedulingQueue | None:
        """Get a queue by name.

        Args:
            name: Queue name.

        Returns:
            Queue or None.
        """
        return self._queues.get(name)

    def get_or_create(self, name: str) -> SchedulingQueue:
        """Get or create a queue.

        Args:
            name: Queue name.

        Returns:
            Queue.
        """
        with self._lock:
            if name not in self._queues:
                self._queues[name] = SchedulingQueue(name=name)
            return self._queues[name]

    def get_all_queues(self) -> list[SchedulingQueue]:
        """Get all queues.

        Returns:
            List of queues.
        """
        with self._lock:
            return list(self._queues.values())

    def get_total_size(self) -> int:
        """Get total size across all queues.

        Returns:
            Total tasks.
        """
        with self._lock:
            return sum(q.size for q in self._queues.values())

    def clear_all(self) -> None:
        """Clear all queues."""
        with self._lock:
            for queue in self._queues.values():
                queue.clear()
