"""Checkpoint management for EREN Cognitive Workflow Engine.

Handles workflow state checkpointing and recovery.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from core.workflows.types import (
    Checkpoint,
    NodeExecution,
    WorkflowExecution,
)

if TYPE_CHECKING:
    pass


class CheckpointManager:
    """Manages workflow checkpoints.

    The Checkpoint Manager does NOT:
    - Execute tasks
    - Know about implementations

    It ONLY:
    - Creates checkpoints
    - Stores state snapshots
    - Restores from checkpoints
    """

    def __init__(self):
        """Initialize checkpoint manager."""
        self._checkpoints: dict[str, Checkpoint] = {}
        self._execution_checkpoints: dict[str, list[str]] = {}  # execution_id -> checkpoint_ids

    def create_checkpoint(
        self,
        execution: WorkflowExecution,
        metadata: dict | None = None,
    ) -> Checkpoint:
        """Create a checkpoint.

        Args:
            execution: Current execution state.
            metadata: Additional metadata.

        Returns:
            Created checkpoint.
        """
        checkpoint_id = str(uuid.uuid4())

        # Serialize node executions
        node_executions = {}
        for node_id, node_exec in execution.node_executions.items():
            node_executions[node_id] = {
                "status": node_exec.status.value,
                "result": node_exec.result,
                "error": node_exec.error,
                "retry_count": node_exec.retry_count,
                "started_at": node_exec.started_at.isoformat() if node_exec.started_at else None,
                "completed_at": node_exec.completed_at.isoformat() if node_exec.completed_at else None,
            }

        checkpoint = Checkpoint(
            checkpoint_id=checkpoint_id,
            execution_id=execution.execution_id,
            state=execution.state.copy(),
            node_executions=node_executions,
            completed_node_ids=execution.completed_node_ids.copy(),
            current_node_ids=execution.current_node_ids.copy(),
            metadata=metadata or {},
        )

        self._checkpoints[checkpoint_id] = checkpoint

        if execution.execution_id not in self._execution_checkpoints:
            self._execution_checkpoints[execution.execution_id] = []
        self._execution_checkpoints[execution.execution_id].append(checkpoint_id)
        execution.checkpoint_ids.append(checkpoint_id)

        return checkpoint

    def get_checkpoint(self, checkpoint_id: str) -> Checkpoint | None:
        """Get a checkpoint.

        Args:
            checkpoint_id: Checkpoint ID.

        Returns:
            Checkpoint or None.
        """
        return self._checkpoints.get(checkpoint_id)

    def get_latest_checkpoint(
        self,
        execution_id: str,
    ) -> Checkpoint | None:
        """Get the latest checkpoint for an execution.

        Args:
            execution_id: Execution ID.

        Returns:
            Latest checkpoint or None.
        """
        checkpoint_ids = self._execution_checkpoints.get(execution_id, [])
        if not checkpoint_ids:
            return None

        latest_id = checkpoint_ids[-1]
        return self._checkpoints.get(latest_id)

    def get_all_checkpoints(
        self,
        execution_id: str,
    ) -> list[Checkpoint]:
        """Get all checkpoints for an execution.

        Args:
            execution_id: Execution ID.

        Returns:
            List of checkpoints.
        """
        checkpoint_ids = self._execution_checkpoints.get(execution_id, [])
        return [
            self._checkpoints[cid]
            for cid in checkpoint_ids
            if cid in self._checkpoints
        ]

    def restore_from_checkpoint(
        self,
        checkpoint_id: str,
    ) -> WorkflowExecution | None:
        """Restore execution from checkpoint.

        Args:
            checkpoint_id: Checkpoint ID.

        Returns:
            Restored execution or None.
        """
        checkpoint = self._checkpoints.get(checkpoint_id)
        if not checkpoint:
            return None

        # Create new execution from checkpoint
        execution = WorkflowExecution(
            execution_id=f"{checkpoint.execution_id}-restored-{uuid.uuid4().hex[:8]}",
            workflow_id="",  # Will be set by caller
            workflow_name="",
            state=checkpoint.state.copy(),
            completed_node_ids=checkpoint.completed_node_ids.copy(),
            current_node_ids=checkpoint.current_node_ids.copy(),
        )

        # Restore node executions
        for node_id, node_data in checkpoint.node_executions.items():
            from core.workflows.types import NodeStatus

            node_exec = NodeExecution(
                node_id=node_id,
                execution_id=execution.execution_id,
                status=NodeStatus(node_data["status"]),
                result=node_data.get("result"),
                error=node_data.get("error", ""),
                retry_count=node_data.get("retry_count", 0),
            )

            if node_data.get("started_at"):
                node_exec.started_at = datetime.fromisoformat(node_data["started_at"])
            if node_data.get("completed_at"):
                node_exec.completed_at = datetime.fromisoformat(node_data["completed_at"])

            execution.node_executions[node_id] = node_exec

        return execution

    def delete_checkpoint(self, checkpoint_id: str) -> bool:
        """Delete a checkpoint.

        Args:
            checkpoint_id: Checkpoint ID.

        Returns:
            True if deleted.
        """
        checkpoint = self._checkpoints.pop(checkpoint_id, None)
        if checkpoint:
            # Remove from execution tracking
            if checkpoint.execution_id in self._execution_checkpoints:
                ids = self._execution_checkpoints[checkpoint.execution_id]
                if checkpoint_id in ids:
                    ids.remove(checkpoint_id)
            return True
        return False

    def delete_execution_checkpoints(self, execution_id: str) -> int:
        """Delete all checkpoints for an execution.

        Args:
            execution_id: Execution ID.

        Returns:
            Number of checkpoints deleted.
        """
        checkpoint_ids = self._execution_checkpoints.pop(execution_id, [])
        deleted = 0

        for cid in checkpoint_ids:
            if cid in self._checkpoints:
                del self._checkpoints[cid]
                deleted += 1

        return deleted

    def get_checkpoint_count(self, execution_id: str) -> int:
        """Get checkpoint count for an execution.

        Args:
            execution_id: Execution ID.

        Returns:
            Number of checkpoints.
        """
        return len(self._execution_checkpoints.get(execution_id, []))


# Global checkpoint manager
_checkpoint_manager: CheckpointManager | None = None
_checkpoint_lock = __import__("threading").Lock()


def get_checkpoint_manager() -> CheckpointManager:
    """Get the global checkpoint manager.

    Returns:
        Global CheckpointManager instance.
    """
    global _checkpoint_manager
    with _checkpoint_lock:
        if _checkpoint_manager is None:
            _checkpoint_manager = CheckpointManager()
        return _checkpoint_manager


def reset_checkpoint_manager() -> None:
    """Reset the global checkpoint manager."""
    global _checkpoint_manager
    with _checkpoint_lock:
        _checkpoint_manager = None
