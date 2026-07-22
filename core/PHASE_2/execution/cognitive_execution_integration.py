"""Cognitive Execution Runtime (PR-054).

Provides execution runtime capabilities for EREN OS.
Architecture only — no AI, no storage backend.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any, Callable


# =============================================================================
# Execution Events
# =============================================================================


class ExecutionEventType(str, Enum):
    """Types of execution events."""
    TASK_STARTED = "task_started"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
    TASK_CANCELLED = "task_cancelled"
    TASK_RETRY = "task_retry"


@dataclass
class ExecutionEvent:
    """Execution event."""
    event_type: ExecutionEventType
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    task_id: str = ""
    session_id: str = ""
    duration_ms: float = 0.0
    success: bool = True
    error: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


# =============================================================================
# Execution Status
# =============================================================================


class ExecutionStatus(str, Enum):
    """Status of execution."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# =============================================================================
# Executable Task
# =============================================================================


@dataclass
class ExecutableTask:
    """A task that can be executed."""
    id: str
    name: str
    handler: Callable
    args: tuple = ()
    kwargs: dict = field(default_factory=dict)
    timeout_seconds: float = 30.0
    retry_count: int = 0
    max_retries: int = 3


# =============================================================================
# Execution Runtime
# =============================================================================


class ExecutionRuntime:
    """Runtime for executing tasks."""

    def __init__(self):
        self._tasks: dict[str, ExecutableTask] = {}
        self._results: dict[str, Any] = {}
        self._status: dict[str, ExecutionStatus] = {}
        self._subscribers: list[Callable] = []

    def register_task(self, task: ExecutableTask) -> None:
        """Register a task."""
        self._tasks[task.id] = task
        self._status[task.id] = ExecutionStatus.PENDING

    def execute_task(self, task_id: str) -> dict[str, Any]:
        """Execute a registered task."""
        import time
        
        task = self._tasks.get(task_id)
        if not task:
            return {"success": False, "error": "Task not found"}

        self._status[task_id] = ExecutionStatus.RUNNING
        self._publish(ExecutionEvent(
            event_type=ExecutionEventType.TASK_STARTED,
            task_id=task_id,
        ))

        start = time.perf_counter()
        attempts = 0

        while attempts <= task.max_retries:
            try:
                result = task.handler(*task.args, **task.kwargs)
                duration_ms = (time.perf_counter() - start) * 1000

                self._status[task_id] = ExecutionStatus.COMPLETED
                self._results[task_id] = result

                self._publish(ExecutionEvent(
                    event_type=ExecutionEventType.TASK_COMPLETED,
                    task_id=task_id,
                    duration_ms=duration_ms,
                    success=True,
                ))

                return {
                    "success": True,
                    "result": result,
                    "duration_ms": duration_ms,
                    "attempts": attempts + 1,
                }

            except Exception as e:
                attempts += 1
                if attempts <= task.max_retries:
                    self._publish(ExecutionEvent(
                        event_type=ExecutionEventType.TASK_RETRY,
                        task_id=task_id,
                        error=str(e),
                    ))
                else:
                    duration_ms = (time.perf_counter() - start) * 1000
                    self._status[task_id] = ExecutionStatus.FAILED
                    self._results[task_id] = None

                    self._publish(ExecutionEvent(
                        event_type=ExecutionEventType.TASK_FAILED,
                        task_id=task_id,
                        duration_ms=duration_ms,
                        success=False,
                        error=str(e),
                    ))

                    return {
                        "success": False,
                        "error": str(e),
                        "duration_ms": duration_ms,
                        "attempts": attempts,
                    }

        return {"success": False, "error": "Max retries exceeded"}

    def cancel_task(self, task_id: str) -> bool:
        """Cancel a task."""
        if task_id in self._tasks:
            self._status[task_id] = ExecutionStatus.CANCELLED
            self._publish(ExecutionEvent(
                event_type=ExecutionEventType.TASK_CANCELLED,
                task_id=task_id,
            ))
            return True
        return False

    def get_status(self, task_id: str) -> ExecutionStatus | None:
        """Get task status."""
        return self._status.get(task_id)

    def get_result(self, task_id: str) -> Any | None:
        """Get task result."""
        return self._results.get(task_id)

    def subscribe(self, callback: Callable) -> None:
        """Subscribe to execution events."""
        self._subscribers.append(callback)

    def _publish(self, event: ExecutionEvent) -> None:
        """Publish an event."""
        for subscriber in self._subscribers:
            try:
                subscriber(event)
            except Exception:
                pass
