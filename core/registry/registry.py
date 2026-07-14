"""Dynamic registry of EREN cognitive engines.

`EngineRegistry` lets engines be registered and resolved **by name at runtime**,
so consumers (e.g. the orchestrator) discover engines through dependency
injection instead of importing and instantiating concrete classes.

Design principles:

- **Dependency Injection:** engines are *injected* into the registry (via the
  constructor or `register`); the registry never constructs engines itself and
  depends only on the `CognitiveEngine` abstraction.
- **No conditional dispatch:** resolution is an O(1) dictionary lookup keyed by
  `engine.name` — there are no ``if/elif`` chains selecting engines by type.
- **Advanced discovery:** engines can be found by name, capability, or type
  using flexible search and filter operations.
- **Descriptor-based:** engines are stored with rich metadata (EngineDescriptor)
  enabling dependency validation, event contract verification, and compatibility checking.

This is thin infrastructure, not business logic: it stores and hands back
objects. It contains no AI, no domain logic, and no cognition.
"""

from __future__ import annotations

import threading
from collections.abc import Iterable, Sequence

from core.contracts import CognitiveEngine
from core.registry.exceptions import (
    CompatibilityError,
    DependencyNotFoundError,
    EngineAlreadyRegisteredError,
    EngineNotFoundError,
    ValidationError,
)
from core.registry.models import EngineDescriptor, RegistrySnapshot
from core.registry.types import EngineStatus, SearchOptions, VersionRequirement


