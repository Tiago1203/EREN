"""Cognitive Capability Registry (CCR).

EREN NO registra motores. EREN registra CAPACIDADES COGNITIVAS.

El CCR es el catálogo central de todas las capacidades cognitivas disponibles
dentro de EREN. El Orchestrator nunca conocerá motores concretos. Siempre
solicitará capacidades.

Este módulo es el Kernel de un Sistema Operativo Cognitivo.

Arquitectura only — no business logic, no AI, no implementations.
"""

from __future__ import annotations

from core.capabilities.capability import Capability, CapabilityTemplates
from core.capabilities.capability_registry import CapabilityRegistry
from core.capabilities.descriptor import (
    CapabilityDescriptor,
    CapabilityMatch,
    CapabilityVersion,
    RegistrySnapshot,
)
from core.capabilities.exceptions import (
    CapabilityAlreadyRegisteredError,
    CapabilityNotFoundError,
    CapabilityRegistryError,
    CapabilityUnavailableError,
    CircularDependencyError,
    DependencyNotSatisfiedError,
    EventContractViolationError,
    PermissionDeniedError,
    ProviderNotFoundError,
    ResolutionError,
    ValidationError,
    VersionIncompatibleError,
)
from core.capabilities.resolver import (
    CapabilityMatcher,
    CapabilityResolver,
    ResolutionCriteria,
)
from core.capabilities.types import (
    CapabilityCategory,
    CapabilityFilter,
    CapabilityId,
    CapabilityMetadata,
    CapabilityPriority,
    CapabilityStatus,
    CriticalityLevel,
    EventContract,
    Permission,
    SearchOptions,
    SecurityLevel,
    TimeEstimate,
    VersionRange,
)
from core.capabilities.validators import (
    CapabilityValidator,
    DependencyValidator,
    VersionValidator,
)

__all__ = [
    # Core
    "Capability",
    "CapabilityRegistry",
    "CapabilityTemplates",
    # Descriptors
    "CapabilityDescriptor",
    "CapabilityMatch",
    "CapabilityVersion",
    "RegistrySnapshot",
    # Types
    "CapabilityCategory",
    "CapabilityFilter",
    "CapabilityId",
    "CapabilityMetadata",
    "CapabilityPriority",
    "CapabilityStatus",
    "CriticalityLevel",
    "EventContract",
    "Permission",
    "SearchOptions",
    "SecurityLevel",
    "TimeEstimate",
    "VersionRange",
    # Resolver
    "CapabilityMatcher",
    "CapabilityResolver",
    "ResolutionCriteria",
    # Validators
    "CapabilityValidator",
    "DependencyValidator",
    "VersionValidator",
    # Exceptions
    "CapabilityRegistryError",
    "CapabilityNotFoundError",
    "CapabilityAlreadyRegisteredError",
    "DependencyNotSatisfiedError",
    "PermissionDeniedError",
    "CapabilityUnavailableError",
    "VersionIncompatibleError",
    "EventContractViolationError",
    "ResolutionError",
    "ValidationError",
    "CircularDependencyError",
    "ProviderNotFoundError",
]
