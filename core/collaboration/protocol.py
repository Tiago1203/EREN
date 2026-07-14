"""Collaboration protocols for EREN Multi-Agent Collaboration Engine.

Defines communication protocols between agents.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable

from core.collaboration.types import (
    CollaborationMessage,
    MessageType,
    MessageStatus,
    CollaborationSession,
)

if TYPE_CHECKING:
    pass


class ProtocolHandler:
    """Handles collaboration protocols.

    The Protocol Handler does NOT:
    - Execute tasks
    - Know about implementations

    It ONLY:
    - Defines protocols
    - Validates messages
    - Routes messages
    """

    def __init__(self):
        """Initialize protocol handler."""
        self._handlers: dict[MessageType, list[Callable]] = {
            msg_type: [] for msg_type in MessageType
        }

    def register_handler(
        self,
        message_type: MessageType,
        handler: Callable,
    ) -> None:
        """Register a message handler.

        Args:
            message_type: Type of message.
            handler: Handler function.
        """
        if message_type not in self._handlers:
            self._handlers[message_type] = []
        self._handlers[message_type].append(handler)

    def handle(
        self,
        message: CollaborationMessage,
    ) -> Any | None:
        """Handle a message.

        Args:
            message: Message to handle.

        Returns:
            Handler result or None.
        """
        handlers = self._handlers.get(message.message_type, [])
        results = []

        for handler in handlers:
            try:
                result = handler(message)
                results.append(result)
            except Exception:
                pass

        return results if results else None

    def validate_message(
        self,
        message: CollaborationMessage,
    ) -> tuple[bool, str]:
        """Validate a message.

        Args:
            message: Message to validate.

        Returns:
            Tuple of (is_valid, error_message).
        """
        if not message.message_id:
            return False, "Message ID is required"

        if not message.session_id:
            return False, "Session ID is required"

        if not message.sender_id:
            return False, "Sender ID is required"

        if not message.message_type:
            return False, "Message type is required"

        return True, ""


class CommunicationPattern:
    """Communication patterns between agents."""

    @staticmethod
    def one_to_one(
        sender_id: str,
        receiver_id: str,
        content: Any,
    ) -> list[str]:
        """One-to-one communication.

        Args:
            sender_id: Sender ID.
            receiver_id: Receiver ID.
            content: Message content.

        Returns:
            List of receiver IDs.
        """
        return [receiver_id]

    @staticmethod
    def one_to_many(
        sender_id: str,
        receiver_ids: list[str],
        content: Any,
    ) -> list[str]:
        """One-to-many communication.

        Args:
            sender_id: Sender ID.
            receiver_ids: List of receiver IDs.
            content: Message content.

        Returns:
            List of receiver IDs.
        """
        return receiver_ids

    @staticmethod
    def many_to_one(
        sender_ids: list[str],
        receiver_id: str,
        content: Any,
    ) -> list[str]:
        """Many-to-one communication.

        Args:
            sender_ids: List of sender IDs.
            receiver_id: Receiver ID.
            content: Message content.

        Returns:
            List of receiver IDs.
        """
        return [receiver_id]

    @staticmethod
    def many_to_many(
        sender_ids: list[str],
        receiver_ids: list[str],
        content: Any,
    ) -> list[str]:
        """Many-to-many communication.

        Args:
            sender_ids: List of sender IDs.
            receiver_ids: List of receiver IDs.
            content: Message content.

        Returns:
            List of receiver IDs.
        """
        return receiver_ids

    @staticmethod
    def broadcast(
        sender_id: str,
        all_participants: list[str],
        content: Any,
    ) -> list[str]:
        """Broadcast to all participants.

        Args:
            sender_id: Sender ID.
            all_participants: All participants in session.
            content: Message content.

        Returns:
            List of receiver IDs (all except sender).
        """
        return [p for p in all_participants if p != sender_id]


class MessageBuilder:
    """Builds collaboration messages."""

    @staticmethod
    def request(
        session_id: str,
        sender_id: str,
        receiver_ids: list[str],
        content: Any,
        correlation_id: str = "",
    ) -> CollaborationMessage:
        """Build a request message."""
        return CollaborationMessage.create(
            session_id=session_id,
            sender_id=sender_id,
            message_type=MessageType.REQUEST,
            content=content,
            receiver_ids=receiver_ids,
        )

    @staticmethod
    def response(
        session_id: str,
        sender_id: str,
        reply_to: str,
        content: Any,
    ) -> CollaborationMessage:
        """Build a response message."""
        return CollaborationMessage(
            message_id="",  # Will be set by create
            session_id=session_id,
            sender_id=sender_id,
            message_type=MessageType.RESPONSE,
            content=content,
            reply_to=reply_to,
        )

    @staticmethod
    def broadcast(
        session_id: str,
        sender_id: str,
        all_participants: list[str],
        content: Any,
    ) -> CollaborationMessage:
        """Build a broadcast message."""
        receivers = CommunicationPattern.broadcast(sender_id, all_participants, content)
        return CollaborationMessage.create(
            session_id=session_id,
            sender_id=sender_id,
            message_type=MessageType.BROADCAST,
            content=content,
            receiver_ids=receivers,
        )

    @staticmethod
    def proposal(
        session_id: str,
        sender_id: str,
        receiver_ids: list[str],
        title: str,
        description: str,
        content: Any,
    ) -> CollaborationMessage:
        """Build a proposal message."""
        return CollaborationMessage.create(
            session_id=session_id,
            sender_id=sender_id,
            message_type=MessageType.PROPOSAL,
            content={
                "title": title,
                "description": description,
                "content": content,
            },
            receiver_ids=receiver_ids,
        )

    @staticmethod
    def vote(
        session_id: str,
        sender_id: str,
        receiver_ids: list[str],
        proposal_id: str,
        vote_value: str,
    ) -> CollaborationMessage:
        """Build a vote message."""
        return CollaborationMessage.create(
            session_id=session_id,
            sender_id=sender_id,
            message_type=MessageType.VOTE,
            content={
                "proposal_id": proposal_id,
                "vote": vote_value,
            },
            receiver_ids=receiver_ids,
        )

    @staticmethod
    def cancel(
        session_id: str,
        sender_id: str,
        receiver_ids: list[str],
        reason: str,
    ) -> CollaborationMessage:
        """Build a cancel message."""
        return CollaborationMessage.create(
            session_id=session_id,
            sender_id=sender_id,
            message_type=MessageType.CANCEL,
            content={"reason": reason},
            receiver_ids=receiver_ids,
        )

    @staticmethod
    def escalation(
        session_id: str,
        sender_id: str,
        receiver_ids: list[str],
        escalation_type: str,
        reason: str,
        data: dict | None = None,
    ) -> CollaborationMessage:
        """Build an escalation message."""
        return CollaborationMessage.create(
            session_id=session_id,
            sender_id=sender_id,
            message_type=MessageType.ESCALATION,
            content={
                "type": escalation_type,
                "reason": reason,
                "data": data or {},
            },
            receiver_ids=receiver_ids,
        )
