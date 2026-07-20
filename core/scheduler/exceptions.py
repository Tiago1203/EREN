"""Exceptions for the Cognitive Scheduler."""

from __future__ import annotations


class SchedulingError(Exception):
    """Base exception for scheduling errors."""

    def __init__(self, message: str = "", **kwargs) -> None:
        super().__init__(message)
        self.message = message
        self.context = kwargs


class TaskNotFoundError(SchedulingError):
    """Raised when a task is not found."""

    def __init__(self, task_id: str = "") -> None:
        super().__init__(f"Task '{task_id}' not found")
        self.task_id = task_id


class TaskAlreadyScheduledError(SchedulingError):
    """Raised when a task is already scheduled."""

    def __init__(self, task_id: str = "") -> None:
        super().__init__(f"Task '{task_id}' is already scheduled")
        self.task_id = task_id


class InvalidTaskStateError(SchedulingError):
    """Raised when a task state transition is invalid."""

    def __init__(
        self,
        task_id: str = "",
        from_state: str = "",
        to_state: str = "",
    ) -> None:
        super().__init__(
            f"Invalid task state transition for '{task_id}' from '{from_state}' to '{to_state}'"
        )
        self.task_id = task_id
        self.from_state = from_state
        self.to_state = to_state


class CapacityExceededError(SchedulingError):
    """Raised when capacity is exceeded."""

    def __init__(
        self,
        capability: str = "",
        max_capacity: int = 0,
    ) -> None:
        super().__init__(
            f"Capacity exceeded for capability '{capability}' (max: {max_capacity})"
        )
        self.capability = capability
        self.max_capacity = max_capacity


class QueueFullError(SchedulingError):
    """Raised when queue is full."""

    def __init__(self, queue_name: str = "", max_size: int = 0) -> None:
        super().__init__(
            f"Queue '{queue_name}' is full (max size: {max_size})"
        )
        self.queue_name = queue_name
        self.max_size = max_size


class TaskTimeoutError(SchedulingError):
    """Raised when a task times out."""

    def __init__(
        self,
        task_id: str = "",
        timeout_ms: int = 0,
    ) -> None:
        super().__init__(
            f"Task '{task_id}' timed out after {timeout_ms}ms"
        )
        self.task_id = task_id
        self.timeout_ms = timeout_ms


class DependencyError(SchedulingError):
    """Raised when task dependencies are not met."""

    def __init__(self, task_id: str = "", dependency_id: str = "") -> None:
        super().__init__(
            f"Task '{task_id}' has unmet dependency: {dependency_id}"
        )
        self.task_id = task_id
        self.dependency_id = dependency_id


class StrategyError(SchedulingError):
    """Raised when a scheduling strategy error occurs."""

    def __init__(self, strategy: str = "", reason: str = "") -> None:
        super().__init__(
            f"Strategy '{strategy}' error: {reason}"
        )
        self.strategy = strategy
        self.reason = reason