class EngineRegistry:
    """In-memory registry of cognitive engines keyed by ``engine.name``.

    Engines are provided from the outside (constructor or :meth:`register`),
    keeping construction and wiring a caller concern (Dependency Injection).

    Features:
    - Thread-safe registration and lookup
    - Rich metadata via EngineDescriptor
    - Capability-based discovery
    - Dependency validation
    - Version compatibility checking
    - Event contract verification
    """

    def __init__(self, engines: Iterable[CognitiveEngine] | None = None) -> None:
        self._engines: dict[str, CognitiveEngine] = {}
        self._descriptors: dict[str, EngineDescriptor] = {}
        self._lock = threading.RLock()
        for engine in engines or ():
            self.register(engine)

    # --------------------------------------------------------------------------
    # Basic Operations
    # --------------------------------------------------------------------------

    def register(
        self,
        engine: CognitiveEngine,
        descriptor: EngineDescriptor | None = None,
        *,
        replace: bool = False,
    ) -> None:
        """Register ``engine`` under its ``name``.

        Args:
            engine: The cognitive engine to register.
            descriptor: Optional rich metadata about the engine.
            replace: If True, replace an existing engine with the same name.

        Raises:
            EngineAlreadyRegisteredError: If engine name is taken and replace=False.
        """
        with self._lock:
            name = engine.name
            if name in self._engines and not replace:
                raise EngineAlreadyRegisteredError(name)

            self._engines[name] = engine

            # Create or use provided descriptor
            if descriptor is None:
                descriptor = EngineDescriptor.create(
                    engine_id=name,
                    display_name=name,
                    description=engine.describe(),
                    version="1.0.0",
                )

            self._descriptors[name] = descriptor

    def unregister(self, name: str) -> None:
        """Remove the engine registered under ``name``.

        Args:
            name: The name of the engine to remove.

        Raises:
            EngineNotFoundError: If no engine exists with that name.
        """
        with self._lock:
            if name not in self._engines:
                raise EngineNotFoundError(name)

            del self._engines[name]
            if name in self._descriptors:
                del self._descriptors[name]

    def get(self, name: str) -> CognitiveEngine:
        """Return the engine registered under ``name`` (O(1) lookup).

        Args:
            name: The name of the engine to retrieve.

        Returns:
            The registered cognitive engine.

        Raises:
            EngineNotFoundError: If no engine exists with that name.
        """
        with self._lock:
            if name not in self._engines:
                raise EngineNotFoundError(name)
            return self._engines[name]

    def get_descriptor(self, name: str) -> EngineDescriptor:
        """Return the descriptor for a registered engine.

        Args:
            name: The name of the engine.

        Returns:
            The engine's descriptor with rich metadata.

        Raises:
            EngineNotFoundError: If no engine exists with that name.
        """
        with self._lock:
            if name not in self._descriptors:
                raise EngineNotFoundError(name)
            return self._descriptors[name]

    def list(self) -> Sequence[CognitiveEngine]:
        """Return all registered engines."""
        with self._lock:
            return tuple(self._engines.values())

    def list_descriptors(self) -> Sequence[EngineDescriptor]:
        """Return all registered engine descriptors."""
        with self._lock:
            return tuple(self._descriptors.values())

    def __contains__(self, name: object) -> bool:
        return name in self._engines

    def __len__(self) -> int:
        return len(self._engines)

    # --------------------------------------------------------------------------
    # Status Management
    # --------------------------------------------------------------------------

    def set_status(self, name: str, status: EngineStatus) -> None:
        """Update the status of a registered engine.

        Args:
            name: The name of the engine.
            status: The new status.

        Raises:
            EngineNotFoundError: If no engine exists with that name.
        """
        with self._lock:
            if name not in self._descriptors:
                raise EngineNotFoundError(name)

            # Create new descriptor with updated status
            from dataclasses import replace
            old = self._descriptors[name]
            self._descriptors[name] = replace(old, status=status)

    def get_active_engines(self) -> Sequence[EngineDescriptor]:
        """Return all engines with ACTIVE status."""
        with self._lock:
            return tuple(
                d for d in self._descriptors.values()
                if d.status == EngineStatus.ACTIVE
            )

    # --------------------------------------------------------------------------
    # Search and Discovery
    # --------------------------------------------------------------------------

    def find_by_capability(self, capability: str) -> Sequence[EngineDescriptor]:
        """Find engines that provide a specific capability.

        Args:
            capability: The name of the capability to search for.

        Returns:
            Sequence of engine descriptors that have the capability.
        """
        with self._lock:
            return tuple(
                d for d in self._descriptors.values()
                if d.has_capability(capability)
            )

    def find_by_tag(self, tag: str) -> Sequence[EngineDescriptor]:
        """Find engines with a specific tag.

        Args:
            tag: The tag to search for.

        Returns:
            Sequence of engine descriptors with the tag.
        """
        with self._lock:
            return tuple(
                d for d in self._descriptors.values()
                if tag in d.metadata.tags
            )

    def search(self, options: SearchOptions) -> Sequence[EngineDescriptor]:
        """Search engines with advanced filtering and sorting.

        Args:
            options: Search options including filter, sort, and pagination.

        Returns:
            Sequence of matching engine descriptors.
        """
        with self._lock:
            results = list(self._descriptors.values())

            # Apply filter
            if options.filter:
                results = [d for d in results if options.filter.matches(d)]

            # Sort
            if options.sort_by == "priority":
                results.sort(
                    key=lambda d: d.priority.value,
                    reverse=not options.ascending,
                )
            elif options.sort_by == "name":
                results.sort(key=lambda d: d.engine_id, reverse=not options.ascending)

            # Pagination
            if options.offset:
                results = results[options.offset:]
            if options.limit:
                results = results[:options.limit]

            return tuple(results)

    # --------------------------------------------------------------------------
    # Dependency and Compatibility
    # --------------------------------------------------------------------------

    def validate_dependencies(self, name: str) -> list[DependencyNotFoundError]:
        """Validate that all dependencies of an engine are registered.

        Args:
            name: The name of the engine to validate.

        Returns:
            List of errors for missing required dependencies (empty if all satisfied).

        Raises:
            EngineNotFoundError: If the engine itself is not registered.
        """
        with self._lock:
            if name not in self._descriptors:
                raise EngineNotFoundError(name)

            errors = []
            descriptor = self._descriptors[name]

            for dep in descriptor.get_required_dependencies():
                if dep.engine_name not in self._engines:
                    errors.append(
                        DependencyNotFoundError(
                            engine=name,
                            missing_dependency=dep.engine_name,
                            required_version=dep.min_version,
                        )
                    )
                elif not self._is_version_compatible(dep):
                    errors.append(
                        CompatibilityError(
                            engine=name,
                            dependency=dep.engine_name,
                            required_version=dep.min_version,
                            actual_version=self._descriptors[dep.engine_name].version,
                        )
                    )

            return errors

    def check_event_contracts(self, name: str) -> list[ValidationError]:
        """Verify that an engine's event contracts are satisfiable.

        Args:
            name: The name of the engine to check.

        Returns:
            List of validation errors for unsatisfiable contracts.

        Raises:
            EngineNotFoundError: If the engine is not registered.
        """
        with self._lock:
            if name not in self._descriptors:
                raise EngineNotFoundError(name)

            errors = []
            descriptor = self._descriptors[name]

            # Check that required events are published by someone
            for contract in descriptor.events.consumes:
                if not contract.is_critical:
                    continue

                # Find who publishes this event
                publishers = [
                    d for d in self._descriptors.values()
                    if d.publishes_event(contract.event_type)
                    and d.status == EngineStatus.ACTIVE
                ]

                if not publishers:
                    errors.append(
                        ValidationError(
                            engine=name,
                            message=f"Required event '{contract.event_type}' is not published by any active engine",
                        )
                    )

            return errors

    def _is_version_compatible(self, dep: VersionRequirement) -> bool:
        """Check if a dependency version is compatible."""
        if dep.engine_name not in self._descriptors:
            return False
        actual_version = self._descriptors[dep.engine_name].version
        return dep.is_satisfied_by(actual_version)

    # --------------------------------------------------------------------------
    # Snapshot
    # --------------------------------------------------------------------------

    def snapshot(self) -> RegistrySnapshot:
        """Create a point-in-time snapshot of the registry.

        Returns:
            A snapshot containing all current engine descriptors.
        """
        with self._lock:
            return RegistrySnapshot.from_registry(self)
