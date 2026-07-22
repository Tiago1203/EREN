"""Memory coordinator for EREN OS Cognitive Memory System.

The coordinator is an INTERNAL component of MemoryEngine responsible ONLY for
coordinating access to different memory systems.

The Coordinator does NOT store information. It only decides:
- Where to read?
- Where to write?
- In what order?
- How to combine results?
- What policy to apply?

The Coordinator NEVER knows PostgreSQL, Redis, Chroma, Qdrant, etc.
"""

from __future__ import annotations

import threading
import time
from collections.abc import Callable
from typing import TYPE_CHECKING

from core.PHASE_2.memory.registry import MemoryRegistry, get_memory_registry
from core.PHASE_2.memory.selector import MemorySelector
from core.PHASE_2.memory.types import (
    MemoryAccessPolicy,
    MemoryEntry,
    MemoryOperation,
    MemoryQuery,
    MemoryResponse,
    MemoryResult,
    MemoryState,
    MemoryType,
)

if TYPE_CHECKING:
    pass


class MemoryCoordinator:
    """Coordinates all memory operations in EREN.

    This is an INTERNAL component of MemoryEngine.
    The ExecutionCoordinator NEVER accesses this directly.

    Architecture:
        ExecutionCoordinator
                │
                ▼
        MemoryEngine
                │
                ▼
        MemoryCoordinator
                │
         ├── MemoryRegistry
         ├── MemorySelector
         ├── MemoryPolicies
         └── Memory Providers

    Philosophy:
        - Does NOT store information
        - Only decides WHERE to read/write
        - Only decides IN WHAT ORDER
        - Only decides HOW TO COMBINE results
        - Only decides WHAT POLICY to apply

    Example:
        User: "¿Recuerdas qué monitor estaba reparando ayer?"
        ↓
        MemoryEngine
        ↓
        MemoryCoordinator
        ↓
        Working Memory → Conversation → Long Term → Vector
        ↓
        Respuesta
    """

    def __init__(
        self,
        registry: MemoryRegistry | None = None,
        default_policy: MemoryAccessPolicy = MemoryAccessPolicy.FIRST_AVAILABLE,
    ):
        """Initialize coordinator.

        Args:
            registry: Memory registry (uses global if None).
            default_policy: Default access policy.
        """
        self._registry = registry or get_memory_registry()
        self._selector = MemorySelector(self._registry)
        self._default_policy = default_policy
        self._selector.policy = default_policy
        self._lock = threading.RLock()

        # Event handlers
        self._event_handlers: dict[str, list[Callable]] = {}

    # =========================================================================
    # Properties
    # =========================================================================

    @property
    def registry(self) -> MemoryRegistry:
        """Get memory registry."""
        return self._registry

    @property
    def selector(self) -> MemorySelector:
        """Get memory selector."""
        return self._selector

    @property
    def default_policy(self) -> MemoryAccessPolicy:
        """Get default access policy."""
        return self._default_policy

    @default_policy.setter
    def default_policy(self, policy: MemoryAccessPolicy) -> None:
        """Set default access policy."""
        self._default_policy = policy
        self._selector.policy = policy

    # =========================================================================
    # Read Operations
    # =========================================================================

    def read(
        self,
        key: str,
        memory_types: list[MemoryType] | None = None,
        policy: MemoryAccessPolicy | None = None,
    ) -> MemoryResponse:
        """Read from memory.

        Decides which memory to use based on policy.

        Args:
            key: Memory key.
            memory_types: Optional memory type filter.
            policy: Access policy (uses default if None).

        Returns:
            Memory response with results.
        """
        start_time = time.time()

        policy = policy or self._default_policy
        self._selector.policy = policy

        memories = self._selector.select_for_read(memory_types)

        if not memories:
            return MemoryResponse(
                operation=MemoryOperation.READ,
                success=False,
                error="No memory available",
            )

        # Read from selected memories
        results: list[MemoryResult] = []
        errors: list[str] = []

        for memory in memories:
            try:
                response = memory.read(key)
                results.extend(response.results)
                memory._metrics.record_read(
                    latency_ms=int((time.time() - start_time) * 1000),
                    hit=len(response.results) > 0,
                )
            except Exception as e:
                errors.append(str(e))

        duration_ms = int((time.time() - start_time) * 1000)

        self._emit_event("MemoryRead", {
            "key": key,
            "memory_types": [m.memory_type.value for m in memories],
            "results_count": len(results),
            "duration_ms": duration_ms,
        })

        return MemoryResponse(
            results=results,
            operation=MemoryOperation.READ,
            success=len(errors) == 0,
            error="; ".join(errors) if errors else "",
            metadata={
                "durations_ms": duration_ms,
                "memories_queried": len(memories),
            },
        )

    # =========================================================================
    # Write Operations
    # =========================================================================

    def write(
        self,
        entry: MemoryEntry,
        memory_types: list[MemoryType] | None = None,
        policy: MemoryAccessPolicy | None = None,
    ) -> MemoryResponse:
        """Write to memory.

        Decides which memories to write to based on policy.

        Args:
            entry: Memory entry to write.
            memory_types: Optional memory type filter.
            policy: Access policy (uses default if None).

        Returns:
            Memory response.
        """
        start_time = time.time()

        policy = policy or self._default_policy
        self._selector.policy = policy

        memories = self._selector.select_for_write(memory_types)

        if not memories:
            return MemoryResponse(
                operation=MemoryOperation.WRITE,
                success=False,
                error="No writable memory available",
            )

        results: list[MemoryResult] = []
        errors: list[str] = []

        for memory in memories:
            try:
                response = memory.write(entry)
                results.extend(response.results)
                memory._metrics.record_write(
                    latency_ms=int((time.time() - start_time) * 1000),
                )
            except Exception as e:
                errors.append(str(e))

        duration_ms = int((time.time() - start_time) * 1000)

        self._emit_event("MemoryWrite", {
            "key": entry.key,
            "memory_type": entry.memory_type.value,
            "memories_written": len(results),
            "duration_ms": duration_ms,
        })

        return MemoryResponse(
            results=results,
            operation=MemoryOperation.WRITE,
            success=len(errors) == 0,
            error="; ".join(errors) if errors else "",
            metadata={
                "durations_ms": duration_ms,
                "memories_written": len(memories),
            },
        )

    # =========================================================================
    # Search Operations
    # =========================================================================

    def search(
        self,
        query: MemoryQuery,
        policy: MemoryAccessPolicy | None = None,
    ) -> MemoryResponse:
        """Search memory.

        Decides which memories to search based on policy.

        Args:
            query: Search query.
            policy: Access policy (uses default if None).

        Returns:
            Memory response with search results.
        """
        start_time = time.time()

        policy = policy or self._default_policy
        self._selector.policy = policy

        memories = self._selector.select_for_search(query.memory_types)

        if not memories:
            return MemoryResponse(
                operation=MemoryOperation.SEARCH,
                success=False,
                error="No searchable memory available",
            )

        results: list[MemoryResult] = []
        errors: list[str] = []

        for memory in memories:
            try:
                response = memory.search(query)
                results.extend(response.results)
                memory._metrics.record_search(
                    latency_ms=int((time.time() - start_time) * 1000),
                )
            except Exception as e:
                errors.append(str(e))

        # Sort by score
        results.sort(key=lambda r: r.score, reverse=True)

        # Apply limit
        if query.limit > 0:
            results = results[:query.limit]

        duration_ms = int((time.time() - start_time) * 1000)

        self._emit_event("MemorySearch", {
            "query": query.query,
            "memory_types": [m.memory_type.value for m in memories],
            "results_count": len(results),
            "duration_ms": duration_ms,
        })

        return MemoryResponse(
            results=results,
            operation=MemoryOperation.SEARCH,
            success=len(errors) == 0,
            error="; ".join(errors) if errors else "",
            metadata={
                "durations_ms": duration_ms,
                "memories_searched": len(memories),
            },
        )

    # =========================================================================
    # Delete Operations
    # =========================================================================

    def delete(
        self,
        key: str,
        memory_types: list[MemoryType] | None = None,
    ) -> MemoryResponse:
        """Delete from memory.

        Args:
            key: Memory key to delete.
            memory_types: Optional memory type filter.

        Returns:
            Memory response.
        """
        memories = self._selector.select_for_write(memory_types)

        if not memories:
            return MemoryResponse(
                operation=MemoryOperation.DELETE,
                success=False,
                error="No writable memory available",
            )

        results: list[MemoryResult] = []
        errors: list[str] = []

        for memory in memories:
            try:
                response = memory.delete(key)
                results.extend(response.results)
            except Exception as e:
                errors.append(str(e))

        self._emit_event("MemoryDelete", {
            "key": key,
            "memories_deleted": len(results),
        })

        return MemoryResponse(
            results=results,
            operation=MemoryOperation.DELETE,
            success=len(errors) == 0,
            error="; ".join(errors) if errors else "",
        )

    # =========================================================================
    # Clear Operations
    # =========================================================================

    def clear(
        self,
        memory_types: list[MemoryType] | None = None,
    ) -> MemoryResponse:
        """Clear memories.

        Args:
            memory_types: Optional memory type filter.

        Returns:
            Memory response.
        """
        memories = self._selector.select_for_write(memory_types)

        if not memories:
            return MemoryResponse(
                operation=MemoryOperation.CLEAR,
                success=False,
                error="No writable memory available",
            )

        results: list[MemoryResult] = []
        errors: list[str] = []

        for memory in memories:
            try:
                response = memory.clear()
                results.extend(response.results)
            except Exception as e:
                errors.append(str(e))

        self._emit_event("MemoryClear", {
            "memories_cleared": len(results),
        })

        return MemoryResponse(
            results=results,
            operation=MemoryOperation.CLEAR,
            success=len(errors) == 0,
            error="; ".join(errors) if errors else "",
        )

    # =========================================================================
    # Merge Operations
    # =========================================================================

    def merge(
        self,
        entries: list[MemoryEntry],
        policy: MemoryAccessPolicy = MemoryAccessPolicy.MERGE_ALL,
    ) -> MemoryResponse:
        """Merge multiple entries.

        Args:
            entries: Entries to merge.
            policy: Write policy.

        Returns:
            Memory response.
        """
        results: list[MemoryResult] = []
        errors: list[str] = []

        for entry in entries:
            response = self.write(entry, policy=policy)
            results.extend(response.results)
            if not response.success:
                errors.append(response.error)

        return MemoryResponse(
            results=results,
            operation=MemoryOperation.MERGE,
            success=len(errors) == 0,
            error="; ".join(errors) if errors else "",
        )

    # =========================================================================
    # Events
    # =========================================================================

    def on(self, event_type: str, handler: Callable) -> None:
        """Register an event handler.

        Args:
            event_type: Event type.
            handler: Event handler function.
        """
        with self._lock:
            if event_type not in self._event_handlers:
                self._event_handlers[event_type] = []
            if handler not in self._event_handlers[event_type]:
                self._event_handlers[event_type].append(handler)

    def off(self, event_type: str, handler: Callable) -> None:
        """Unregister an event handler.

        Args:
            event_type: Event type.
            handler: Event handler function.
        """
        with self._lock:
            if event_type in self._event_handlers:
                if handler in self._event_handlers[event_type]:
                    self._event_handlers[event_type].remove(handler)

    def _emit_event(self, event_type: str, data: dict) -> None:
        """Emit an event.

        Args:
            event_type: Event type.
            data: Event data.
        """
        handlers = self._event_handlers.get(event_type, [])
        for handler in handlers:
            try:
                handler(data)
            except Exception:
                pass

    # =========================================================================
    # Utility
    # =========================================================================

    def get_metrics(self) -> dict[str, dict]:
        """Get metrics for all memories.

        Returns:
            Dictionary of memory_id -> metrics.
        """
        return {
            m.memory_id: m.metrics.to_dict()
            for m in self._registry.list_all()
        }

    def get_status(self) -> dict:
        """Get overall status.

        Returns:
            Status dictionary.
        """
        memories = self._registry.list_all()
        ready = sum(1 for m in memories if m.state == MemoryState.READY)

        return {
            "total_memories": len(memories),
            "ready_memories": ready,
            "default_policy": self._default_policy.value,
        }


# Alias for backward compatibility
MemoryOrchestrator = MemoryCoordinator


# Global coordinator instance
_global_coordinator: MemoryCoordinator | None = None
_coordinator_lock = threading.Lock()


def get_memory_coordinator() -> MemoryCoordinator:
    """Get the global memory coordinator.

    Returns:
        Global MemoryCoordinator instance.
    """
    global _global_coordinator
    with _coordinator_lock:
        if _global_coordinator is None:
            _global_coordinator = MemoryCoordinator()
        return _global_coordinator


def reset_memory_coordinator() -> None:
    """Reset the global coordinator."""
    global _global_coordinator
    with _coordinator_lock:
        if _global_coordinator is not None:
            _global_coordinator.registry.clear()
        _global_coordinator = None


# Backward compatibility aliases
def get_memory_orchestrator() -> MemoryCoordinator:
    """Get the global memory coordinator (backward compatibility)."""
    return get_memory_coordinator()


def reset_memory_orchestrator() -> None:
    """Reset the global coordinator (backward compatibility)."""
    reset_memory_coordinator()
