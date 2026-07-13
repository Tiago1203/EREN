"""Service Provider for the Cognitive Dependency Injection Container.

Resolves services from the container.

Architecture only -- no implementations.
"""

import threading
import uuid
from datetime import datetime, timezone
from typing import Any, Callable, Optional

from .dependency_validator import DependencyValidator
from .exceptions import (
    ContainerDisposedException,
    DependencyResolutionException,
    ServiceNotFoundException,
)
from .service_factory import ServiceFactory
from .service_lifetime import ServiceLifetime
from .service_scope import ScopeType, ServiceScope


class ServiceProvider:
    """Resolves services from the container.

    Handles all service resolution logic.
    """

    def __init__(
        self,
        registry,
        validator: DependencyValidator,
        scope: ServiceScope,
    ):
        """Initialize the provider.

        Args:
            registry: Service registry.
            validator: Dependency validator.
            scope: Root scope.
        """
        self._registry = registry
        self._validator = validator
        self._root_scope = scope
        self._current_scope = scope
        self._is_disposed = False
        self._lock = threading.RLock()
        self._resolution_stack: list[str] = []

    def resolve(self, contract: str) -> Any:
        """Resolve a service.

        Args:
            contract: Contract name.

        Returns:
            Service instance.

        Raises:
            ServiceNotFoundException: If service not found.
            DependencyResolutionException: If resolution fails.
        """
        self._check_disposed()

        result = self.try_resolve(contract)
        if result is None:
            raise ServiceNotFoundException(contract)
        return result

    def try_resolve(self, contract: str) -> Optional[Any]:
        """Try to resolve a service without throwing.

        Args:
            contract: Contract name.

        Returns:
            Service instance or None.
        """
        self._check_disposed()

        try:
            return self._resolve_internal(contract)
        except Exception:
            return None

    def resolve_required(self, contract: str) -> Any:
        """Resolve a required service.

        Args:
            contract: Contract name.

        Returns:
            Service instance.

        Raises:
            ServiceNotFoundException: If service not found.
        """
        instance = self.try_resolve(contract)
        if instance is None:
            raise ServiceNotFoundException(contract)
        return instance

    def resolve_all(self, contract: str) -> list:
        """Resolve all implementations of a contract.

        Args:
            contract: Contract name.

        Returns:
            List of service instances.
        """
        self._check_disposed()

        descriptors = self._registry.get_descriptors(contract)
        instances = []

        for descriptor in descriptors:
            factory = ServiceFactory(descriptor)
            try:
                instance = factory.get_instance(
                    resolver=lambda c: self._resolve_internal(c),
                    scope_id=self._current_scope.scope_id,
                )
                instances.append(instance)
            except Exception:
                pass

        return instances

    def _resolve_internal(self, contract: str) -> Any:
        """Internal resolution logic.

        Args:
            contract: Contract name.

        Returns:
            Service instance.
        """
        # Check for circular dependencies
        if contract in self._resolution_stack:
            raise DependencyResolutionException(
                contract,
                f"Circular dependency detected: {' -> '.join(self._resolution_stack + [contract])}"
            )

        self._resolution_stack.append(contract)

        try:
            # Get factory from registry
            factory = self._registry.get_factory(contract)
            if factory is None:
                raise ServiceNotFoundException(contract)

            # Resolve in current scope
            instance = self._current_scope.resolve(contract, factory)

            return instance

        finally:
            self._resolution_stack.remove(contract)

    def create_scope(
        self,
        scope_type: str = ScopeType.CUSTOM,
        scope_id: str = None,
    ) -> ServiceScope:
        """Create a child scope.

        Args:
            scope_type: Type of scope.
            scope_id: Optional scope ID.

        Returns:
            New scope.
        """
        self._check_disposed()
        return self._current_scope.create_child(scope_type, scope_id)

    def use_scope(self, scope: ServiceScope) -> None:
        """Set the current scope.

        Args:
            scope: Scope to use.
        """
        self._check_disposed()
        self._current_scope = scope

    def reset_scope(self) -> None:
        """Reset to root scope."""
        self._check_disposed()
        self._current_scope = self._root_scope

    @property
    def current_scope(self) -> ServiceScope:
        """Get current scope."""
        return self._current_scope

    @property
    def is_disposed(self) -> bool:
        """Check if provider is disposed."""
        return self._is_disposed

    def dispose(self) -> None:
        """Dispose the provider."""
        with self._lock:
            if self._is_disposed:
                return

            self._is_disposed = True
            self._root_scope.dispose()
            self._current_scope = None

    def _check_disposed(self) -> None:
        """Check if disposed.

        Raises:
            ContainerDisposedException: If disposed.
        """
        if self._is_disposed:
            raise ContainerDisposedException()
