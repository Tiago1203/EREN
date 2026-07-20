"""Conversation domain events."""
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class ConversationStarted:
    """Event fired when a conversation starts."""
    conversation_id: UUID
    tenant_id: UUID
    user_id: UUID
    primary_domain: str
    timestamp: datetime


@dataclass(frozen=True)
class MessageReceived:
    """Event fired when a message is received."""
    conversation_id: UUID
    message_id: UUID
    role: str
    timestamp: datetime


@dataclass(frozen=True)
class ResponseGenerated:
    """Event fired when a response is generated."""
    conversation_id: UUID
    message_id: UUID
    confidence: float
    latency_ms: int
    tokens_used: int
    timestamp: datetime
