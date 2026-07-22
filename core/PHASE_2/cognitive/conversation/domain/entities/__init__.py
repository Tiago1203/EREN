"""Conversation domain entities."""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from core.PHASE_1.infrastructure.shared.primitives.entity_id import EntityId


class ConversationStatus(str, Enum):
    """Conversation status enumeration."""
    ACTIVE = "active"
    ENDED = "ended"
    ARCHIVED = "archived"


class MessageRole(str, Enum):
    """Message role enumeration."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


@dataclass
class ConversationId(EntityId):
    """Conversation identifier."""
    pass


@dataclass
class MessageId(EntityId):
    """Message identifier."""
    pass


@dataclass
class Conversation:
    """Conversation aggregate root."""
    id: ConversationId
    tenant_id: UUID
    user_id: UUID
    session_id: UUID
    status: ConversationStatus
    primary_domain: str
    created_at: datetime
    updated_at: datetime
    ended_at: Optional[datetime] = None
    message_count: int = 0
    average_confidence: float = 0.0
    
    @classmethod
    def create(
        cls,
        tenant_id: UUID,
        user_id: UUID,
        session_id: UUID,
        primary_domain: str = "biomedical",
    ) -> "Conversation":
        """Create a new conversation."""
        now = datetime.utcnow()
        return cls(
            id=ConversationId(uuid4()),
            tenant_id=tenant_id,
            user_id=user_id,
            session_id=session_id,
            status=ConversationStatus.ACTIVE,
            primary_domain=primary_domain,
            created_at=now,
            updated_at=now,
        )
    
    def add_message(self) -> None:
        """Increment message count."""
        self.message_count += 1
        self.updated_at = datetime.utcnow()
    
    def update_confidence(self, confidence: float) -> None:
        """Update average confidence."""
        # Rolling average
        if self.message_count == 0:
            self.average_confidence = confidence
        else:
            self.average_confidence = (
                (self.average_confidence * (self.message_count - 1) + confidence)
                / self.message_count
            )
    
    def end(self) -> None:
        """End the conversation."""
        self.status = ConversationStatus.ENDED
        self.ended_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()


@dataclass
class Message:
    """Message entity."""
    id: MessageId
    conversation_id: ConversationId
    role: MessageRole
    content: str
    created_at: datetime
    latency_ms: int = 0
    confidence: float = 0.0
    tokens_used: int = 0
    reasoning_steps: int = 0
    user_feedback: Optional[str] = None
    
    @classmethod
    def create(
        cls,
        conversation_id: ConversationId,
        role: MessageRole,
        content: str,
    ) -> "Message":
        """Create a new message."""
        return cls(
            id=MessageId(uuid4()),
            conversation_id=conversation_id,
            role=role,
            content=content,
            created_at=datetime.utcnow(),
        )
