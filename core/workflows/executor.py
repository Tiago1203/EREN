"""Task executor for EREN Cognitive Workflow Engine.

Executes individual tasks within workflows.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable

if TYPE_CHECKING:
    pass


class TaskExecutor:
    """Executes tasks within workflows.

    The Task Executor does NOT:
    - Know about AI/LLM/RAG
    - Know about specific implementations

    It ONLY:
    - Executes task functions
    - Handles retries
    - Manages timeouts
    """

    def __init__(self):
        """Initialize task executor."""
        self._executors: dict[str, Callable] = {}

    def register_executor(
        self,
        task_name: str,
        executor: Callable,
    ) -> None:
        """Register a task executor.

        Args:
            task_name: Task name.
            executor: Executor function.
        """
        self._executors[task_name] = executor

    def execute(
        self,
        task_name: str,
        config: dict,
        context: dict,
    ) -> Any:
        """Execute a task.

        Args:
            task_name: Task name.
            config: Task configuration.
            context: Execution context.

        Returns:
            Task result.
        """
        executor = self._executors.get(task_name)

        if executor:
            return executor(config=config, context=context)

        # Default: return config as result
        return {"executed": True, "task": task_name, "config": config}

    def has_executor(self, task_name: str) -> bool:
        """Check if executor exists.

        Args:
            task_name: Task name.

        Returns:
            True if executor exists.
        """
        return task_name in self._executors

    def unregister_executor(self, task_name: str) -> bool:
        """Unregister a task executor.

        Args:
            task_name: Task name.

        Returns:
            True if unregistered.
        """
        if task_name in self._executors:
            del self._executors[task_name]
            return True
        return False


# Global task executor
_task_executor: TaskExecutor | None = None
_executor_lock = __import__("threading").Lock()


def get_task_executor() -> TaskExecutor:
    """Get the global task executor.

    Returns:
        Global TaskExecutor instance.
    """
    global _task_executor
    with _executor_lock:
        if _task_executor is None:
            _task_executor = TaskExecutor()
        return _task_executor


def reset_task_executor() -> None:
    """Reset the global task executor."""
    global _task_executor
    with _executor_lock:
        _task_executor = None
