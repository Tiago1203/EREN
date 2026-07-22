"""Memory stores for different memory types.

Each memory store implements the behavior of a specific memory type,
inspired by cognitive psychology research.

Architecture only — no business logic, no AI.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from .memory_models import MemoryEntry, MemoryQuery, MemoryQueryResult
from .memory_types import (
    ConsolidationPolicy,
    IndexingPolicy,
    MemoryStatus,
    MemoryType,
    RetentionPolicy,
    RetrievalMode,
    RetrievalPolicy,
    SearchOptions,
)

if TYPE_CHECKING:
    pass


# =============================================================================
# Base Memory Store
# =============================================================================


class MemoryStore(ABC):
    """Abstract base class for memory stores.

    Each memory type has a specialized store that implements
    its unique characteristics and policies.
    """

    def __init__(
        self,
        memory_type: MemoryType,
        retention_policy: RetentionPolicy,
        indexing_policy: IndexingPolicy,
        retrieval_policy: RetrievalPolicy,
        consolidation_policy: ConsolidationPolicy | None = None,
    ) -> None:
        self._memory_type = memory_type
        self._retention_policy = retention_policy
        self._indexing_policy = indexing_policy
        self._retrieval_policy = retrieval_policy
        self._consolidation_policy = consolidation_policy

        # Internal storage
        self._memories: dict[str, MemoryEntry] = {}
        self._index: dict[str, set[str]] = {}  # keyword -> memory_ids

    @property
    def memory_type(self) -> MemoryType:
        """Get the memory type."""
        return self._memory_type

    # =======================================================================
    # Storage Operations
    # =======================================================================

    @abstractmethod
    def store(self, memory: MemoryEntry) -> None:
        """Store a memory entry."""
        ...

    @abstractmethod
    def retrieve(self, memory_id: str) -> MemoryEntry | None:
        """Retrieve a memory by ID."""
        ...

    @abstractmethod
    def update(self, memory: MemoryEntry) -> None:
        """Update a memory entry."""
        ...

    @abstractmethod
    def delete(self, memory_id: str) -> bool:
        """Delete a memory entry."""
        ...

    # =======================================================================
    # Query Operations
    # =======================================================================

    @abstractmethod
    def search(
        self,
        query: MemoryQuery,
        options: SearchOptions | None = None,
    ) -> list[MemoryQueryResult]:
        """Search for memories matching the query."""
        ...

    @abstractmethod
    def find_similar(
        self,
        memory_id: str,
        threshold: float = 0.7,
    ) -> list[MemoryEntry]:
        """Find memories similar to the given one."""
        ...

    # =======================================================================
    # Lifecycle Operations
    # =======================================================================

    @abstractmethod
    def consolidate(self, memory_id: str) -> list[MemoryEntry]:
        """Consolidate memory to long-term storage."""
        ...

    @abstractmethod
    def decay(self, memory_id: str, elapsed_seconds: float) -> MemoryEntry:
        """Apply time-based decay to a memory."""
        ...

    @abstractmethod
    def strengthen(self, memory_id: str, amount: float) -> MemoryEntry:
        """Strengthen a memory (e.g., after recall)."""
        ...

    # =======================================================================
    # Utility Methods
    # =======================================================================

    def count(self) -> int:
        """Get the number of stored memories."""
        return len(self._memories)

    def list_all(self) -> list[MemoryEntry]:
        """List all memories in this store."""
        return list(self._memories.values())

    def get_statistics(self) -> dict:
        """Get statistics about this store."""
        return {
            "type": self._memory_type.value,
            "count": len(self._memories),
            "avg_strength": (
                sum(m.strength for m in self._memories.values()) / len(self._memories)
                if self._memories else 0
            ),
        }


# =============================================================================
# Working Memory Store
# =============================================================================


@dataclass
class WorkingMemorySlot:
    """A slot in working memory (limited capacity)."""

    memory_id: str
    content: str
    created_at: str
    last_accessed: str
    access_count: int = 0


class WorkingMemoryStore(MemoryStore):
    """Working memory store.

    Working memory has limited capacity (~7 items) and holds
    information currently being processed. Inspired by Baddeley's
    model of working memory.
    """

    DEFAULT_CAPACITY: int = 7

    def __init__(
        self,
        capacity: int = DEFAULT_CAPACITY,
    ) -> None:
        super().__init__(
            memory_type=MemoryType.WORKING,
            retention_policy=RetentionPolicy(
                memory_type=MemoryType.WORKING,
                min_duration_seconds=0,
                max_duration_seconds=60,  # ~1 minute
                decay_rate=0.1,
                consolidation_threshold=0.8,
                forget_threshold=0.1,
            ),
            indexing_policy=IndexingPolicy(
                memory_type=MemoryType.WORKING,
                index_keywords=False,
                index_entities=False,
            ),
            retrieval_policy=RetrievalPolicy(
                memory_type=MemoryType.WORKING,
                retrieval_mode=RetrievalMode.RECALL,
                max_results=5,
            ),
        )
        self._capacity = capacity
        self._slots: list[WorkingMemorySlot] = []
        self._central_executor: str | None = None  # Phonological loop, visuospatial sketchpad

    def store(self, memory: MemoryEntry) -> None:
        """Store in working memory (limited slots)."""
        if len(self._slots) >= self._capacity:
            # Remove oldest/first item
            self._slots.pop(0)

        slot = WorkingMemorySlot(
            memory_id=memory.memory_id,
            content=memory.summary or str(memory.content.data)[:50],
            created_at=memory.metadata.created_at,
            last_accessed=datetime.now(UTC).isoformat(),
        )
        self._slots.append(slot)
        self._memories[memory.memory_id] = memory

    def retrieve(self, memory_id: str) -> MemoryEntry | None:
        """Retrieve and update access time."""
        memory = self._memories.get(memory_id)
        if memory:
            # Update slot access
            for slot in self._slots:
                if slot.memory_id == memory_id:
                    slot.last_accessed = datetime.now(UTC).isoformat()
                    slot.access_count += 1
                    break
        return memory

    def update(self, memory: MemoryEntry) -> None:
        """Update working memory entry."""
        self._memories[memory.memory_id] = memory

    def delete(self, memory_id: str) -> bool:
        """Delete from working memory."""
        if memory_id in self._memories:
            del self._memories[memory_id]
            self._slots = [s for s in self._slots if s.memory_id != memory_id]
            return True
        return False

    def search(
        self,
        query: MemoryQuery,
        options: SearchOptions | None = None,
    ) -> list[MemoryQueryResult]:
        """Working memory search (sequential through slots)."""
        results: list[MemoryQueryResult] = []

        for memory in self._memories.values():
            if query.query_text:
                if query.query_text.lower() in str(memory.content.data).lower():
                    results.append(MemoryQueryResult(
                        memory=memory,
                        relevance_score=1.0,
                        match_reasons=("keyword_match",),
                    ))
            else:
                results.append(MemoryQueryResult(
                    memory=memory,
                    relevance_score=0.5,
                    match_reasons=("working_memory",),
                ))

        return results[:self._retrieval_policy.max_results]

    def find_similar(self, memory_id: str, threshold: float = 0.7) -> list[MemoryEntry]:
        """Working memory doesn't support similarity (limited items)."""
        return []

    def consolidate(self, memory_id: str) -> list[MemoryEntry]:
        """Working memory doesn't consolidate."""
        return []

    def decay(self, memory_id: str, elapsed_seconds: float) -> MemoryEntry:
        """Apply rapid decay to working memory."""
        if memory_id not in self._memories:
            raise ValueError(f"Memory {memory_id} not found")

        memory = self._memories[memory_id]
        new_strength = self._retention_policy.calculate_decay(
            elapsed_seconds,
            memory.strength,
        )

        if new_strength <= 0:
            # Forgot this memory
            return memory.model_copy(
                update={
                    "strength": 0,
                    "status": MemoryStatus.FORGOTTEN,
                }
            )

        return memory.weaken(memory.strength - new_strength)

    def strengthen(self, memory_id: str, amount: float) -> MemoryEntry:
        """Strengthen working memory (refresh)."""
        if memory_id not in self._memories:
            raise ValueError(f"Memory {memory_id} not found")

        memory = self._memories[memory_id]

        # Refresh moves to end of slots
        self._slots = [s for s in self._slots if s.memory_id != memory_id]

        return memory.strengthen(amount)


