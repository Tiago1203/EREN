"""Cognitive Dependency Injection Container (CDIC).

The official component for dependency injection in EREN.

Architecture only -- no implementations, no business logic.

This component does NOT:
- Implement business logic
- Use AI
- Break existing contracts
- Modify existing motors

It ONLY provides dependency injection infrastructure.
"""

import threading
import uuid
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any

from .container_builder import ContainerBuilder
from .container_events import ContainerEventPublisher, ContainerEventType
from .container_metrics import ContainerMetricsCollector
from .container_trace import ContainerTraceCollector
from .dependency_graph import DependencyGraph
from .dependency_validator import DependencyValidator
from .exceptions import (
    ContainerDisposedException,
    ValidationException,
)
from .service_lifetime import ServiceLifetime
from .service_provider import ServiceProvider
from .service_registry import ServiceRegistry
from .service_scope import ScopeType, ServiceScope


class CognitiveContainer:
    """The main Cognitive Dependency Injection Container.

    Responsibilities:
    - Register services
    - Resolve dependencies
    - Create scopes
    - Control lifecycles
    - Detect circular dependencies
    - Validate dependency graph
    - Deliver instances

    The Container does NOT:
    - Implement business logic
    - Use AI
    - Break existing contracts
    - Modify existing motors
    """

    def __init__(
        self,
        registry: ServiceRegistry | None = None,
        validator: DependencyValidator | None = None,
        graph: DependencyGraph | None = None,
    ):
        """Initialize the container.

        Args:
            registry: Optional service registry.
            validator: Optional dependency validator.
            graph: Optional dependency graph.
        """
        self._id = str(uuid.uuid4())
        self._registry = registry or ServiceRegistry()
        self._graph = graph or DependencyGraph()
        self._validator = validator or DependencyValidator(self._registry, self._graph)

        # Create root scope
        self._root_scope = ServiceScope(
            scope_id=f"root_{self._id}",
            scope_type=ScopeType.APPLICATION,
        )

        # Create provider
        self._provider = ServiceProvider(
            registry=self._registry,
            validator=self._validator,
            scope=self._root_scope,
        )

        # Observability
        self._event_publisher = ContainerEventPublisher()
        self._metrics = ContainerMetricsCollector()
        self._trace = ContainerTraceCollector()

        # State
        self._is_disposed = False
        self._lock = threading.RLock()
        self._created_at = datetime.now(UTC).isoformat()

        # Publish creation event
        self._event_publisher.publish(
            ContainerEventType.CONTAINER_CREATED,
            container_id=self._id,
        )

    @property
    def id(self) -> str:
        """Get container ID."""
        return self._id

    @property
    def is_disposed(self) -> bool:
        """Check if container is disposed."""
        return self._is_disposed

    @property
    def created_at(self) -> str:
        """Get creation timestamp."""
        return self._created_at

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
    ) -> "CognitiveContainer":
        """Register a service.

        Args:
            contract: Contract/interface name.
            implementation: Implementation type or instance.
            lifetime: Service lifetime.
            factory: Factory function.
            arguments: Constructor arguments.
            keyword_arguments: Constructor keyword arguments.
            tags: Tags for grouping.
            metadata: Additional metadata.
            dependencies: List of dependencies.
            replace: Whether to replace.

        Returns:
            Self for chaining.
        """
        self._check_disposed()

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

        self._metrics.record_service_registered()

        self._event_publisher.publish(
            ContainerEventType.SERVICE_REGISTERED,
            contract=contract,
            lifetime=lifetime,
        )

        self._trace.add_entry(
            operation="register",
            contract=contract,
            success=True,
            metadata={"lifetime": lifetime},
        )

        return self

    def resolve(self, contract: str) -> Any:
        """Resolve a service.

        Args:
            contract: Contract name.

        Returns:
            Service instance.

        Raises:
            ServiceNotFoundException: If not found.
        """
        self._check_disposed()

        start_time = datetime.now(UTC)

        try:
            instance = self._provider.resolve(contract)

            duration_ms = int(
                (datetime.now(UTC) - start_time).total_seconds() * 1000
            )
            self._metrics.record_service_resolved(duration_ms)

            self._event_publisher.publish(
                ContainerEventType.SERVICE_RESOLVED,
                contract=contract,
                duration_ms=duration_ms,
            )

            self._trace.add_entry(
                operation="resolve",
                contract=contract,
                duration_ms=duration_ms,
                success=True,
            )

            return instance

        except Exception as e:
            duration_ms = int(
                (datetime.now(UTC) - start_time).total_seconds() * 1000
            )
            self._metrics.record_resolution_error()

            self._event_publisher.publish(
                ContainerEventType.RESOLUTION_FAILED,
                contract=contract,
                error=str(e),
            )

            self._trace.add_entry(
                operation="resolve",
                contract=contract,
                duration_ms=duration_ms,
                success=False,
                error=str(e),
            )

            raise

    def try_resolve(self, contract: str) -> Any | None:
        """Try to resolve without throwing.

        Args:
            contract: Contract name.

        Returns:
            Instance or None.
        """
        self._check_disposed()

        return self._provider.try_resolve(contract)

    def resolve_all(self, contract: str) -> list:
        """Resolve all implementations.

        Args:
            contract: Contract name.

        Returns:
            List of instances.
        """
        self._check_disposed()

        return self._provider.resolve_all(contract)

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

        scope = self._provider.create_scope(scope_type, scope_id)

        self._metrics.record_scope_created()

        self._event_publisher.publish(
            ContainerEventType.SCOPE_CREATED,
            scope_id=scope.scope_id,
            scope_type=scope_type,
        )

        self._trace.add_entry(
            operation="create_scope",
            contract="",
            scope_id=scope.scope_id,
            success=True,
            metadata={"scope_type": scope_type},
        )

        return scope

    def use_scope(self, scope: ServiceScope) -> "CognitiveContainer":
        """Set current scope.

        Args:
            scope: Scope to use.

        Returns:
            Self for chaining.
        """
        self._check_disposed()

        self._provider.use_scope(scope)
        return self

    def reset_scope(self) -> "CognitiveContainer":
        """Reset to root scope.

        Returns:
            Self for chaining.
        """
        self._check_disposed()

        self._provider.reset_scope()
        return self

    def validate(self) -> bool:
        """Validate the container.

        Returns:
            True if valid.

        Raises:
            ValidationException: If invalid.
        """
        self._check_disposed()

        start_time = datetime.now(UTC)

        result = self._validator.validate()

        duration_ms = int(
            (datetime.now(UTC) - start_time).total_seconds() * 1000
        )
        self._metrics.record_validation_time(duration_ms)

        if result.is_valid:
            self._event_publisher.publish(
                ContainerEventType.DEPENDENCY_VALIDATED,
                duration_ms=duration_ms,
            )
        else:
            self._event_publisher.publish(
                ContainerEventType.DEPENDENCY_VALIDATION_FAILED,
                error_count=len(result.errors),
            )
            raise ValidationException(
                "container_validation",
                [e.message for e in result.errors],
            )

        return True

    def get_trace(self) -> list:
        """Get container trace."""
        return self._trace.get_all_entries()

    def get_metrics(self) -> dict:
        """Get container metrics."""
        return self._metrics.to_dict()

    def get_graph(self) -> dict:
        """Get dependency graph."""
        return self._graph.to_dict()

    def dispose(self) -> None:
        """Dispose the container."""
        with self._lock:
            if self._is_disposed:
                return

            self._is_disposed = True
            self._provider.dispose()

            self._event_publisher.publish(
                ContainerEventType.CONTAINER_DISPOSED,
                container_id=self._id,
            )

            self._trace.add_entry(
                operation="dispose",
                contract="",
                success=True,
            )

    def _check_disposed(self) -> None:
        """Check if disposed.

        Raises:
            ContainerDisposedException: If disposed.
        """
        if self._is_disposed:
            raise ContainerDisposedException()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.dispose()
        return False


class ContainerFactory:
    """Factory for creating containers."""

    @staticmethod
    def create_default() -> CognitiveContainer:
        """Create a default container."""
        return CognitiveContainer()

    @staticmethod
    def create_builder() -> ContainerBuilder:
        """Create a container builder."""
        return ContainerBuilder()
