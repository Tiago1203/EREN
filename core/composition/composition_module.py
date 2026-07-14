"""Composition Module for the Cognitive Composition Root.

Base module classes for EREN composition.

Architecture only -- no implementations.
"""

from typing import Any

from .module_descriptor import ModuleDescriptor


class CompositionModule:
    """Base class for composition modules.

    All EREN modules should inherit from this class.
    """

    def __init__(self, name: str):
        """Initialize the module.

        Args:
            name: Module name.
        """
        self._name = name
        self._descriptor: ModuleDescriptor | None = None

    @property
    def name(self) -> str:
        """Get module name."""
        return self._name

    def get_descriptor(self) -> ModuleDescriptor:
        """Get module descriptor.

        Returns:
            Module descriptor.
        """
        if self._descriptor is None:
            self._descriptor = self._create_descriptor()
        return self._descriptor

    def _create_descriptor(self) -> ModuleDescriptor:
        """Create module descriptor.

        Override in subclasses.

        Returns:
            Module descriptor.
        """
        return ModuleDescriptor(
            module_name=self._name,
            module_type=self.get_module_type(),
            description=self.get_description(),
        )

    def get_module_type(self) -> str:
        """Get module type.

        Override in subclasses.

        Returns:
            Module type.
        """
        return "core"

    def get_description(self) -> str:
        """Get module description.

        Override in subclasses.

        Returns:
            Description.
        """
        return f"Module: {self._name}"

    def register(self, container: Any) -> None:
        """Register module contracts.

        Override in subclasses.

        Args:
            container: DI container.
        """
        pass

    def initialize(self, container: Any) -> None:
        """Initialize module.

        Override in subclasses.

        Args:
            container: DI container.
        """
        pass

    def validate(self) -> bool:
        """Validate module configuration.

        Override in subclasses.

        Returns:
            True if valid.
        """
        return True


# Pre-defined module types
class CoreModule(CompositionModule):
    """Base class for core modules."""

    def get_module_type(self) -> str:
        return "core"


class InfrastructureModule(CompositionModule):
    """Base class for infrastructure modules."""

    def get_module_type(self) -> str:
        return "infrastructure"


class CognitiveModule(CompositionModule):
    """Base class for cognitive modules."""

    def get_module_type(self) -> str:
        return "cognitive"


class CapabilityModule(CompositionModule):
    """Base class for capability modules."""

    def get_module_type(self) -> str:
        return "capability"
