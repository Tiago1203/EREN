"""EREN engine registry.

The Engine Registry is the central catalog of all cognitive engines.
The Orchestrator never knows concrete implementations — it only queries the Registry.

Architecture only — no business logic, no AI, no engine implementations.
"""

from __future__ import annotations

from core.PHASE_2.registry.exceptions import (
    CircularDependencyError,
    CompatibilityError,
    DependencyNotFoundError,
    EngineAlreadyRegisteredError,
    EngineNotFoundError,
    EventContractError,
    RegistryError,
    ValidationError,
)
from core.PHASE_2.registry.interfaces import EngineRegistryPort, RegistryProvider
from core.PHASE_2.registry.models import EngineDescriptor, RegistrySnapshot
from core.PHASE_2.registry.registry import EngineRegistry
from core.PHASE_2.registry.types import (
    Capability,
    EngineFilter,
    EngineMetadata,
    EnginePriority,
    EngineStatus,
    EventContract,
    EventContracts,
    SearchOptions,
    VersionRequirement,
)

__all__ = [
    # Core
    "EngineRegistry",
    "EngineRegistryPort",
    "RegistryProvider",
    # Models
    "EngineDescriptor",
    "RegistrySnapshot",
    # Types
    "Capability",
    "EngineFilter",
    "EngineMetadata",
    "EnginePriority",
    "EngineStatus",
    "EventContract",
    "EventContracts",
    "SearchOptions",
    "VersionRequirement",
    # Exceptions
    "RegistryError",
    "EngineNotFoundError",
    "EngineAlreadyRegisteredError",
    "DependencyNotFoundError",
    "CompatibilityError",
    "ValidationError",
    "EventContractError",
    "CircularDependencyError",
]
