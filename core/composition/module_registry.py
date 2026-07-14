"""Module Registry for the Cognitive Composition Root.

Central registry for all composition modules.

Architecture only -- no implementations.
"""

import threading

from .exceptions import (
    ModuleAlreadyRegisteredException,
)
from .module_descriptor import ModuleDescriptor, ModuleInstance


class ModuleRegistry:
    """Central registry for composition modules.

    Thread-safe registry that manages all module descriptors.
    """

    def __init__(self):
        """Initialize the registry."""
        # Map of module_name -> ModuleDescriptor
        self._modules: dict[str, ModuleDescriptor] = {}

        # Map of module_name -> ModuleInstance
        self._instances: dict[str, ModuleInstance] = {}

        # Map of tag -> list of module names
        self._by_tag: dict[str, list[str]] = {}

        # Map of capability -> list of module names
        self._by_capability: dict[str, list[str]] = {}

        # Thread safety
        self._lock = threading.RLock()

        # Statistics
        self._registration_count = 0

    def register(
        self,
        module: ModuleDescriptor,
        *,
        replace: bool = False,
    ) -> None:
        """Register a module.

        Args:
            module: Module descriptor.
            replace: Whether to replace existing registration.

        Raises:
            ModuleAlreadyRegisteredException: If module already exists.
        """
        with self._lock:
            if module.module_name in self._modules and not replace:
                raise ModuleAlreadyRegisteredException(module.module_name)

            self._modules[module.module_name] = module

            # Index by tags
            for tag in module.tags:
                if tag not in self._by_tag:
                    self._by_tag[tag] = []
                self._by_tag[tag].append(module.module_name)

            # Index by capabilities
            for capability in module.capabilities:
                if capability not in self._by_capability:
                    self._by_capability[capability] = []
                self._by_capability[capability].append(module.module_name)

            self._registration_count += 1

    def unregister(self, module_name: str) -> bool:
        """Unregister a module.

        Args:
            module_name: Name of the module to unregister.

        Returns:
            True if unregistered.
        """
        with self._lock:
            if module_name in self._modules:
                module = self._modules[module_name]

                # Remove from tag indexes
                for tag in module.tags:
                    if tag in self._by_tag:
                        self._by_tag[tag] = [
                            n for n in self._by_tag[tag] if n != module_name
                        ]

                # Remove from capability indexes
                for capability in module.capabilities:
                    if capability in self._by_capability:
                        self._by_capability[capability] = [
                            n for n in self._by_capability[capability]
                            if n != module_name
                        ]

                del self._modules[module_name]

                if module_name in self._instances:
                    del self._instances[module_name]

                return True
            return False

    def get(self, module_name: str) -> ModuleDescriptor | None:
        """Get a module descriptor.

        Args:
            module_name: Name of the module.

        Returns:
            Module descriptor or None.
        """
        with self._lock:
            return self._modules.get(module_name)

    def get_instance(self, module_name: str) -> ModuleInstance | None:
        """Get a module instance.

        Args:
            module_name: Name of the module.

        Returns:
            Module instance or None.
        """
        with self._lock:
            return self._instances.get(module_name)

    def create_instance(self, module_name: str) -> ModuleInstance | None:
        """Create a module instance.

        Args:
            module_name: Name of the module.

        Returns:
            Module instance or None.
        """
        with self._lock:
            descriptor = self._modules.get(module_name)
            if descriptor is None:
                return None

            instance = ModuleInstance(descriptor=descriptor)
            self._instances[module_name] = instance
            return instance

    def get_all(self) -> list[ModuleDescriptor]:
        """Get all module descriptors.

        Returns:
            List of all descriptors.
        """
        with self._lock:
            return list(self._modules.values())

    def get_all_names(self) -> list[str]:
        """Get all module names.

        Returns:
            List of module names.
        """
        with self._lock:
            return list(self._modules.keys())

    def find_by_tag(self, tag: str) -> list[ModuleDescriptor]:
        """Find modules by tag.

        Args:
            tag: Tag to search for.

        Returns:
            List of matching descriptors.
        """
        with self._lock:
            module_names = self._by_tag.get(tag, [])
            return [self._modules[name] for name in module_names if name in self._modules]

    def find_by_capability(self, capability: str) -> list[ModuleDescriptor]:
        """Find modules by capability.

        Args:
            capability: Capability to search for.

        Returns:
            List of matching descriptors.
        """
        with self._lock:
            module_names = self._by_capability.get(capability, [])
            return [self._modules[name] for name in module_names if name in self._modules]

    def find_by_type(self, module_type: str) -> list[ModuleDescriptor]:
        """Find modules by type.

        Args:
            module_type: Module type to search for.

        Returns:
            List of matching descriptors.
        """
        with self._lock:
            return [
                m for m in self._modules.values() if m.module_type == module_type
            ]

    def is_registered(self, module_name: str) -> bool:
        """Check if a module is registered.

        Args:
            module_name: Name of the module.

        Returns:
            True if registered.
        """
        with self._lock:
            return module_name in self._modules

    def clear(self) -> None:
        """Clear all registrations."""
        with self._lock:
            self._modules.clear()
            self._instances.clear()
            self._by_tag.clear()
            self._by_capability.clear()

    @property
    def module_count(self) -> int:
        """Get the number of registered modules."""
        with self._lock:
            return len(self._modules)

    @property
    def registration_count(self) -> int:
        """Get the number of registrations."""
        with self._lock:
            return self._registration_count

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        with self._lock:
            return {
                "modules": list(self._modules.keys()),
                "module_count": len(self._modules),
                "registration_count": self._registration_count,
                "tags": list(self._by_tag.keys()),
                "capabilities": list(self._by_capability.keys()),
            }
