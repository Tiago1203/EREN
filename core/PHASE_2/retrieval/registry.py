"""Retrieval registry for EREN Semantic Retrieval Engine.

Manages retrieval strategies and memory providers.
"""

from __future__ import annotations

import threading
from collections.abc import Callable
from typing import TYPE_CHECKING

from core.PHASE_2.retrieval.types import MemorySource

if TYPE_CHECKING:
    from core.PHASE_2.retrieval.strategy import RetrievalStrategy


class RetrievalRegistry:
    """Registry for retrieval components.

    Manages:
    - Retrieval strategies
    - Memory providers
    - Rankers
    - Context builders
    """

    def __init__(self):
        """Initialize registry."""
        self._lock = threading.RLock()
        self._strategies: dict[str, RetrievalStrategy] = {}
        self._memory_providers: dict[MemorySource, Callable] = {}
        self._rankers: dict[str, Callable] = {}
        self._context_builders: dict[str, Callable] = {}

    # =========================================================================
    # Strategies
    # =========================================================================

    def register_strategy(self, name: str, strategy: RetrievalStrategy) -> None:
        """Register a retrieval strategy.

        Args:
            name: Strategy name.
            strategy: Strategy instance.
        """
        with self._lock:
            self._strategies[name] = strategy

    def get_strategy(self, name: str) -> RetrievalStrategy | None:
        """Get a strategy by name.

        Args:
            name: Strategy name.

        Returns:
            Strategy or None.
        """
        with self._lock:
            return self._strategies.get(name)

    def list_strategies(self) -> list[str]:
        """List registered strategies.

        Returns:
            List of strategy names.
        """
        with self._lock:
            return list(self._strategies.keys())

    def unregister_strategy(self, name: str) -> bool:
        """Unregister a strategy.

        Args:
            name: Strategy name.

        Returns:
            True if unregistered.
        """
        with self._lock:
            if name in self._strategies:
                del self._strategies[name]
                return True
            return False

    # =========================================================================
    # Memory Providers
    # =========================================================================

    def register_memory_provider(
        self,
        source: MemorySource,
        provider: Callable,
    ) -> None:
        """Register a memory provider.

        Args:
            source: Memory source.
            provider: Provider callable.
        """
        with self._lock:
            self._memory_providers[source] = provider

    def get_memory_provider(self, source: MemorySource) -> Callable | None:
        """Get a memory provider.

        Args:
            source: Memory source.

        Returns:
            Provider callable or None.
        """
        with self._lock:
            return self._memory_providers.get(source)

    def list_memory_sources(self) -> list[MemorySource]:
        """List registered memory sources.

        Returns:
            List of memory sources.
        """
        with self._lock:
            return list(self._memory_providers.keys())

    def has_memory_source(self, source: MemorySource) -> bool:
        """Check if memory source is registered.

        Args:
            source: Memory source.

        Returns:
            True if registered.
        """
        with self._lock:
            return source in self._memory_providers

    def unregister_memory_provider(self, source: MemorySource) -> bool:
        """Unregister a memory provider.

        Args:
            source: Memory source.

        Returns:
            True if unregistered.
        """
        with self._lock:
            if source in self._memory_providers:
                del self._memory_providers[source]
                return True
            return False

    # =========================================================================
    # Rankers
    # =========================================================================

    def register_ranker(self, name: str, ranker: Callable) -> None:
        """Register a result ranker.

        Args:
            name: Ranker name.
            ranker: Ranker callable.
        """
        with self._lock:
            self._rankers[name] = ranker

    def get_ranker(self, name: str) -> Callable | None:
        """Get a ranker by name.

        Args:
            name: Ranker name.

        Returns:
            Ranker callable or None.
        """
        with self._lock:
            return self._rankers.get(name)

    def list_rankers(self) -> list[str]:
        """List registered rankers.

        Returns:
            List of ranker names.
        """
        with self._lock:
            return list(self._rankers.keys())

    # =========================================================================
    # Context Builders
    # =========================================================================

    def register_context_builder(self, name: str, builder: Callable) -> None:
        """Register a context builder.

        Args:
            name: Builder name.
            builder: Builder callable.
        """
        with self._lock:
            self._context_builders[name] = builder

    def get_context_builder(self, name: str) -> Callable | None:
        """Get a context builder by name.

        Args:
            name: Builder name.

        Returns:
            Builder callable or None.
        """
        with self._lock:
            return self._context_builders.get(name)

    def list_context_builders(self) -> list[str]:
        """List registered context builders.

        Returns:
            List of builder names.
        """
        with self._lock:
            return list(self._context_builders.keys())

    # =========================================================================
    # Utility
    # =========================================================================

    def clear(self) -> None:
        """Clear all registrations."""
        with self._lock:
            self._strategies.clear()
            self._memory_providers.clear()
            self._rankers.clear()
            self._context_builders.clear()

    def get_status(self) -> dict:
        """Get registry status.

        Returns:
            Status dictionary.
        """
        with self._lock:
            return {
                "strategies": len(self._strategies),
                "memory_sources": len(self._memory_providers),
                "rankers": len(self._rankers),
                "context_builders": len(self._context_builders),
            }


# Global registry instance
_global_registry: RetrievalRegistry | None = None
_registry_lock = threading.Lock()


def get_retrieval_registry() -> RetrievalRegistry:
    """Get the global retrieval registry.

    Returns:
        Global RetrievalRegistry instance.
    """
    global _global_registry
    with _registry_lock:
        if _global_registry is None:
            _global_registry = RetrievalRegistry()
        return _global_registry


def reset_retrieval_registry() -> None:
    """Reset the global registry."""
    global _global_registry
    with _registry_lock:
        if _global_registry is not None:
            _global_registry.clear()
        _global_registry = None
