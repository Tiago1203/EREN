"""Plugin Context for EREN OS Cognitive Plugin Framework.

Provides context information for plugins during lifecycle operations.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass


@dataclass
class PluginContext:
    """Context passed to plugins during lifecycle operations.

    Contains all information a plugin needs to initialize and operate.
    """

    # Identity
    plugin_id: str = ""
    plugin_version: str = ""

    # Runtime information
    runtime_config: dict = field(default_factory=dict)
    runtime_id: str = ""
    environment: str = "production"

    # Dependency context
    dependency_context: dict = field(default_factory=dict)
    available_plugins: dict = field(default_factory=dict)

    # Service references (via contracts)
    capability_registry: Any = None
    event_bus: Any = None
    container: Any = None

    # Configuration
    plugin_config: dict = field(default_factory=dict)

    # Metadata
    metadata: dict = field(default_factory=dict)

    # Thread safety
    _lock: threading.RLock = field(default_factory=threading.RLock, repr=False)

    def __post_init__(self) -> None:
        """Initialize thread lock."""
        if self._lock is None:
            self._lock = threading.RLock()

    # =========================================================================
    # Dependency Access
    # =========================================================================

    def get_dependency(self, plugin_id: str) -> Any | None:
        """Get a dependency plugin instance.

        Args:
            plugin_id: Plugin ID of dependency.

        Returns:
            Plugin instance or None.
        """
        with self._lock:
            return self.dependency_context.get(plugin_id)

    def has_dependency(self, plugin_id: str) -> bool:
        """Check if a dependency is available.

        Args:
            plugin_id: Plugin ID.

        Returns:
            True if dependency is available.
        """
        with self._lock:
            return plugin_id in self.dependency_context

    def get_all_dependencies(self) -> dict[str, Any]:
        """Get all available dependencies.

        Returns:
            Dictionary of plugin_id -> instance.
        """
        with self._lock:
            return dict(self.dependency_context)

    # =========================================================================
    # Service Access
    # =========================================================================

    def get_capability(self, capability_name: str) -> Any | None:
        """Get a capability from the registry.

        Args:
            capability_name: Capability name.

        Returns:
            Capability instance or None.
        """
        if self.capability_registry:
            return self.capability_registry.get(capability_name)
        return None

    def has_capability(self, capability_name: str) -> bool:
        """Check if a capability is available.

        Args:
            capability_name: Capability name.

        Returns:
            True if capability is available.
        """
        if self.capability_registry:
            return self.capability_registry.has(capability_name)
        return False

    def publish_event(self, event_type: str, data: dict | None = None) -> None:
        """Publish an event.

        Args:
            event_type: Event type.
            data: Event data.
        """
        if self.event_bus:
            self.event_bus.publish(event_type, self.plugin_id, data or {})

    # =========================================================================
    # Configuration Access
    # =========================================================================

    def get_config(self, key: str, default: Any = None) -> Any:
        """Get a configuration value.

        Args:
            key: Configuration key.
            default: Default value.

        Returns:
            Configuration value or default.
        """
        with self._lock:
            return self.plugin_config.get(key, default)

    def set_config(self, key: str, value: Any) -> None:
        """Set a configuration value.

        Args:
            key: Configuration key.
            value: Configuration value.
        """
        with self._lock:
            self.plugin_config[key] = value

    def get_runtime_config(self, key: str, default: Any = None) -> Any:
        """Get a runtime configuration value.

        Args:
            key: Configuration key.
            default: Default value.

        Returns:
            Configuration value or default.
        """
        with self._lock:
            return self.runtime_config.get(key, default)

    # =========================================================================
    # Metadata Access
    # =========================================================================

    def set_metadata(self, key: str, value: Any) -> None:
        """Set metadata.

        Args:
            key: Metadata key.
            value: Metadata value.
        """
        with self._lock:
            self.metadata[key] = value

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata.

        Args:
            key: Metadata key.
            default: Default value.

        Returns:
            Metadata value or default.
        """
        with self._lock:
            return self.metadata.get(key, default)

    # =========================================================================
    # Utility
    # =========================================================================

    def to_dict(self) -> dict:
        """Convert to dictionary.

        Returns:
            Dictionary representation.
        """
        with self._lock:
            return {
                "plugin_id": self.plugin_id,
                "plugin_version": self.plugin_version,
                "runtime_config": dict(self.runtime_config),
                "runtime_id": self.runtime_id,
                "environment": self.environment,
                "dependency_context": list(self.dependency_context.keys()),
                "available_plugins": list(self.available_plugins.keys()),
                "plugin_config": dict(self.plugin_config),
                "metadata": dict(self.metadata),
            }

    def copy(self) -> "PluginContext":
        """Create a copy of the context.

        Returns:
            New PluginContext copy.
        """
        with self._lock:
            return PluginContext(
                plugin_id=self.plugin_id,
                plugin_version=self.plugin_version,
                runtime_config=dict(self.runtime_config),
                runtime_id=self.runtime_id,
                environment=self.environment,
                dependency_context=dict(self.dependency_context),
                available_plugins=dict(self.available_plugins),
                capability_registry=self.capability_registry,
                event_bus=self.event_bus,
                container=self.container,
                plugin_config=dict(self.plugin_config),
                metadata=dict(self.metadata),
            )
