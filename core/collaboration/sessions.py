"""Collaboration Sessions for EREN Multi-Agent Collaboration Engine.

Manages collaboration sessions between agents.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from core.collaboration.types import (
    CollaborationSession,
    CollaborationStatus,
    TaskAssignment,
)

if TYPE_CHECKING:
    pass


class SessionManager:
    """Manages collaboration sessions.

    The Session Manager does NOT:
    - Execute tasks
    - Handle message transport

    It ONLY:
    - Creates sessions
    - Tracks session state
    - Manages participants
    - Stores results
    """

    def __init__(self):
        """Initialize session manager."""
        self._sessions: dict[str, CollaborationSession] = {}
        self._agent_sessions: dict[str, list[str]] = {}  # agent_id -> session_ids

    def create_session(
        self,
        initiator_id: str,
        goal: str,
        description: str,
        participant_ids: list[str] | None = None,
        timeout_seconds: float = 300.0,
        consensus_required: bool = True,
    ) -> CollaborationSession:
        """Create a new collaboration session.

        Args:
            initiator_id: Initiating agent ID.
            goal: Collaboration goal.
            description: Session description.
            participant_ids: Initial participant IDs.
            timeout_seconds: Session timeout.
            consensus_required: Whether consensus is required.

        Returns:
            Created session.
        """
        session_id = str(uuid.uuid4())

        session = CollaborationSession(
            session_id=session_id,
            goal=goal,
            description=description,
            initiator_id=initiator_id,
            participant_ids=participant_ids or [],
            status=CollaborationStatus.CREATED,
            timeout_seconds=timeout_seconds,
            consensus_required=consensus_required,
        )

        self._sessions[session_id] = session

        # Track initiator
        if initiator_id not in self._agent_sessions:
            self._agent_sessions[initiator_id] = []
        self._agent_sessions[initiator_id].append(session_id)

        return session

    def get_session(self, session_id: str) -> CollaborationSession | None:
        """Get a session.

        Args:
            session_id: Session ID.

        Returns:
            Session or None.
        """
        return self._sessions.get(session_id)

    def get_all_sessions(self) -> list[CollaborationSession]:
        """Get all sessions.

        Returns:
            List of sessions.
        """
        return list(self._sessions.values())

    def get_active_sessions(self) -> list[CollaborationSession]:
        """Get all active sessions.

        Returns:
            List of active sessions.
        """
        return [
            s for s in self._sessions.values()
            if s.status == CollaborationStatus.ACTIVE
        ]

    def get_agent_sessions(self, agent_id: str) -> list[CollaborationSession]:
        """Get all sessions for an agent.

        Args:
            agent_id: Agent ID.

        Returns:
            List of sessions.
        """
        session_ids = self._agent_sessions.get(agent_id, [])
        return [
            self._sessions[sid]
            for sid in session_ids
            if sid in self._sessions
        ]

    def start_session(self, session_id: str) -> bool:
        """Start a session.

        Args:
            session_id: Session ID.

        Returns:
            True if started.
        """
        session = self._sessions.get(session_id)
        if not session:
            return False

        session.status = CollaborationStatus.ACTIVE
        session.started_at = datetime.now(timezone.utc)
        return True

    def complete_session(
        self,
        session_id: str,
        final_result: Any = None,
    ) -> bool:
        """Complete a session.

        Args:
            session_id: Session ID.
            final_result: Final aggregated result.

        Returns:
            True if completed.
        """
        session = self._sessions.get(session_id)
        if not session:
            return False

        session.status = CollaborationStatus.COMPLETED
        session.completed_at = datetime.now(timezone.utc)
        session.final_result = final_result
        return True

    def cancel_session(
        self,
        session_id: str,
        reason: str = "",
    ) -> bool:
        """Cancel a session.

        Args:
            session_id: Session ID.
            reason: Cancellation reason.

        Returns:
            True if cancelled.
        """
        session = self._sessions.get(session_id)
        if not session:
            return False

        session.status = CollaborationStatus.CANCELLED
        session.completed_at = datetime.now(timezone.utc)
        session.metadata["cancellation_reason"] = reason
        return True

    def fail_session(
        self,
        session_id: str,
        reason: str = "",
    ) -> bool:
        """Mark session as failed.

        Args:
            session_id: Session ID.
            reason: Failure reason.

        Returns:
            True if marked as failed.
        """
        session = self._sessions.get(session_id)
        if not session:
            return False

        session.status = CollaborationStatus.FAILED
        session.completed_at = datetime.now(timezone.utc)
        session.metadata["failure_reason"] = reason
        return True

    def join_session(
        self,
        session_id: str,
        agent_id: str,
    ) -> bool:
        """Join a session.

        Args:
            session_id: Session ID.
            agent_id: Agent ID.

        Returns:
            True if joined.
        """
        session = self._sessions.get(session_id)
        if not session:
            return False

        session.add_participant(agent_id)

        if agent_id not in self._agent_sessions:
            self._agent_sessions[agent_id] = []
        if session_id not in self._agent_sessions[agent_id]:
            self._agent_sessions[agent_id].append(session_id)

        return True

    def leave_session(
        self,
        session_id: str,
        agent_id: str,
    ) -> bool:
        """Leave a session.

        Args:
            session_id: Session ID.
            agent_id: Agent ID.

        Returns:
            True if left.
        """
        session = self._sessions.get(session_id)
        if not session:
            return False

        session.remove_participant(agent_id)

        if agent_id in self._agent_sessions:
            self._agent_sessions[agent_id] = [
                sid for sid in self._agent_sessions[agent_id]
                if sid != session_id
            ]

        return True

    def add_result(
        self,
        session_id: str,
        agent_id: str,
        result: Any,
    ) -> bool:
        """Add a result to a session.

        Args:
            session_id: Session ID.
            agent_id: Agent ID.
            result: Result value.

        Returns:
            True if added.
        """
        session = self._sessions.get(session_id)
        if not session:
            return False

        session.add_result(agent_id, result)
        return True

    def add_decision(
        self,
        session_id: str,
        decision: dict,
    ) -> bool:
        """Add a decision to a session.

        Args:
            session_id: Session ID.
            decision: Decision dict.

        Returns:
            True if added.
        """
        session = self._sessions.get(session_id)
        if not session:
            return False

        session.decisions.append(decision)
        return True

    def get_stats(self) -> dict:
        """Get session statistics.

        Returns:
            Statistics dictionary.
        """
        counts = {
            "total": len(self._sessions),
            "active": 0,
            "completed": 0,
            "failed": 0,
            "cancelled": 0,
        }

        for session in self._sessions.values():
            if session.status == CollaborationStatus.ACTIVE:
                counts["active"] += 1
            elif session.status == CollaborationStatus.COMPLETED:
                counts["completed"] += 1
            elif session.status == CollaborationStatus.FAILED:
                counts["failed"] += 1
            elif session.status == CollaborationStatus.CANCELLED:
                counts["cancelled"] += 1

        return counts

    def clear_completed(
        self,
        before_hours: int = 24,
    ) -> int:
        """Clear completed sessions.

        Args:
            before_hours: Clear sessions completed before this many hours ago.

        Returns:
            Number of sessions cleared.
        """
        cutoff = datetime.now(timezone.utc).timestamp() - (before_hours * 3600)
        cleared = 0

        to_remove = []
        for session_id, session in self._sessions.items():
            if session.completed_at and session.completed_at.timestamp() < cutoff:
                to_remove.append(session_id)
                cleared += 1

        for session_id in to_remove:
            self._sessions.pop(session_id, None)

        return cleared


# Global session manager
_global_session_manager: SessionManager | None = None
_session_lock = __import__("threading").Lock()


def get_session_manager() -> SessionManager:
    """Get the global session manager.

    Returns:
        Global SessionManager instance.
    """
    global _global_session_manager
    with _session_lock:
        if _global_session_manager is None:
            _global_session_manager = SessionManager()
        return _global_session_manager


def reset_session_manager() -> None:
    """Reset the global session manager."""
    global _global_session_manager
    with _session_lock:
        _global_session_manager = None
