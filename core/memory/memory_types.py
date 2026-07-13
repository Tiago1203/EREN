"""Type definitions for the Cognitive Memory System.

Provides comprehensive type definitions for different memory types,
inspired by human cognitive memory architecture.

Architecture only — no business logic, no AI.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, IntEnum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


# =============================================================================
# Memory Type Classification
# =============================================================================


class MemoryType(str, Enum):
    """Types of memory in the cognitive system.

    Inspired by human memory architecture:
    - Working: Active processing
    - Short-term: Temporary storage
    - Long-term: Persistent storage
    - Episodic: Events and experiences
    - Semantic: Facts and concepts
    - Procedural: Skills and actions
    - Temporal: Time relationships
    - Spatial: Location relationships
    """

    WORKING = "working"  # Active cognitive processing
    SHORT_TERM = "short_term"  # Temporary storage (seconds to minutes)
    LONG_TERM = "long_term"  # Persistent storage (days to years)
    EPISODIC = "episodic"  # Events and experiences
    SEMANTIC = "semantic"  # Facts, concepts, knowledge
    PROCEDURAL = "procedural"  # Skills, procedures, how-to
    TEMPORAL = "temporal"  # Time-based relationships
    SPATIAL = "spatial"  # Location-based relationships

    @classmethod
    def all(cls) -> list[str]:
        """Get all memory type values."""
        return [m.value for m in cls]

    def is_temporary(self) -> bool:
        """Check if this memory type is temporary (working/short-term)."""
        return self in (MemoryType.WORKING, MemoryType.SHORT_TERM)

    def is_persistent(self) -> bool:
        """Check if this memory type is persistent (long-term)."""
        return self in (
            MemoryType.LONG_TERM,
            MemoryType.EPISODIC,
            MemoryType.SEMANTIC,
            MemoryType.PROCEDURAL,
        )


class MemoryStatus(IntEnum):
    """Lifecycle status of a memory entry."""

    ACTIVE = 0  # Currently in use
    ACCESSIBLE = 1  # Can be retrieved
    DORMANT = 2  # Not recently accessed
    ARCHIVED = 3  # Stored but not indexed
    CONSOLIDATING = 4  # Being transferred to long-term
    DECAYING = 5  # Being forgotten
    FORGOTTEN = 6  # No longer stored


class MemoryStrength(IntEnum):
    """Strength/importance of a memory.

    Based on synaptic plasticity and memory consolidation research.
    """

    FRAGILE = 0  # Very weak, will decay quickly
    WEAK = 10  # Short-term, easily forgotten
    MODERATE = 20  # Average strength
    STRONG = 30  # Important, resists decay
    VIVID = 40  # Very important, permanent
    EIDETIC = 50  # Photographic/impossible to forget


# =============================================================================
# Memory Access and Query Types
# =============================================================================


class AccessPattern(str, Enum):
    """Pattern of memory access."""

    SEQUENTIAL = "sequential"  # Accessed in order
    RANDOM = "random"  # Accessed randomly
    FREQUENT = "frequent"  # Accessed often
    SPARSE = "sparse"  # Rarely accessed
    CONTEXTUAL = "contextual"  # Access depends on context


class RetrievalMode(str, Enum):
    """How memory is retrieved."""

    RECALL = "recall"  # Active retrieval
    RECOGNITION = "recognition"  # Identify from cues
    RELARNING = "relearning"  # Rebuild from fragments
    ASSOCIATION = "association"  # Through related memories
    SERIAL = "serial"  # Sequential search


@dataclass
class MemoryAccess:
    """Record of a memory access."""

    timestamp: str  # ISO 8601
    pattern: AccessPattern
    retrieval_mode: RetrievalMode
    context_id: str = ""
    duration_ms: float = 0.0


# =============================================================================
# Memory Content Types
# =============================================================================


class ContentType(str, Enum):
    """Type of content stored in memory."""

    TEXT = "text"  # Plain text
    STRUCTURED = "structured"  # JSON/structured data
    IMAGE = "image"  # Visual information
    AUDIO = "audio"  # Audio information
    SENSOR = "sensor"  # Sensor readings
    EMOTION = "emotion"  # Emotional state
    DECISION = "decision"  # Decision made
    OUTCOME = "outcome"  # Result of action
    RELATIONSHIP = "relationship"  # Links between memories
    PATTERN = "pattern"  # Recognized pattern


@dataclass(frozen=True, slots=True)
class MemoryContent:
    """Content of a memory entry."""

    type: ContentType
    data: str | dict | bytes
    encoding: str = "utf-8"  # Character encoding
    mime_type: str = "text/plain"


# =============================================================================
# Memory Relationships
# =============================================================================


class RelationshipType(str, Enum):
    """Types of relationships between memories."""

    CAUSAL = "causal"  # A caused B
    TEMPORAL = "temporal"  # A happened before/after B
    SPATIAL = "spatial"  # A happened at/in B location
    SEMANTIC = "semantic"  # A is similar/related to B
    REFERENTIAL = "referential"  # A references B
    PARTITIVE = "partitive"  # A is part of B
    CONTRADICTORY = "contradictory"  # A contradicts B
    ENHANCING = "enhancing"  # A strengthens B


@dataclass(frozen=True, slots=True)
class MemoryRelationship:
    """Relationship between memory entries."""

    target_id: str
    relationship_type: RelationshipType
    strength: float = 1.0  # 0.0 to 1.0
    bidirectional: bool = False


# =============================================================================
# Memory Metadata
# =============================================================================


@dataclass(frozen=True, slots=True)
class MemoryMetadata:
    """Metadata for a memory entry."""

    created_at: str  # ISO 8601
    updated_at: str  # ISO 8601
    last_accessed_at: str = ""
    access_count: int = 0
    access_history: tuple[MemoryAccess, ...] = field(default_factory=tuple)
    source: str = ""  # Where the memory came from
    confidence: float = 1.0  # Confidence in accuracy
    tags: tuple[str, ...] = field(default_factory=tuple)
    importance: int = 0  # User/AI assigned importance
    emotional_valence: float = 0.0  # -1.0 (negative) to 1.0 (positive)
    emotional_arousal: float = 0.0  # 0.0 (calm) to 1.0 (arousing)

    @classmethod
    def now(cls, **kwargs) -> MemoryMetadata:
        """Create metadata with current timestamp."""
        timestamp = datetime.now(timezone.utc).isoformat()
        return cls(created_at=timestamp, updated_at=timestamp, **kwargs)

    def record_access(self, access: MemoryAccess) -> MemoryMetadata:
        """Return updated metadata with new access record."""
        from dataclasses import replace
        history = list(self.access_history) + [access]
        return replace(
            self,
            last_accessed_at=access.timestamp,
            access_count=self.access_count + 1,
            access_history=tuple(history),
        )


# =============================================================================
# Memory Policies
# =============================================================================


@dataclass
class RetentionPolicy:
    """Policy for how long memories are retained."""

    memory_type: MemoryType
    min_duration_seconds: float = 60.0  # Minimum retention time
    max_duration_seconds: float = 3600.0  # Maximum before review
    decay_rate: float = 0.01  # Strength loss per time unit
    consolidation_threshold: float = 0.5  # Strength to trigger consolidation
    forget_threshold: float = 0.1  # Strength below which to forget

    def should_consolidate(self, strength: float) -> bool:
        """Check if memory should be consolidated to long-term."""
        return strength >= self.consolidation_threshold

    def should_forget(self, strength: float) -> bool:
        """Check if memory should be forgotten."""
        return strength <= self.forget_threshold

    def calculate_decay(self, elapsed_seconds: float, current_strength: float) -> float:
        """Calculate new strength after decay."""
        decay = self.decay_rate * (elapsed_seconds / 60.0)  # Per minute
        return max(0.0, current_strength - decay)


@dataclass
class IndexingPolicy:
    """Policy for how memories are indexed."""

    memory_type: MemoryType
    index_keywords: bool = True
    index_entities: bool = True
    index_concepts: bool = True
    index_relationships: bool = True
    index_temporal: bool = True
    index_spatial: bool = True
    index_emotional: bool = True
    similarity_threshold: float = 0.7  # Threshold for similar memory detection


@dataclass
class RetrievalPolicy:
    """Policy for how memories are retrieved."""

    memory_type: MemoryType
    retrieval_mode: RetrievalMode = RetrievalMode.RECALL
    max_results: int = 10
    min_relevance: float = 0.5
    include_context: bool = True
    include_relationships: bool = True
    temporal_window_seconds: float | None = None  # None = no limit


@dataclass
class ConsolidationPolicy:
    """Policy for memory consolidation (STM to LTM)."""

    trigger_on_access_count: int = 3
    trigger_on_importance: int = 5
    trigger_on_emotional_valence: bool = True
    min_consolidation_strength: float = 0.5
    parallel_consolidation: bool = True  # Consolidate related memories too
    forget_duplicates: bool = True


# =============================================================================
# Query and Filter Types
# =============================================================================


@dataclass
class MemoryFilter:
    """Filter criteria for memory queries."""

    memory_type: MemoryType | None = None
    status: MemoryStatus | None = None
    min_strength: MemoryStrength | None = None
    min_confidence: float | None = None
    tags: tuple[str, ...] | None = None
    has_tag: str | None = None
    created_after: str | None = None  # ISO 8601
    created_before: str | None = None
    content_type: ContentType | None = None
    source: str | None = None
    has_relationships: bool | None = None
    relationship_to: str | None = None


@dataclass
class SearchOptions:
    """Options for memory search operations."""

    filter: MemoryFilter | None = None
    sort_by: str = "relevance"  # relevance, strength, time, importance
    ascending: bool = False
    limit: int | None = 100
    offset: int = 0


# =============================================================================
# Context Types
# =============================================================================


@dataclass
class RetrievalContext:
    """Context for memory retrieval."""

    session_id: str = ""
    user_id: str = ""
    device_id: str = ""
    location: str = ""
    task: str = ""  # Current task
    emotional_state: str = ""
    time_context: str = ""  # morning, afternoon, evening, night


@dataclass
class ConsolidationContext:
    """Context for memory consolidation."""

    trigger: str  # What triggered consolidation
    source_memory_id: str = ""
    related_memory_ids: tuple[str, ...] = field(default_factory=tuple)
    preserve_temporal_order: bool = True
    merge_duplicates: bool = True


# =============================================================================
# Memory Statistics
# =============================================================================


@dataclass
class MemoryStatistics:
    """Statistics about memory usage."""

    total_memories: int = 0
    by_type: dict[str, int] = field(default_factory=dict)
    by_status: dict[str, int] = field(default_factory=dict)
    average_strength: float = 0.0
    total_size_bytes: int = 0
    consolidation_count: int = 0
    forgotten_count: int = 0
    avg_retrieval_time_ms: float = 0.0
