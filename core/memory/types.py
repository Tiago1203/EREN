"""Memory types for EREN OS Cognitive Memory Orchestrator.

Defines all types, enums, and value objects used by the memory system.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass


# =============================================================================
# Memory Types
# =============================================================================


class MemoryType(str, Enum):
    """Types of memory in the system."""

    WORKING = "working"          # Short-term, session-based
    CONVERSATION = "conversation"  # Current conversation context
    EPISODIC = "episodic"        # Past experiences/events
    SEMANTIC = "semantic"        # General knowledge/facts
    VECTOR = "vector"            # Embedding-based search
    CLINICAL = "clinical"        # Medical/clinical information
    DEVICE = "device"            # Device state/metrics
    SHORT_TERM = "short_term"    # Immediate context
    LONG_TERM = "long_term"      # Persistent storage

    @classmethod
    def is_short_term(cls, memory_type: "MemoryType") -> bool:
        """Check if memory type is short-term."""
        return memory_type in (cls.WORKING, cls.CONVERSATION, cls.SHORT_TERM)

    @classmethod
    def is_long_term(cls, memory_type: "MemoryType") -> bool:
        """Check if memory type is long-term."""
        return memory_type in (
            cls.EPISODIC, cls.SEMANTIC, cls.LONG_TERM, cls.CLINICAL
        )


# =============================================================================
# Memory State
# =============================================================================


class MemoryState(str, Enum):
    """States for memory lifecycle."""

    UNREGISTERED = "unregistered"
    REGISTERED = "registered"
    INITIALIZED = "initialized"
    READY = "ready"
    UNAVAILABLE = "unavailable"
    DISABLED = "disabled"


# =============================================================================
# Memory Access Policies
# =============================================================================


class MemoryAccessPolicy(str, Enum):
    """Policies for memory access."""

    FIRST_AVAILABLE = "first_available"
    LONG_TERM_ONLY = "long_term_only"
    SHORT_TERM_ONLY = "short_term_only"
    MERGE_ALL = "merge_all"
    READ_ONLY = "read_only"
    WRITE_THROUGH = "write_through"
    CACHE_FIRST = "cache_first"


# =============================================================================
# Memory Operation
# =============================================================================


class MemoryOperation(str, Enum):
    """Types of memory operations."""

    READ = "read"
    WRITE = "write"
    SEARCH = "search"
    DELETE = "delete"
    CLEAR = "clear"
    MERGE = "merge"


# =============================================================================
# Memory Query
# =============================================================================


@dataclass
class MemoryQuery:
    """Query for memory operations."""

    query: str
    memory_types: list[MemoryType] | None = None
    limit: int = 10
    offset: int = 0
    filters: dict = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "query": self.query,
            "memory_types": [m.value for m in self.memory_types] if self.memory_types else None,
            "limit": self.limit,
            "offset": self.offset,
            "filters": self.filters,
            "metadata": self.metadata,
        }


# =============================================================================
# Memory Result
# =============================================================================


@dataclass
class MemoryResult:
    """Result from memory operation."""

    content: str
    memory_type: MemoryType
    memory_id: str
    score: float = 0.0
    metadata: dict = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "content": self.content,
            "memory_type": self.memory_type.value,
            "memory_id": self.memory_id,
            "score": self.score,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat(),
        }


# =============================================================================
# Memory Response
# =============================================================================


@dataclass
class MemoryResponse:
    """Response from memory operations."""

    results: list[MemoryResult] = field(default_factory=list)
    operation: MemoryOperation = MemoryOperation.READ
    success: bool = True
    error: str = ""
    metadata: dict = field(default_factory=dict)

    @property
    def content(self) -> str:
        """Get combined content from all results."""
        return "\n".join(r.content for r in self.results)

    @property
    def is_empty(self) -> bool:
        """Check if response is empty."""
        return len(self.results) == 0

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "results": [r.to_dict() for r in self.results],
            "operation": self.operation.value,
            "success": self.success,
            "error": self.error,
            "metadata": self.metadata,
        }


# =============================================================================
# Memory Entry
# =============================================================================


@dataclass
class MemoryEntry:
    """Entry to store in memory."""

    content: str
    memory_type: MemoryType
    key: str = ""
    metadata: dict = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime | None = None

    def __post_init__(self):
        """Generate key if not provided."""
        if not self.key:
            import uuid
            self.key = str(uuid.uuid4())

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "content": self.content,
            "memory_type": self.memory_type.value,
            "key": self.key,
            "metadata": self.metadata,
            "tags": self.tags,
            "timestamp": self.timestamp.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
        }


# =============================================================================
# Memory Metrics
# =============================================================================


@dataclass
class MemoryMetrics:
    """Metrics for a memory."""

    total_reads: int = 0
    total_writes: int = 0
    total_searches: int = 0
    total_hits: int = 0
    total_misses: int = 0
    average_latency_ms: float = 0.0
    total_latency_ms: int = 0

    @property
    def hit_rate(self) -> float:
        """Calculate hit rate."""
        total = self.total_hits + self.total_misses
        if total == 0:
            return 0.0
        return (self.total_hits / total) * 100

    def record_read(self, latency_ms: int, hit: bool = True) -> None:
        """Record a read operation."""
        self.total_reads += 1
        if hit:
            self.total_hits += 1
        else:
            self.total_misses += 1
        self.total_latency_ms += latency_ms
        self._update_average()

    def record_write(self, latency_ms: int) -> None:
        """Record a write operation."""
        self.total_writes += 1
        self.total_latency_ms += latency_ms
        self._update_average()

    def record_search(self, latency_ms: int) -> None:
        """Record a search operation."""
        self.total_searches += 1
        self.total_latency_ms += latency_ms
        self._update_average()

    def _update_average(self) -> None:
        """Update average latency."""
        total_ops = self.total_reads + self.total_writes + self.total_searches
        if total_ops > 0:
            self.average_latency_ms = self.total_latency_ms / total_ops

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "total_reads": self.total_reads,
            "total_writes": self.total_writes,
            "total_searches": self.total_searches,
            "total_hits": self.total_hits,
            "total_misses": self.total_misses,
            "hit_rate": self.hit_rate,
            "average_latency_ms": self.average_latency_ms,
        }
