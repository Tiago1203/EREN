"""Module Loader for the Cognitive Composition Root.

Loads modules with various strategies.

Architecture only -- no implementations.
"""

import threading
from typing import Callable, Optional

from .module_descriptor import ModuleDescriptor
from .module_registry import ModuleRegistry


class LoadStrategy:
    """Strategies for loading modules."""

    MANUAL = "manual"
    AUTO = "auto"
    BY_CONFIG = "by_config"
    BY_CAPABILITY = "by_capability"
    BY_TAG = "by_tag"
    CONDITIONAL = "conditional"


class ModuleLoader:
    """Loads modules with various strategies.

    Supports:
    - Manual loading
    - Automatic loading
    - Configuration-based loading
    - Capability-based loading
    - Tag-based loading
    - Conditional loading
    """

    def __init__(self, registry: ModuleRegistry):
        """Initialize the loader.

        Args:
            registry: Module registry.
        """
        self._registry = registry
        self._load_order: list[str] = []
        self._load_conditions: dict[str, Callable[[], bool]] = {}
        self._lock = threading.RLock()

    def load(self, module: ModuleDescriptor) -> bool:
        """Load a single module.

        Args:
            module: Module to load.

        Returns:
            True if loaded successfully.
        """
        with self._lock:
            if module.module_name in self._load_order:
                return False

            # Check conditional loading
            if module.module_name in self._load_conditions:
                if not self._load_conditions[module.module_name]():
                    return False

            # Add to load order respecting dependencies
            self._add_with_dependencies(module)
            return True

    def load_all(self, modules: list[ModuleDescriptor]) -> list[str]:
        """Load all modules.

        Args:
            modules: Modules to load.

        Returns:
            List of loaded module names.
        """
        with self._lock:
            loaded = []

            # Sort by dependencies
            sorted_modules = self._topological_sort(modules)

            for module in sorted_modules:
                if self.load(module):
                    loaded.append(module.module_name)

            return loaded

    def load_by_tag(self, tag: str, modules: list[ModuleDescriptor]) -> list[str]:
        """Load modules with a specific tag.

        Args:
            tag: Tag to filter by.
            modules: All available modules.

        Returns:
            List of loaded module names.
        """
        filtered = [m for m in modules if tag in m.tags]
        return self.load_all(filtered)

    def load_by_capability(
        self,
        capability: str,
        modules: list[ModuleDescriptor],
    ) -> list[str]:
        """Load modules with a specific capability.

        Args:
            capability: Capability to filter by.
            modules: All available modules.

        Returns:
            List of loaded module names.
        """
        filtered = [m for m in modules if capability in m.capabilities]
        return self.load_all(filtered)

    def load_by_config(
        self,
        config: dict,
        modules: list[ModuleDescriptor],
    ) -> list[str]:
        """Load modules based on configuration.

        Args:
            config: Configuration dict.
            modules: All available modules.

        Returns:
            List of loaded module names.
        """
        loaded = []

        # Load explicitly enabled modules
        if "modules" in config:
            enabled = config["modules"]
            if isinstance(enabled, list):
                for module in modules:
                    if module.module_name in enabled:
                        if self.load(module):
                            loaded.append(module.module_name)

        # Load by tags
        if "tags" in config:
            tags = config["tags"]
            if isinstance(tags, list):
                for tag in tags:
                    tagged = self.load_by_tag(tag, modules)
                    loaded.extend(tagged)

        # Load by capabilities
        if "capabilities" in config:
            caps = config["capabilities"]
            if isinstance(caps, list):
                for cap in caps:
                    capable = self.load_by_capability(cap, modules)
                    loaded.extend(capable)

        return list(set(loaded))

    def register_condition(
        self,
        module_name: str,
        condition: Callable[[], bool],
    ) -> None:
        """Register a condition for conditional loading.

        Args:
            module_name: Module to condition.
            condition: Function that returns True if should load.
        """
        with self._lock:
            self._load_conditions[module_name] = condition

    def _add_with_dependencies(self, module: ModuleDescriptor) -> None:
        """Add module respecting dependencies.

        Args:
            module: Module to add.
        """
        # Add dependencies first
        for dep in module.dependencies:
            dep_module = self._registry.get(dep.module_name)
            if dep_module and dep.module_name not in self._load_order:
                self._add_with_dependencies(dep_module)

        # Add this module
        if module.module_name not in self._load_order:
            self._load_order.append(module.module_name)

    def _topological_sort(
        self,
        modules: list[ModuleDescriptor],
    ) -> list[ModuleDescriptor]:
        """Sort modules topologically by dependencies.

        Args:
            modules: Modules to sort.

        Returns:
            Sorted list of modules.
        """
        sorted_modules = []
        visited = set()
        temp_visited = set()

        def visit(m: ModuleDescriptor) -> None:
            if m.module_name in temp_visited:
                # Cycle detected - skip for now
                return
            if m.module_name in visited:
                return

            temp_visited.add(m.module_name)

            # Visit dependencies first
            for dep in m.dependencies:
                dep_module = self._registry.get(dep.module_name)
                if dep_module:
                    visit(dep_module)

            temp_visited.remove(m.module_name)
            visited.add(m.module_name)
            sorted_modules.append(m)

        for module in modules:
            if module.module_name not in visited:
                visit(module)

        return sorted_modules

    def get_load_order(self) -> list[str]:
        """Get the load order.

        Returns:
            List of module names in load order.
        """
        with self._lock:
            return list(self._load_order)

    def clear(self) -> None:
        """Clear the load order."""
        with self._lock:
            self._load_order.clear()
            self._load_conditions.clear()
