"""Cognitive Memory Engine.

The main engine that orchestrates all memory types and provides
the unified memory interface for EREN's cognitive system.

Architecture only — no AI, no storage backend.
"""

from __future__ import annotations

import threading
import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from .exceptions import (
    MemoryAlreadyExistsError,
    MemoryCapacityError,
    MemoryDecayError,
    MemoryNotFoundError,
    MemoryRetrievalError,
)
from .memory_models import MemoryEntry, MemoryQuery, MemoryQueryResult, MemoryTemplates
from .memory_stores import (
    LongTermMemoryStore,
    MemoryStore,
    ShortTermMemoryStore,
    WorkingMemoryStore,
    create_memory_store,
)
from .memory_types import (
    AccessPattern,
    ConsolidationContext,
    ContentType,
    MemoryAccess,
    MemoryContent,
    MemoryFilter,
    MemoryRelationship,
    MemoryStatus,
    MemoryType,
    RelationshipType,
    RetrievalContext,
    SearchOptions,
)

if TYPE_CHECKING:
    pass


class CognitiveMemoryEngine:
    """Main memory engine that orchestrates all memory types.

    The Cognitive Memory Engine implements a multi-store memory system
    inspired by human memory architecture:

    - Working Memory: Active processing, limited capacity
    - Short-Term Memory: Temporary storage, seconds to minutes
    - Long-Term Memory: Persistent storage, includes episodic, semantic, procedural

    Features:
    - Unified interface across all memory types
    - Automatic memory transfer (consolidation)
    - Memory decay and forgetting
    - Context-aware retrieval
    - Relationship tracking
    """

    def __init__(self) -> None:
        """Initialize the cognitive memory engine."""
        # Memory stores
        self._working_memory = WorkingMemoryStore(capacity=7)
        self._short_term_memory = ShortTermMemoryStore()
        self._long_term_memory = LongTermMemoryStore()

        # Additional specialized stores
        self._episodic_memory = create_memory_store(MemoryType.EPISODIC)
        self._semantic_memory = create_memory_store(MemoryType.SEMANTIC)
        self._procedural_memory = create_memory_store(MemoryType.PROCEDURAL)

        # Thread safety
        self._lock = threading.RLock()

        # Configuration
        self._decay_enabled = True
        self._consolidation_enabled = True

    # =======================================================================
    # Memory Storage Operations
    # =======================================================================

    def store(
        self,
        content: str | dict,
        memory_type: MemoryType,
        summary: str = "",
        tags: tuple[str, ...] = (),
        relationships: list[MemoryRelationship] | None = None,
        importance: int = 0,
        source: str = "",
    ) -> str:
        """Store a new memory.

        Args:
            content: The content to store (text or structured data)
            memory_type: Type of memory (working, short-term, long-term, etc.)
            summary: Brief summary for quick retrieval
            tags: Tags for categorization
            relationships: Links to other memories
            importance: User/AI assigned importance (0-10)
            source: Source of the memory

        Returns:
            The memory ID of the stored memory.
        """
        with self._lock:
            memory_id = self._generate_memory_id()

            # Determine content type
            if isinstance(content, dict):
                content_type = ContentType.STRUCTURED
            else:
                content_type = ContentType.TEXT

            # Create content
            memory_content = MemoryContent(
                type=content_type,
                data=content,
            )

            # Create memory entry
            memory = MemoryEntry.create(
                memory_id=memory_id,
                memory_type=memory_type,
                content=memory_content,
                summary=summary,
                tags=tags,
                source=source,
                importance=importance,
            )

            # Add relationships
            if relationships:
                memory = MemoryEntry(  # type: ignore
                    **{
                        **memory.__dict__,
                        "relationships": tuple(relationships),
                    }
                )

            # Store in appropriate store
            store = self._get_store(memory_type)
            store.store(memory)

            return memory_id

    def retrieve(self, memory_id: str, memory_type: MemoryType | None = None) -> MemoryEntry | None:
        """Retrieve a memory by ID.

        Args:
            memory_id: The memory ID to retrieve
            memory_type: Optional specific type to search (searches all if None)

        Returns:
            The memory entry if found, None otherwise.
        """
        with self._lock:
            # Try specified type first
            if memory_type:
                store = self._get_store(memory_type)
                memory = store.retrieve(memory_id)
                if memory:
                    self._record_access(memory, AccessPattern.RANDOM)
                return memory

            # Search all stores
            for store in self._get_all_stores():
                memory = store.retrieve(memory_id)
                if memory:
                    self._record_access(memory, AccessPattern.RANDOM)
                    return memory

            return None

    def update(
        self,
        memory_id: str,
        memory_type: MemoryType,
        updates: dict,
    ) -> MemoryEntry:
        """Update an existing memory.

        Args:
            memory_id: The memory ID to update
            memory_type: The type of memory
            updates: Dictionary of fields to update

        Returns:
            The updated memory entry.
        """
        with self._lock:
            store = self._get_store(memory_type)
            memory = store.retrieve(memory_id)

            if not memory:
                raise MemoryNotFoundError(memory_id)

            # Apply updates (create new immutable entry)
            from dataclasses import replace
            updated = replace(memory, **updates)

            store.update(updated)
            return updated

    def delete(self, memory_id: str, memory_type: MemoryType) -> bool:
        """Delete a memory.

        Args:
            memory_id: The memory ID to delete
            memory_type: The type of memory

        Returns:
            True if deleted, False if not found.
        """
        with self._lock:
            store = self._get_store(memory_type)
            return store.delete(memory_id)

    # =======================================================================
    # Memory Search Operations
    # =======================================================================

    def search(
        self,
        query: MemoryQuery,
        options: SearchOptions | None = None,
    ) -> list[MemoryQueryResult]:
        """Search memories across all types.

        Args:
            query: The search query
            options: Search options (pagination, filtering)

        Returns:
            List of matching memories with relevance scores.
        """
        with self._lock:
            all_results: list[MemoryQueryResult] = []

            # Search each store
            stores_to_search = self._get_all_stores()

            for store in stores_to_search:
                try:
                    results = store.search(query, options)
                    all_results.extend(results)
                except Exception:
                    pass

            # Sort by relevance
            all_results.sort(key=lambda r: r.relevance_score, reverse=True)

            # Apply limit
            if options and options.limit:
                all_results = all_results[:options.limit]

            return all_results

    def find_related(
        self,
        memory_id: str,
        relationship_type: RelationshipType | None = None,
    ) -> list[MemoryEntry]:
        """Find memories related to a given memory.

        Args:
            memory_id: The memory to find relations for
            relationship_type: Optional filter by relationship type

        Returns:
            List of related memories.
        """
        with self._lock:
            # Find the memory first
            memory = self.retrieve(memory_id)
            if not memory:
                return []

            # Get related IDs
            related_ids = memory.get_related_memories(relationship_type)

            # Retrieve related memories
            related: list[MemoryEntry] = []
            for rel_id in related_ids:
                rel_memory = self.retrieve(rel_id)
                if rel_memory:
                    related.append(rel_memory)

            return related

    def find_similar(
        self,
        memory_id: str,
        threshold: float = 0.7,
    ) -> list[MemoryEntry]:
        """Find memories similar to a given memory.

        Args:
            memory_id: The memory to find similarities for
            threshold: Minimum similarity threshold (0-1)

        Returns:
            List of similar memories.
        """
        with self._lock:
            similar: list[MemoryEntry] = []

            for store in self._get_all_stores():
                try:
                    results = store.find_similar(memory_id, threshold)
                    similar.extend(results)
                except Exception:
                    pass

            return similar[:10]  # Limit results

    # =======================================================================
    # Memory Lifecycle Operations
    # =======================================================================

    def consolidate(
        self,
        memory_id: str,
        target_type: MemoryType = MemoryType.LONG_TERM,
    ) -> list[MemoryEntry]:
        """Consolidate a memory to long-term storage.

        Args:
            memory_id: The memory to consolidate
            target_type: The target memory type

        Returns:
            List of affected memories (source and consolidated).
        """
        with self._lock:
            affected: list[MemoryEntry] = []

            # Find in current stores
            for store in self._get_all_stores():
                memory = store.retrieve(memory_id)
                if memory:
                    consolidated = store.consolidate(memory_id)
                    affected.extend(consolidated)

                    # Copy to target if different
                    if target_type != memory.memory_type:
                        target_store = self._get_store(target_type)
                        for mem in consolidated:
                            target_store.store(mem)

                    break

            return affected

    def strengthen(
        self,
        memory_id: str,
        amount: float = 0.1,
    ) -> MemoryEntry:
        """Strengthen a memory (e.g., after recall).

        Args:
            memory_id: The memory to strengthen
            amount: Amount to strengthen (0-1)

        Returns:
            The updated memory.
        """
        with self._lock:
            for store in self._get_all_stores():
                memory = store.retrieve(memory_id)
                if memory:
                    return store.strengthen(memory_id, amount)

            raise MemoryNotFoundError(memory_id)

    def decay(self, memory_id: str, elapsed_seconds: float) -> MemoryEntry:
        """Apply time-based decay to a memory.

        Args:
            memory_id: The memory to decay
            elapsed_seconds: Time elapsed since last access

        Returns:
            The updated memory with potentially reduced strength.
        """
        with self._lock:
            for store in self._get_all_stores():
                memory = store.retrieve(memory_id)
                if memory:
                    return store.decay(memory_id, elapsed_seconds)

            raise MemoryNotFoundError(memory_id)

    # =======================================================================
    # Memory Relationship Operations
    # =======================================================================

    def add_relationship(
        self,
        source_id: str,
        target_id: str,
        relationship_type: RelationshipType,
        strength: float = 1.0,
        bidirectional: bool = False,
    ) -> None:
        """Add a relationship between two memories.

        Args:
            source_id: The source memory ID
            target_id: The target memory ID
            relationship_type: Type of relationship
            strength: Relationship strength (0-1)
            bidirectional: Whether relationship is bidirectional
        """
        with self._lock:
            # Get source memory
            source = self.retrieve(source_id)
            if not source:
                raise MemoryNotFoundError(source_id)

            # Create relationship
            relationship = MemoryRelationship(
                target_id=target_id,
                relationship_type=relationship_type,
                strength=strength,
                bidirectional=bidirectional,
            )

            # Update source
            from dataclasses import replace
            updated = replace(
                source,
                relationships=source.relationships + (relationship,),
            )

            # Save back
            store = self._get_store(source.memory_type)
            store.update(updated)

    def remove_relationship(
        self,
        source_id: str,
        target_id: str,
    ) -> None:
        """Remove a relationship between two memories.

        Args:
            source_id: The source memory ID
            target_id: The target memory ID
        """
        with self._lock:
            source = self.retrieve(source_id)
            if not source:
                raise MemoryNotFoundError(source_id)

            # Filter out relationship
            new_relationships = tuple(
                r for r in source.relationships
                if r.target_id != target_id
            )

            from dataclasses import replace
            updated = replace(source, relationships=new_relationships)

            store = self._get_store(source.memory_type)
            store.update(updated)

    # =======================================================================
    # Context Operations
    # =======================================================================

    def store_with_context(
        self,
        content: str | dict,
        context: RetrievalContext,
        memory_type: MemoryType = MemoryType.SHORT_TERM,
        **kwargs,
    ) -> str:
        """Store a memory with contextual information.

        Args:
            content: The content to store
            context: The retrieval context
            memory_type: Type of memory
            **kwargs: Additional arguments for store()

        Returns:
            The memory ID.
        """
        # Add context tags
        tags = list(kwargs.get("tags", ()))
        if context.device_id:
            tags.append(f"device:{context.device_id}")
        if context.location:
            tags.append(f"location:{context.location}")
        if context.task:
            tags.append(f"task:{context.task}")

        kwargs["tags"] = tuple(tags)

        return self.store(content, memory_type, **kwargs)

    def retrieve_with_context(
        self,
        query: str,
        context: RetrievalContext,
    ) -> list[MemoryQueryResult]:
        """Retrieve memories matching context.

        Args:
            query: Search query
            context: The retrieval context

        Returns:
            List of matching memories with context relevance.
        """
        # Build query
        memory_query = MemoryQuery(
            query_text=query,
            context={
                "session_id": context.session_id,
                "user_id": context.user_id,
                "device_id": context.device_id,
                "location": context.location,
                "task": context.task,
            },
        )

        # Search
        results = self.search(memory_query)

        # Boost by context relevance
        for result in results:
            context_score = self._calculate_context_relevance(
                result.memory,
                context,
            )
            result.relevance_score = (
                result.relevance_score * 0.7 + context_score * 0.3
            )

        # Re-sort
        results.sort(key=lambda r: r.relevance_score, reverse=True)

        return results

    # =======================================================================
    # Statistics and Snapshot
    # =======================================================================

    def get_statistics(self) -> dict:
        """Get memory system statistics.

        Returns:
            Dictionary of statistics.
        """
        with self._lock:
            stats = {
                "working_memory": self._working_memory.get_statistics(),
                "short_term_memory": self._short_term_memory.get_statistics(),
                "long_term_memory": self._long_term_memory.get_statistics(),
            }

            # Add counts
            stats["total_memories"] = sum(
                s["count"] for s in stats.values()
            )

            return stats

    def snapshot(self) -> dict:
        """Create a snapshot of the memory system.

        Returns:
            Dictionary snapshot of current state.
        """
        with self._lock:
            return {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "statistics": self.get_statistics(),
                "decay_enabled": self._decay_enabled,
                "consolidation_enabled": self._consolidation_enabled,
            }

    # =======================================================================
    # Private Helper Methods
    # =======================================================================

    def _get_store(self, memory_type: MemoryType) -> MemoryStore:
        """Get the appropriate store for a memory type."""
        stores = {
            MemoryType.WORKING: self._working_memory,
            MemoryType.SHORT_TERM: self._short_term_memory,
            MemoryType.LONG_TERM: self._long_term_memory,
            MemoryType.EPISODIC: self._episodic_memory,
            MemoryType.SEMANTIC: self._semantic_memory,
            MemoryType.PROCEDURAL: self._procedural_memory,
        }

        store = stores.get(memory_type)
        if store:
            return store

        return self._long_term_memory  # Default

    def _get_all_stores(self) -> list[MemoryStore]:
        """Get all memory stores."""
        return [
            self._working_memory,
            self._short_term_memory,
            self._long_term_memory,
            self._episodic_memory,
            self._semantic_memory,
            self._procedural_memory,
        ]

    def _generate_memory_id(self) -> str:
        """Generate a unique memory ID."""
        return f"mem_{uuid.uuid4().hex[:16]}"

    def _record_access(
        self,
        memory: MemoryEntry,
        pattern: AccessPattern,
    ) -> None:
        """Record a memory access."""
        access = MemoryAccess(
            timestamp=datetime.now(timezone.utc).isoformat(),
            pattern=pattern,
            retrieval_mode="recall",
        )
        # Access is recorded in the memory's metadata

    def _calculate_context_relevance(
        self,
        memory: MemoryEntry,
        context: RetrievalContext,
    ) -> float:
        """Calculate context-based relevance score."""
        score = 0.5  # Base score

        # Check tags for context match
        for tag in memory.metadata.tags:
            if context.device_id and f"device:{context.device_id}" == tag:
                score += 0.2
            if context.location and f"location:{context.location}" == tag:
                score += 0.2
            if context.task and f"task:{context.task}" == tag:
                score += 0.1

        return min(1.0, score)
