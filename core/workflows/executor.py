"""Workflow executor for EREN Cognitive Workflow Platform.

Executes tasks and invokes capabilities.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable

if TYPE_CHECKING:
    pass


class WorkflowExecutor:
    """Executes workflow tasks.

    The Workflow Executor does NOT:
    - Know about AI/LLM/RAG
    - Know about specific implementations

    It ONLY:
    - Executes tasks
    - Invokes agents
    - Invokes capabilities
    - Waits for results
    - Reports status
    """

    def __init__(self):
        """Initialize workflow executor."""
        self._executors: dict[str, Callable] = {}
        self._agent_handlers: dict[str, Callable] = {}
        self._capability_handlers: dict[str, Callable] = {}

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

    def register_agent_handler(
        self,
        agent_type: str,
        handler: Callable,
    ) -> None:
        """Register an agent handler.

        Args:
            agent_type: Agent type.
            handler: Handler function.
        """
        self._agent_handlers[agent_type] = handler

    def register_capability_handler(
        self,
        capability_name: str,
        handler: Callable,
    ) -> None:
        """Register a capability handler.

        Args:
            capability_name: Capability name.
            handler: Handler function.
        """
        self._capability_handlers[capability_name] = handler

    def execute_task(
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

        return {"executed": True, "task": task_name}

    def invoke_agent(
        self,
        agent_type: str,
        task: dict,
        context: dict,
    ) -> Any:
        """Invoke an agent.

        Args:
            agent_type: Agent type.
            task: Task to execute.
            context: Execution context.

        Returns:
            Agent result.
        """
        handler = self._agent_handlers.get(agent_type)

        if handler:
            return handler(task=task, context=context)

        return {"agent_invoked": True, "type": agent_type}

    def invoke_capability(
        self,
        capability_name: str,
        params: dict,
        context: dict,
    ) -> Any:
        """Invoke a capability.

        Args:
            capability_name: Capability name.
            params: Capability parameters.
            context: Execution context.

        Returns:
            Capability result.
        """
        handler = self._capability_handlers.get(capability_name)

        if handler:
            return handler(params=params, context=context)

        return {"capability_invoked": True, "name": capability_name}

    def has_executor(self, task_name: str) -> bool:
        """Check if executor exists."""
        return task_name in self._executors

    def has_agent_handler(self, agent_type: str) -> bool:
        """Check if agent handler exists."""
        return agent_type in self._agent_handlers

    def has_capability_handler(self, capability_name: str) -> bool:
        """Check if capability handler exists."""
        return capability_name in self._capability_handlers


# Alias for backwards compatibility
TaskExecutor = WorkflowExecutor


# Global workflow executor
_executor: WorkflowExecutor | None = None
_executor_lock = __import__("threading").Lock()


def get_task_executor() -> WorkflowExecutor:
    """Get the global task executor."""
    global _executor
    with _executor_lock:
        if _executor is None:
            _executor = WorkflowExecutor()
        return _executor


def reset_task_executor() -> None:
    """Reset the global task executor."""
    global _executor
    with _executor_lock:
        _executor = None
