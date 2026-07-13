"""Service Factory for the Cognitive Dependency Injection Container.

Factory for creating service instances with dependency injection.

Architecture only -- no implementations.
"""

import threading
import weakref
from datetime import datetime, timezone
from typing import Any, Callable, Optional

from .service_descriptor import ServiceDescriptor, ServiceInstance
from .service_lifetime import ServiceLifetime
from .exceptions import FactoryExecutionException


class ServiceFactory:
    """Factory for creating service instances.

    Handles all lifetime modes and instance caching.
    """

    def __init__(self, descriptor: ServiceDescriptor):
        """Initialize the factory.

        Args:
            descriptor: Service descriptor.
        """
        self._descriptor = descriptor
        self._instance: Optional[Any] = None
        self._lock = threading.RLock()
        self._lazy_initialized = False
        self._created_at: Optional[str] = None
        self._resolution_count = 0

    @property
    def descriptor(self) -> ServiceDescriptor:
        """Get the service descriptor."""
        return self._descriptor

    @property
    def instance(self) -> Optional[Any]:
        """Get the current instance (if any)."""
        return self._instance

    def get_instance(
        self,
        resolver: Callable[[str], Any],
        scope_id: Optional[str] = None,
    ) -> Any:
        """Get or create a service instance based on lifetime.

        Args:
            resolver: Function to resolve dependencies.
            scope_id: Scope ID for scoped services.

        Returns:
            Service instance.

        Raises:
            FactoryExecutionException: If factory execution fails.
        """
        self._resolution_count += 1

        if self._descriptor.lifetime == ServiceLifetime.SINGLETON:
            return self._get_singleton(resolver)

        elif self._descriptor.lifetime == ServiceLifetime.LAZY_SINGLETON:
            return self._get_lazy_singleton(resolver)

        elif self._descriptor.lifetime == ServiceLifetime.WEAK_SINGLETON:
            return self._get_weak_singleton(resolver)

        elif self._descriptor.lifetime == ServiceLifetime.SCOPED:
            return self._get_scoped(resolver, scope_id)

        elif self._descriptor.lifetime == ServiceLifetime.FACTORY:
            return self._execute_factory(resolver)

        else:  # TRANSIENT
            return self._create_instance(resolver)

    def _get_singleton(self, resolver: Callable) -> Any:
        """Get or create singleton instance.

        Args:
            resolver: Function to resolve dependencies.

        Returns:
            Singleton instance.
        """
        if self._instance is None:
            with self._lock:
                if self._instance is None:
                    self._instance = self._create_instance(resolver)
                    self._created_at = datetime.now(timezone.utc).isoformat()
        return self._instance

    def _get_lazy_singleton(self, resolver: Callable) -> Any:
        """Get or create lazy singleton instance.

        Args:
            resolver: Function to resolve dependencies.

        Returns:
            Lazy singleton instance.
        """
        if not self._lazy_initialized:
            with self._lock:
                if not self._lazy_initialized:
                    self._instance = self._create_instance(resolver)
                    self._created_at = datetime.now(timezone.utc).isoformat()
                    self._lazy_initialized = True
        return self._instance

    def _get_weak_singleton(self, resolver: Callable) -> Any:
        """Get or create weak singleton instance.

        Args:
            resolver: Function to resolve dependencies.

        Returns:
            Weak singleton instance (or None if garbage collected).
        """
        if self._instance is None or self._is_garbage_collected():
            with self._lock:
                if self._instance is None or self._is_garbage_collected():
                    self._instance = self._create_instance(resolver)
                    self._created_at = datetime.now(timezone.utc).isoformat()
        return self._instance

    def _is_garbage_collected(self) -> bool:
        """Check if weak reference was garbage collected."""
        if not isinstance(self._instance, weakref.ref):
            return False
        return self._instance() is None

    def _get_scoped(
        self,
        resolver: Callable,
        scope_id: Optional[str],
    ) -> Any:
        """Get scoped instance.

        Args:
            resolver: Function to resolve dependencies.
            scope_id: Scope ID.

        Returns:
            Scoped instance.
        """
        # For scoped services, instance is managed by scope
        # Factory just creates the instance
        return self._create_instance(resolver)

    def _execute_factory(self, resolver: Callable) -> Any:
        """Execute factory function.

        Args:
            resolver: Function to resolve dependencies.

        Returns:
            Factory result.

        Raises:
            FactoryExecutionException: If factory fails.
        """
        if self._descriptor.factory is None:
            raise FactoryExecutionException(
                self._descriptor.contract,
                "No factory function provided"
            )

        try:
            # Inject resolver as dependency if factory accepts it
            import inspect
            sig = inspect.signature(self._descriptor.factory)
            params = {}

            for param_name, param in sig.parameters.items():
                if param_name == "resolver":
                    params[param_name] = resolver
                elif param.annotation != inspect.Parameter.empty:
                    try:
                        params[param_name] = resolver(param.annotation)
                    except Exception:
                        pass

            result = self._descriptor.factory(**params)
            return result

        except Exception as e:
            raise FactoryExecutionException(
                self._descriptor.contract,
                str(e)
            )

    def _create_instance(self, resolver: Callable) -> Any:
        """Create a new instance using constructor injection.

        Args:
            resolver: Function to resolve dependencies.

        Returns:
            New service instance.
        """
        impl = self._descriptor.implementation

        # If it's already an instance, return it
        if not isinstance(impl, type):
            return impl

        # Resolve constructor dependencies
        import inspect
        try:
            sig = inspect.signature(impl.__init__)
        except (ValueError, TypeError):
            # Can't inspect, try direct instantiation
            return impl(*self._descriptor.arguments, **self._descriptor.keyword_arguments)

        resolved_args = []
        resolved_kwargs = {}

        for param_name, param in sig.parameters.items():
            if param_name == "self":
                continue

            if param_name in self._descriptor.keyword_arguments:
                resolved_kwargs[param_name] = self._descriptor.keyword_arguments[param_name]
            elif param.annotation in self._descriptor.keyword_arguments:
                resolved_kwargs[param_name] = self._descriptor.keyword_arguments[param.annotation]
            else:
                try:
                    resolved_args.append(resolver(param.annotation))
                except Exception:
                    if param.default != inspect.Parameter.empty:
                        pass  # Use default
                    elif param_name in self._descriptor.arguments:
                        resolved_args.append(
                            self._descriptor.arguments[self._descriptor.arguments.index(param_name)]
                        )

        return impl(*resolved_args, **resolved_kwargs)

    def dispose(self):
        """Dispose of the instance."""
        with self._lock:
            if self._instance is not None:
                if hasattr(self._instance, "dispose"):
                    self._instance.dispose()
                self._instance = None
                self._lazy_initialized = False

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "contract": self._descriptor.contract,
            "lifetime": self._descriptor.lifetime,
            "has_instance": self._instance is not None,
            "created_at": self._created_at,
            "resolution_count": self._resolution_count,
        }
