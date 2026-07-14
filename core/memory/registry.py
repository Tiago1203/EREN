"""Memory registry for EREN OS Cognitive Memory Orchestrator.

Manages memory registration and discovery.
"""

from __future__ import annotations

import threading
from typing import TYPE_CHECKING, Callable

from core.memory.base import BaseMemoryInterface
from core.memory.types import MemoryType, MemoryState
from core.memory.exceptions import MemoryAlreadyExistsError, MemoryNotRegisteredError

if TYPE_CHECKING:
    pass


class MemoryRegistry:
    """Registry for managing memory instances.

    Provides:
    - Memory registration
    - Memory discovery
    - State management
    """

    def __init__(self):
        """Initialize the registry."""
        self._memories: dict[str, BaseMemoryInterface] = {}
        self._lock = threading.RLock()
        self._event_handlers: dict[str, list[Callable]] = {}

    # =========================================================================
    # Registration
    # =========================================================================

    def register(self, memory: BaseMemoryInterface) -> None:
        """Register a memory.

        Args:
            memory: Memory instance.

        Raises:
            MemoryAlreadyExistsError: If already registered.
        """
        with self._lock:
            memory_id = memory.memory_id

            if memory_id in self._memories:
                raise MemoryAlreadyExistsError(memory_id)

            self._memories[memory_id] = memory

            self._emit_event("MemoryRegistered", {
                "memory_id": memory_id,
                "memory_type": memory.memory_type.value,
            })

    def unregister(self, memory_id: str) -> bool:
        """Unregister a memory.

        Args:
            memory_id: Memory identifier.

        Returns:
            True if unregistered.
        """
        with self._lock:
            if memory_id not in self._memories:
                return False

            memory = self._memories[memory_id]

            # Shutdown if needed
            if memory.state == MemoryState.READY:
                try:
                    memory.shutdown()
                except Exception:
                    pass

            del self._memories[memory_id]

            self._emit_event("MemoryUnregistered", {"memory_id": memory_id})
            return True

    # =========================================================================
    # Retrieval
    # =========================================================================

    def get(self, memory_id: str) -> BaseMemoryInterface:
        """Get a memory.

        Args:
            memory_id: Memory identifier.

        Returns:
            Memory instance.

        Raises:
            MemoryNotRegisteredError: If not found.
        """
        with self._lock:
            if memory_id not in self._memories:
                raise MemoryNotRegisteredError(memory_id)
            return self._memories[memory_id]

    def get_or_none(self, memory_id: str) -> BaseMemoryInterface | None:
        """Get a memory or None.

        Args:
            memory_id: Memory identifier.

        Returns:
            Memory instance or None.
        """
        with self._lock:
            return self._memories.get(memory_id)

    def has(self, memory_id: str) -> bool:
        """Check if memory is registered.

        Args:
            memory_id: Memory identifier.

        Returns:
            True if registered.
        """
        with self._lock:
            return memory_id in self._memories

    # =========================================================================
    # Queries
    # =========================================================================

    def list_all(self) -> list[BaseMemoryInterface]:
        """List all memories.

        Returns:
            List of memory instances.
        """
        with self._lock:
            return list(self._memories.values())

    def list_by_type(self, memory_type: MemoryType) -> list[BaseMemoryInterface]:
        """List memories by type.

        Args:
            memory_type: Memory type.

        Returns:
            List of memory instances.
        """
        with self._lock:
            return [
                m for m in self._memories.values()
                if m.memory_type == memory_type
            ]

    def list_by_state(self, state: MemoryState) -> list[BaseMemoryInterface]:
        """List memories by state.

        Args:
            state: Memory state.

        Returns:
            List of memory instances.
        """
        with self._lock:
            return [m for m in self._memories.values() if m.state == state]

    def list_ready(self) -> list[BaseMemoryInterface]:
        """List all ready memories.

        Returns:
            List of ready memory instances.
        """
        return self.list_by_state(MemoryState.READY)

    # =========================================================================
    # State Management
    # =========================================================================

    def set_state(self, memory_id: str, state: MemoryState) -> bool:
        """Set memory state.

        Args:
            memory_id: Memory identifier.
            state: New state.

        Returns:
            True if state was set.
        """
        with self._lock:
            if memory_id not in self._memories:
                return False

            self._memories[memory_id]._state = state
            self._emit_event("MemoryStateChanged", {
                "memory_id": memory_id,
                "state": state.value,
            })
            return True

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

    def clear(self) -> None:
        """Clear all registrations."""
        with self._lock:
            for memory in self._memories.values():
                if memory.state == MemoryState.READY:
                    try:
                        memory.shutdown()
                    except Exception:
                        pass
            self._memories.clear()

    def __len__(self) -> int:
        """Get memory count."""
        with self._lock:
            return len(self._memories)

    def __contains__(self, memory_id: str) -> bool:
        """Check if memory is registered."""
        return self.has(memory_id)


# Global registry instance
_global_registry: MemoryRegistry | None = None
_registry_lock = threading.Lock()


def get_memory_registry() -> MemoryRegistry:
    """Get the global memory registry.

    Returns:
        Global MemoryRegistry instance.
    """
    global _global_registry
    with _registry_lock:
        if _global_registry is None:
            _global_registry = MemoryRegistry()
        return _global_registry


def reset_memory_registry() -> None:
    """Reset the global registry."""
    global _global_registry
    with _registry_lock:
        if _global_registry is not None:
            _global_registry.clear()
        _global_registry = None
