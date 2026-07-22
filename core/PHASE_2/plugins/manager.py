"""Plugin Manager for EREN OS Cognitive Plugin Framework.

Main manager for plugin lifecycle and coordination.
"""

from __future__ import annotations

import threading
from collections.abc import Callable
from typing import TYPE_CHECKING

from core.PHASE_2.plugins.context import PluginContext
from core.PHASE_2.plugins.descriptor import PluginDescriptor
from core.PHASE_2.plugins.exceptions import (
    PluginActivationError,
    PluginException,
    PluginNotFoundError,
)
from core.PHASE_2.plugins.loader import PluginLoader
from core.PHASE_2.plugins.registry import PluginRegistry, get_plugin_registry
from core.PHASE_2.plugins.types import (
    PluginCategory,
    PluginPolicy,
    PluginState,
    ValidationResult,
)

if TYPE_CHECKING:
    pass


class PluginManager:
    """Main plugin manager.

    Coordinates plugin lifecycle:
    1. Discover
    2. Validate
    3. Load
    4. Initialize
    5. Register
    6. Activate
    """

    def __init__(
        self,
        registry: PluginRegistry | None = None,
        loader: PluginLoader | None = None,
        default_policy: PluginPolicy = PluginPolicy.GRACEFUL,
    ):
        """Initialize the plugin manager.

        Args:
            registry: Plugin registry.
            loader: Plugin loader.
            default_policy: Default plugin policy.
        """
        self._registry = registry or get_plugin_registry()
        self._loader = loader or PluginLoader()
        self._default_policy = default_policy

        # Event handlers
        self._event_handlers: dict[str, list[Callable]] = {}

        # Statistics
        self._load_count = 0
        self._activation_count = 0
        self._failure_count = 0
        self._lock = threading.RLock()

    # =========================================================================
    # Discovery
    # =========================================================================

    def discover(self, manifest: dict | str) -> PluginDescriptor:
        """Discover a plugin from manifest.

        Args:
            manifest: Manifest dict or path.

        Returns:
            Plugin descriptor.

        Raises:
            PluginException: If discovery fails.
        """
        from core.PHASE_2.plugins.manifest import PluginManifestParser

        if isinstance(manifest, str):
            # Assume it's a path
            manifest_data = PluginManifestParser.from_file(manifest)
        else:
            manifest_data = PluginManifestParser.from_dict(manifest)

        descriptor = PluginDescriptor(manifest=manifest_data)
        descriptor.transition_to(PluginState.DISCOVERED)

        return descriptor

    def discover_from_directory(self, directory: str) -> list[PluginDescriptor]:
        """Discover all plugins in a directory.

        Args:
            directory: Directory path.

        Returns:
            List of discovered plugins.
        """
        return self._loader.load_from_directory(directory)

    # =========================================================================
    # Validation
    # =========================================================================

    def validate(self, descriptor: PluginDescriptor) -> ValidationResult:
        """Validate a plugin.

        Args:
            descriptor: Plugin descriptor.

        Returns:
            Validation result.
        """
        result = ValidationResult(is_valid=True)

        # Check manifest
        if not descriptor.manifest.plugin_id:
            result.is_valid = False
            result.manifest_valid = False
            result.errors.append("Missing plugin_id in manifest")

        if not descriptor.manifest.version:
            result.is_valid = False
            result.manifest_valid = False
            result.errors.append("Missing version in manifest")

        # Check dependencies
        all_plugins = self._registry.list_all()
        plugin_ids = {p.plugin_id for p in all_plugins}

        for dep_id in descriptor.manifest.dependencies:
            if dep_id not in plugin_ids:
                result.is_valid = False
                result.dependencies_satisfied = False
                result.errors.append(f"Missing dependency: {dep_id}")

            # Check if dependency is active
            dep = self._registry.get_or_none(dep_id)
            if dep and dep.state != PluginState.ACTIVE:
                result.warnings.append(
                    f"Dependency '{dep_id}' is not active (state: {dep.state.value})"
                )

        return result

    # =========================================================================
    # Registration
    # =========================================================================

    def register(self, descriptor: PluginDescriptor) -> None:
        """Register a plugin.

        Args:
            descriptor: Plugin descriptor.

        Raises:
            PluginAlreadyRegisteredError: If plugin already registered.
        """
        # Validate first
        result = self.validate(descriptor)
        if not result.is_valid:
            raise PluginException(
                f"Plugin validation failed: {result.errors}",
            )

        descriptor.transition_to(PluginState.REGISTERED)
        self._registry.register(descriptor)

        self._emit_event("PluginRegistered", {
            "plugin_id": descriptor.plugin_id,
            "state": descriptor.state.value,
        })

    def unregister(self, plugin_id: str) -> bool:
        """Unregister a plugin.

        Args:
            plugin_id: Plugin ID.

        Returns:
            True if unregistered.
        """
        if plugin_id not in self._registry:
            return False

        descriptor = self._registry.get(plugin_id)

        # Deactivate first if active
        if descriptor.is_active:
            self.deactivate(plugin_id)

        descriptor.transition_to(PluginState.UNLOADED)
        result = self._registry.unregister(plugin_id)

        if result:
            self._emit_event("PluginUnregistered", {
                "plugin_id": plugin_id,
            })

        return result

    # =========================================================================
    # Lifecycle
    # =========================================================================

    def load(self, plugin_id: str, context: PluginContext | None = None) -> bool:
        """Load a plugin.

        Args:
            plugin_id: Plugin ID.
            context: Optional plugin context.

        Returns:
            True if loaded successfully.
        """
        if plugin_id not in self._registry:
            raise PluginNotFoundError(plugin_id)

        descriptor = self._registry.get(plugin_id)

        # Create context if not provided
        if context is None:
            context = self._create_context(descriptor)

        # Load the plugin
        success = self._loader.initialize_plugin(descriptor, context)

        if success:
            descriptor.transition_to(PluginState.LOADED)
            self._load_count += 1
            self._emit_event("PluginLoaded", {
                "plugin_id": plugin_id,
            })
        else:
            self._failure_count += 1
            self._emit_event("PluginLoadFailed", {
                "plugin_id": plugin_id,
                "error": descriptor.error,
            })

        return success

    def initialize(self, plugin_id: str, context: PluginContext | None = None) -> bool:
        """Initialize a plugin.

        Args:
            plugin_id: Plugin ID.
            context: Optional plugin context.

        Returns:
            True if initialized successfully.
        """
        if plugin_id not in self._registry:
            raise PluginNotFoundError(plugin_id)

        descriptor = self._registry.get(plugin_id)

        if not descriptor.is_loaded:
            # Load first
            if not self.load(plugin_id, context):
                return False

        # Create context if not provided
        if context is None:
            context = self._create_context(descriptor)

        # Initialize
        try:
            if descriptor.instance and hasattr(descriptor.instance, "on_initialize"):
                descriptor.instance.on_initialize(context)

            descriptor.transition_to(PluginState.INITIALIZED)
            self._emit_event("PluginInitialized", {
                "plugin_id": plugin_id,
            })
            return True

        except Exception as e:
            descriptor.set_error(str(e))
            descriptor.transition_to(PluginState.FAILED)
            self._failure_count += 1
            self._emit_event("PluginInitializationFailed", {
                "plugin_id": plugin_id,
                "error": str(e),
            })
            return False

    def activate(self, plugin_id: str) -> bool:
        """Activate a plugin.

        Args:
            plugin_id: Plugin ID.

        Returns:
            True if activated successfully.
        """
        if plugin_id not in self._registry:
            raise PluginNotFoundError(plugin_id)

        descriptor = self._registry.get(plugin_id)

        # Check dependencies
        deps_satisfied, missing = self._registry.check_dependencies(plugin_id)
        if not deps_satisfied:
            raise PluginActivationError(
                f"Dependencies not satisfied: {missing}",
                plugin_id,
            )

        # Activate
        try:
            if descriptor.instance and hasattr(descriptor.instance, "on_activate"):
                descriptor.instance.on_activate()

            descriptor.transition_to(PluginState.ACTIVE)
            descriptor.clear_error()
            self._activation_count += 1

            self._emit_event("PluginActivated", {
                "plugin_id": plugin_id,
            })
            return True

        except Exception as e:
            descriptor.set_error(str(e))
            descriptor.transition_to(PluginState.FAILED)
            self._failure_count += 1
            self._emit_event("PluginActivationFailed", {
                "plugin_id": plugin_id,
                "error": str(e),
            })
            return False

    def deactivate(self, plugin_id: str) -> bool:
        """Deactivate a plugin.

        Args:
            plugin_id: Plugin ID.

        Returns:
            True if deactivated successfully.
        """
        if plugin_id not in self._registry:
            raise PluginNotFoundError(plugin_id)

        descriptor = self._registry.get(plugin_id)

        try:
            if descriptor.instance and hasattr(descriptor.instance, "on_deactivate"):
                descriptor.instance.on_deactivate()

            descriptor.transition_to(PluginState.PAUSED)

            self._emit_event("PluginDeactivated", {
                "plugin_id": plugin_id,
            })
            return True

        except Exception as e:
            descriptor.set_error(str(e))
            return False

    def reload(self, plugin_id: str) -> bool:
        """Reload a plugin.

        Args:
            plugin_id: Plugin ID.

        Returns:
            True if reloaded successfully.
        """
        if plugin_id not in self._registry:
            raise PluginNotFoundError(plugin_id)

        descriptor = self._registry.get(plugin_id)

        # Deactivate if active
        if descriptor.is_active:
            self.deactivate(plugin_id)

        # Unload
        descriptor.transition_to(PluginState.UNLOADED)

        # Reload
        success = self.load(plugin_id)

        if success:
            self._emit_event("PluginReloaded", {
                "plugin_id": plugin_id,
            })

        return success

    # =========================================================================
    # Bulk Operations
    # =========================================================================

    def activate_all(self) -> dict[str, bool]:
        """Activate all registered plugins.

        Returns:
            Dictionary of plugin_id -> success.
        """
        results = {}
        plugins = self._registry.list_all()

        # Sort by priority (higher first)
        plugins.sort(key=lambda p: p.priority, reverse=True)

        for plugin in plugins:
            if plugin.state in (PluginState.REGISTERED, PluginState.INITIALIZED):
                results[plugin.plugin_id] = self.activate(plugin.plugin_id)

        return results

    def deactivate_all(self) -> dict[str, bool]:
        """Deactivate all active plugins.

        Returns:
            Dictionary of plugin_id -> success.
        """
        results = {}
        active_plugins = self._registry.list_active()

        # Sort by priority (lower first)
        active_plugins.sort(key=lambda p: p.priority)

        for plugin in active_plugins:
            results[plugin.plugin_id] = self.deactivate(plugin.plugin_id)

        return results

    # =========================================================================
    # Context Creation
    # =========================================================================

    def _create_context(self, descriptor: PluginDescriptor) -> PluginContext:
        """Create plugin context.

        Args:
            descriptor: Plugin descriptor.

        Returns:
            Plugin context.
        """
        # Get dependency instances
        dependencies = {}
        for dep_id in descriptor.manifest.dependencies:
            dep = self._registry.get_or_none(dep_id)
            if dep and dep.instance:
                dependencies[dep_id] = dep.instance

        return PluginContext(
            plugin_id=descriptor.plugin_id,
            plugin_version=descriptor.version,
            dependency_context=dependencies,
            plugin_config=descriptor.manifest.configuration,
        )

    # =========================================================================
    # Event Handling
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
    # Statistics
    # =========================================================================

    def get_statistics(self) -> dict:
        """Get plugin statistics.

        Returns:
            Dictionary with statistics.
        """
        with self._lock:
            return {
                "total_plugins": self._registry.count(),
                "active_plugins": self._registry.active_count(),
                "loaded_count": self._load_count,
                "activation_count": self._activation_count,
                "failure_count": self._failure_count,
                "by_state": {
                    state.value: self._registry.count_by_state(state)
                    for state in PluginState
                },
                "by_category": {
                    cat.value: self._registry.count_by_category(cat)
                    for cat in PluginCategory
                },
            }

    def to_dict(self) -> dict:
        """Convert to dictionary.

        Returns:
            Dictionary representation.
        """
        return {
            "default_policy": self._default_policy.value,
            "statistics": self.get_statistics(),
        }


# Global manager instance
_global_manager: PluginManager | None = None
_manager_lock = threading.Lock()


def get_plugin_manager() -> PluginManager:
    """Get the global plugin manager.

    Returns:
        Global PluginManager instance.
    """
    global _global_manager
    with _manager_lock:
        if _global_manager is None:
            _global_manager = PluginManager()
        return _global_manager
