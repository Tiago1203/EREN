"""State Store for EREN Cognitive Workflow Platform.

Persistent state management for workflows.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from core.workflows.types import (
    WorkflowExecution,
    WorkflowStatus,
)

if TYPE_CHECKING:
    pass


class StateStore:
    """Manages workflow state storage.

    The State Store does NOT:
    - Execute tasks
    - Know about implementations
    - Make decisions

    It ONLY:
    - Saves state
    - Reads state
    - Updates state
    - Versions state
    """

    def __init__(self):
        """Initialize state store."""
        self._executions: dict[str, WorkflowExecution] = {}
        self._versions: dict[str, list[dict]] = {}  # execution_id -> version snapshots

    def create_execution(
        self,
        execution_id: str,
        workflow_id: str,
        workflow_name: str,
        input_data: dict | None = None,
    ) -> WorkflowExecution:
        """Create a new execution.

        Args:
            execution_id: Execution ID.
            workflow_id: Workflow ID.
            workflow_name: Workflow name.
            input_data: Initial input data.

        Returns:
            Created execution.
        """
        execution = WorkflowExecution(
            execution_id=execution_id,
            workflow_id=workflow_id,
            workflow_name=workflow_name,
            input_data=input_data or {},
        )

        self._executions[execution_id] = execution
        self._versions[execution_id] = []

        return execution

    def save_execution(self, execution: WorkflowExecution) -> bool:
        """Save an execution.

        Args:
            execution: Execution to save.

        Returns:
            True if saved.
        """
        self._executions[execution.execution_id] = execution
        return True

    def load_execution(self, execution_id: str) -> WorkflowExecution | None:
        """Load an execution.

        Args:
            execution_id: Execution ID.

        Returns:
            Execution or None.
        """
        return self._executions.get(execution_id)

    def delete_execution(self, execution_id: str) -> bool:
        """Delete an execution.

        Args:
            execution_id: Execution ID.

        Returns:
            True if deleted.
        """
        if execution_id in self._executions:
            del self._executions[execution_id]
            self._versions.pop(execution_id, None)
            return True
        return False

    def create_version(self, execution: WorkflowExecution) -> str:
        """Create a version snapshot.

        Args:
            execution: Execution to snapshot.

        Returns:
            Version ID.
        """
        version_id = str(uuid.uuid4())

        snapshot = {
            "version_id": version_id,
            "execution_id": execution.execution_id,
            "status": execution.status.value,
            "state": execution.state.copy(),
            "current_node_ids": execution.current_node_ids.copy(),
            "completed_node_ids": execution.completed_node_ids.copy(),
            "failed_node_ids": execution.failed_node_ids.copy(),
            "created_at": datetime.now(UTC).isoformat(),
        }

        if execution.execution_id not in self._versions:
            self._versions[execution.execution_id] = []

        self._versions[execution.execution_id].append(snapshot)

        return version_id

    def load_version(
        self,
        execution_id: str,
        version_id: str,
    ) -> dict | None:
        """Load a specific version.

        Args:
            execution_id: Execution ID.
            version_id: Version ID.

        Returns:
            Version snapshot or None.
        """
        versions = self._versions.get(execution_id, [])
        for v in versions:
            if v["version_id"] == version_id:
                return v
        return None

    def load_latest_version(self, execution_id: str) -> dict | None:
        """Load the latest version.

        Args:
            execution_id: Execution ID.

        Returns:
            Latest version or None.
        """
        versions = self._versions.get(execution_id, [])
        if versions:
            return versions[-1]
        return None

    def list_versions(self, execution_id: str) -> list[str]:
        """List all version IDs.

        Args:
            execution_id: Execution ID.

        Returns:
            List of version IDs.
        """
        versions = self._versions.get(execution_id, [])
        return [v["version_id"] for v in versions]

    def get_all_executions(self) -> list[WorkflowExecution]:
        """Get all executions.

        Returns:
            List of executions.
        """
        return list(self._executions.values())

    def get_executions_by_status(
        self,
        status: WorkflowStatus,
    ) -> list[WorkflowExecution]:
        """Get executions by status.

        Args:
            status: Workflow status.

        Returns:
            List of executions.
        """
        return [
            e for e in self._executions.values()
            if e.status == status
        ]


# Global state store
_state_store: StateStore | None = None
_store_lock = __import__("threading").Lock()


def get_state_store() -> StateStore:
    """Get the global state store.

    Returns:
        Global StateStore instance.
    """
    global _state_store
    with _store_lock:
        if _state_store is None:
            _state_store = StateStore()
        return _state_store


def reset_state_store() -> None:
    """Reset the global state store."""
    global _state_store
    with _store_lock:
        _state_store = None
