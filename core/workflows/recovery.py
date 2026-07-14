"""Recovery Manager for EREN Cognitive Workflow Platform.

Handles workflow recovery, rollback, and compensation.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from core.workflows.types import (
    CompensationRecord,
    WorkflowExecution,
)

if TYPE_CHECKING:
    pass


class RecoveryManager:
    """Manages workflow recovery.

    The Recovery Manager does NOT:
    - Execute tasks
    - Know about implementations

    It ONLY:
    - Handles recovery
    - Manages rollback
    - Handles compensation
    - Coordinates saga
    """

    def __init__(self):
        """Initialize recovery manager."""
        self._compensation_log: dict[str, list[CompensationRecord]] = {}
        self._recovery_strategies: dict[str, Any] = {}

    def create_compensation(
        self,
        execution_id: str,
        node_id: str,
        action: str,
    ) -> CompensationRecord:
        """Create a compensation record.

        Args:
            execution_id: Execution ID.
            node_id: Node ID.
            action: Compensation action.

        Returns:
            Created compensation record.
        """
        record = CompensationRecord(
            record_id=str(uuid.uuid4()),
            node_id=node_id,
            action=action,
        )

        if execution_id not in self._compensation_log:
            self._compensation_log[execution_id] = []

        self._compensation_log[execution_id].append(record)
        return record

    def execute_compensation(
        self,
        execution_id: str,
        compensator: Any = None,
    ) -> tuple[bool, list[str]]:
        """Execute compensation for an execution.

        Args:
            execution_id: Execution ID.
            compensator: Optional compensator function.

        Returns:
            Tuple of (success, errors).
        """
        records = self._compensation_log.get(execution_id, [])
        if not records:
            return True, []

        errors = []
        success = True

        # Execute in reverse order (LIFO)
        for record in reversed(records):
            if record.executed:
                continue

            try:
                if compensator:
                    compensator(record.node_id, record.action)
                record.executed = True
                record.executed_at = datetime.now(UTC)
            except Exception as e:
                record.error = str(e)
                errors.append(str(e))
                success = False

        return success, errors

    def get_compensation_status(
        self,
        execution_id: str,
    ) -> dict:
        """Get compensation status.

        Args:
            execution_id: Execution ID.

        Returns:
            Status dictionary.
        """
        records = self._compensation_log.get(execution_id, [])

        return {
            "total": len(records),
            "executed": sum(1 for r in records if r.executed),
            "pending": sum(1 for r in records if not r.executed),
            "failed": sum(1 for r in records if r.error),
        }

    def rollback_to_version(
        self,
        execution: WorkflowExecution,
        version_snapshot: dict,
    ) -> bool:
        """Rollback to a version.

        Args:
            execution: Current execution.
            version_snapshot: Version to rollback to.

        Returns:
            True if rolled back.
        """
        execution.state = version_snapshot.get("state", {}).copy()
        execution.current_node_ids = version_snapshot.get("current_node_ids", []).copy()
        execution.completed_node_ids = version_snapshot.get("completed_node_ids", []).copy()
        execution.failed_node_ids = version_snapshot.get("failed_node_ids", []).copy()

        return True

    def register_recovery_strategy(
        self,
        strategy_name: str,
        strategy: Any,
    ) -> None:
        """Register a recovery strategy.

        Args:
            strategy_name: Strategy name.
            strategy: Strategy function.
        """
        self._recovery_strategies[strategy_name] = strategy

    def get_recovery_strategy(self, strategy_name: str) -> Any | None:
        """Get a recovery strategy.

        Args:
            strategy_name: Strategy name.

        Returns:
            Strategy or None.
        """
        return self._recovery_strategies.get(strategy_name)

    def recover_workflow(
        self,
        execution: WorkflowExecution,
        strategy_name: str = "default",
    ) -> WorkflowExecution:
        """Recover a workflow execution.

        Args:
            execution: Execution to recover.
            strategy_name: Recovery strategy name.

        Returns:
            Recovered execution.
        """
        strategy = self._recovery_strategies.get(strategy_name)

        if strategy:
            return strategy(execution)

        # Default: mark as failed
        from core.workflows.types import WorkflowStatus
        execution.status = WorkflowStatus.FAILED
        return execution


# Global recovery manager
_recovery_manager: RecoveryManager | None = None
_recovery_lock = __import__("threading").Lock()


def get_recovery_manager() -> RecoveryManager:
    """Get the global recovery manager.

    Returns:
        Global RecoveryManager instance.
    """
    global _recovery_manager
    with _recovery_lock:
        if _recovery_manager is None:
            _recovery_manager = RecoveryManager()
        return _recovery_manager


def reset_recovery_manager() -> None:
    """Reset the global recovery manager."""
    global _recovery_manager
    with _recovery_lock:
        _recovery_manager = None
