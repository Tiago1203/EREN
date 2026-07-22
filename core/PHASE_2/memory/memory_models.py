"""Memory models for the Cognitive Memory System.

Defines the core memory entry and related models.

Architecture only — no business logic, no AI.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .memory_types import (
    ContentType,
    MemoryAccess,
    MemoryContent,
    MemoryMetadata,
    MemoryRelationship,
    MemoryStatus,
    MemoryStrength,
    MemoryType,
    RelationshipType,
)

if TYPE_CHECKING:
    pass


# =============================================================================
# Core Memory Entry
# =============================================================================


@dataclass(frozen=True, slots=True)
class MemoryEntry:
    """A single memory entry in the cognitive memory system.

    Memory entries are the atomic units of stored information.
    They are inspired by memory traces in cognitive science.

    Key characteristics:
    - Immutable once created (new version on update)
    - Rich metadata for retrieval decisions
    - Relationships to other memories
    - Content with type and encoding
    """

    # Identity
    memory_id: str  # Unique identifier
    memory_type: MemoryType  # Type of memory

    # Content
    content: MemoryContent
    summary: str = ""  # Brief summary for quick retrieval

    # Strength and status
    strength: float = 1.0  # 0.0 to 1.0, based on MemoryStrength
    status: MemoryStatus = MemoryStatus.ACTIVE

    # Relationships
    relationships: tuple[MemoryRelationship, ...] = field(default_factory=tuple)

    # Metadata
    metadata: MemoryMetadata = field(default_factory=MemoryMetadata)

    # Factory methods
    @classmethod
    def create(
        cls,
        memory_id: str,
        memory_type: MemoryType,
        content: MemoryContent,
        summary: str = "",
        strength: float = 1.0,
        **kwargs,
    ) -> MemoryEntry:
        """Create a new memory entry with current timestamp."""
        return cls(
            memory_id=memory_id,
            memory_type=memory_type,
            content=content,
            summary=summary,
            strength=strength,
            metadata=MemoryMetadata.now(**kwargs),
        )

    # Identity methods
    @property
    def id_string(self) -> str:
        """Get the memory ID as a string."""
        return self.memory_id

    # Content methods
    def get_text_content(self) -> str:
        """Get text content if available."""
        if self.content.type == ContentType.TEXT:
            return str(self.content.data)
        return str(self.content.data)

    # Strength methods
    def get_strength_level(self) -> MemoryStrength:
        """Get the MemoryStrength level for current strength."""
        if self.strength <= 0.0:
            return MemoryStrength.FRAGILE
        elif self.strength <= 0.2:
            return MemoryStrength.WEAK
        elif self.strength <= 0.4:
            return MemoryStrength.MODERATE
        elif self.strength <= 0.6:
            return MemoryStrength.STRONG
        elif self.strength <= 0.8:
            return MemoryStrength.VIVID
        else:
            return MemoryStrength.EIDETIC

    def is_accessible(self) -> bool:
        """Check if memory can be retrieved."""
        return self.status in (
            MemoryStatus.ACTIVE,
            MemoryStatus.ACCESSIBLE,
        )

    def is_forgotten(self) -> bool:
        """Check if memory has been forgotten."""
        return self.status == MemoryStatus.FORGOTTEN

    def needs_consolidation(self) -> bool:
        """Check if memory needs consolidation."""
        return (
            self.strength >= 0.5
            and self.status == MemoryStatus.DORMANT
        )

    # Relationship methods
    def get_related_memories(
        self,
        relationship_type: RelationshipType | None = None,
    ) -> list[str]:
        """Get IDs of related memories."""
        if relationship_type is None:
            return [r.target_id for r in self.relationships]

        return [
            r.target_id
            for r in self.relationships
            if r.relationship_type == relationship_type
        ]

    def has_relationship_to(self, target_id: str) -> bool:
        """Check if this memory has a relationship to target."""
        return any(r.target_id == target_id for r in self.relationships)

    # Access tracking
    def record_access(
        self,
        access: MemoryAccess,
    ) -> MemoryEntry:
        """Return updated entry with new access recorded."""
        from dataclasses import replace
        return replace(
            self,
            metadata=self.metadata.record_access(access),
        )

    # Strength modification
    def strengthen(self, amount: float) -> MemoryEntry:
        """Return entry with increased strength."""
        from dataclasses import replace
        new_strength = min(1.0, self.strength + amount)
        new_status = MemoryStatus.ACTIVE if new_strength > 0.5 else self.status
        return replace(
            self,
            strength=new_strength,
            status=new_status,
        )

    def weaken(self, amount: float) -> MemoryEntry:
        """Return entry with decreased strength."""
        from dataclasses import replace
        new_strength = max(0.0, self.strength - amount)
        new_status = MemoryStatus.DORMANT if new_strength < 0.3 else self.status
        return replace(
            self,
            strength=new_strength,
            status=new_status,
        )

    # String representation
    def __str__(self) -> str:
        """Human-readable representation."""
        return (
            f"Memory({self.memory_id[:8]}..., "
            f"type={self.memory_type.value}, "
            f"strength={self.strength:.2f})"
        )


# =============================================================================
# Memory Query Result
# =============================================================================


@dataclass
class MemoryQueryResult:
    """Result of a memory query."""

    memory: MemoryEntry
    relevance_score: float  # 0.0 to 1.0
    retrieval_context: dict = field(default_factory=dict)
    match_reasons: tuple[str, ...] = field(default_factory=tuple)

    def __str__(self) -> str:
        return f"{self.memory.memory_id[:8]}... (relevance: {self.relevance_score:.2f})"


@dataclass
class MemoryQuery:
    """A query for memory retrieval."""

    query_text: str = ""
    memory_type: MemoryType | None = None
    content_types: tuple[ContentType, ...] = field(default_factory=tuple)
    related_to: str | None = None
    relationship_type: RelationshipType | None = None
    similar_to: str | None = None
    temporal_range: tuple[str, str] | None = None  # (start, end) ISO 8601
    context: dict = field(default_factory=dict)


# =============================================================================
# Memory Graph
# =============================================================================


@dataclass
class MemoryNode:
    """A node in the memory relationship graph."""

    memory_id: str
    memory_type: MemoryType
    centrality: float = 0.0  # Importance in the graph


@dataclass
class MemoryGraph:
    """Graph representation of memory relationships."""

    nodes: dict[str, MemoryNode] = field(default_factory=dict)
    edges: list[tuple[str, str, RelationshipType]] = field(default_factory=list)

    def add_memory(self, memory: MemoryEntry) -> None:
        """Add a memory to the graph."""
        self.nodes[memory.memory_id] = MemoryNode(
            memory_id=memory.memory_id,
            memory_type=memory.memory_type,
        )

        for rel in memory.relationships:
            self.edges.append((
                memory.memory_id,
                rel.target_id,
                rel.relationship_type,
            ))
            if rel.bidirectional:
                self.edges.append((
                    rel.target_id,
                    memory.memory_id,
                    rel.relationship_type,
                ))


# =============================================================================
# Memory Snapshot
# =============================================================================


@dataclass
class MemorySnapshot:
    """Point-in-time snapshot of memory state."""

    timestamp: str  # ISO 8601
    total_memories: int
    by_type: dict[str, int]
    by_status: dict[str, int]
    average_strength: float
    memories: tuple[MemoryEntry, ...]


# =============================================================================
# Memory Templates
# =============================================================================


class MemoryTemplates:
    """Predefined memory creation templates for clinical use."""

    @staticmethod
    def clinical_encounter(
        memory_id: str,
        patient_id: str,
        encounter_type: str,
        summary: str,
    ) -> MemoryEntry:
        """Template for clinical encounter memory."""
        return MemoryEntry.create(
            memory_id=memory_id,
            memory_type=MemoryType.EPISODIC,
            content=MemoryContent(
                type=ContentType.STRUCTURED,
                data={
                    "patient_id": patient_id,
                    "encounter_type": encounter_type,
                },
            ),
            summary=summary,
            tags=(patient_id, "clinical", "encounter"),
        )

    @staticmethod
    def device_diagnostic(
        memory_id: str,
        device_id: str,
        diagnostic_result: str,
    ) -> MemoryEntry:
        """Template for device diagnostic memory."""
        return MemoryEntry.create(
            memory_id=memory_id,
            memory_type=MemoryType.EPISODIC,
            content=MemoryContent(
                type=ContentType.STRUCTURED,
                data={
                    "device_id": device_id,
                    "result": diagnostic_result,
                },
            ),
            summary=f"Diagnostic: {device_id}",
            tags=(device_id, "diagnostic", "device"),
        )

    @staticmethod
    def procedure_outcome(
        memory_id: str,
        procedure: str,
        outcome: str,
        patient_id: str = "",
    ) -> MemoryEntry:
        """Template for procedure outcome memory."""
        tags = [procedure, "procedure", "outcome"]
        if patient_id:
            tags.append(patient_id)

        return MemoryEntry.create(
            memory_id=memory_id,
            memory_type=MemoryType.EPISODIC,
            content=MemoryContent(
                type=ContentType.OUTCOME,
                data={
                    "procedure": procedure,
                    "outcome": outcome,
                    "patient_id": patient_id,
                },
            ),
            summary=f"{procedure}: {outcome}",
            tags=tuple(tags),
        )

    @staticmethod
    def technical_knowledge(
        memory_id: str,
        topic: str,
        content: str,
    ) -> MemoryEntry:
        """Template for technical knowledge (semantic) memory."""
        return MemoryEntry.create(
            memory_id=memory_id,
            memory_type=MemoryType.SEMANTIC,
            content=MemoryContent(
                type=ContentType.TEXT,
                data=content,
            ),
            summary=topic,
            tags=(topic, "knowledge", "technical"),
        )

    @staticmethod
    def skill_procedure(
        memory_id: str,
        skill_name: str,
        procedure_steps: list[str],
    ) -> MemoryEntry:
        """Template for procedural (skill) memory."""
        return MemoryEntry.create(
            memory_id=memory_id,
            memory_type=MemoryType.PROCEDURAL,
            content=MemoryContent(
                type=ContentType.STRUCTURED,
                data={"steps": procedure_steps},
            ),
            summary=f"Procedure: {skill_name}",
            tags=(skill_name, "procedure", "skill"),
        )
