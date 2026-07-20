"""Memory selector for EREN OS Cognitive Memory Orchestrator.

Implements various selection strategies for choosing memories.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from core.memory.base import BaseMemoryInterface
from core.memory.registry import MemoryRegistry
from core.memory.types import (
    MemoryAccessPolicy,
    MemoryType,
)

if TYPE_CHECKING:
    pass


class MemorySelector:
    """Selects memories based on various policies.

    The Orchestrator uses this to decide which memories to use for
    read/write operations.
    """

    def __init__(
        self,
        registry: MemoryRegistry,
        default_memory_id: str | None = None,
    ):
        """Initialize selector.

        Args:
            registry: Memory registry.
            default_memory_id: Default memory to use.
        """
        self._registry = registry
        self._default_memory_id = default_memory_id
        self._policy: MemoryAccessPolicy = MemoryAccessPolicy.FIRST_AVAILABLE

    @property
    def policy(self) -> MemoryAccessPolicy:
        """Get current selection policy."""
        return self._policy

    @policy.setter
    def policy(self, policy: MemoryAccessPolicy) -> None:
        """Set selection policy."""
        self._policy = policy

    @property
    def default_memory_id(self) -> str | None:
        """Get default memory ID."""
        return self._default_memory_id

    @default_memory_id.setter
    def default_memory_id(self, memory_id: str | None) -> None:
        """Set default memory ID."""
        self._default_memory_id = memory_id

    def select_for_read(
        self,
        memory_types: list[MemoryType] | None = None,
    ) -> list[BaseMemoryInterface]:
        """Select memories for read operation.

        Args:
            memory_types: Optional memory type filter.

        Returns:
            List of selected memories.
        """
        memories = self._get_eligible_memories(memory_types)

        if not memories:
            return []

        if self._policy == MemoryAccessPolicy.FIRST_AVAILABLE:
            return [self._select_first(memories)]
        elif self._policy == MemoryAccessPolicy.LONG_TERM_ONLY:
            return self._select_long_term(memories)
        elif self._policy == MemoryAccessPolicy.SHORT_TERM_ONLY:
            return self._select_short_term(memories)
        elif self._policy == MemoryAccessPolicy.MERGE_ALL:
            return memories
        elif self._policy == MemoryAccessPolicy.CACHE_FIRST:
            return self._select_cache_first(memories)
        else:
            return [self._select_first(memories)]

    def select_for_write(
        self,
        memory_types: list[MemoryType] | None = None,
    ) -> list[BaseMemoryInterface]:
        """Select memories for write operation.

        Args:
            memory_types: Optional memory type filter.

        Returns:
            List of selected memories.
        """
        memories = self._get_eligible_memories(memory_types)

        if not memories:
            return []

        if self._policy == MemoryAccessPolicy.READ_ONLY:
            return []
        elif self._policy == MemoryAccessPolicy.WRITE_THROUGH:
            return memories
        elif self._policy == MemoryAccessPolicy.LONG_TERM_ONLY:
            return self._select_long_term(memories)
        elif self._policy == MemoryAccessPolicy.SHORT_TERM_ONLY:
            return self._select_short_term(memories)
        else:
            return [self._select_first(memories)]

    def select_for_search(
        self,
        memory_types: list[MemoryType] | None = None,
    ) -> list[BaseMemoryInterface]:
        """Select memories for search operation.

        Args:
            memory_types: Optional memory type filter.

        Returns:
            List of selected memories.
        """
        return self.select_for_read(memory_types)

    def _get_eligible_memories(
        self,
        memory_types: list[MemoryType] | None,
    ) -> list[BaseMemoryInterface]:
        """Get eligible memories.

        Args:
            memory_types: Optional memory type filter.

        Returns:
            List of eligible memories.
        """
        memories = self._registry.list_ready()

        if memory_types:
            memories = [m for m in memories if m.memory_type in memory_types]

        return memories

    def _select_first(
        self,
        memories: list[BaseMemoryInterface],
    ) -> BaseMemoryInterface | None:
        """Select first memory.

        Args:
            memories: Eligible memories.

        Returns:
            First memory or None.
        """
        if not memories:
            return None

        # Try default first
        if self._default_memory_id:
            for m in memories:
                if m.memory_id == self._default_memory_id:
                    return m

        return memories[0]

    def _select_long_term(
        self,
        memories: list[BaseMemoryInterface],
    ) -> list[BaseMemoryInterface]:
        """Select long-term memories.

        Args:
            memories: Eligible memories.

        Returns:
            Long-term memories.
        """
        return [
            m for m in memories
            if MemoryType.is_long_term(m.memory_type)
        ]

    def _select_short_term(
        self,
        memories: list[BaseMemoryInterface],
    ) -> list[BaseMemoryInterface]:
        """Select short-term memories.

        Args:
            memories: Eligible memories.

        Returns:
            Short-term memories.
        """
        return [
            m for m in memories
            if MemoryType.is_short_term(m.memory_type)
        ]

    def _select_cache_first(
        self,
        memories: list[BaseMemoryInterface],
    ) -> list[BaseMemoryInterface]:
        """Select cache memories first.

        Args:
            memories: Eligible memories.

        Returns:
            Cache memories first.
        """
        cache_memories = [m for m in memories if m.memory_type == MemoryType.WORKING]
        other_memories = [m for m in memories if m.memory_type != MemoryType.WORKING]
        return cache_memories + other_memories
