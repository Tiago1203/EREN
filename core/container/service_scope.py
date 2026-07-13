"""Service Scope for the Cognitive Dependency Injection Container.

Hierarchical scopes for dependency management.

Architecture only -- no implementations.
"""

import threading
import uuid
from datetime import datetime, timezone
from typing import Any, Callable, Optional

from .service_descriptor import ServiceInstance
from .service_factory import ServiceFactory
from .exceptions import ScopeDisposedException


class ScopeType:
    """Scope types for hierarchical dependency management."""

    APPLICATION = "application"
    HOSPITAL = "hospital"
    USER = "user"
    SESSION = "session"
    WORKFLOW = "workflow"
    CUSTOM = "custom"


class ServiceScope:
    """A scope for scoped service instances.

    Supports hierarchical scopes where child scopes inherit parent's services.
    """

    def __init__(
        self,
        scope_id: str,
        scope_type: str,
        parent: Optional["ServiceScope"] = None,
    ):
        """Initialize a scope.

        Args:
            scope_id: Unique scope identifier.
            scope_type: Type of scope (APPLICATION, SESSION, etc.).
            parent: Parent scope (if any).
        """
        self._scope_id = scope_id or str(uuid.uuid4())
        self._scope_type = scope_type
        self._parent = parent
        self._children: list["ServiceScope"] = []
        self._instances: dict[str, ServiceInstance] = {}
        self._factories: dict[str, ServiceFactory] = {}
        self._is_disposed = False
        self._lock = threading.RLock()
        self._created_at = datetime.now(timezone.utc).isoformat()

        # Register with parent
        if parent is not None:
            parent._children.append(self)

    @property
    def scope_id(self) -> str:
        """Get scope ID."""
        return self._scope_id

    @property
    def scope_type(self) -> str:
        """Get scope type."""
        return self._scope_type

    @property
    def parent(self) -> Optional["ServiceScope"]:
        """Get parent scope."""
        return self._parent

    @property
    def children(self) -> list["ServiceScope"]:
        """Get child scopes."""
        with self._lock:
            return list(self._children)

    @property
    def is_disposed(self) -> bool:
        """Check if scope is disposed."""
        return self._is_disposed

    @property
    def created_at(self) -> str:
        """Get creation timestamp."""
        return self._created_at

    def resolve(
        self,
        contract: str,
        factory: ServiceFactory,
    ) -> Any:
        """Resolve a service within this scope.

        Args:
            contract: Contract name.
            factory: Service factory.

        Returns:
            Service instance.

        Raises:
            ScopeDisposedException: If scope is disposed.
        """
        self._check_disposed()

        with self._lock:
            # Check if already resolved in this scope
            if contract in self._instances:
                instance = self._instances[contract]
                instance.increment_resolution()
                return instance.instance

            # Try parent scope if not found locally
            if self._parent is not None:
                try:
                    return self._parent.resolve(contract, factory)
                except KeyError:
                    pass  # Fall through to create in this scope

            # Create new instance
            instance_obj = factory.get_instance(
                resolver=lambda c: self.resolve(c, self._factories.get(c)),
                scope_id=self._scope_id,
            )

            service_instance = ServiceInstance(
                instance=instance_obj,
                created_at=datetime.now(timezone.utc).isoformat(),
                scope_id=self._scope_id,
            )

            self._instances[contract] = service_instance
            self._factories[contract] = factory

            return instance_obj

    def register_factory(self, contract: str, factory: ServiceFactory) -> None:
        """Register a factory for a contract in this scope.

        Args:
            contract: Contract name.
            factory: Service factory.
        """
        self._check_disposed()
        with self._lock:
            self._factories[contract] = factory

    def get_instance(self, contract: str) -> Optional[Any]:
        """Get an existing instance in this scope.

        Args:
            contract: Contract name.

        Returns:
            Instance or None.
        """
        self._check_disposed()
        with self._lock:
            if contract in self._instances:
                return self._instances[contract].instance
            return None

    def has_instance(self, contract: str) -> bool:
        """Check if an instance exists in this scope.

        Args:
            contract: Contract name.

        Returns:
            True if instance exists.
        """
        self._check_disposed()
        with self._lock:
            return contract in self._instances

    def create_child(
        self,
        scope_type: str = ScopeType.CUSTOM,
        scope_id: str = None,
    ) -> "ServiceScope":
        """Create a child scope.

        Args:
            scope_type: Type of child scope.
            scope_id: Optional scope ID.

        Returns:
            New child scope.
        """
        self._check_disposed()
        return ServiceScope(
            scope_id=scope_id,
            scope_type=scope_type,
            parent=self,
        )

    def dispose(self) -> None:
        """Dispose this scope and all its instances."""
        with self._lock:
            if self._is_disposed:
                return

            self._is_disposed = True

            # Dispose child scopes first
            for child in self._children:
                child.dispose()

            # Remove from parent
            if self._parent is not None:
                with self._parent._lock:
                    if self in self._parent._children:
                        self._parent._children.remove(self)

            # Dispose all instances
            for service_instance in self._instances.values():
                if hasattr(service_instance.instance, "dispose"):
                    service_instance.instance.dispose()

            self._instances.clear()
            self._factories.clear()

    def _check_disposed(self) -> None:
        """Check if scope is disposed.

        Raises:
            ScopeDisposedException: If disposed.
        """
        if self._is_disposed:
            raise ScopeDisposedException(self._scope_id)

    def get_all_contracts(self) -> list[str]:
        """Get all contracts resolved in this scope.

        Returns:
            List of contract names.
        """
        with self._lock:
            return list(self._instances.keys())

    def get_statistics(self) -> dict:
        """Get scope statistics.

        Returns:
            Dictionary of statistics.
        """
        with self._lock:
            return {
                "scope_id": self._scope_id,
                "scope_type": self._scope_type,
                "is_disposed": self._is_disposed,
                "created_at": self._created_at,
                "instance_count": len(self._instances),
                "child_count": len(self._children),
                "has_parent": self._parent is not None,
            }

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return self.get_statistics()
