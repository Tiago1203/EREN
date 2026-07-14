"""EREN OS Cognitive Capability SDK.

This module implements the Cognitive Capability SDK (CCSDK), the official
framework for developing cognitive capabilities for EREN.

Philosophy:
    Developers never implement directly the Cognitive Kernel.
    They develop capabilities using the Capability SDK.

Key Concepts:
    - Capability: A self-contained cognitive function
    - BaseCapability: Abstract base for all capabilities
    - Builder: Builder pattern for creating capabilities
    - Registry: Manages capability registration
    - LifecycleManager: Handles capability lifecycle

Example:
    >>> from core.sdk import BaseCapability, CapabilityBuilder
    >>> class MyCapability(BaseCapability):
    ...     def initialize(self, context): pass
    ...     def execute(self, context): return CapabilityResult(success=True)
    ...     def shutdown(self): pass
    ...
    >>> metadata = CapabilityBuilder().named("my-capability").build()
"""

from __future__ import annotations

# Core
from core.sdk.capability import BaseCapability
from core.sdk.builder import CapabilityBuilder, CapabilityClassBuilder
from core.sdk.lifecycle import LifecycleManager, get_lifecycle_manager
from core.sdk.registry import (
    CapabilityRegistry,
    get_capability_registry,
    reset_capability_registry,
)

# Types
from core.sdk.types import (
    CapabilityState,
    CapabilityCategory,
    CapabilityPriority,
    CapabilityMetadata,
    CapabilityContext,
    CapabilityResult,
    CapabilityHealth,
    ValidationResult,
)

# Exceptions
from core.sdk.exceptions import (
    SDKException,
    CapabilityInitializationError,
    CapabilityExecutionError,
    CapabilityNotFoundError,
    CapabilityAlreadyRegisteredError,
    CapabilityValidationError,
    CapabilityDependencyError,
    CapabilityContractError,
    CapabilityStateError,
    CapabilityBuilderError,
    CapabilityContextError,
)


__all__ = [
    # Core
    "BaseCapability",
    "CapabilityBuilder",
    "CapabilityClassBuilder",
    "LifecycleManager",
    "get_lifecycle_manager",
    "CapabilityRegistry",
    "get_capability_registry",
    "reset_capability_registry",
    # Types
    "CapabilityState",
    "CapabilityCategory",
    "CapabilityPriority",
    "CapabilityMetadata",
    "CapabilityContext",
    "CapabilityResult",
    "CapabilityHealth",
    "ValidationResult",
    # Exceptions
    "SDKException",
    "CapabilityInitializationError",
    "CapabilityExecutionError",
    "CapabilityNotFoundError",
    "CapabilityAlreadyRegisteredError",
    "CapabilityValidationError",
    "CapabilityDependencyError",
    "CapabilityContractError",
    "CapabilityStateError",
    "CapabilityBuilderError",
    "CapabilityContextError",
]
