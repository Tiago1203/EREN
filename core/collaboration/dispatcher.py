"""Task dispatcher for EREN Multi-Agent Collaboration Engine.

Dispatches tasks to agents in collaboration.
"""

from __future__ import annotations

from datetime import UTC
from typing import TYPE_CHECKING, Any

from core.collaboration.types import TaskAssignment

if TYPE_CHECKING:
    pass


class TaskDispatcher:
    """Dispatches tasks to agents.

    The Task Dispatcher does NOT:
    - Execute tasks
    - Know about implementations

    It ONLY:
    - Assigns tasks
    - Tracks assignments
    - Manages dependencies
    """

    def __init__(self):
        """Initialize task dispatcher."""
        self._assignments: dict[str, TaskAssignment] = {}
        self._agent_assignments: dict[str, list[str]] = {}  # agent_id -> assignment_ids
        self._session_assignments: dict[str, list[str]] = {}  # session_id -> assignment_ids

    def create_assignment(
        self,
        session_id: str,
        task_id: str,
        agent_id: str,
        description: str,
        priority: int = 5,
        depends_on: list[str] | None = None,
    ) -> TaskAssignment:
        """Create a task assignment.

        Args:
            session_id: Session ID.
            task_id: Task ID.
            agent_id: Agent ID.
            description: Task description.
            priority: Task priority (1-10).
            depends_on: Dependent task IDs.

        Returns:
            Created assignment.
        """
        assignment = TaskAssignment.create(
            session_id=session_id,
            task_id=task_id,
            agent_id=agent_id,
            description=description,
            priority=priority,
            depends_on=depends_on or [],
        )

        self._assignments[assignment.assignment_id] = assignment

        # Track by agent
        if agent_id not in self._agent_assignments:
            self._agent_assignments[agent_id] = []
        self._agent_assignments[agent_id].append(assignment.assignment_id)

        # Track by session
        if session_id not in self._session_assignments:
            self._session_assignments[session_id] = []
        self._session_assignments[session_id].append(assignment.assignment_id)

        return assignment

    def get_assignment(
        self,
        assignment_id: str,
    ) -> TaskAssignment | None:
        """Get an assignment.

        Args:
            assignment_id: Assignment ID.

        Returns:
            Assignment or None.
        """
        return self._assignments.get(assignment_id)

    def get_agent_assignments(
        self,
        agent_id: str,
        status: str | None = None,
    ) -> list[TaskAssignment]:
        """Get assignments for an agent.

        Args:
            agent_id: Agent ID.
            status: Optional status filter.

        Returns:
            List of assignments.
        """
        assignment_ids = self._agent_assignments.get(agent_id, [])
        assignments = [self._assignments[a_id] for a_id in assignment_ids if a_id in self._assignments]

        if status:
            assignments = [a for a in assignments if a.status == status]

        return assignments

    def get_session_assignments(
        self,
        session_id: str,
        status: str | None = None,
    ) -> list[TaskAssignment]:
        """Get all assignments for a session.

        Args:
            session_id: Session ID.
            status: Optional status filter.

        Returns:
            List of assignments.
        """
        assignment_ids = self._session_assignments.get(session_id, [])
        assignments = [self._assignments[a_id] for a_id in assignment_ids if a_id in self._assignments]

        if status:
            assignments = [a for a in assignments if a.status == status]

        return assignments

    def accept(
        self,
        assignment_id: str,
    ) -> bool:
        """Accept an assignment.

        Args:
            assignment_id: Assignment ID.

        Returns:
            True if accepted.
        """
        assignment = self._assignments.get(assignment_id)
        if not assignment or assignment.status != "pending":
            return False

        assignment.status = "accepted"
        from datetime import datetime
        assignment.accepted_at = datetime.now(UTC)
        return True

    def decline(
        self,
        assignment_id: str,
    ) -> bool:
        """Decline an assignment.

        Args:
            assignment_id: Assignment ID.

        Returns:
            True if declined.
        """
        assignment = self._assignments.get(assignment_id)
        if not assignment or assignment.status != "pending":
            return False

        assignment.status = "declined"
        return True

    def complete(
        self,
        assignment_id: str,
        result: Any,
    ) -> bool:
        """Complete an assignment.

        Args:
            assignment_id: Assignment ID.
            result: Task result.

        Returns:
            True if completed.
        """
        assignment = self._assignments.get(assignment_id)
        if not assignment or assignment.status not in ["pending", "accepted"]:
            return False

        assignment.status = "completed"
        assignment.result = result
        from datetime import datetime
        assignment.completed_at = datetime.now(UTC)
        return True

    def fail(
        self,
        assignment_id: str,
        error: str,
    ) -> bool:
        """Mark assignment as failed.

        Args:
            assignment_id: Assignment ID.
            error: Error message.

        Returns:
            True if marked as failed.
        """
        assignment = self._assignments.get(assignment_id)
        if not assignment or assignment.status not in ["pending", "accepted"]:
            return False

        assignment.status = "failed"
        assignment.error = error
        from datetime import datetime
        assignment.completed_at = datetime.now(UTC)
        return True

    def cancel(
        self,
        assignment_id: str,
    ) -> bool:
        """Cancel an assignment.

        Args:
            assignment_id: Assignment ID.

        Returns:
            True if cancelled.
        """
        assignment = self._assignments.get(assignment_id)
        if not assignment:
            return False

        assignment.status = "cancelled"
        from datetime import datetime
        assignment.completed_at = datetime.now(UTC)
        return True

    def reassign(
        self,
        assignment_id: str,
        new_agent_id: str,
    ) -> bool:
        """Reassign a task to another agent.

        Args:
            assignment_id: Assignment ID.
            new_agent_id: New agent ID.

        Returns:
            True if reassigned.
        """
        assignment = self._assignments.get(assignment_id)
        if not assignment:
            return False

        # Remove from old agent
        old_agent = assignment.agent_id
        if old_agent in self._agent_assignments:
            self._agent_assignments[old_agent] = [
                a_id for a_id in self._agent_assignments[old_agent]
                if a_id != assignment_id
            ]

        # Add to new agent
        if new_agent_id not in self._agent_assignments:
            self._agent_assignments[new_agent_id] = []
        self._agent_assignments[new_agent_id].append(assignment_id)

        assignment.agent_id = new_agent_id
        assignment.status = "pending"
        assignment.accepted_at = None
        assignment.completed_at = None
        assignment.result = None
        assignment.error = ""

        return True

    def get_ready_tasks(
        self,
        session_id: str,
    ) -> list[TaskAssignment]:
        """Get tasks ready for execution (dependencies met).

        Args:
            session_id: Session ID.

        Returns:
            List of ready tasks.
        """
        assignments = self.get_session_assignments(session_id, status="pending")
        ready = []

        for assignment in assignments:
            # Check dependencies
            deps_met = True
            for dep_id in assignment.depends_on:
                dep = self._assignments.get(dep_id)
                if not dep or dep.status != "completed":
                    deps_met = False
                    break

            if deps_met:
                ready.append(assignment)

        return ready

    def get_stats(
        self,
        session_id: str,
    ) -> dict:
        """Get session statistics.

        Args:
            session_id: Session ID.

        Returns:
            Statistics dictionary.
        """
        assignments = self.get_session_assignments(session_id)

        counts = {
            "total": len(assignments),
            "pending": 0,
            "accepted": 0,
            "completed": 0,
            "failed": 0,
            "cancelled": 0,
            "declined": 0,
        }

        for a in assignments:
            if a.status in counts:
                counts[a.status] += 1

        return counts

    def clear_session(
        self,
        session_id: str,
    ) -> int:
        """Clear all assignments for a session.

        Args:
            session_id: Session ID.

        Returns:
            Number of assignments cleared.
        """
        assignment_ids = self._session_assignments.pop(session_id, [])

        for a_id in assignment_ids:
            assignment = self._assignments.pop(a_id, None)
            if assignment:
                # Remove from agent tracking
                if assignment.agent_id in self._agent_assignments:
                    self._agent_assignments[assignment.agent_id] = [
                        a_id for a_id in self._agent_assignments[assignment.agent_id]
                        if a_id != a_id
                    ]

        return len(assignment_ids)


# Global task dispatcher
_global_task_dispatcher: TaskDispatcher | None = None
_dispatcher_lock = __import__("threading").Lock()


def get_task_dispatcher() -> TaskDispatcher:
    """Get the global task dispatcher.

    Returns:
        Global TaskDispatcher instance.
    """
    global _global_task_dispatcher
    with _dispatcher_lock:
        if _global_task_dispatcher is None:
            _global_task_dispatcher = TaskDispatcher()
        return _global_task_dispatcher


def reset_task_dispatcher() -> None:
    """Reset the global task dispatcher."""
    global _global_task_dispatcher
    with _dispatcher_lock:
        _global_task_dispatcher = None
