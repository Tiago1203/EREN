"""Memory domain services."""
from typing import Protocol
from core.PHASE_2.cognitive.memory.domain.entities import MemoryBlock, MemoryType


class MemoryStore(Protocol):
    """Protocol for memory storage backends."""
    
    async def store(self, block: MemoryBlock) -> None:
        """Store a memory block."""
        ...
    
    async def retrieve(self, key: str) -> MemoryBlock | None:
        """Retrieve a memory block."""
        ...
    
    async def forget(self, key: str) -> None:
        """Delete a memory block."""
        ...


class WorkingMemory(MemoryStore):
    """Transient working memory (Redis)."""
    ttl: int = 300  # 5 minutes
    
    async def store(self, block: MemoryBlock) -> None:
        """Store in working memory with TTL."""
        # Implementation would use Redis
        pass
    
    async def retrieve(self, key: str) -> MemoryBlock | None:
        """Retrieve from working memory."""
        pass
    
    async def forget(self, key: str) -> None:
        """Delete from working memory."""
        pass


class SessionMemory(MemoryStore):
    """Conversation-scoped memory (Redis)."""
    ttl: int = 1800  # 30 minutes
    max_history: int = 50
    
    async def store(self, block: MemoryBlock) -> None:
        """Store in session memory."""
        pass
    
    async def retrieve(self, key: str) -> MemoryBlock | None:
        """Retrieve from session memory."""
        pass
    
    async def forget(self, key: str) -> None:
        """Delete from session memory."""
        pass


class LongTermMemory(MemoryStore):
    """Persistent memory (PostgreSQL)."""
    
    async def store(self, block: MemoryBlock) -> None:
        """Store in long-term memory."""
        pass
    
    async def retrieve(self, key: str) -> MemoryBlock | None:
        """Retrieve from long-term memory."""
        pass
    
    async def forget(self, key: str) -> None:
        """Delete from long-term memory."""
        pass


class MemoryManager:
    """Unified interface to all memory types."""
    
    def __init__(
        self,
        working: WorkingMemory,
        session: SessionMemory,
        long_term: LongTermMemory,
    ):
        self.working = working
        self.session = session
        self.long_term = long_term
    
    async def store(
        self,
        key: str,
        value: any,
        memory_type: MemoryType,
        importance: float = 0.5,
        is_sensitive: bool = False,
    ) -> None:
        """Store memory in appropriate tier."""
        # Implementation would delegate to correct store
        pass
    
    async def retrieve(self, key: str) -> list[MemoryBlock]:
        """Retrieve from all tiers."""
        results = []
        # Implementation would check each tier
        return results
