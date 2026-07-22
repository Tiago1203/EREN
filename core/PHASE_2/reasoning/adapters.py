"""Adapters for the Cognitive Reasoning Engine.

Provides adapters for integration with:
- Cognitive Context
- Memory Engine
- Event Bus

Architecture only -- no AI, no business logic.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:
    pass


# =============================================================================
# Context Adapter Protocol
# =============================================================================


class ContextReader(Protocol):
    """Protocol for reading from cognitive context."""

    def get_evidence(self) -> list[Any]:
        """Get evidence from context."""
        ...

    def get_hypotheses(self) -> list[Any]:
        """Get hypotheses from context."""
        ...

    def get_device_info(self) -> dict[str, Any]:
        """Get device information."""
        ...


class ContextWriter(Protocol):
    """Protocol for writing to cognitive context."""

    def write_conclusion(self, conclusion: str) -> None:
        """Write a conclusion to context."""
        ...

    def update_confidence(self, confidence: float) -> None:
        """Update confidence in context."""
        ...


# =============================================================================
# Reasoning Context Adapter
# =============================================================================


class ReasoningContextAdapter:
    """Adapter for Cognitive Context.
    
    Responsibilities:
    - Read evidence from context
    - Read hypotheses from context
    - Write conclusions to context
    - Update confidence in context
    
    NEVER accesses ContextManager directly.
    """

    def __init__(
        self,
        reader: ContextReader | None = None,
        writer: ContextWriter | None = None,
    ) -> None:
        """Initialize the adapter.
        
        Args:
            reader: Context reader implementation.
            writer: Context writer implementation.
        """
        self._reader = reader
        self._writer = writer

    def read_evidence(self) -> list[Any]:
        """Read evidence from context.
        
        Returns:
            List of evidence from context.
        """
        if self._reader:
            return self._reader.get_evidence()
        return []

    def read_hypotheses(self) -> list[Any]:
        """Read hypotheses from context.
        
        Returns:
            List of hypotheses from context.
        """
        if self._reader:
            return self._reader.get_hypotheses()
        return []

    def read_device_info(self) -> dict[str, Any]:
        """Read device information from context.
        
        Returns:
            Device information dictionary.
        """
        if self._reader:
            return self._reader.get_device_info()
        return {}

    def write_conclusion(self, conclusion: str) -> None:
        """Write a conclusion to context.
        
        Args:
            conclusion: The conclusion to write.
        """
        if self._writer:
            self._writer.write_conclusion(conclusion)

    def update_confidence(self, confidence: float) -> None:
        """Update confidence in context.
        
        Args:
            confidence: The confidence value.
        """
        if self._writer:
            self._writer.update_confidence(confidence)


# =============================================================================
# Memory Adapter Protocol
# =============================================================================


class MemoryRetriever(Protocol):
    """Protocol for memory retrieval."""

    def retrieve(self, query: str) -> list[Any]:
        """Retrieve memories by query."""
        ...

    def search(self, query: str, limit: int = 10) -> list[Any]:
        """Search memories."""
        ...


class MemoryStorer(Protocol):
    """Protocol for memory storage."""

    def store(self, content: str, memory_type: str) -> str:
        """Store a memory.
        
        Returns:
            Memory ID.
        """
        ...


# =============================================================================
# Reasoning Memory Adapter
# =============================================================================


class ReasoningMemoryAdapter:
    """Adapter for Memory Engine.
    
    Exposes ONLY:
    - retrieve()
    - store()
    - search()
    
    NEVER depends on concrete Memory Engine.
    """

    def __init__(
        self,
        retriever: MemoryRetriever | None = None,
        storer: MemoryStorer | None = None,
    ) -> None:
        """Initialize the adapter.
        
        Args:
            retriever: Memory retriever implementation.
            storer: Memory storer implementation.
        """
        self._retriever = retriever
        self._storer = storer

    def retrieve(self, query: str) -> list[Any]:
        """Retrieve memories by query.
        
        Args:
            query: Search query.
            
        Returns:
            List of retrieved memories.
        """
        if self._retriever:
            return self._retriever.retrieve(query)
        return []

    def store(self, content: str, memory_type: str = "reasoning") -> str:
        """Store a reasoning memory.
        
        Args:
            content: Memory content.
            memory_type: Type of memory (reasoning, evidence, hypothesis).
            
        Returns:
            Memory ID or empty string if failed.
        """
        if self._storer:
            return self._storer.store(content, memory_type)
        return ""

    def search(self, query: str, limit: int = 10) -> list[Any]:
        """Search memories.
        
        Args:
            query: Search query.
            limit: Maximum results.
            
        Returns:
            List of matching memories.
        """
        if self._retriever:
            return self._retriever.search(query, limit)
        return []
