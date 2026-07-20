"""
Base Context Provider.

Abstract base class for all context providers.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

import asyncio


@dataclass(frozen=True)
class ContextItem:
    """
    A piece of context for the AI.
    
    Attributes:
        source: Provider name that generated this item
        content: The context content
        relevance_score: Score from 0.0 to 1.0 indicating relevance
        metadata: Additional metadata about the context
    """
    source: str
    content: str
    relevance_score: float
    metadata: dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self) -> None:
        if not 0.0 <= self.relevance_score <= 1.0:
            raise ValueError("relevance_score must be between 0.0 and 1.0")


@dataclass
class ContextQuery:
    """
    Query parameters for context building.
    
    Attributes:
        conversation_id: Current conversation ID
        user_id: User making the request
        tenant_id: Tenant/Organization ID
        max_items: Maximum number of context items to return
        max_tokens: Maximum tokens to use for context
        sources: Filter by specific sources (None = all)
        query: Original user query for relevance matching
    """
    conversation_id: str
    user_id: str
    tenant_id: str
    max_items: int = 50
    max_tokens: int = 4096
    sources: list[str] | None = None
    query: str = ""


class BaseContextProvider(ABC):
    """
    Base class for all context providers.
    
    Each provider is responsible for gathering context
    from a specific domain or source.
    
    Providers are executed in order of priority (lower = higher priority).
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """
        Provider name for identification.
        
        This name is used to:
        - Identify the source in ContextItems
        - Filter providers in ContextQuery.sources
        """
        raise NotImplementedError
    
    @property
    def priority(self) -> int:
        """
        Provider priority (lower = higher priority).
        
        Default priority is 100. Providers with lower numbers
        are executed first.
        
        Priority ranges:
        - 1-20: Critical (conversation, session)
        - 21-40: High (memory, devices)
        - 41-60: Medium (incidents, knowledge)
        - 61-80: Low (recommendations, capacity)
        - 81-100: Background (history, analytics)
        """
        return 100
    
    @property
    def timeout(self) -> float:
        """
        Timeout for provider execution in seconds.
        
        If execution takes longer than this, the provider
        will return an empty list.
        """
        return 5.0
    
    @abstractmethod
    async def get_context(
        self,
        query: ContextQuery,
    ) -> list[ContextItem]:
        """
        Get context items for the given query.
        
        Returns list of ContextItem ordered by relevance (highest first).
        
        Args:
            query: Context query with parameters
            
        Returns:
            List of ContextItem sorted by relevance_score descending
        """
        raise NotImplementedError
    
    async def _fetch_with_timeout(
        self,
        coroutine,
    ) -> list[ContextItem]:
        """
        Fetch context with timeout to prevent hanging.
        
        Args:
            coroutine: The async operation to execute
            
        Returns:
            Context items if successful, empty list on timeout
        """
        try:
            return await asyncio.wait_for(coroutine, timeout=self.timeout)
        except asyncio.TimeoutError:
            return []
        except Exception:
            # Log error but don't fail the whole context building
            return []
    
    def _create_item(
        self,
        content: str,
        relevance_score: float,
        metadata: dict | None = None,
    ) -> ContextItem:
        """Helper to create a ContextItem."""
        return ContextItem(
            source=self.name,
            content=content,
            relevance_score=relevance_score,
            metadata=metadata or {},
        )
    
    def _create_items(
        self,
        items: list[tuple[str, float, dict | None]],
    ) -> list[ContextItem]:
        """Helper to create multiple ContextItems."""
        return [
            self._create_item(content, score, meta)
            for content, score, meta in items
        ]
    
    def _should_run(self, query: ContextQuery) -> bool:
        """
        Check if this provider should run for the given query.
        
        Default implementation checks if provider name is in query.sources.
        """
        if query.sources is None:
            return True
        return self.name in query.sources
