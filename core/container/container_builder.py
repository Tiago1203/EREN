"""Container Builder for the Cognitive Dependency Injection Container.

Builder pattern for creating containers.

Architecture only -- no implementations.
"""

from typing import Any, Callable, Optional

from .dependency_graph import DependencyGraph
from .dependency_validator import DependencyValidator
from .service_descriptor import ServiceDescriptor
from .service_lifetime import ServiceLifetime
from .service_registry import ServiceRegistry


class ContainerBuilder:
    """Builder for creating configured containers.

    Supports fluent API for registration.
    """

    def __init__(self):
        """Initialize the builder."""
        self._registry = ServiceRegistry()
        self._graph = DependencyGraph()
        self._validator = DependencyValidator(self._registry, self._graph)
        self._validated = False

    def register(
        self,
        contract: str,
        implementation: Any,
        lifetime: str = ServiceLifetime.TRANSIENT,
        *,
        factory: Optional[Callable] = None,
        arguments: tuple = None,
        keyword_arguments: dict = None,
        tags: set = None,
        metadata: dict = None,
        dependencies: list = None,
        replace: bool = False,
    ) -> "ContainerBuilder":
        """Register a service.

        Args:
            contract: Contract/interface name.
            implementation: Implementation type or instance.
            lifetime: Service lifetime.
            factory: Factory function (if lifetime is FACTORY).
            arguments: Constructor arguments.
            keyword_arguments: Constructor keyword arguments.
            tags: Tags for grouping.
            metadata: Additional metadata.
            dependencies: List of dependencies.
            replace: Whether to replace existing registration.

        Returns:
            Self for chaining.
        """
        self._registry.register(
            contract=contract,
            implementation=implementation,
            lifetime=lifetime,
            factory=factory,
            arguments=arguments,
            keyword_arguments=keyword_arguments,
            tags=tags,
            metadata=metadata,
            dependencies=dependencies,
            replace=replace,
        )
        self._validated = False
        return self

    def register_descriptor(
        self,
        descriptor: ServiceDescriptor,
        replace: bool = False,
    ) -> "ContainerBuilder":
        """Register from a descriptor.

        Args:
            descriptor: Service descriptor.
            replace: Whether to replace.

        Returns:
            Self for chaining.
        """
        self._registry.register_descriptor(descriptor, replace)
        self._validated = False
        return self

    def register_singleton(
        self,
        contract: str,
        implementation: Any,
        *,
        dependencies: list = None,
    ) -> "ContainerBuilder":
        """Register a singleton service.

        Args:
            contract: Contract name.
            implementation: Implementation type.
            dependencies: List of dependencies.

        Returns:
            Self for chaining.
        """
        return self.register(
            contract=contract,
            implementation=implementation,
            lifetime=ServiceLifetime.SINGLETON,
            dependencies=dependencies,
        )

    def register_scoped(
        self,
        contract: str,
        implementation: Any,
        *,
        dependencies: list = None,
    ) -> "ContainerBuilder":
        """Register a scoped service.

        Args:
            contract: Contract name.
            implementation: Implementation type.
            dependencies: List of dependencies.

        Returns:
            Self for chaining.
        """
        return self.register(
            contract=contract,
            implementation=implementation,
            lifetime=ServiceLifetime.SCOPED,
            dependencies=dependencies,
        )

    def register_transient(
        self,
        contract: str,
        implementation: Any,
        *,
        dependencies: list = None,
    ) -> "ContainerBuilder":
        """Register a transient service.

        Args:
            contract: Contract name.
            implementation: Implementation type.
            dependencies: List of dependencies.

        Returns:
            Self for chaining.
        """
        return self.register(
            contract=contract,
            implementation=implementation,
            lifetime=ServiceLifetime.TRANSIENT,
            dependencies=dependencies,
        )

    def register_factory(
        self,
        contract: str,
        factory: Callable,
        *,
        lifetime: str = ServiceLifetime.FACTORY,
    ) -> "ContainerBuilder":
        """Register a factory.

        Args:
            contract: Contract name.
            factory: Factory function.
            lifetime: Lifetime mode.

        Returns:
            Self for chaining.
        """
        return self.register(
            contract=contract,
            implementation=None,
            lifetime=lifetime,
            factory=factory,
        )

    def validate(self) -> "ContainerBuilder":
        """Validate the container configuration.

        Returns:
            Self for chaining.
        """
        result = self._validator.validate()
        self._validated = result.is_valid
        return self

    def get_registry(self) -> ServiceRegistry:
        """Get the registry.

        Returns:
            Service registry.
        """
        return self._registry

    def get_validator(self) -> DependencyValidator:
        """Get the validator.

        Returns:
            Dependency validator.
        """
        return self._validator

    def get_graph(self) -> DependencyGraph:
        """Get the dependency graph.

        Returns:
            Dependency graph.
        """
        return self._graph

    def is_validated(self) -> bool:
        """Check if container has been validated.

        Returns:
            True if validated.
        """
        return self._validated
