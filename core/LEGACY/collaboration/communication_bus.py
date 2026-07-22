"""Communication Bus for EREN Multi-Agent Collaboration Engine.

Handles message routing and communication between agents.
This is the infrastructure layer - it only handles message transport.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from core.LEGACY.collaboration.types import (
    CollaborationMessage,
    MessageStatus,
    MessageType,
)

if TYPE_CHECKING:
    pass


class CommunicationBus:
    """Handles message routing and transport.

    The Communication Bus does NOT:
    - Execute tasks
    - Know about collaboration semantics
    - Handle business logic

    It ONLY:
    - Sends messages
    - Receives messages
    - Routes messages
    - Handles pub/sub
    - Tracks delivery
    """

    def __init__(self):
        """Initialize communication bus."""
        # Inboxes: agent_id -> messages
        self._inboxes: dict[str, list[CollaborationMessage]] = {}
        # Pending acknowledgments
        self._pending_ack: dict[str, CollaborationMessage] = {}
        # Subscribers: pattern -> [callbacks]
        self._subscribers: dict[str, list[Callable]] = {}
        # Message history
        self._history: list[CollaborationMessage] = []

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

        # Add to inboxes
        for receiver_id in message.receiver_ids:
            if receiver_id not in self._inboxes:
                self._inboxes[receiver_id] = []
            self._inboxes[receiver_id].append(message)

        # Track for acknowledgment
        self._pending_ack[message.message_id] = message

        # Add to history
        self._history.append(message)
        if len(self._history) > 1000:
            self._history = self._history[-500:]

        # Trigger pub/sub
        self._trigger_subscribers(message)

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
        pattern: str,
        callback: Callable,
    ) -> None:
        """Subscribe to messages matching a pattern.

        Args:
            pattern: Pattern to match (e.g., "session:*" or "agent:*").
            callback: Callback function.
        """
        if pattern not in self._subscribers:
            self._subscribers[pattern] = []
        self._subscribers[pattern].append(callback)

    def unsubscribe(
        self,
        pattern: str,
        callback: Callable,
    ) -> None:
        """Unsubscribe from pattern.

        Args:
            pattern: Pattern.
            callback: Callback to remove.
        """
        if pattern in self._subscribers:
            self._subscribers[pattern] = [
                cb for cb in self._subscribers[pattern]
                if cb != callback
            ]

    def _trigger_subscribers(self, message: CollaborationMessage) -> None:
        """Trigger subscribers for a message."""
        patterns = [
            f"session:{message.session_id}",
            f"agent:{message.sender_id}",
            f"type:{message.message_type.value}",
            "*",  # Wildcard subscriber
        ]

        for pattern in patterns:
            if pattern in self._subscribers:
                for callback in self._subscribers[pattern]:
                    try:
                        callback(message)
                    except Exception:
                        pass

    def broadcast(
        self,
        sender_id: str,
        receiver_ids: list[str],
        content: Any,
        session_id: str = "",
    ) -> CollaborationMessage:
        """Broadcast to multiple agents.

        Args:
            sender_id: Sender agent ID.
            receiver_ids: List of receiver IDs.
            content: Message content.
            session_id: Optional session ID.

        Returns:
            Broadcast message.
        """
        message = CollaborationMessage.create(
            session_id=session_id,
            sender_id=sender_id,
            message_type=MessageType.BROADCAST,
            content=content,
            receiver_ids=receiver_ids,
        )

        return self.send(message)

    def route(
        self,
        sender_id: str,
        receiver_id: str,
        content: Any,
        session_id: str = "",
        message_type: MessageType = MessageType.REQUEST,
    ) -> CollaborationMessage:
        """Route a message to a specific agent.

        Args:
            sender_id: Sender agent ID.
            receiver_id: Receiver agent ID.
            content: Message content.
            session_id: Optional session ID.
            message_type: Message type.

        Returns:
            Routed message.
        """
        message = CollaborationMessage.create(
            session_id=session_id,
            sender_id=sender_id,
            message_type=message_type,
            content=content,
            receiver_ids=[receiver_id],
        )

        return self.send(message)

    def get_messages(
        self,
        session_id: str,
    ) -> list[CollaborationMessage]:
        """Get all messages for a session.

        Args:
            session_id: Session ID.

        Returns:
            List of messages.
        """
        return [m for m in self._history if m.session_id == session_id]

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
        return [m for m in self._history if m.sender_id == agent_id]

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

    def clear_history(self) -> int:
        """Clear message history.

        Returns:
            Number of messages cleared.
        """
        count = len(self._history)
        self._history.clear()
        return count

    def get_stats(self) -> dict:
        """Get communication statistics.

        Returns:
            Statistics dictionary.
        """
        return {
            "total_inboxes": len(self._inboxes),
            "total_messages": len(self._history),
            "pending_acknowledgments": len(self._pending_ack),
            "subscribers": len(self._subscribers),
        }


# Global communication bus
_global_comm_bus: CommunicationBus | None = None
_bus_lock = __import__("threading").Lock()


def get_communication_bus() -> CommunicationBus:
    """Get the global communication bus.

    Returns:
        Global CommunicationBus instance.
    """
    global _global_comm_bus
    with _bus_lock:
        if _global_comm_bus is None:
            _global_comm_bus = CommunicationBus()
        return _global_comm_bus


def reset_communication_bus() -> None:
    """Reset the global communication bus."""
    global _global_comm_bus
    with _bus_lock:
        _global_comm_bus = None
