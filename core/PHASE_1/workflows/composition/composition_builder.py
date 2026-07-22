"""Composition Builder for the Cognitive Composition Root.

Builder pattern for creating compositions.

Architecture only -- no implementations.
"""


from .composition_validator import CompositionValidator
from .exceptions import (
    CompositionBuildException,
    CompositionValidationException,
)
from .module_descriptor import ModuleDescriptor
from .module_loader import ModuleLoader
from .module_registry import ModuleRegistry


class CompositionBuilder:
    """Builder for creating compositions.

    Supports fluent API for module registration.
    """

    def __init__(self):
        """Initialize the builder."""
        self._registry = ModuleRegistry()
        self._loader = ModuleLoader(self._registry)
        self._modules: list[ModuleDescriptor] = []
        self._validated = False
        self._built = False

    def add_module(self, module: ModuleDescriptor) -> "CompositionBuilder":
        """Add a module.

        Args:
            module: Module descriptor.

        Returns:
            Self for chaining.
        """
        self._modules.append(module)
        self._registry.register(module)
        self._validated = False
        return self

    def add_default_modules(self) -> "CompositionBuilder":
        """Add default EREN modules.

        Returns:
            Self for chaining.
        """
        # Event Bus Module
        self.add_module(
            ModuleDescriptor(
                module_name="EventBusModule",
                module_type="infrastructure",
                description="Event Bus infrastructure",
                order=1,
            )
        )

        # Capability Registry Module
        self.add_module(
            ModuleDescriptor(
                module_name="CapabilityRegistryModule",
                module_type="infrastructure",
                description="Capability Registry",
                order=2,
            )
        )

        # Context Manager Module
        self.add_module(
            ModuleDescriptor(
                module_name="ContextManagerModule",
                module_type="infrastructure",
                description="Context Manager",
                order=3,
            )
        )

        # Memory Module
        self.add_module(
            ModuleDescriptor(
                module_name="MemoryModule",
                module_type="cognitive",
                description="Memory Engine",
                order=4,
            )
        )

        # Knowledge Module
        self.add_module(
            ModuleDescriptor(
                module_name="KnowledgeModule",
                module_type="cognitive",
                description="Knowledge Engine",
                order=5,
            )
        )

        # Tool Module
        self.add_module(
            ModuleDescriptor(
                module_name="ToolModule",
                module_type="cognitive",
                description="Tool Engine",
                order=6,
            )
        )

        # Planner Module
        self.add_module(
            ModuleDescriptor(
                module_name="PlannerModule",
                module_type="cognitive",
                description="Planner Engine",
                order=7,
            )
        )

        # Reasoning Module
        self.add_module(
            ModuleDescriptor(
                module_name="ReasoningModule",
                module_type="cognitive",
                description="Reasoning Engine",
                order=8,
            )
        )

        # Decision Module
        self.add_module(
            ModuleDescriptor(
                module_name="DecisionModule",
                module_type="cognitive",
                description="Decision Engine",
                order=9,
            )
        )

        # Scheduler Module
        self.add_module(
            ModuleDescriptor(
                module_name="SchedulerModule",
                module_type="infrastructure",
                description="Scheduler",
                order=10,
            )
        )

        # Session Module
        self.add_module(
            ModuleDescriptor(
                module_name="SessionModule",
                module_type="infrastructure",
                description="Session Manager",
                order=11,
            )
        )

        # Lifecycle Module
        self.add_module(
            ModuleDescriptor(
                module_name="LifecycleModule",
                module_type="infrastructure",
                description="Lifecycle Manager",
                order=12,
            )
        )

        # Orchestrator Module
        self.add_module(
            ModuleDescriptor(
                module_name="OrchestratorModule",
                module_type="infrastructure",
                description="Cognitive Orchestrator",
                order=13,
            )
        )

        # Boot Module
        self.add_module(
            ModuleDescriptor(
                module_name="BootModule",
                module_type="infrastructure",
                description="Boot Manager",
                order=14,
            )
        )

        return self

    def configure(self, **kwargs) -> "CompositionBuilder":
        """Configure the builder.

        Args:
            **kwargs: Configuration options.

        Returns:
            Self for chaining.
        """
        # Store configuration for later use
        self._config = kwargs
        return self

    def validate(self) -> "CompositionBuilder":
        """Validate the composition.

        Returns:
            Self for chaining.

        Raises:
            CompositionValidationException: If validation fails.
        """
        validator = CompositionValidator(self._registry)

        # Get required modules
        required_modules = [m.module_name for m in self._modules]

        result = validator.validate(required_modules=required_modules)

        if not result.is_valid:
            raise CompositionValidationException(
                "module_validation",
                [e.message for e in result.errors],
            )

        self._validated = True
        return self

    def build(self) -> dict:
        """Build the composition.

        Returns:
            Composition result dictionary.

        Raises:
            CompositionBuildException: If build fails.
        """
        if self._built:
            raise CompositionBuildException(
                "Composition already built",
                stage="build",
            )

        try:
            # Load modules
            loaded_modules = self._loader.load_all(self._modules)

            # Create result
            result = {
                "modules": loaded_modules,
                "module_count": len(loaded_modules),
                "registry": self._registry.to_dict(),
                "load_order": self._loader.get_load_order(),
            }

            self._built = True
            return result

        except Exception as e:
            raise CompositionBuildException(
                str(e),
                stage="build",
            )

    def get_registry(self) -> ModuleRegistry:
        """Get the module registry.

        Returns:
            Module registry.
        """
        return self._registry

    def get_loader(self) -> ModuleLoader:
        """Get the module loader.

        Returns:
            Module loader.
        """
        return self._loader

    def is_validated(self) -> bool:
        """Check if composition has been validated.

        Returns:
            True if validated.
        """
        return self._validated

    def is_built(self) -> bool:
        """Check if composition has been built.

        Returns:
            True if built.
        """
        return self._built
