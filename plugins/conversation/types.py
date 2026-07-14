"""Conversation memory types for EREN Conversation Memory Plugin.

Defines all types, enums, and value objects for conversation memory.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


# =============================================================================
# Conversation Types
# =============================================================================


class ConversationRole(str, Enum):
    """Roles in a conversation."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"


class ConversationType(str, Enum):
    """Types of conversations."""

    CHAT = "chat"
    MEDICAL = "medical"
    TECHNICAL = "technical"
    GENERAL = "general"


class ConversationState(str, Enum):
    """States of a conversation."""

    ACTIVE = "active"
    ARCHIVED = "archived"
    SUMMARIZED = "summarized"
    DELETED = "deleted"


# =============================================================================
# Conversation Entry
# =============================================================================


@dataclass
class ConversationEntry:
    """A single entry in a conversation."""

    entry_id: str
    conversation_id: str
    role: ConversationRole
    content: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict = field(default_factory=dict)
    tokens: int = 0

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "entry_id": self.entry_id,
            "conversation_id": self.conversation_id,
            "role": self.role.value,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
            "tokens": self.tokens,
        }

    @classmethod
    def from_dict(cls, data: dict) -> ConversationEntry:
        """Create from dictionary."""
        data["role"] = ConversationRole(data["role"])
        if "timestamp" in data and isinstance(data["timestamp"], str):
            data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        return cls(**data)


# =============================================================================
# Conversation Summary
# =============================================================================


@dataclass
class ConversationSummary:
    """Summary of a conversation."""

    conversation_id: str
    summary: str
    key_points: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    entries_count: int = 0
    tokens_saved: int = 0

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "conversation_id": self.conversation_id,
            "summary": self.summary,
            "key_points": self.key_points,
            "created_at": self.created_at.isoformat(),
            "entries_count": self.entries_count,
            "tokens_saved": self.tokens_saved,
        }

    @classmethod
    def from_dict(cls, data: dict) -> ConversationSummary:
        """Create from dictionary."""
        if "created_at" in data and isinstance(data["created_at"], str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        return cls(**data)


# =============================================================================
# Conversation Metadata
# =============================================================================


@dataclass
class ConversationMetadata:
    """Metadata for a conversation."""

    conversation_id: str
    title: str = ""
    conversation_type: ConversationType = ConversationType.GENERAL
    user_id: str = ""
    session_id: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_activity: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    entries_count: int = 0
    total_tokens: int = 0
    state: ConversationState = ConversationState.ACTIVE
    tags: list[str] = field(default_factory=list)
    context_window: int = 10  # Number of entries to include

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "conversation_id": self.conversation_id,
            "title": self.title,
            "conversation_type": self.conversation_type.value,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "entries_count": self.entries_count,
            "total_tokens": self.total_tokens,
            "state": self.state.value,
            "tags": self.tags,
            "context_window": self.context_window,
        }

    @classmethod
    def from_dict(cls, data: dict) -> ConversationMetadata:
        """Create from dictionary."""
        if "conversation_type" in data:
            data["conversation_type"] = ConversationType(data["conversation_type"])
        if "state" in data:
            data["state"] = ConversationState(data["state"])
        for dt_field in ["created_at", "updated_at", "last_activity"]:
            if dt_field in data and isinstance(data[dt_field], str):
                data[dt_field] = datetime.fromisoformat(data[dt_field])
        return cls(**data)


# =============================================================================
# Conversation Search
# =============================================================================


@dataclass
class ConversationSearch:
    """Search parameters for conversations."""

    query: str = ""
    user_id: str | None = None
    session_id: str | None = None
    conversation_type: ConversationType | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None
    limit: int = 10
    offset: int = 0

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "query": self.query,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "conversation_type": self.conversation_type.value if self.conversation_type else None,
            "date_from": self.date_from.isoformat() if self.date_from else None,
            "date_to": self.date_to.isoformat() if self.date_to else None,
            "limit": self.limit,
            "offset": self.offset,
        }


# =============================================================================
# Conversation Metrics
# =============================================================================


