"""Agent context management for EREN Cognitive Agent Runtime.

Manages shared context between agents.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from core.PHASE_2.agents.types import AgentContext, AgentMessage

if TYPE_CHECKING:
    pass


class ContextManager:
    """Manages shared context between agents.

    The Context Manager does NOT:
    - Execute tasks
    - Know about implementations

    It ONLY:
    - Stores and retrieves context
    - Manages shared data
    - Handles agent messages
    """

    def __init__(self):
        """Initialize context manager."""
        self._contexts: dict[str, AgentContext] = {}
        self._messages: dict[str, list[AgentMessage]] = {}  # session_id -> messages

    def create_context(
        self,
        session_id: str | None = None,
        correlation_id: str = "",
    ) -> AgentContext:
        """Create a new context.

        Args:
            session_id: Session ID.
            correlation_id: Correlation ID.

        Returns:
            New context.
        """
        session_id = session_id or str(uuid.uuid4())
        context = AgentContext(
            session_id=session_id,
            correlation_id=correlation_id,
        )
        self._contexts[session_id] = context
        return context

    def get_context(self, session_id: str) -> AgentContext | None:
        """Get context by session ID.

        Args:
            session_id: Session ID.

        Returns:
            Context or None.
        """
        return self._contexts.get(session_id)

    def delete_context(self, session_id: str) -> None:
        """Delete a context.

        Args:
            session_id: Session ID.
        """
        self._contexts.pop(session_id, None)
        self._messages.pop(session_id, None)

    def store_result(
        self,
        session_id: str,
        task_id: str,
        result: Any,
    ) -> None:
        """Store task result in context.

        Args:
            session_id: Session ID.
            task_id: Task ID.
            result: Task result.
        """
        context = self._contexts.get(session_id)
        if context:
            context.put_result(task_id, result)

    def retrieve_result(
        self,
        session_id: str,
        task_id: str,
    ) -> Any | None:
        """Retrieve task result from context.

        Args:
            session_id: Session ID.
            task_id: Task ID.

        Returns:
            Result or None.
        """
        context = self._contexts.get(session_id)
        if context:
            return context.get_result(task_id)
        return None

    def store_shared(
        self,
        session_id: str,
        key: str,
        value: Any,
    ) -> None:
        """Store shared data in context.

        Args:
            session_id: Session ID.
            key: Data key.
            value: Data value.
        """
        context = self._contexts.get(session_id)
        if context:
            context.put_shared(key, value)

    def retrieve_shared(
        self,
        session_id: str,
        key: str,
    ) -> Any | None:
        """Retrieve shared data from context.

        Args:
            session_id: Session ID.
            key: Data key.

        Returns:
            Data or None.
        """
        context = self._contexts.get(session_id)
        if context:
            return context.get_shared(key)
        return None

    def update_agent_state(
        self,
        session_id: str,
        agent_id: str,
        state: dict,
    ) -> None:
        """Update agent state in context.

        Args:
            session_id: Session ID.
            agent_id: Agent ID.
            state: Agent state.
        """
        context = self._contexts.get(session_id)
        if context:
            context.agent_states[agent_id] = state
            context.updated_at = datetime.now(UTC)

    def get_agent_state(
        self,
        session_id: str,
        agent_id: str,
    ) -> dict | None:
        """Get agent state from context.

        Args:
            session_id: Session ID.
            agent_id: Agent ID.

        Returns:
            Agent state or None.
        """
        context = self._contexts.get(session_id)
        if context:
            return context.agent_states.get(agent_id)
        return None

    def send_message(
        self,
        session_id: str,
        sender_id: str,
        receiver_id: str,
        content: Any,
        message_type: str = "request",
        correlation_id: str = "",
    ) -> AgentMessage:
        """Send a message between agents.

        Args:
            session_id: Session ID.
            sender_id: Sender agent ID.
            receiver_id: Receiver agent ID.
            content: Message content.
            message_type: Message type.
            correlation_id: Correlation ID.

        Returns:
            Sent message.
        """
        message = AgentMessage(
            message_id=str(uuid.uuid4()),
            sender_id=sender_id,
            receiver_id=receiver_id,
            content=content,
            type=message_type,
            correlation_id=correlation_id,
        )

        if session_id not in self._messages:
            self._messages[session_id] = []
        self._messages[session_id].append(message)

        return message

    def get_messages(
        self,
        session_id: str,
        agent_id: str | None = None,
    ) -> list[AgentMessage]:
        """Get messages for a session or agent.

        Args:
            session_id: Session ID.
            agent_id: Optional agent ID to filter.

        Returns:
            List of messages.
        """
        messages = self._messages.get(session_id, [])

        if agent_id:
            messages = [
                m for m in messages
                if m.sender_id == agent_id or m.receiver_id == agent_id
            ]

        return messages

    def clear_messages(
        self,
        session_id: str,
        before_id: str | None = None,
    ) -> None:
        """Clear messages from session.

        Args:
            session_id: Session ID.
            before_id: Optional message ID to clear before.
        """
        if session_id in self._messages:
            if before_id:
                messages = self._messages[session_id]
                idx = next(
                    (i for i, m in enumerate(messages) if m.message_id == before_id),
                    0,
                )
                self._messages[session_id] = messages[idx + 1:]
            else:
                self._messages[session_id] = []

    def get_all_contexts(self) -> list[AgentContext]:
        """Get all active contexts.

        Returns:
            List of contexts.
        """
        return list(self._contexts.values())


# Global context manager
_global_context_manager: ContextManager | None = None
_context_lock = __import__("threading").Lock()


def get_context_manager() -> ContextManager:
    """Get the global context manager.

    Returns:
        Global ContextManager instance.
    """
    global _global_context_manager
    with _context_lock:
        if _global_context_manager is None:
            _global_context_manager = ContextManager()
        return _global_context_manager


def reset_context_manager() -> None:
    """Reset the global context manager."""
    global _global_context_manager
    with _context_lock:
        _global_context_manager = None
