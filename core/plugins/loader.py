"""Plugin Loader for EREN OS Cognitive Plugin Framework.

Handles plugin loading and initialization.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Type

from core.plugins.descriptor import PluginDescriptor
from core.plugins.manifest import PluginManifestParser
from core.plugins.types import PluginState, PluginContext
from core.plugins.exceptions import (
    PluginLoadError,
    PluginLoaderError,
    PluginManifestError,
)

if TYPE_CHECKING:
    pass


class PluginLoader:
    """Loads plugins from various sources.

    Supports:
    - Python modules
    - Python files
    - Plugin directories
    - Custom loaders
    """

    def __init__(self):
        """Initialize the loader."""
        self._loaders: dict[str, Callable] = {}
        self._loaded_modules: dict[str, Any] = {}
        self._plugin_factories: dict[str, Type] = {}

    # =========================================================================
    # Registration
    # =========================================================================

    def register_loader(self, source_type: str, loader: Callable) -> None:
        """Register a custom loader.

        Args:
            source_type: Source type identifier.
            loader: Loader function.
        """
        self._loaders[source_type] = loader

    def register_factory(self, plugin_id: str, factory: Type) -> None:
        """Register a plugin factory.

        Args:
            plugin_id: Plugin ID.
            factory: Plugin factory class.
        """
        self._plugin_factories[plugin_id] = factory

    # =========================================================================
    # Loading
    # =========================================================================

    def load_from_manifest(self, manifest_path: str | Path) -> PluginDescriptor:
        """Load plugin from manifest file.

        Args:
            manifest_path: Path to plugin manifest.

        Returns:
            Plugin descriptor.

        Raises:
            PluginManifestError: If manifest is invalid.
            PluginLoadError: If loading fails.
        """
        manifest = PluginManifestParser.from_file(manifest_path)
        return self.load_from_manifest_data(manifest)

    def load_from_manifest_data(self, manifest) -> PluginDescriptor:
        """Load plugin from manifest data.

        Args:
            manifest: Plugin manifest.

        Returns:
            Plugin descriptor.
        """
        descriptor = PluginDescriptor(manifest=manifest)
        descriptor.transition_to(PluginState.LOADED)
        return descriptor

    def load_from_module(
        self,
        module_name: str,
        class_name: str | None = None,
    ) -> PluginDescriptor:
        """Load plugin from Python module.

        Args:
            module_name: Module name to import.
            class_name: Optional class name in module.

        Returns:
            Plugin descriptor.

        Raises:
            PluginLoadError: If loading fails.
        """
        try:
            # Import module
            module = importlib.import_module(module_name)
            self._loaded_modules[module_name] = module

            # Get plugin class
            if class_name:
                plugin_class = getattr(module, class_name)
            else:
                # Look for plugin class
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if isinstance(attr, type) and hasattr(attr, "get_manifest"):
                        plugin_class = attr
                        break
                else:
                    raise PluginLoadError(
                        f"No plugin class found in module: {module_name}",
                        module_name,
                    )

            # Create instance
            instance = plugin_class()

            # Get manifest
            manifest = getattr(instance, "get_manifest", lambda: None)()
            if not manifest:
                raise PluginLoadError(
                    f"Plugin does not provide manifest: {module_name}",
                    module_name,
                )

            # Create descriptor
            descriptor = PluginDescriptor(
                manifest=manifest,
                instance=instance,
                factory=plugin_class,
            )
            descriptor.transition_to(PluginState.LOADED)

            return descriptor

        except ImportError as e:
            raise PluginLoadError(
                f"Failed to import module: {e}",
                module_name,
            ) from e
        except Exception as e:
            raise PluginLoadError(
                f"Failed to load plugin: {e}",
                module_name,
            ) from e

    def load_from_file(self, file_path: str | Path) -> PluginDescriptor:
        """Load plugin from Python file.

        Args:
            file_path: Path to plugin file.

        Returns:
            Plugin descriptor.

        Raises:
            PluginLoadError: If loading fails.
        """
        file_path = Path(file_path)

        try:
            # Load module from file
            spec = importlib.util.spec_from_file_location(
                f"plugin_{file_path.stem}",
                file_path,
            )
            if not spec or not spec.loader:
                raise PluginLoadError(
                    f"Failed to load plugin file: {file_path}",
                    str(file_path),
                )

            module = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = module
            spec.loader.exec_module(module)

            self._loaded_modules[file_path.stem] = module

            # Find plugin class
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if isinstance(attr, type) and hasattr(attr, "get_manifest"):
                    plugin_class = attr
                    break
            else:
                raise PluginLoadError(
                    f"No plugin class found in file: {file_path}",
                    str(file_path),
                )

            # Create instance
            instance = plugin_class()

            # Get manifest
            manifest = getattr(instance, "get_manifest", lambda: None)()
            if not manifest:
                raise PluginLoadError(
                    f"Plugin does not provide manifest: {file_path}",
                    str(file_path),
                )

            # Create descriptor
            descriptor = PluginDescriptor(
                manifest=manifest,
                instance=instance,
                factory=plugin_class,
            )
            descriptor.transition_to(PluginState.LOADED)

            return descriptor

        except Exception as e:
            if isinstance(e, PluginLoadError):
                raise
            raise PluginLoadError(
                f"Failed to load plugin from file: {e}",
                str(file_path),
            ) from e

    def load_from_directory(
        self,
        directory: str | Path,
        pattern: str = "*.json",
    ) -> list[PluginDescriptor]:
        """Load all plugins from a directory.

        Args:
            directory: Directory to scan.
            pattern: File pattern to match.

        Returns:
            List of plugin descriptors.
        """
        directory = Path(directory)
        descriptors = []

        if not directory.exists():
            return descriptors

        for manifest_file in directory.glob(pattern):
            try:
                descriptor = self.load_from_manifest(manifest_file)
                descriptors.append(descriptor)
            except PluginManifestError:
                continue

        return descriptors

    # =========================================================================
    # Instantiation
    # =========================================================================

    def create_instance(self, descriptor: PluginDescriptor) -> Any:
        """Create a plugin instance.

        Args:
            descriptor: Plugin descriptor.

        Returns:
            Plugin instance.
        """
        if descriptor.instance:
            return descriptor.instance

        if descriptor.factory:
            return descriptor.factory()

        # Try to find registered factory
        factory = self._plugin_factories.get(descriptor.plugin_id)
        if factory:
            return factory()

        raise PluginLoadError(
            f"No factory found for plugin: {descriptor.plugin_id}",
            descriptor.plugin_id,
        )

    def initialize_plugin(
        self,
        descriptor: PluginDescriptor,
        context: PluginContext,
    ) -> bool:
        """Initialize a plugin.

        Args:
            descriptor: Plugin descriptor.
            context: Plugin context.

        Returns:
            True if initialization succeeded.
        """
        try:
            instance = self.create_instance(descriptor)

            # Call initialize if available
            if hasattr(instance, "initialize"):
                instance.initialize(context)

            # Call on_load if available
            if hasattr(instance, "on_load"):
                instance.on_load(context)

            descriptor.instance = instance
            descriptor.transition_to(PluginState.INITIALIZED)
            return True

        except Exception as e:
            descriptor.set_error(str(e))
            descriptor.transition_to(PluginState.FAILED)
            return False

    # =========================================================================
    # Utility
    # =========================================================================

    def get_loaded_modules(self) -> dict[str, Any]:
        """Get all loaded modules.

        Returns:
            Dictionary of module_name -> module.
        """
        return dict(self._loaded_modules)

    def is_loaded(self, module_name: str) -> bool:
        """Check if module is loaded.

        Args:
            module_name: Module name.

        Returns:
            True if loaded.
        """
        return module_name in self._loaded_modules
