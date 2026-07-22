"""Agent communicator for EREN Cognitive Agent Runtime.

Handles inter-agent communication.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any

from core.PHASE_2.agents.types import AgentMessage

if TYPE_CHECKING:
    pass


class AgentCommunicator:
    """Handles communication between agents.

    The Communicator does NOT:
    - Execute tasks
    - Know about implementations

    It ONLY:
    - Routes messages
    - Manages message queues
    - Handles timeouts
    """

    def __init__(self):
        """Initialize communicator."""
        self._pending: dict[str, list[AgentMessage]] = {}  # receiver_id -> messages
        self._replies: dict[str, AgentMessage] = {}  # correlation_id -> reply
        self._callbacks: dict[str, list] = {}  # receiver_id -> callbacks

    def send(
        self,
        sender_id: str,
        receiver_id: str,
        content: Any,
        message_type: str = "request",
        correlation_id: str = "",
    ) -> AgentMessage:
        """Send a message to an agent.

        Args:
            sender_id: Sender agent ID.
            receiver_id: Receiver agent ID.
            content: Message content.
            message_type: Message type.
            correlation_id: Correlation ID for replies.

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

        # Queue message
        if receiver_id not in self._pending:
            self._pending[receiver_id] = []
        self._pending[receiver_id].append(message)

        # Trigger callbacks
        self._trigger_callbacks(receiver_id, message)

        return message

    def send_reply(
        self,
        original_message: AgentMessage,
        content: Any,
    ) -> AgentMessage:
        """Send a reply to a message.

        Args:
            original_message: Original message to reply to.
            content: Reply content.

        Returns:
            Reply message.
        """
        reply = AgentMessage(
            message_id=str(uuid.uuid4()),
            sender_id=original_message.receiver_id,
            receiver_id=original_message.sender_id,
            content=content,
            type="response",
            correlation_id=original_message.message_id,
            reply_to=original_message.message_id,
        )

        # Store reply for correlation
        self._replies[original_message.message_id] = reply

        # Queue to receiver
        if original_message.sender_id not in self._pending:
            self._pending[original_message.sender_id] = []
        self._pending[original_message.sender_id].append(reply)

        return reply

    def receive(self, receiver_id: str) -> AgentMessage | None:
        """Receive a message for an agent.

        Args:
            receiver_id: Receiver agent ID.

        Returns:
            Message or None.
        """
        if self._pending.get(receiver_id):
            return self._pending[receiver_id].pop(0)
        return None

    def receive_all(self, receiver_id: str) -> list[AgentMessage]:
        """Receive all messages for an agent.

        Args:
            receiver_id: Receiver agent ID.

        Returns:
            List of messages.
        """
        messages = self._pending.pop(receiver_id, [])
        return messages

    def peek(self, receiver_id: str) -> list[AgentMessage]:
        """Peek at messages without removing.

        Args:
            receiver_id: Receiver agent ID.

        Returns:
            List of messages.
        """
        return self._pending.get(receiver_id, [])

    def get_reply(
        self,
        correlation_id: str,
    ) -> AgentMessage | None:
        """Get reply by correlation ID.

        Args:
            correlation_id: Original message ID.

        Returns:
            Reply or None.
        """
        return self._replies.get(correlation_id)

    def subscribe(
        self,
        agent_id: str,
        callback,
    ) -> None:
        """Subscribe to messages for an agent.

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

    def _trigger_callbacks(
        self,
        receiver_id: str,
        message: AgentMessage,
    ) -> None:
        """Trigger callbacks for a message.

        Args:
            receiver_id: Receiver agent ID.
            message: Received message.
        """
        if receiver_id in self._callbacks:
            for callback in self._callbacks[receiver_id]:
                try:
                    callback(message)
                except Exception:
                    pass  # Don't let callback errors break communication

    def broadcast(
        self,
        sender_id: str,
        receiver_ids: list[str],
        content: Any,
        message_type: str = "broadcast",
    ) -> list[AgentMessage]:
        """Broadcast to multiple agents.

        Args:
            sender_id: Sender agent ID.
            receiver_ids: List of receiver IDs.
            content: Message content.
            message_type: Message type.

        Returns:
            List of sent messages.
        """
        messages = []
        for receiver_id in receiver_ids:
            msg = self.send(
                sender_id=sender_id,
                receiver_id=receiver_id,
                content=content,
                message_type=message_type,
            )
            messages.append(msg)
        return messages

    def clear(self, agent_id: str | None = None) -> None:
        """Clear pending messages.

        Args:
            agent_id: Optional agent ID to clear. If None, clear all.
        """
        if agent_id:
            self._pending.pop(agent_id, None)
        else:
            self._pending.clear()
            self._replies.clear()


# Global communicator
_global_communicator: AgentCommunicator | None = None
_comm_lock = __import__("threading").Lock()


def get_communicator() -> AgentCommunicator:
    """Get the global agent communicator.

    Returns:
        Global AgentCommunicator instance.
    """
    global _global_communicator
    with _comm_lock:
        if _global_communicator is None:
            _global_communicator = AgentCommunicator()
        return _global_communicator


def reset_communicator() -> None:
    """Reset the global agent communicator."""
    global _global_communicator
    with _comm_lock:
        _global_communicator = None
