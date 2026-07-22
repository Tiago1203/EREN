"""Service Descriptor for the Cognitive Dependency Injection Container.

Describes how a service should be created and managed.

Architecture only -- no implementations.
"""

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from .service_lifetime import ServiceLifetime


@dataclass
class ServiceDescriptor:
    """Descriptor for a registered service.

    Contains all information needed to create service instances.
    """

    # Contract (interface/abstraction) that this service implements
    contract: str

    # Implementation type or factory function
    implementation: Any

    # How long the service instance should live
    lifetime: str = ServiceLifetime.TRANSIENT

    # Factory function (if using FACTORY lifetime)
    factory: Callable | None = None

    # Constructor arguments (if any)
    arguments: tuple = field(default_factory=tuple)

    # Constructor keyword arguments (if any)
    keyword_arguments: dict = field(default_factory=dict)

    # Whether this is the default implementation for the contract
    is_default: bool = True

    # Tags for grouping services
    tags: set = field(default_factory=set)

    # Metadata for documentation/debugging
    metadata: dict = field(default_factory=dict)

    # Dependencies required by this service
    dependencies: list = field(default_factory=list)

    def __post_init__(self):
        """Validate descriptor after creation."""
        if not self.contract:
            raise ValueError("Contract cannot be empty")

        if self.lifetime == ServiceLifetime.FACTORY and self.factory is None:
            raise ValueError("Factory lifetime requires a factory function")

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "contract": self.contract,
            "implementation": (
                self.implementation.__name__
                if callable(self.implementation)
                else str(self.implementation)
            ),
            "lifetime": self.lifetime,
            "is_default": self.is_default,
            "tags": list(self.tags),
            "dependencies": self.dependencies,
            "metadata": self.metadata,
        }

    def with_tags(self, *tags: str) -> "ServiceDescriptor":
        """Add tags to the descriptor.

        Args:
            *tags: Tags to add.

        Returns:
            New descriptor with added tags.
        """
        new_tags = self.tags.copy()
        new_tags.update(tags)
        return ServiceDescriptor(
            contract=self.contract,
            implementation=self.implementation,
            lifetime=self.lifetime,
            factory=self.factory,
            arguments=self.arguments,
            keyword_arguments=self.keyword_arguments,
            is_default=self.is_default,
            tags=new_tags,
            metadata=self.metadata.copy(),
            dependencies=self.dependencies.copy(),
        )

    def with_dependencies(self, *dependencies: str) -> "ServiceDescriptor":
        """Add dependencies to the descriptor.

        Args:
            *dependencies: Dependencies to add.

        Returns:
            New descriptor with added dependencies.
        """
        return ServiceDescriptor(
            contract=self.contract,
            implementation=self.implementation,
            lifetime=self.lifetime,
            factory=self.factory,
            arguments=self.arguments,
            keyword_arguments=self.keyword_arguments,
            is_default=self.is_default,
            tags=self.tags.copy(),
            metadata=self.metadata.copy(),
            dependencies=list(dependencies) + self.dependencies,
        )


@dataclass
class ServiceInstance:
    """Represents a resolved service instance.

    Tracks instance state and metadata.
    """

    # The actual service instance
    instance: Any

    # When the instance was created
    created_at: str

    # How many times this instance has been resolved
    resolution_count: int = 0

    # Scope this instance belongs to (if scoped)
    scope_id: str | None = None

    # Whether this is the actual implementation
    is_implementation: bool = True

    def increment_resolution(self):
        """Increment resolution counter."""
        self.resolution_count += 1

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "created_at": self.created_at,
            "resolution_count": self.resolution_count,
            "scope_id": self.scope_id,
            "instance_type": (
                type(self.instance).__name__
                if self.instance is not None
                else None
            ),
        }