@dataclass
class ConversationMetrics:
    """Metrics for conversation memory."""

    total_conversations: int = 0
    total_entries: int = 0
    total_summaries: int = 0
    total_tokens: int = 0
    average_entries_per_conversation: float = 0.0
    average_tokens_per_entry: float = 0.0
    hit_rate: float = 0.0
    average_latency_ms: float = 0.0

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "total_conversations": self.total_conversations,
            "total_entries": self.total_entries,
            "total_summaries": self.total_summaries,
            "total_tokens": self.total_tokens,
            "average_entries_per_conversation": self.average_entries_per_conversation,
            "average_tokens_per_entry": self.average_tokens_per_entry,
            "hit_rate": self.hit_rate,
            "average_latency_ms": self.average_latency_ms,
        }


# =============================================================================
# Conversation Configuration
# =============================================================================


@dataclass
class ConversationConfiguration:
    """Configuration for conversation memory."""

    max_context_entries: int = 20
    max_tokens_per_entry: int = 4000
    summary_threshold_entries: int = 50
    summary_max_length: int = 500
    ttl_days: int = 30
    auto_archive_days: int = 7
    enable_summarization: bool = True
    enable_full_text_search: bool = True
    database_path: str = ":memory:"
    enable_multi_user: bool = True
    enable_multi_session: bool = True


# =============================================================================
# Conversation Chunk (for RAG integration)
# =============================================================================


@dataclass
class ConversationChunk:
    """A chunk of conversation for RAG integration.

    Allows future vector search capabilities.
    """

    chunk_id: str
    conversation_id: str
    entry_id: str
    content: str
    role: str
    sequence: int
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "chunk_id": self.chunk_id,
            "conversation_id": self.conversation_id,
            "entry_id": self.entry_id,
            "content": self.content,
            "role": self.role,
            "sequence": self.sequence,
            "metadata": self.metadata,
        }


# =============================================================================
# Conversation Attachment
# =============================================================================


@dataclass
class ConversationAttachment:
    """An attachment in a conversation (image, PDF, audio, DICOM, etc.)."""

    attachment_id: str
    conversation_id: str
    entry_id: str | None = None
    filename: str = ""
    content_type: str = ""
    url: str = ""
    size_bytes: int = 0
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "attachment_id": self.attachment_id,
            "conversation_id": self.conversation_id,
            "entry_id": self.entry_id,
            "filename": self.filename,
            "content_type": self.content_type,
            "url": self.url,
            "size_bytes": self.size_bytes,
            "metadata": self.metadata,
        }


# =============================================================================
# Conversation Reference
# =============================================================================


@dataclass
class ConversationReference:
    """A reference to another conversation or entity."""

    reference_id: str
    conversation_id: str
    entry_id: str
    reference_type: str  # conversation, document, patient, etc.
    reference_target: str  # ID of referenced entity
    description: str = ""
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "reference_id": self.reference_id,
            "conversation_id": self.conversation_id,
            "entry_id": self.entry_id,
            "reference_type": self.reference_type,
            "reference_target": self.reference_target,
            "description": self.description,
            "metadata": self.metadata,
        }


# =============================================================================
# Conversation Statistics
# =============================================================================


@dataclass
class ConversationStatistics:
    """Statistics for a conversation."""

    conversation_id: str
    total_entries: int = 0
    user_entries: int = 0
    assistant_entries: int = 0
    system_entries: int = 0
    total_tokens: int = 0
    average_response_time_ms: float = 0.0
    first_entry_at: datetime | None = None
    last_entry_at: datetime | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "conversation_id": self.conversation_id,
            "total_entries": self.total_entries,
            "user_entries": self.user_entries,
            "assistant_entries": self.assistant_entries,
            "system_entries": self.system_entries,
            "total_tokens": self.total_tokens,
            "average_response_time_ms": self.average_response_time_ms,
            "first_entry_at": self.first_entry_at.isoformat() if self.first_entry_at else None,
            "last_entry_at": self.last_entry_at.isoformat() if self.last_entry_at else None,
        }


# =============================================================================
# Conversation Search Result
# =============================================================================


@dataclass
class ConversationSearchResult:
    """Result from a conversation search."""

    entries: list[ConversationEntry]
    total: int
    query: str
    filters_applied: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "entries": [e.to_dict() for e in self.entries],
            "total": self.total,
            "query": self.query,
            "filters_applied": self.filters_applied,
        }
