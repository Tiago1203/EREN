"""Base memory interface for EREN OS Cognitive Memory Orchestrator.

Defines the contract that all memory implementations must follow.
The Orchestrator never knows concrete implementations like PostgreSQL, Redis, Chroma, etc.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from core.PHASE_2.memory.types import (
    MemoryEntry,
    MemoryMetrics,
    MemoryQuery,
    MemoryResponse,
    MemoryState,
    MemoryType,
)

if TYPE_CHECKING:
    pass


class BaseMemoryInterface(ABC):
    """Abstract base class for memory implementations.

    The Memory Orchestrator uses this interface to interact with memories.
    Concrete implementations (PostgreSQL, Redis, Chroma, etc.) are not known
    by the Orchestrator.

    Example:
        class PostgreSQLMemory(BaseMemoryInterface):
            def initialize(self, config: dict) -> None:
                # Setup PostgreSQL connection
                pass

            async def read(self, key: str) -> MemoryResponse:
                # Read from PostgreSQL
                pass
    """

    @property
    @abstractmethod
    def memory_id(self) -> str:
        """Get memory identifier."""
        pass

    @property
    @abstractmethod
    def memory_type(self) -> MemoryType:
        """Get memory type."""
        pass

    @property
    def state(self) -> MemoryState:
        """Get current memory state."""
        return self._state

    @property
    def metrics(self) -> MemoryMetrics:
        """Get memory metrics."""
        return self._metrics

    def __init__(self) -> None:
        """Initialize base memory interface."""
        self._state = MemoryState.UNREGISTERED
        self._metrics = MemoryMetrics()
        self._config: dict = {}

    # =========================================================================
    # Lifecycle
    # =========================================================================

    @abstractmethod
    def initialize(self, config: dict) -> None:
        """Initialize the memory.

        Args:
            config: Memory configuration.

        Raises:
            MemoryConfigurationError: If initialization fails.
        """
        pass

    @abstractmethod
    def shutdown(self) -> None:
        """Shutdown the memory.

        Must release all resources.
        """
        pass

    # =========================================================================
    # Read Operations
    # =========================================================================

    @abstractmethod
    def read(self, key: str) -> MemoryResponse:
        """Read from memory.

        Args:
            key: Memory key.

        Returns:
            Memory response with results.

        Raises:
            MemoryReadError: If read fails.
        """
        pass

    @abstractmethod
    def read_batch(self, keys: list[str]) -> MemoryResponse:
        """Read multiple keys from memory.

        Args:
            keys: List of memory keys.

        Returns:
            Memory response with results.
        """
        pass

    # =========================================================================
    # Write Operations
    # =========================================================================

    @abstractmethod
    def write(self, entry: MemoryEntry) -> MemoryResponse:
        """Write to memory.

        Args:
            entry: Memory entry to write.

        Returns:
            Memory response.

        Raises:
            MemoryWriteError: If write fails.
        """
        pass

    @abstractmethod
    def write_batch(self, entries: list[MemoryEntry]) -> MemoryResponse:
        """Write multiple entries to memory.

        Args:
            entries: List of memory entries.

        Returns:
            Memory response.
        """
        pass

    # =========================================================================
    # Search Operations
    # =========================================================================

    @abstractmethod
    def search(self, query: MemoryQuery) -> MemoryResponse:
        """Search memory.

        Args:
            query: Search query.

        Returns:
            Memory response with search results.
        """
        pass

    # =========================================================================
    # Delete Operations
    # =========================================================================

    @abstractmethod
    def delete(self, key: str) -> MemoryResponse:
        """Delete from memory.

        Args:
            key: Memory key to delete.

        Returns:
            Memory response.
        """
        pass

    @abstractmethod
    def clear(self) -> MemoryResponse:
        """Clear all memory.

        Returns:
            Memory response.
        """
        pass

    # =========================================================================
    # Utility
    # =========================================================================

    def health_check(self) -> dict:
        """Check memory health.

        Returns:
            Health status dictionary.
        """
        return {
            "memory_id": self.memory_id,
            "memory_type": self.memory_type.value,
            "state": self.state.value,
            "healthy": self._state == MemoryState.READY,
        }

    def to_dict(self) -> dict:
        """Convert to dictionary.

        Returns:
            Dictionary representation.
        """
        return {
            "memory_id": self.memory_id,
            "memory_type": self.memory_type.value,
            "state": self._state.value,
            "metrics": self._metrics.to_dict(),
            "config": self._config,
        }

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"{self.__class__.__name__}("
            f"id={self.memory_id}, "
            f"type={self.memory_type.value}, "
            f"state={self._state.value})"
        )


# Type alias for memory interface
MemoryInterface = BaseMemoryInterface