# =============================================================================
# Short-Term Memory Store
# =============================================================================


class ShortTermMemoryStore(MemoryStore):
    """Short-term memory store.

    Short-term memory holds information for seconds to minutes.
    Inspired by Atkinson-Shiffrin model.
    """

    def __init__(self) -> None:
        super().__init__(
            memory_type=MemoryType.SHORT_TERM,
            retention_policy=RetentionPolicy(
                memory_type=MemoryType.SHORT_TERM,
                min_duration_seconds=30,
                max_duration_seconds=300,  # 5 minutes
                decay_rate=0.05,
                consolidation_threshold=0.6,
                forget_threshold=0.2,
            ),
            indexing_policy=IndexingPolicy(
                memory_type=MemoryType.SHORT_TERM,
                index_keywords=True,
                index_entities=True,
            ),
            retrieval_policy=RetrievalPolicy(
                memory_type=MemoryType.SHORT_TERM,
                retrieval_mode=RetrievalMode.RECALL,
                max_results=10,
            ),
            consolidation_policy=ConsolidationPolicy(
                trigger_on_access_count=3,
            ),
        )

    def store(self, memory: MemoryEntry) -> None:
        """Store in short-term memory."""
        self._memories[memory.memory_id] = memory
        self._index_memory(memory)

    def retrieve(self, memory_id: str) -> MemoryEntry | None:
        """Retrieve from short-term memory."""
        return self._memories.get(memory_id)

    def update(self, memory: MemoryEntry) -> None:
        """Update short-term memory entry."""
        self._memories[memory.memory_id] = memory

    def delete(self, memory_id: str) -> bool:
        """Delete from short-term memory."""
        if memory_id in self._memories:
            memory = self._memories[memory_id]
            self._unindex_memory(memory)
            del self._memories[memory_id]
            return True
        return False

    def search(
        self,
        query: MemoryQuery,
        options: SearchOptions | None = None,
    ) -> list[MemoryQueryResult]:
        """Search short-term memory."""
        results: list[MemoryQueryResult] = []

        for memory in self._memories.values():
            score = self._calculate_relevance(memory, query)
            if score >= self._retrieval_policy.min_relevance:
                results.append(MemoryQueryResult(
                    memory=memory,
                    relevance_score=score,
                    match_reasons=self._get_match_reasons(memory, query),
                ))

        results.sort(key=lambda r: r.relevance_score, reverse=True)
        return results[:self._retrieval_policy.max_results]

    def find_similar(self, memory_id: str, threshold: float = 0.7) -> list[MemoryEntry]:
        """Find similar memories based on keywords."""
        if memory_id not in self._memories:
            return []

        target = self._memories[memory_id]
        similar: list[tuple[MemoryEntry, float]] = []

        target_keywords = self._extract_keywords(target)

        for memory in self._memories.values():
            if memory.memory_id == memory_id:
                continue

            memory_keywords = self._extract_keywords(memory)
            similarity = self._calculate_keyword_similarity(
                target_keywords,
                memory_keywords,
            )

            if similarity >= threshold:
                similar.append((memory, similarity))

        similar.sort(key=lambda x: x[1], reverse=True)
        return [m[0] for m in similar]

    def consolidate(self, memory_id: str) -> list[MemoryEntry]:
        """Prepare memory for consolidation to long-term."""
        if memory_id not in self._memories:
            return []

        memory = self._memories[memory_id]

        # Check if should consolidate
        if not self._retention_policy.should_consolidate(memory.strength):
            return []

        # Return memory with updated status
        updated = memory.model_copy(
            update={
                "status": MemoryStatus.CONSOLIDATING,
            }
        )
        self._memories[memory_id] = updated

        return [updated]

    def decay(self, memory_id: str, elapsed_seconds: float) -> MemoryEntry:
        """Apply decay to short-term memory."""
        if memory_id not in self._memories:
            raise ValueError(f"Memory {memory_id} not found")

        memory = self._memories[memory_id]
        new_strength = self._retention_policy.calculate_decay(
            elapsed_seconds,
            memory.strength,
        )

        if self._retention_policy.should_forget(new_strength):
            return memory.model_copy(
                update={
                    "strength": 0,
                    "status": MemoryStatus.FORGOTTEN,
                }
            )

        return memory.weaken(memory.strength - new_strength)

    def strengthen(self, memory_id: str, amount: float) -> MemoryEntry:
        """Strengthen short-term memory."""
        if memory_id not in self._memories:
            raise ValueError(f"Memory {memory_id} not found")

        memory = self._memories[memory_id]
        return memory.strengthen(amount)

    # Helper methods
    def _index_memory(self, memory: MemoryEntry) -> None:
        """Index memory for search."""
        keywords = self._extract_keywords(memory)
        for keyword in keywords:
            if keyword not in self._index:
                self._index[keyword] = set()
            self._index[keyword].add(memory.memory_id)

    def _unindex_memory(self, memory: MemoryEntry) -> None:
        """Remove memory from index."""
        keywords = self._extract_keywords(memory)
        for keyword in keywords:
            if keyword in self._index:
                self._index[keyword].discard(memory.memory_id)

    def _extract_keywords(self, memory: MemoryEntry) -> set[str]:
        """Extract keywords from memory."""
        text = str(memory.content.data).lower()
        # Simple tokenization
        words = set(text.split())
        return {w for w in words if len(w) > 3}

    def _calculate_keyword_similarity(
        self,
        keywords1: set[str],
        keywords2: set[str],
    ) -> float:
        """Calculate Jaccard similarity between keyword sets."""
        if not keywords1 or not keywords2:
            return 0.0
        intersection = len(keywords1 & keywords2)
        union = len(keywords1 | keywords2)
        return intersection / union if union > 0 else 0.0

    def _calculate_relevance(self, memory: MemoryEntry, query: MemoryQuery) -> float:
        """Calculate relevance score for memory-query pair."""
        score = 0.0

        if query.query_text:
            keywords = self._extract_keywords(memory)
            query_keywords = set(query.query_text.lower().split())
            if query_keywords & keywords:
                score += 0.5
            if query.query_text.lower() in str(memory.content.data).lower():
                score += 0.5

        score *= memory.strength

        return min(1.0, score)

    def _get_match_reasons(self, memory: MemoryEntry, query: MemoryQuery) -> tuple[str, ...]:
        """Get reasons why memory matches query."""
        reasons = []
        if query.query_text:
            if query.query_text.lower() in str(memory.content.data).lower():
                reasons.append("content_match")
        return tuple(reasons)


