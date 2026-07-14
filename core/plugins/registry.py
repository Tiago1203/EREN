"""Plugin Registry for EREN OS Cognitive Plugin Framework.

Manages plugin registration and discovery.
"""

from __future__ import annotations

import threading
from typing import TYPE_CHECKING, Any, Callable

from core.plugins.descriptor import PluginDescriptor
from core.plugins.types import PluginState, PluginCategory
from core.plugins.exceptions import (
    PluginNotFoundError,
    PluginAlreadyRegisteredError,
)

if TYPE_CHECKING:
    pass


class PluginRegistry:
    """Registry for managing plugins.

    Provides:
    - Plugin registration
    - Plugin discovery
    - State management
    - Dependency resolution
    """

    def __init__(self):
        """Initialize the registry."""
        self._plugins: dict[str, PluginDescriptor] = {}
        self._by_category: dict[PluginCategory, list[str]] = {}
        self._by_contract: dict[str, list[str]] = {}
        self._factories: dict[str, Callable] = {}
        self._lock = threading.RLock()

    # =========================================================================
    # Registration
    # =========================================================================

    def register(self, descriptor: PluginDescriptor, replace: bool = False) -> None:
        """Register a plugin.

        Args:
            descriptor: Plugin descriptor.
            replace: Whether to replace existing.

        Raises:
            PluginAlreadyRegisteredError: If plugin already registered.
        """
        plugin_id = descriptor.plugin_id

        with self._lock:
            if plugin_id in self._plugins and not replace:
                raise PluginAlreadyRegisteredError(plugin_id)

            self._plugins[plugin_id] = descriptor

            # Index by category
            category = descriptor.manifest.category
            if category not in self._by_category:
                self._by_category[category] = []
            if plugin_id not in self._by_category[category]:
                self._by_category[category].append(plugin_id)

            # Index by contracts
            for contract in descriptor.manifest.contracts:
                if contract not in self._by_contract:
                    self._by_contract[contract] = []
                if plugin_id not in self._by_contract[contract]:
                    self._by_contract[contract].append(plugin_id)

    def unregister(self, plugin_id: str) -> bool:
        """Unregister a plugin.

        Args:
            plugin_id: Plugin ID.

        Returns:
            True if unregistered.
        """
        with self._lock:
            if plugin_id not in self._plugins:
                return False

            descriptor = self._plugins[plugin_id]

            # Remove from category index
            category = descriptor.manifest.category
            if category in self._by_category and plugin_id in self._by_category[category]:
                self._by_category[category].remove(plugin_id)

            # Remove from contract index
            for contract in descriptor.manifest.contracts:
                if contract in self._by_contract and plugin_id in self._by_contract[contract]:
                    self._by_contract[contract].remove(plugin_id)

            # Remove plugin
            del self._plugins[plugin_id]
            return True

    # =========================================================================
    # Retrieval
    # =========================================================================

    def get(self, plugin_id: str) -> PluginDescriptor:
        """Get a plugin descriptor.

        Args:
            plugin_id: Plugin ID.

        Returns:
            Plugin descriptor.

        Raises:
            PluginNotFoundError: If plugin not found.
        """
        with self._lock:
            if plugin_id not in self._plugins:
                raise PluginNotFoundError(plugin_id)
            return self._plugins[plugin_id]

    def get_or_none(self, plugin_id: str) -> PluginDescriptor | None:
        """Get a plugin descriptor or None.

        Args:
            plugin_id: Plugin ID.

        Returns:
            Plugin descriptor or None.
        """
        with self._lock:
            return self._plugins.get(plugin_id)

    def has(self, plugin_id: str) -> bool:
        """Check if plugin is registered.

        Args:
            plugin_id: Plugin ID.

        Returns:
            True if registered.
        """
        with self._lock:
            return plugin_id in self._plugins

    # =========================================================================
    # Queries
    # =========================================================================

    def list_all(self) -> list[PluginDescriptor]:
        """List all registered plugins.

        Returns:
            List of plugin descriptors.
        """
        with self._lock:
            return list(self._plugins.values())

    def list_by_state(self, state: PluginState) -> list[PluginDescriptor]:
        """List plugins by state.

        Args:
            state: Plugin state.

        Returns:
            List of plugins in the state.
        """
        with self._lock:
            return [p for p in self._plugins.values() if p.state == state]

    def list_by_category(self, category: PluginCategory) -> list[PluginDescriptor]:
        """List plugins by category.

        Args:
            category: Plugin category.

        Returns:
            List of plugins in the category.
        """
        with self._lock:
            plugin_ids = self._by_category.get(category, [])
            return [self._plugins[pid] for pid in plugin_ids if pid in self._plugins]

    def list_by_contract(self, contract: str) -> list[PluginDescriptor]:
        """List plugins implementing a contract.

        Args:
            contract: Contract name.

        Returns:
            List of plugins implementing the contract.
        """
        with self._lock:
            plugin_ids = self._by_contract.get(contract, [])
            return [self._plugins[pid] for pid in plugin_ids if pid in self._plugins]

    def list_active(self) -> list[PluginDescriptor]:
        """List all active plugins.

        Returns:
            List of active plugins.
        """
        return self.list_by_state(PluginState.ACTIVE)

    def list_with_capability(self, capability: str) -> list[PluginDescriptor]:
        """List plugins with a specific capability.

        Args:
            capability: Capability name.

        Returns:
            List of plugins with the capability.
        """
        with self._lock:
            return [
                p for p in self._plugins.values()
                if capability in p.manifest.capabilities
            ]

    # =========================================================================
    # Counts
    # =========================================================================

    def count(self) -> int:
        """Get total plugin count."""
        with self._lock:
            return len(self._plugins)

    def count_by_state(self, state: PluginState) -> int:
        """Get plugin count by state."""
        with self._lock:
            return len([p for p in self._plugins.values() if p.state == state])

    def count_by_category(self, category: PluginCategory) -> int:
        """Get plugin count by category."""
        with self._lock:
            return len(self._by_category.get(category, []))

    def active_count(self) -> int:
        """Get active plugin count."""
        return self.count_by_state(PluginState.ACTIVE)

    # =========================================================================
    # Factories
    # =========================================================================

    def register_factory(self, plugin_id: str, factory: Callable) -> None:
        """Register a plugin factory.

        Args:
            plugin_id: Plugin ID.
            factory: Factory function.
        """
        with self._lock:
            self._factories[plugin_id] = factory

    def get_factory(self, plugin_id: str) -> Callable | None:
        """Get a plugin factory.

        Args:
            plugin_id: Plugin ID.

        Returns:
            Factory function or None.
        """
        with self._lock:
            return self._factories.get(plugin_id)

    def has_factory(self, plugin_id: str) -> bool:
        """Check if factory exists for plugin."""
        with self._lock:
            return plugin_id in self._factories

    # =========================================================================
    # Dependency Resolution
    # =========================================================================

    def get_dependencies(self, plugin_id: str) -> list[PluginDescriptor]:
        """Get plugin dependencies.

        Args:
            plugin_id: Plugin ID.

        Returns:
            List of dependency descriptors.
        """
        with self._lock:
            if plugin_id not in self._plugins:
                return []

            plugin = self._plugins[plugin_id]
            dependencies = []

            for dep_id in plugin.manifest.dependencies:
                if dep_id in self._plugins:
                    dependencies.append(self._plugins[dep_id])

            return dependencies

    def check_dependencies(self, plugin_id: str) -> tuple[bool, list[str]]:
        """Check if all dependencies are satisfied.

        Args:
            plugin_id: Plugin ID.

        Returns:
            Tuple of (all_satisfied, missing_dependencies).
        """
        with self._lock:
            if plugin_id not in self._plugins:
                return False, []

            plugin = self._plugins[plugin_id]
            missing = []

            for dep_id in plugin.manifest.dependencies:
                if dep_id not in self._plugins:
                    missing.append(dep_id)
                elif self._plugins[dep_id].state != PluginState.ACTIVE:
                    missing.append(dep_id)

            return len(missing) == 0, missing

    # =========================================================================
    # Utility
    # =========================================================================

    def clear(self) -> None:
        """Clear all registrations."""
        with self._lock:
            self._plugins.clear()
            self._by_category.clear()
            self._by_contract.clear()
            self._factories.clear()

    def __len__(self) -> int:
        """Get plugin count."""
        with self._lock:
            return len(self._plugins)

    def __contains__(self, plugin_id: str) -> bool:
        """Check if plugin is registered."""
        return self.has(plugin_id)


# Global registry instance
_global_registry: PluginRegistry | None = None
_registry_lock = threading.Lock()


def get_plugin_registry() -> PluginRegistry:
    """Get the global plugin registry.

    Returns:
        Global PluginRegistry instance.
    """
    global _global_registry
    with _registry_lock:
        if _global_registry is None:
            _global_registry = PluginRegistry()
        return _global_registry


def reset_plugin_registry() -> None:
    """Reset the global registry."""
    global _global_registry
    with _registry_lock:
        if _global_registry is not None:
            _global_registry.clear()
        _global_registry = None
