"""Session store for the Cognitive Session Manager.

Provides session storage and retrieval.

Architecture only -- no implementations, no business logic.
"""

from __future__ import annotations

import threading
from typing import TYPE_CHECKING

from .session import CognitiveSession
from .session_state import SessionState

if TYPE_CHECKING:
    pass


class SessionStore:
    """In-memory session store.

    This is the default implementation. In production, this should be
    replaced with a persistent store (Redis, PostgreSQL, etc.).
    """

    def __init__(self) -> None:
        """Initialize the session store."""
        self._sessions: dict[str, CognitiveSession] = {}
        self._by_user: dict[str, list[str]] = {}
        self._by_hospital: dict[str, list[str]] = {}
        self._by_tenant: dict[str, list[str]] = {}
        self._by_state: dict[SessionState, list[str]] = {}
        self._lock = threading.RLock()

    def save(self, session: CognitiveSession) -> None:
        """Save a session.

        Args:
            session: Session to save.
        """
        with self._lock:
            session_id = session.metadata.session_id

            # Save to main store
            self._sessions[session_id] = session

            # Index by user
            if session.user_id:
                self._by_user.setdefault(session.user_id, []).append(session_id)

            # Index by hospital
            if session.hospital_id:
                self._by_hospital.setdefault(session.hospital_id, []).append(session_id)

            # Index by tenant
            if session.tenant_id:
                self._by_tenant.setdefault(session.tenant_id, []).append(session_id)

            # Index by state
            self._by_state.setdefault(session.state, []).append(session_id)

    def get(self, session_id: str) -> CognitiveSession | None:
        """Get a session by ID.

        Args:
            session_id: Session ID.

        Returns:
            Session or None.
        """
        with self._lock:
            return self._sessions.get(session_id)

    def delete(self, session_id: str) -> bool:
        """Delete a session.

        Args:
            session_id: Session ID.

        Returns:
            True if deleted.
        """
        with self._lock:
            session = self._sessions.get(session_id)
            if not session:
                return False

            # Remove from all indexes
            self._sessions.pop(session_id, None)

            if session.user_id and session_id in self._by_user.get(session.user_id, []):
                self._by_user[session.user_id].remove(session_id)

            if session.hospital_id and session_id in self._by_hospital.get(session.hospital_id, []):
                self._by_hospital[session.hospital_id].remove(session_id)

            if session.tenant_id and session_id in self._by_tenant.get(session.tenant_id, []):
                self._by_tenant[session.tenant_id].remove(session_id)

            if session_id in self._by_state.get(session.state, []):
                self._by_state[session.state].remove(session_id)

            return True

    def find_by_user(self, user_id: str) -> list[CognitiveSession]:
        """Find sessions by user.

        Args:
            user_id: User ID.

        Returns:
            List of sessions.
        """
        with self._lock:
            session_ids = self._by_user.get(user_id, [])
            return [self._sessions[sid] for sid in session_ids if sid in self._sessions]

    def find_by_hospital(self, hospital_id: str) -> list[CognitiveSession]:
        """Find sessions by hospital.

        Args:
            hospital_id: Hospital ID.

        Returns:
            List of sessions.
        """
        with self._lock:
            session_ids = self._by_hospital.get(hospital_id, [])
            return [self._sessions[sid] for sid in session_ids if sid in self._sessions]

    def find_by_tenant(self, tenant_id: str) -> list[CognitiveSession]:
        """Find sessions by tenant.

        Args:
            tenant_id: Tenant ID.

        Returns:
            List of sessions.
        """
        with self._lock:
            session_ids = self._by_tenant.get(tenant_id, [])
            return [self._sessions[sid] for sid in session_ids if sid in self._sessions]

    def find_by_state(self, state: SessionState) -> list[CognitiveSession]:
        """Find sessions by state.

        Args:
            state: Session state.

        Returns:
            List of sessions.
        """
        with self._lock:
            session_ids = self._by_state.get(state, [])
            return [self._sessions[sid] for sid in session_ids if sid in self._sessions]

    def find_active(self) -> list[CognitiveSession]:
        """Find all active sessions.

        Returns:
            List of active sessions.
        """
        return self.find_by_state(SessionState.ACTIVE)

    def find_by_correlation(self, correlation_id: str) -> CognitiveSession | None:
        """Find session by correlation ID.

        Args:
            correlation_id: Correlation ID.

        Returns:
            Session or None.
        """
        with self._lock:
            for session in self._sessions.values():
                if session.metadata.correlation_id == correlation_id:
                    return session
            return None

    def count(self) -> int:
        """Count total sessions.

        Returns:
            Total session count.
        """
        with self._lock:
            return len(self._sessions)

    def count_by_state(self, state: SessionState) -> int:
        """Count sessions by state.

        Args:
            state: Session state.

        Returns:
            Session count.
        """
        with self._lock:
            return len(self._by_state.get(state, []))

    def clear(self) -> None:
        """Clear all sessions."""
        with self._lock:
            self._sessions.clear()
            self._by_user.clear()
            self._by_hospital.clear()
            self._by_tenant.clear()
            self._by_state.clear()

    def cleanup_expired(self, timeout_ms: int) -> list[str]:
        """Clean up expired sessions.

        Args:
            timeout_ms: Timeout in milliseconds.

        Returns:
            List of deleted session IDs.
        """
        with self._lock:
            expired_ids = []

            for session_id, session in list(self._sessions.items()):
                if session.state in (SessionState.COMPLETED, SessionState.ARCHIVED):
                    continue

                if session.is_expired(timeout_ms):
                    expired_ids.append(session_id)
                    self.delete(session_id)

            return expired_ids
