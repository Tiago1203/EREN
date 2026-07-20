"""
Memory Context Provider.

Provides memory context for the AI.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .base import BaseContextProvider, ContextItem, ContextQuery

if TYPE_CHECKING:
    from core.ai.memory import MemoryManager


class MemoryContextProvider(BaseContextProvider):
    """
    Provides memory context for the AI.
    
    Retrieves relevant memories from short-term and long-term memory.
    """
    
    def __init__(
        self,
        memory_manager: MemoryManager | None = None,
    ):
        self._memory = memory_manager
    
    @property
    def name(self) -> str:
        return "memory"
    
    @property
    def priority(self) -> int:
        return 15  # Critical priority
    
    async def get_context(
        self,
        query: ContextQuery,
    ) -> list[ContextItem]:
        """Get memory context."""
        items = []
        
        if not query.query:
            return items
        
        # Search relevant memories
        memories = await self._search_safe(query.query, query.user_id)
        
        for memory in memories[:5]:
            items.append(self._memory_to_context(memory))
        
        return items
    
    async def _search_safe(self, search_query: str, user_id: str) -> list[dict]:
        """Safely search memories."""
        if self._memory is None:
            return self._mock_search(search_query)
        try:
            results = await self._memory.search(
                query=search_query,
                user_id=user_id,
            )
            return [
                {
                    "id": r.id if hasattr(r, 'id') else str(r),
                    "content": r.content if hasattr(r, 'content') else str(r),
                    "memory_type": r.memory_type if hasattr(r, 'memory_type') else "unknown",
                }
                for r in results
            ]
        except Exception:
            return []
    
    def _memory_to_context(self, memory: dict) -> ContextItem:
        """Convert memory to ContextItem."""
        return self._create_item(
            content=f"Previous context ({memory.get('memory_type', 'memory')}): {memory['content']}",
            relevance_score=0.85,
            metadata={"type": "memory", "memory_id": memory.get("id")},
        )
    
    def _mock_search(self, query: str) -> list[dict]:
        """Mock search for testing."""
        return [
            {
                "id": "mem-001",
                "content": f"User previously asked about {query}. We discussed maintenance schedules.",
                "memory_type": "semantic",
            },
        ]
