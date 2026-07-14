"""Shared context for EREN Multi-Agent Collaboration Engine.

Manages shared context between collaborating agents.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass


class SharedContext:
    """Manages shared context between agents.

    The Shared Context does NOT:
    - Execute tasks
    - Know about implementations

    It ONLY:
    - Stores shared data
    - Tracks access
    - Manages visibility
    """

    def __init__(self):
        """Initialize shared context."""
        # Session contexts: session_id -> context_data
        self._contexts: dict[str, dict[str, Any]] = {}
        # Agent contributions: session_id -> {agent_id -> contributions}
        self._contributions: dict[str, dict[str, dict]] = {}
        # Access tracking
        self._access_log: list[dict] = []

    def create_session_context(
        self,
        session_id: str,
    ) -> None:
        """Create a context for a session.

        Args:
            session_id: Session ID.
        """
        if session_id not in self._contexts:
            self._contexts[session_id] = {}
            self._contributions[session_id] = {}

    def delete_session_context(
        self,
        session_id: str,
    ) -> None:
        """Delete a session context.

        Args:
            session_id: Session ID.
        """
        self._contexts.pop(session_id, None)
        self._contributions.pop(session_id, None)

    def put(
        self,
        session_id: str,
        key: str,
        value: Any,
        agent_id: str = "",
    ) -> None:
        """Put a value in shared context.

        Args:
            session_id: Session ID.
            key: Key.
            value: Value.
            agent_id: Contributing agent ID.
        """
        if session_id not in self._contexts:
            self.create_session_context(session_id)

        self._contexts[session_id][key] = value

        # Track contribution
        if agent_id:
            if agent_id not in self._contributions[session_id]:
                self._contributions[session_id][agent_id] = {}
            self._contributions[session_id][agent_id][key] = {
                "value": value,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

        # Log access
        self._access_log.append({
            "session_id": session_id,
            "key": key,
            "action": "put",
            "agent_id": agent_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    def get(
        self,
        session_id: str,
        key: str,
        agent_id: str = "",
    ) -> Any | None:
        """Get a value from shared context.

        Args:
            session_id: Session ID.
            key: Key.
            agent_id: Accessing agent ID.

        Returns:
            Value or None.
        """
        value = self._contexts.get(session_id, {}).get(key)

        # Log access
        self._access_log.append({
            "session_id": session_id,
            "key": key,
            "action": "get",
            "agent_id": agent_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

        return value

    def get_all(
        self,
        session_id: str,
    ) -> dict[str, Any]:
        """Get all values in a session context.

        Args:
            session_id: Session ID.

        Returns:
            All context values.
        """
        return self._contexts.get(session_id, {}).copy()

    def delete(
        self,
        session_id: str,
        key: str,
    ) -> bool:
        """Delete a key from shared context.

        Args:
            session_id: Session ID.
            key: Key.

        Returns:
            True if deleted.
        """
        if session_id in self._contexts:
            if key in self._contexts[session_id]:
                del self._contexts[session_id][key]
                return True
        return False

    def update(
        self,
        session_id: str,
        updates: dict[str, Any],
        agent_id: str = "",
    ) -> None:
        """Update multiple keys.

        Args:
            session_id: Session ID.
            updates: Key-value pairs.
            agent_id: Contributing agent ID.
        """
        for key, value in updates.items():
            self.put(session_id, key, value, agent_id)

    def merge(
        self,
        session_id: str,
        source_agent_id: str,
        target_agent_id: str,
    ) -> dict[str, Any]:
        """Merge contributions from one agent to another.

        Args:
            session_id: Session ID.
            source_agent_id: Source agent ID.
            target_agent_id: Target agent ID.

        Returns:
            Merged contributions.
        """
        source = self._contributions.get(session_id, {}).get(source_agent_id, {})
        target = self._contributions.get(session_id, {}).get(target_agent_id, {})

        merged = target.copy()
        merged.update(source)

        return merged

    def get_agent_contributions(
        self,
        session_id: str,
        agent_id: str,
    ) -> dict:
        """Get contributions from an agent.

        Args:
            session_id: Session ID.
            agent_id: Agent ID.

        Returns:
            Agent's contributions.
        """
        return self._contributions.get(session_id, {}).get(agent_id, {}).copy()

    def get_contributors(
        self,
        session_id: str,
    ) -> list[str]:
        """Get list of contributing agents.

        Args:
            session_id: Session ID.

        Returns:
            List of agent IDs.
        """
        return list(self._contributions.get(session_id, {}).keys())

    def get_access_log(
        self,
        session_id: str | None = None,
        limit: int = 100,
    ) -> list[dict]:
        """Get access log.

        Args:
            session_id: Optional session filter.
            limit: Maximum entries.

        Returns:
            Access log entries.
        """
        log = self._access_log

        if session_id:
            log = [e for e in log if e["session_id"] == session_id]

        return log[-limit:]

    def clear(self, session_id: str) -> None:
        """Clear a session context.

        Args:
            session_id: Session ID.
        """
        self._contexts.pop(session_id, None)
        self._contributions.pop(session_id, None)


# Global shared context
_global_shared_context: SharedContext | None = None
_context_lock = __import__("threading").Lock()


def get_shared_context() -> SharedContext:
    """Get the global shared context.

    Returns:
        Global SharedContext instance.
    """
    global _global_shared_context
    with _context_lock:
        if _global_shared_context is None:
            _global_shared_context = SharedContext()
        return _global_shared_context


def reset_shared_context() -> None:
    """Reset the global shared context."""
    global _global_shared_context
    with _context_lock:
        _global_shared_context = None
