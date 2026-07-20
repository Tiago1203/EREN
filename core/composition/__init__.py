"""Cognitive Composition Root (CCRoot).

The official composition root for EREN OS.

Architecture only -- no implementations, no business logic.
"""

from core.composition.composition_builder import CompositionBuilder
from core.composition.composition_events import (
    CompositionEventPublisher,
    CompositionEventType,
)
from core.composition.composition_metrics import CompositionMetricsCollector
from core.composition.composition_module import (
    CapabilityModule,
    CognitiveModule,
    CompositionModule,
    CoreModule,
    InfrastructureModule,
)
from core.composition.composition_root import (
    CognitiveCompositionRoot,
    CompositionRootFactory,
)
from core.composition.composition_trace import (
    CompositionTraceCollector,
    CompositionTraceEntry,
)
from core.composition.composition_validator import (
    CompositionValidator,
    ValidationError,
    ValidationResult,
)
from core.composition.exceptions import (
    CompositionBuildException,
    CompositionException,
    CompositionValidationException,
    ContractRegistrationException,
    ModuleAlreadyRegisteredException,
    ModuleDependencyException,
    ModuleNotFoundException,
    ModuleRegistrationException,
    ModuleValidationException,
    RuntimeInitializationException,
)
from core.composition.module_descriptor import (
    ModuleContract,
    ModuleDependency,
    ModuleDescriptor,
    ModuleInstance,
)
from core.composition.module_loader import LoadStrategy, ModuleLoader
from core.composition.module_registry import ModuleRegistry

__all__ = [
    # Main Composition Root
    "CognitiveCompositionRoot",
    "CompositionRootFactory",
    "CompositionBuilder",
    # Modules
    "CompositionModule",
    "CoreModule",
    "InfrastructureModule",
    "CognitiveModule",
    "CapabilityModule",
    # Events
    "CompositionEventType",
    "CompositionEventPublisher",
    # Metrics
    "CompositionMetricsCollector",
    # Trace
    "CompositionTraceCollector",
    "CompositionTraceEntry",
    # Validator
    "CompositionValidator",
    "ValidationError",
    "ValidationResult",
    # Descriptors
    "ModuleDescriptor",
    "ModuleDependency",
    "ModuleContract",
    "ModuleInstance",
    # Registry
    "ModuleRegistry",
    # Loader
    "ModuleLoader",
    "LoadStrategy",
    # Exceptions
    "CompositionException",
    "ModuleRegistrationException",
    "ModuleValidationException",
    "CompositionValidationException",
    "CompositionBuildException",
    "ModuleDependencyException",
    "RuntimeInitializationException",
    "ModuleNotFoundException",
    "ModuleAlreadyRegisteredException",
    "ContractRegistrationException",
]
