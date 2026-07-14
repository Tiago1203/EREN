"""Cognitive Context Engine types for EREN OS.

Types for the Cognitive Context Engine (CCE).
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


def generate_id() -> str:
    """Generate a unique ID."""
    return str(uuid.uuid4())


# =============================================================================
# Context Priority
# =============================================================================


class ContextPriority(str, Enum):
    """Priority levels for context items."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ContextSource(str, Enum):
    """Sources of context."""

    CONVERSATION = "conversation"
    KNOWLEDGE = "knowledge"
    VECTOR_MEMORY = "vector_memory"
    DEVICE = "device"
    CLINICAL = "clinical"
    USER = "user"


# =============================================================================
# Context Item
# =============================================================================


@dataclass
class ContextItem:
    """A single context item."""

    item_id: str
    source: ContextSource
    content: str

    # Relevance
    relevance_score: float = 0.0
    priority: ContextPriority = ContextPriority.MEDIUM

    # Metadata
    metadata: dict = field(default_factory=dict)

    # Provenance
    document_id: str = ""
    chunk_id: str = ""
    title: str = ""
    author: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    # Token info
    tokens: int = 0

    def __post_init__(self) -> None:
        """Calculate tokens if not set."""
        if self.tokens == 0:
            self.tokens = len(self.content) // 4


# =============================================================================
# Context Package
# =============================================================================


@dataclass
class ContextPackage:
    """Complete context package for a task.

    This is the output of the Cognitive Context Engine.
    The Prompt Builder only receives this package.
    """

    package_id: str
    query: str

    # All context items
    items: list[ContextItem] = field(default_factory=list)

    # Aggregated content
    context_text: str = ""
    context_tokens: int = 0

    # Statistics
    total_items: int = 0
    items_by_source: dict[str, int] = field(default_factory=dict)
    avg_relevance: float = 0.0
    max_relevance: float = 0.0

    # Quality indicators
    has_clinical_context: bool = False
    has_conversation_history: bool = False
    has_knowledge_context: bool = False

    # Budget
    available_tokens: int = 0
    used_tokens: int = 0
    reserved_tokens: int = 500

    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "package_id": self.package_id,
            "query": self.query,
            "total_items": self.total_items,
            "context_tokens": self.context_tokens,
            "items_by_source": self.items_by_source,
            "avg_relevance": self.avg_relevance,
            "has_clinical_context": self.has_clinical_context,
            "has_conversation_history": self.has_conversation_history,
            "has_knowledge_context": self.has_knowledge_context,
            "used_tokens": self.used_tokens,
            "created_at": self.created_at.isoformat(),
        }


# =============================================================================
# Context Query
# =============================================================================


@dataclass
class ContextQuery:
    """Query for context retrieval."""

    query_id: str
    query_text: str

    # Retrieval options
    top_k: int = 10
    min_relevance: float = 0.5

    # Budget
    max_tokens: int = 4000
    reserved_tokens: int = 500

    # Sources to include
    include_conversation: bool = True
    include_knowledge: bool = True
    include_device: bool = True
    include_clinical: bool = True

    # Priority
    prioritize_clinical: bool = True
    prioritize_recent: bool = True

    # Filters
    medical_specialty: str = ""
    language: str = ""
    tags: list[str] = field(default_factory=list)

    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


# =============================================================================
# Retrieval Result
# =============================================================================


@dataclass
class ContextRetrievalResult:
    """Result from context retrieval."""

    query_id: str
    items: list[ContextItem] = field(default_factory=list)

    # Statistics
    total_retrieved: int = 0
    retrieval_time_ms: int = 0

    # Deduplication
    unique_items: int = 0
    duplicates_removed: int = 0

    # Quality
    avg_relevance: float = 0.0
