"""Service Registry for the Cognitive Dependency Injection Container.

Central registry for all service registrations.

Architecture only -- no implementations.
"""

import threading
from collections.abc import Callable
from typing import Any

from .exceptions import (
    DuplicateServiceException,
    InvalidLifetimeException,
)
from .service_descriptor import ServiceDescriptor
from .service_factory import ServiceFactory
from .service_lifetime import ServiceLifetime


class ServiceRegistry:
    """Central registry for service registrations.

    Thread-safe registry that manages all service descriptors.
    """

    def __init__(self):
        """Initialize the registry."""
        # Map of contract -> list of descriptors (supports multiple implementations)
        self._descriptors: dict[str, list[ServiceDescriptor]] = {}

        # Map of contract -> ServiceFactory (for quick access)
        self._factories: dict[str, ServiceFactory] = {}

        # Thread safety
        self._lock = threading.RLock()

        # Statistics
        self._registration_count = 0

    def register(
        self,
        contract: str,
        implementation: Any,
        lifetime: str = ServiceLifetime.TRANSIENT,
        *,
        factory: Callable | None = None,
        arguments: tuple = None,
        keyword_arguments: dict = None,
        tags: set = None,
        metadata: dict = None,
        dependencies: list = None,
        replace: bool = False,
    ) -> None:
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

        Raises:
            InvalidLifetimeException: If lifetime is invalid.
            DuplicateServiceException: If service already exists.
        """
        if not ServiceLifetime.is_valid(lifetime):
            raise InvalidLifetimeException(lifetime)

        descriptor = ServiceDescriptor(
            contract=contract,
            implementation=implementation,
            lifetime=lifetime,
            factory=factory,
            arguments=arguments or (),
            keyword_arguments=keyword_arguments or {},
            tags=tags or set(),
            metadata=metadata or {},
            dependencies=dependencies or [],
        )

        with self._lock:
            # Check for existing registration
            if contract in self._descriptors and not replace:
                existing = self._descriptors[contract]
                if existing and not any(d.is_default for d in existing):
                    raise DuplicateServiceException(
                        contract,
                        existing[0].implementation.__name__ if existing else "unknown"
                    )

            # Add or replace descriptor
            if replace and contract in self._descriptors:
                # Remove old descriptors marked as default
                self._descriptors[contract] = [
                    d for d in self._descriptors[contract]
                    if d.contract != contract or not d.is_default
                ]

            if contract not in self._descriptors:
                self._descriptors[contract] = []

            self._descriptors[contract].append(descriptor)

            # Create factory for the default implementation
            self._factories[contract] = ServiceFactory(descriptor)

            self._registration_count += 1

    def register_descriptor(
        self,
        descriptor: ServiceDescriptor,
        replace: bool = False,
    ) -> None:
        """Register a service from a descriptor.

        Args:
            descriptor: Service descriptor.
            replace: Whether to replace existing registration.
        """
        self.register(
            contract=descriptor.contract,
            implementation=descriptor.implementation,
            lifetime=descriptor.lifetime,
            factory=descriptor.factory,
            arguments=descriptor.arguments,
            keyword_arguments=descriptor.keyword_arguments,
            tags=descriptor.tags,
            metadata=descriptor.metadata,
            dependencies=descriptor.dependencies,
            replace=replace,
        )

    def get_descriptor(self, contract: str) -> ServiceDescriptor | None:
        """Get a service descriptor.

        Args:
            contract: Contract name.

        Returns:
            Service descriptor or None.
        """
        with self._lock:
            descriptors = self._descriptors.get(contract, [])
            for d in descriptors:
                if d.is_default:
                    return d
            return descriptors[0] if descriptors else None

    def get_descriptors(self, contract: str) -> list[ServiceDescriptor]:
        """Get all descriptors for a contract.

        Args:
            contract: Contract name.

        Returns:
            List of descriptors.
        """
        with self._lock:
            return list(self._descriptors.get(contract, []))

    def get_factory(self, contract: str) -> ServiceFactory | None:
        """Get a service factory.

        Args:
            contract: Contract name.

        Returns:
            Service factory or None.
        """
        with self._lock:
            return self._factories.get(contract)

    def get_all_contracts(self) -> list[str]:
        """Get all registered contracts.

        Returns:
            List of contract names.
        """
        with self._lock:
            return list(self._descriptors.keys())

    def get_all_descriptors(self) -> list[ServiceDescriptor]:
        """Get all registered descriptors.

        Returns:
            List of all descriptors.
        """
        with self._lock:
            result = []
            for descriptors in self._descriptors.values():
                result.extend(descriptors)
            return result

    def is_registered(self, contract: str) -> bool:
        """Check if a contract is registered.

        Args:
            contract: Contract name.

        Returns:
            True if registered.
        """
        with self._lock:
            return contract in self._descriptors

    def unregister(self, contract: str) -> bool:
        """Unregister a service.

        Args:
            contract: Contract name.

        Returns:
            True if unregistered.
        """
        with self._lock:
            if contract in self._descriptors:
                del self._descriptors[contract]
            if contract in self._factories:
                factory = self._factories[contract]
                factory.dispose()
                del self._factories[contract]
            return contract in self._descriptors or contract in self._factories

    def clear(self) -> None:
        """Clear all registrations."""
        with self._lock:
            for factory in self._factories.values():
                factory.dispose()
            self._descriptors.clear()
            self._factories.clear()

    def find_by_tag(self, tag: str) -> list[ServiceDescriptor]:
        """Find services by tag.

        Args:
            tag: Tag to search for.

        Returns:
            List of matching descriptors.
        """
        with self._lock:
            result = []
            for descriptors in self._descriptors.values():
                for d in descriptors:
                    if tag in d.tags:
                        result.append(d)
            return result

    def find_by_dependency(self, dependency: str) -> list[ServiceDescriptor]:
        """Find services that depend on a given contract.

        Args:
            dependency: Dependency contract name.

        Returns:
            List of matching descriptors.
        """
        with self._lock:
            result = []
            for descriptors in self._descriptors.values():
                for d in descriptors:
                    if dependency in d.dependencies:
                        result.append(d)
            return result

    @property
    def registration_count(self) -> int:
        """Get the number of registrations."""
        with self._lock:
            return self._registration_count

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        with self._lock:
            return {
                "contracts": list(self._descriptors.keys()),
                "registration_count": self._registration_count,
                "services": [
                    d.to_dict() for d in self.get_all_descriptors()
                ],
            }
