"""Capability Registry for EREN OS Cognitive Capability SDK.

Manages capability registration and discovery.
"""

from __future__ import annotations

import threading
from collections.abc import Callable
from typing import TYPE_CHECKING

from core.PHASE_2.sdk.capability import BaseCapability
from core.PHASE_2.sdk.exceptions import (
    CapabilityAlreadyRegisteredError,
    CapabilityNotFoundError,
)
from core.PHASE_2.sdk.types import CapabilityMetadata, CapabilityState, ValidationResult

if TYPE_CHECKING:
    pass


class CapabilityRegistry:
    """Registry for managing capabilities.

    Provides:
    - Capability registration
    - Capability discovery
    - State management
    - Dependency resolution
    """

    def __init__(self):
        """Initialize the registry."""
        self._capabilities: dict[str, BaseCapability] = {}
        self._metadata: dict[str, CapabilityMetadata] = {}
        self._factories: dict[str, Callable] = {}
        self._lock = threading.RLock()

    # =========================================================================
    # Registration
    # =========================================================================

    def register(
        self,
        capability_id: str,
        capability: BaseCapability,
        metadata: CapabilityMetadata | None = None,
    ) -> None:
        """Register a capability.

        Args:
            capability_id: Unique capability identifier.
            capability: Capability instance.
            metadata: Optional capability metadata.

        Raises:
            CapabilityAlreadyRegisteredError: If already registered.
        """
        with self._lock:
            if capability_id in self._capabilities:
                raise CapabilityAlreadyRegisteredError(capability_id)

            self._capabilities[capability_id] = capability

            if metadata:
                self._metadata[capability_id] = metadata
            else:
                self._metadata[capability_id] = capability.metadata()

            # Set capability ID
            capability._capability_id = capability_id

    def unregister(self, capability_id: str) -> bool:
        """Unregister a capability.

        Args:
            capability_id: Capability identifier.

        Returns:
            True if unregistered.
        """
        with self._lock:
            if capability_id not in self._capabilities:
                return False

            capability = self._capabilities[capability_id]

            # Shutdown if needed
            if capability.state == CapabilityState.READY:
                capability.shutdown()

            del self._capabilities[capability_id]
            if capability_id in self._metadata:
                del self._metadata[capability_id]

            return True

    def register_factory(self, capability_id: str, factory: Callable) -> None:
        """Register a capability factory.

        Args:
            capability_id: Capability identifier.
            factory: Factory function.
        """
        with self._lock:
            self._factories[capability_id] = factory

    # =========================================================================
    # Retrieval
    # =========================================================================

    def get(self, capability_id: str) -> BaseCapability:
        """Get a capability.

        Args:
            capability_id: Capability identifier.

        Returns:
            Capability instance.

        Raises:
            CapabilityNotFoundError: If not found.
        """
        with self._lock:
            if capability_id not in self._capabilities:
                raise CapabilityNotFoundError(capability_id)
            return self._capabilities[capability_id]

    def get_or_none(self, capability_id: str) -> BaseCapability | None:
        """Get a capability or None.

        Args:
            capability_id: Capability identifier.

        Returns:
            Capability or None.
        """
        with self._lock:
            return self._capabilities.get(capability_id)

    def get_metadata(self, capability_id: str) -> CapabilityMetadata | None:
        """Get capability metadata.

        Args:
            capability_id: Capability identifier.

        Returns:
            Capability metadata or None.
        """
        with self._lock:
            return self._metadata.get(capability_id)

    def has(self, capability_id: str) -> bool:
        """Check if capability is registered.

        Args:
            capability_id: Capability identifier.

        Returns:
            True if registered.
        """
        with self._lock:
            return capability_id in self._capabilities

    def create(self, capability_id: str) -> BaseCapability | None:
        """Create a capability from factory.

        Args:
            capability_id: Capability identifier.

        Returns:
            Created capability or None.
        """
        with self._lock:
            factory = self._factories.get(capability_id)
            if not factory:
                return None

            capability = factory()

            # Auto-register
            self._capabilities[capability_id] = capability
            self._metadata[capability_id] = capability.metadata()
            capability._capability_id = capability_id

            return capability

    # =========================================================================
    # Queries
    # =========================================================================

    def list_all(self) -> list[BaseCapability]:
        """List all registered capabilities.

        Returns:
            List of capabilities.
        """
        with self._lock:
            return list(self._capabilities.values())

    def list_by_state(self, state: CapabilityState) -> list[BaseCapability]:
        """List capabilities by state.

        Args:
            state: Capability state.

        Returns:
            List of capabilities in the state.
        """
        with self._lock:
            return [c for c in self._capabilities.values() if c.state == state]

    def list_by_category(self, category: str) -> list[BaseCapability]:
        """List capabilities by category.

        Args:
            category: Category name.

        Returns:
            List of capabilities in the category.
        """
        with self._lock:
            result = []
            for capability in self._capabilities.values():
                metadata = self._metadata.get(capability.capability_id)
                if metadata and metadata.category.value == category:
                    result.append(capability)
            return result

    def list_ready(self) -> list[BaseCapability]:
        """List all ready capabilities.

        Returns:
            List of ready capabilities.
        """
        return self.list_by_state(CapabilityState.READY)

    # =========================================================================
    # Counts
    # =========================================================================

    def count(self) -> int:
        """Get total capability count."""
        with self._lock:
            return len(self._capabilities)

    def count_by_state(self, state: CapabilityState) -> int:
        """Get capability count by state."""
        with self._lock:
            return len([c for c in self._capabilities.values() if c.state == state])

    def ready_count(self) -> int:
        """Get ready capability count."""
        return self.count_by_state(CapabilityState.READY)

    # =========================================================================
    # Validation
    # =========================================================================

    def validate_all(self) -> dict[str, ValidationResult]:
        """Validate all capabilities.

        Returns:
            Dictionary of capability_id -> validation result.
        """
        with self._lock:
            results = {}
            for capability_id, capability in self._capabilities.items():
                results[capability_id] = capability.validate()
            return results

    def health_check_all(self) -> dict[str, dict]:
        """Health check all capabilities.

        Returns:
            Dictionary of capability_id -> health result.
        """
        with self._lock:
            results = {}
            for capability_id, capability in self._capabilities.items():
                results[capability_id] = capability.health().to_dict()
            return results

    # =========================================================================
    # Utility
    # =========================================================================

    def clear(self) -> None:
        """Clear all registrations."""
        with self._lock:
            for capability in self._capabilities.values():
                if capability.state == CapabilityState.READY:
                    capability.shutdown()
            self._capabilities.clear()
            self._metadata.clear()
            self._factories.clear()

    def __len__(self) -> int:
        """Get capability count."""
        with self._lock:
            return len(self._capabilities)

    def __contains__(self, capability_id: str) -> bool:
        """Check if capability is registered."""
        return self.has(capability_id)


# Global registry instance
_global_registry: CapabilityRegistry | None = None
_registry_lock = threading.Lock()


def get_capability_registry() -> CapabilityRegistry:
    """Get the global capability registry.

    Returns:
        Global CapabilityRegistry instance.
    """
    global _global_registry
    with _registry_lock:
        if _global_registry is None:
            _global_registry = CapabilityRegistry()
        return _global_registry


def reset_capability_registry() -> None:
    """Reset the global registry."""
    global _global_registry
    with _registry_lock:
        if _global_registry is not None:
            _global_registry.clear()
        _global_registry = None
