"""Agent messaging for EREN Multi-Agent Collaboration Engine.

Handles message routing between agents.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from core.collaboration.types import (
    CollaborationMessage,
    MessageStatus,
)

if TYPE_CHECKING:
    pass


class AgentMessaging:
    """Handles messaging between agents.

    The Messaging system does NOT:
    - Execute tasks
    - Know about implementations

    It ONLY:
    - Routes messages
    - Manages queues
    - Tracks delivery
    """

    def __init__(self):
        """Initialize messaging system."""
        # Inboxes: agent_id -> messages
        self._inboxes: dict[str, list[CollaborationMessage]] = {}
        # Outboxes: session_id -> messages
        self._outboxes: dict[str, list[CollaborationMessage]] = {}
        # Pending acknowledgments
        self._pending_ack: dict[str, CollaborationMessage] = {}
        # Callbacks
        self._callbacks: dict[str, list] = {}

    def send(
        self,
        message: CollaborationMessage,
    ) -> CollaborationMessage:
        """Send a message.

        Args:
            message: Message to send.

        Returns:
            Sent message.
        """
        message.status = MessageStatus.SENT

        # Add to outbox
        if message.session_id not in self._outboxes:
            self._outboxes[message.session_id] = []
        self._outboxes[message.session_id].append(message)

        # Add to inboxes
        for receiver_id in message.receiver_ids:
            if receiver_id not in self._inboxes:
                self._inboxes[receiver_id] = []
            self._inboxes[receiver_id].append(message)

        # Track for acknowledgment
        self._pending_ack[message.message_id] = message

        return message

    def receive(
        self,
        agent_id: str,
        blocking: bool = False,
        timeout: float = 0.0,
    ) -> CollaborationMessage | None:
        """Receive a message for an agent.

        Args:
            agent_id: Agent ID.
            blocking: Whether to block waiting for message.
            timeout: Timeout in seconds.

        Returns:
            Message or None.
        """
        if agent_id not in self._inboxes:
            return None

        if self._inboxes[agent_id]:
            message = self._inboxes[agent_id].pop(0)
            message.status = MessageStatus.DELIVERED
            return message

        return None

    def receive_all(self, agent_id: str) -> list[CollaborationMessage]:
        """Receive all messages for an agent.

        Args:
            agent_id: Agent ID.

        Returns:
            List of messages.
        """
        messages = self._inboxes.pop(agent_id, [])
        for msg in messages:
            msg.status = MessageStatus.DELIVERED
        return messages

    def peek(self, agent_id: str) -> list[CollaborationMessage]:
        """Peek at messages without removing.

        Args:
            agent_id: Agent ID.

        Returns:
            List of messages.
        """
        return self._inboxes.get(agent_id, [])

    def acknowledge(
        self,
        message_id: str,
    ) -> bool:
        """Acknowledge a message.

        Args:
            message_id: Message ID.

        Returns:
            True if acknowledged.
        """
        if message_id in self._pending_ack:
            message = self._pending_ack.pop(message_id)
            message.status = MessageStatus.ACKNOWLEDGED
            return True
        return False

    def subscribe(
        self,
        agent_id: str,
        callback,
    ) -> None:
        """Subscribe to messages.

        Args:
            agent_id: Agent ID.
            callback: Callback function.
        """
        if agent_id not in self._callbacks:
            self._callbacks[agent_id] = []
        self._callbacks[agent_id].append(callback)

    def unsubscribe(
        self,
        agent_id: str,
        callback,
    ) -> None:
        """Unsubscribe from messages.

        Args:
            agent_id: Agent ID.
            callback: Callback to remove.
        """
        if agent_id in self._callbacks:
            self._callbacks[agent_id] = [
                cb for cb in self._callbacks[agent_id]
                if cb != callback
            ]

    def get_messages(
        self,
        session_id: str,
    ) -> list[CollaborationMessage]:
        """Get all messages in a session.

        Args:
            session_id: Session ID.

        Returns:
            List of messages.
        """
        return self._outboxes.get(session_id, [])

    def get_sent_messages(
        self,
        agent_id: str,
    ) -> list[CollaborationMessage]:
        """Get messages sent by an agent.

        Args:
            agent_id: Agent ID.

        Returns:
            List of sent messages.
        """
        sent = []
        for messages in self._outboxes.values():
            sent.extend([m for m in messages if m.sender_id == agent_id])
        return sent

    def clear_inbox(self, agent_id: str) -> int:
        """Clear an agent's inbox.

        Args:
            agent_id: Agent ID.

        Returns:
            Number of messages cleared.
        """
        count = len(self._inboxes.get(agent_id, []))
        self._inboxes.pop(agent_id, None)
        return count

    def clear_session(self, session_id: str) -> int:
        """Clear all messages in a session.

        Args:
            session_id: Session ID.

        Returns:
            Number of messages cleared.
        """
        messages = self._outboxes.pop(session_id, [])

        # Also remove from inboxes
        for message in messages:
            for inbox in self._inboxes.values():
                inbox[:] = [m for m in inbox if m.message_id != message.message_id]

        return len(messages)

    def get_stats(self) -> dict:
        """Get messaging statistics.

        Returns:
            Statistics dictionary.
        """
        total_inbox = sum(len(inbox) for inbox in self._inboxes.values())
        total_outbox = sum(len(msgs) for msgs in self._outboxes.values())

        return {
            "total_inboxes": len(self._inboxes),
            "total_outboxes": len(self._outboxes),
            "total_inbox_messages": total_inbox,
            "total_outbox_messages": total_outbox,
            "pending_acknowledgments": len(self._pending_ack),
        }


# Global messaging instance
_global_messaging: AgentMessaging | None = None
_messaging_lock = __import__("threading").Lock()


def get_messaging() -> AgentMessaging:
    """Get the global messaging instance.

    Returns:
        Global AgentMessaging instance.
    """
    global _global_messaging
    with _messaging_lock:
        if _global_messaging is None:
            _global_messaging = AgentMessaging()
        return _global_messaging


def reset_messaging() -> None:
    """Reset the global messaging instance."""
    global _global_messaging
    with _messaging_lock:
        _global_messaging = None