# =============================================================================
# Long-Term Memory Store (Base)
# =============================================================================


class LongTermMemoryStore(MemoryStore):
    """Long-term memory store.

    Long-term memory has large capacity and holds information
    for extended periods. Memories can be episodic, semantic,
    or procedural.
    """

    def __init__(self) -> None:
        super().__init__(
            memory_type=MemoryType.LONG_TERM,
            retention_policy=RetentionPolicy(
                memory_type=MemoryType.LONG_TERM,
                min_duration_seconds=86400,  # 1 day minimum
                max_duration_seconds=31536000,  # 1 year
                decay_rate=0.001,
                consolidation_threshold=0.9,
                forget_threshold=0.05,
            ),
            indexing_policy=IndexingPolicy(
                memory_type=MemoryType.LONG_TERM,
                index_keywords=True,
                index_entities=True,
                index_concepts=True,
                index_relationships=True,
                index_temporal=True,
                index_spatial=True,
                index_emotional=True,
            ),
            retrieval_policy=RetrievalPolicy(
                memory_type=MemoryType.LONG_TERM,
                retrieval_mode=RetrievalMode.ASSOCIATION,
                max_results=20,
                include_context=True,
                include_relationships=True,
            ),
        )

        # Additional indexes for LTM
        self._by_entity: dict[str, set[str]] = {}  # entity -> memory_ids
        self._by_concept: dict[str, set[str]] = {}  # concept -> memory_ids
        self._by_temporal: list[tuple[str, str]] = []  # (timestamp, memory_id)

    def store(self, memory: MemoryEntry) -> None:
        """Store in long-term memory with full indexing."""
        self._memories[memory.memory_id] = memory
        self._index_memory(memory)

    def retrieve(self, memory_id: str) -> MemoryEntry | None:
        """Retrieve from long-term memory."""
        memory = self._memories.get(memory_id)
        if memory:
            # Strengthen on retrieval
            self._memories[memory_id] = memory.strengthen(0.05)
        return self._memories.get(memory_id)

    def update(self, memory: MemoryEntry) -> None:
        """Update long-term memory."""
        self._memories[memory.memory_id] = memory

    def delete(self, memory_id: str) -> bool:
        """Delete from long-term memory."""
        if memory_id in self._memories:
            memory = self._memories[memory_id]
            self._unindex_memory(memory)
            del self._memories[memory_id]
            return True
        return False

    def search(
        self,
        query: MemoryQuery,
        options: SearchOptions | None = None,
    ) -> list[MemoryQueryResult]:
        """Long-term memory search with association."""
        results: list[MemoryQueryResult] = []

        for memory in self._memories.values():
            score = self._calculate_relevance(memory, query)
            if score >= self._retrieval_policy.min_relevance:
                results.append(MemoryQueryResult(
                    memory=memory,
                    relevance_score=score,
                    retrieval_context=self._build_context(memory),
                    match_reasons=self._get_match_reasons(memory, query),
                ))

        results.sort(key=lambda r: r.relevance_score, reverse=True)
        return results[:self._retrieval_policy.max_results]

    def find_similar(self, memory_id: str, threshold: float = 0.7) -> list[MemoryEntry]:
        """Find similar memories using multiple signals."""
        if memory_id not in self._memories:
            return []

        target = self._memories[memory_id]
        similar: list[tuple[MemoryEntry, float]] = []

        for memory in self._memories.values():
            if memory.memory_id == memory_id:
                continue

            similarity = self._calculate_similarity(target, memory)
            if similarity >= threshold:
                similar.append((memory, similarity))

        similar.sort(key=lambda x: x[1], reverse=True)
        return [m[0] for m in similar]

    def consolidate(self, memory_id: str) -> list[MemoryEntry]:
        """Consolidate memory (typically from STM)."""
        return []

    def decay(self, memory_id: str, elapsed_seconds: float) -> MemoryEntry:
        """Apply very slow decay to long-term memory."""
        if memory_id not in self._memories:
            raise ValueError(f"Memory {memory_id} not found")

        memory = self._memories[memory_id]
        new_strength = self._retention_policy.calculate_decay(
            elapsed_seconds,
            memory.strength,
        )

        return memory.model_copy(update={"strength": new_strength})

    def strengthen(self, memory_id: str, amount: float) -> MemoryEntry:
        """Strengthen long-term memory (rehearsal)."""
        if memory_id not in self._memories:
            raise ValueError(f"Memory {memory_id} not found")

        memory = self._memories[memory_id]
        return memory.strengthen(amount)

    # LTM-specific methods
    def _index_memory(self, memory: MemoryEntry) -> None:
        """Index memory with LTM-specific indexes."""
        # Basic keyword indexing
        text = str(memory.content.data).lower()
        keywords = set(text.split())
        for keyword in keywords:
            if len(keyword) > 3:
                if keyword not in self._index:
                    self._index[keyword] = set()
                self._index[keyword].add(memory.memory_id)

        # Tags
        for tag in memory.metadata.tags:
            if tag not in self._index:
                self._index[tag] = set()
            self._index[tag].add(memory.memory_id)

        # Temporal index
        self._by_temporal.append((memory.metadata.created_at, memory.memory_id))
        self._by_temporal.sort()

    def _unindex_memory(self, memory: MemoryEntry) -> None:
        """Remove memory from all indexes."""
        for keywords in self._index.values():
            keywords.discard(memory.memory_id)

        self._by_temporal = [
            (t, m) for t, m in self._by_temporal
            if m != memory.memory_id
        ]

    def _calculate_similarity(
        self,
        memory1: MemoryEntry,
        memory2: MemoryEntry,
    ) -> float:
        """Calculate multi-dimensional similarity."""
        scores: list[float] = []

        # Content similarity
        text1 = str(memory1.content.data).lower()
        text2 = str(memory2.content.data).lower()
        common = set(text1.split()) & set(text2.split())
        union = set(text1.split()) | set(text2.split())
        if union:
            scores.append(len(common) / len(union))

        # Tag similarity
        if memory1.metadata.tags and memory2.metadata.tags:
            common_tags = set(memory1.metadata.tags) & set(memory2.metadata.tags)
            union_tags = set(memory1.metadata.tags) | set(memory2.metadata.tags)
            if union_tags:
                scores.append(len(common_tags) / len(union_tags))

        # Relationship similarity
        rel1 = {r.target_id for r in memory1.relationships}
        rel2 = {r.target_id for r in memory2.relationships}
        if rel1 and rel2:
            common_rel = rel1 & rel2
            union_rel = rel1 | rel2
            scores.append(len(common_rel) / len(union_rel))

        return sum(scores) / len(scores) if scores else 0.0

    def _calculate_relevance(self, memory: MemoryEntry, query: MemoryQuery) -> float:
        """Calculate relevance for LTM retrieval."""
        score = 0.0

        # Content match
        if query.query_text:
            text = str(memory.content.data).lower()
            if query.query_text.lower() in text:
                score += 0.4

        # Tag match
        if query.query_text:
            for tag in memory.metadata.tags:
                if query.query_text.lower() in tag.lower():
                    score += 0.3
                    break

        # Strength (accessibility)
        score += memory.strength * 0.2

        # Recency
        recency = self._calculate_recency(memory)
        score += recency * 0.1

        return min(1.0, score)

    def _calculate_recency(self, memory: MemoryEntry) -> float:
        """Calculate recency score (0-1)."""
        if not memory.metadata.last_accessed_at:
            return 0.0

        try:
            last = datetime.fromisoformat(memory.metadata.last_accessed_at)
            now = datetime.now(UTC)
            hours_ago = (now - last).total_seconds() / 3600

            if hours_ago < 1:
                return 1.0
            elif hours_ago < 24:
                return 0.8
            elif hours_ago < 168:  # 1 week
                return 0.5
            else:
                return 0.2
        except Exception:
            return 0.0

    def _build_context(self, memory: MemoryEntry) -> dict:
        """Build retrieval context for memory."""
        return {
            "related_count": len(memory.relationships),
            "strength_level": memory.get_strength_level().name,
            "access_count": memory.metadata.access_count,
        }

    def _get_match_reasons(self, memory: MemoryEntry, query: MemoryQuery) -> tuple[str, ...]:
        """Get match reasons."""
        reasons = []
        if query.query_text:
            text = str(memory.content.data).lower()
            if query.query_text.lower() in text:
                reasons.append("content_match")
            for tag in memory.metadata.tags:
                if query.query_text.lower() in tag.lower():
                    reasons.append("tag_match")
                    break
        return tuple(reasons)


# =============================================================================
# Factory
# =============================================================================


def create_memory_store(memory_type: MemoryType) -> MemoryStore:
    """Factory function to create memory stores by type."""
    stores = {
        MemoryType.WORKING: WorkingMemoryStore,
        MemoryType.SHORT_TERM: ShortTermMemoryStore,
        MemoryType.LONG_TERM: LongTermMemoryStore,
        MemoryType.EPISODIC: LongTermMemoryStore,  # Uses LTM store
        MemoryType.SEMANTIC: LongTermMemoryStore,
        MemoryType.PROCEDURAL: LongTermMemoryStore,
        MemoryType.TEMPORAL: LongTermMemoryStore,
        MemoryType.SPATIAL: LongTermMemoryStore,
    }

    store_class = stores.get(memory_type, LongTermMemoryStore)
    return store_class()
