"""Workflow runtime for EREN Cognitive Workflow Platform.

Runtime for orchestrating workflow execution.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Callable

from core.workflows.types import (
    WorkflowDefinition,
    WorkflowExecution,
    WorkflowStatus,
    NodeExecution,
    NodeStatus,
)
from core.workflows.state_store import get_state_store, StateStore
from core.workflows.checkpoint import get_checkpoint_manager, CheckpointManager
from core.workflows.scheduler import get_workflow_scheduler, WorkflowScheduler
from core.workflows.executor import get_task_executor, TaskExecutor

if TYPE_CHECKING:
    pass


class WorkflowRuntime:
    """Runtime for orchestrating workflow execution.

    The Workflow Runtime does NOT:
    - Know about implementations
    - Know about AI/LLM/RAG
    - Execute tasks directly

    It ONLY:
    - Creates instances
    - Starts workflows
    - Pauses workflows
    - Resumes workflows
    - Cancels workflows
    - Finishes workflows
    """

    def __init__(self):
        """Initialize workflow runtime."""
        self._state_store = get_state_store()
        self._checkpoint_manager = get_checkpoint_manager()
        self._scheduler = get_workflow_scheduler()
        self._executor = get_task_executor()

        # Event handlers
        self._event_handlers: dict[str, list[Callable]] = {}

    def register_event_handler(
        self,
        event: str,
        handler: Callable,
    ) -> None:
        """Register an event handler.

        Args:
            event: Event name.
            handler: Handler function.
        """
        if event not in self._event_handlers:
            self._event_handlers[event] = []
        self._event_handlers[event].append(handler)

    def _emit_event(self, event: str, *args, **kwargs) -> None:
        """Emit an event."""
        handlers = self._event_handlers.get(event, [])
        for handler in handlers:
            try:
                handler(*args, **kwargs)
            except Exception:
                pass

    def create_instance(
        self,
        definition: WorkflowDefinition,
        input_data: dict | None = None,
    ) -> WorkflowExecution:
        """Create a workflow instance.

        Args:
            definition: Workflow definition.
            input_data: Initial input data.

        Returns:
            Created execution.
        """
        execution_id = str(uuid.uuid4())

        execution = self._state_store.create_execution(
            execution_id=execution_id,
            workflow_id=definition.workflow_id,
            workflow_name=definition.name,
            input_data=input_data,
        )

        # Initialize node executions
        for node in definition.nodes:
            node_exec = NodeExecution(
                node_id=node.node_id,
                execution_id=execution_id,
            )
            execution.node_executions[node.node_id] = node_exec

        self._state_store.save_execution(execution)

        return execution

    def start(
        self,
        execution: WorkflowExecution,
        definition: WorkflowDefinition,
    ) -> WorkflowExecution:
        """Start a workflow.

        Args:
            execution: Execution to start.
            definition: Workflow definition.

        Returns:
            Started execution.
        """
        from core.workflows.graph import get_execution_graph

        graph = get_execution_graph(definition)

        # Validate
        is_valid, errors = graph.validate()
        if not is_valid:
            raise ValueError(f"Invalid workflow: {errors}")

        execution.status = WorkflowStatus.RUNNING
        execution.started_at = datetime.now(timezone.utc)
        self._state_store.save_execution(execution)

        self._emit_event("workflow_started", execution)

        # Create initial checkpoint
        self._checkpoint_manager.create_checkpoint(execution, {"phase": "start"})

        return execution

    def pause(self, execution_id: str) -> bool:
        """Pause a workflow.

        Args:
            execution_id: Execution ID.

        Returns:
            True if paused.
        """
        execution = self._state_store.load_execution(execution_id)
        if not execution or execution.status != WorkflowStatus.RUNNING:
            return False

        # Create checkpoint before pausing
        self._checkpoint_manager.create_checkpoint(execution, {"phase": "pause"})

        execution.status = WorkflowStatus.PAUSED
        self._state_store.save_execution(execution)

        self._emit_event("workflow_paused", execution)

        return True

    def resume(self, execution_id: str) -> WorkflowExecution | None:
        """Resume a paused workflow.

        Args:
            execution_id: Execution ID.

        Returns:
            Resumed execution or None.
        """
        execution = self._state_store.load_execution(execution_id)
        if not execution or execution.status != WorkflowStatus.PAUSED:
            return None

        execution.status = WorkflowStatus.RUNNING
        self._state_store.save_execution(execution)

        self._emit_event("workflow_resumed", execution)

        return execution

    def cancel(self, execution_id: str) -> bool:
        """Cancel a workflow.

        Args:
            execution_id: Execution ID.

        Returns:
            True if cancelled.
        """
        execution = self._state_store.load_execution(execution_id)
        if not execution:
            return False

        if execution.status in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED, WorkflowStatus.CANCELLED]:
            return False

        execution.status = WorkflowStatus.CANCELLED
        execution.completed_at = datetime.now(timezone.utc)
        self._state_store.save_execution(execution)

        self._emit_event("workflow_cancelled", execution)

        return True

    def finish(
        self,
        execution: WorkflowExecution,
        status: WorkflowStatus,
        error_message: str = "",
    ) -> WorkflowExecution:
        """Finish a workflow.

        Args:
            execution: Execution to finish.
            status: Final status.
            error_message: Error message if failed.

        Returns:
            Finished execution.
        """
        execution.status = status
        execution.completed_at = datetime.now(timezone.utc)
        execution.error_message = error_message

        self._state_store.save_execution(execution)

        # Create final checkpoint
        self._checkpoint_manager.create_checkpoint(execution, {"phase": "end"})

        if status == WorkflowStatus.COMPLETED:
            self._emit_event("workflow_completed", execution)
        else:
            self._emit_event("workflow_failed", execution, error_message)

        return execution


# Global workflow runtime
_runtime: WorkflowRuntime | None = None
_runtime_lock = __import__("threading").Lock()


def get_workflow_runtime() -> WorkflowRuntime:
    """Get the global workflow runtime."""
    global _runtime
    with _runtime_lock:
        if _runtime is None:
            _runtime = WorkflowRuntime()
        return _runtime


def reset_workflow_runtime() -> None:
    """Reset the global workflow runtime."""
    global _runtime
    with _runtime_lock:
        _runtime = None
