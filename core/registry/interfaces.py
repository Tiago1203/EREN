"""Registry abstraction for EREN.

Defines the :class:`EngineRegistryPort` contract so consumers depend on the
*abstraction* of a registry, not on the concrete :class:`EngineRegistry`
(Dependency Inversion).
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol, runtime_checkable

from core.contracts import CognitiveEngine
from core.registry.models import EngineDescriptor
from core.registry.types import EngineStatus, SearchOptions


@runtime_checkable
class EngineRegistryPort(Protocol):
    """Contract for a dynamic registry of cognitive engines.

    This abstraction allows the Orchestrator to discover engines without
    coupling to a specific registry implementation.
    """

    def register(self, engine: CognitiveEngine, *, replace: bool = False) -> None:
        """Register ``engine`` under its ``name``."""
        ...

    def unregister(self, name: str) -> None:
        """Remove the engine registered under ``name``."""
        ...

    def get(self, name: str) -> CognitiveEngine:
        """Return the engine registered under ``name``."""
        ...

    def list(self) -> Sequence[CognitiveEngine]:
        """Return all registered engines."""
        ...

    def get_descriptor(self, name: str) -> EngineDescriptor:
        """Return the descriptor for a registered engine."""
        ...

    def list_descriptors(self) -> Sequence[EngineDescriptor]:
        """Return all registered engine descriptors."""
        ...

    def find_by_capability(self, capability: str) -> Sequence[EngineDescriptor]:
        """Find engines that provide a specific capability."""
        ...

    def get_active_engines(self) -> Sequence[EngineDescriptor]:
        """Return all engines with ACTIVE status."""
        ...


class RegistryProvider(Protocol):
    """Protocol for components that provide registry access.

    Implement this if you need to access the registry from different
    parts of the application without passing it explicitly.
    """

    def get_registry(self) -> EngineRegistryPort:
        """Get the current registry instance."""
        ...
