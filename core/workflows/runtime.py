"""Workflow runtime for EREN Cognitive Workflow Engine.

Runtime for executing workflows.
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
from core.workflows.state import get_state_manager, StateManager
from core.workflows.graph import get_execution_graph, ExecutionGraph
from core.workflows.checkpoint import get_checkpoint_manager

if TYPE_CHECKING:
    pass


class WorkflowRuntime:
    """Runtime for executing workflows.

    The Workflow Runtime does NOT:
    - Know about implementations
    - Know about AI/LLM/RAG

    It ONLY:
    - Orchestrates execution
    - Manages state transitions
    - Handles checkpoints
    """

    def __init__(self):
        """Initialize workflow runtime."""
        self._state_manager = get_state_manager()
        self._checkpoint_manager = get_checkpoint_manager()

        # Task handlers: node_type -> handler_function
        self._handlers: dict[str, Callable] = {}

        # Event handlers
        self._event_handlers: dict[str, list[Callable]] = {}

    def register_handler(
        self,
        node_type: str,
        handler: Callable,
    ) -> None:
        """Register a task handler.

        Args:
            node_type: Node type.
            handler: Handler function.
        """
        self._handlers[node_type] = handler

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
        """Emit an event.

        Args:
            event: Event name.
            args: Event args.
            kwargs: Event kwargs.
        """
        handlers = self._event_handlers.get(event, [])
        for handler in handlers:
            try:
                handler(*args, **kwargs)
            except Exception:
                pass

    def execute_node(
        self,
        execution: WorkflowExecution,
        node_id: str,
        input_data: dict | None = None,
    ) -> Any:
        """Execute a single node.

        Args:
            execution: Current execution.
            node_id: Node ID.
            input_data: Input data for the node.

        Returns:
            Node result.
        """
        graph = get_execution_graph(execution.workflow_id)
        node = graph.get_node(node_id)

        if not node:
            raise ValueError(f"Node {node_id} not found")

        # Create node execution
        node_exec = NodeExecution(
            node_id=node_id,
            execution_id=execution.execution_id,
            status=NodeStatus.RUNNING,
            started_at=datetime.now(timezone.utc),
        )

        # Start node
        self._state_manager.start_node(
            execution.execution_id,
            node_id,
            node_exec,
        )

        self._emit_event("node_started", execution, node_id)

        try:
            # Get handler
            handler = self._handlers.get(node.node_type.value)

            if handler:
                result = handler(
                    node_config=node.config,
                    input_data=input_data or {},
                    execution_state=execution.state,
                )
            else:
                # No handler - simulate execution
                result = {"status": "simulated", "node_id": node_id}

            # Complete node
            self._state_manager.complete_node(
                execution.execution_id,
                node_id,
                result,
            )

            # Update state
            execution.state[f"node_{node_id}_result"] = result

            self._emit_event("node_completed", execution, node_id, result)

            return result

        except Exception as e:
            # Fail node
            self._state_manager.fail_node(
                execution.execution_id,
                node_id,
                str(e),
            )

            self._emit_event("node_failed", execution, node_id, str(e))

            raise

    def execute_workflow(
        self,
        definition: WorkflowDefinition,
        input_data: dict | None = None,
        auto_complete: bool = True,
        max_iterations: int = 1000,
    ) -> WorkflowExecution:
        """Execute a workflow.

        Args:
            definition: Workflow definition.
            input_data: Initial input data.
            auto_complete: Whether to auto-complete when done.
            max_iterations: Maximum iterations to prevent infinite loops.

        Returns:
            Final execution.
        """
        execution_id = str(uuid.uuid4())

        graph = get_execution_graph(definition)

        # Validate
        is_valid, errors = graph.validate()
        if not is_valid:
            raise ValueError(f"Invalid workflow: {errors}")

        # Create execution
        execution = self._state_manager.create_execution(
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

        # Start execution
        self._state_manager.update_status(
            execution_id,
            WorkflowStatus.RUNNING,
        )

        self._emit_event("workflow_started", execution)

        # Create initial checkpoint
        self._checkpoint_manager.create_checkpoint(execution, {"phase": "start"})

        iteration = 0
        try:
            # Execute loop
            while execution.status == WorkflowStatus.RUNNING:
                iteration += 1
                if iteration > max_iterations:
                    self._state_manager.update_status(
                        execution_id,
                        WorkflowStatus.FAILED,
                    )
                    execution.error_message = "Max iterations exceeded"
                    self._emit_event("workflow_failed", execution, "Max iterations exceeded")
                    break

                # Get next nodes
                ready_nodes = graph.get_ready_nodes(execution)

                if not ready_nodes:
                    # Check if complete
                    if graph.is_complete(execution):
                        self._state_manager.update_status(
                            execution_id,
                            WorkflowStatus.COMPLETED,
                        )
                        self._emit_event("workflow_completed", execution)
                        break
                    else:
                        # Dead end
                        self._state_manager.update_status(
                            execution_id,
                            WorkflowStatus.FAILED,
                        )
                        execution.error_message = "Workflow has no ready nodes"
                        self._emit_event("workflow_failed", execution, "No ready nodes")
                        break

                # Execute ready nodes
                for node_id in ready_nodes:
                    if execution.status != WorkflowStatus.RUNNING:
                        break

                    try:
                        self.execute_node(execution, node_id, input_data)
                    except Exception as e:
                        if not auto_complete:
                            raise

        except Exception as e:
            self._state_manager.update_status(
                execution_id,
                WorkflowStatus.FAILED,
            )
            execution.error_message = str(e)
            self._emit_event("workflow_failed", execution, str(e))

        # Final checkpoint
        self._checkpoint_manager.create_checkpoint(execution, {"phase": "end"})

        return execution

    def pause_workflow(
        self,
        execution_id: str,
    ) -> bool:
        """Pause a workflow execution.

        Args:
            execution_id: Execution ID.

        Returns:
            True if paused.
        """
        execution = self._state_manager.get_execution(execution_id)
        if not execution:
            return False

        if execution.status != WorkflowStatus.RUNNING:
            return False

        # Create checkpoint before pausing
        self._checkpoint_manager.create_checkpoint(execution, {"phase": "pause"})

        self._state_manager.update_status(
            execution_id,
            WorkflowStatus.PAUSED,
        )

        self._emit_event("workflow_paused", execution)

        return True

    def resume_workflow(
        self,
        execution_id: str,
    ) -> WorkflowExecution | None:
        """Resume a paused workflow.

        Args:
            execution_id: Execution ID.

        Returns:
            Updated execution or None.
        """
        execution = self._state_manager.get_execution(execution_id)
        if not execution:
            return None

        if execution.status != WorkflowStatus.PAUSED:
            return None

        self._state_manager.update_status(
            execution_id,
            WorkflowStatus.RUNNING,
        )

        self._emit_event("workflow_resumed", execution)

        return execution

    def cancel_workflow(
        self,
        execution_id: str,
    ) -> bool:
        """Cancel a workflow execution.

        Args:
            execution_id: Execution ID.

        Returns:
            True if cancelled.
        """
        execution = self._state_manager.get_execution(execution_id)
        if not execution:
            return False

        if execution.status in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED, WorkflowStatus.CANCELLED]:
            return False

        self._state_manager.update_status(
            execution_id,
            WorkflowStatus.CANCELLED,
        )

        self._emit_event("workflow_cancelled", execution)

        return True


# Global workflow runtime
_runtime: WorkflowRuntime | None = None
_runtime_lock = __import__("threading").Lock()


def get_workflow_runtime() -> WorkflowRuntime:
    """Get the global workflow runtime.

    Returns:
        Global WorkflowRuntime instance.
    """
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
