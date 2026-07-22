"""EREN OS Cognitive Model Registry (CMR).

This module implements the Cognitive Model Registry, the official system for
registering, discovering, and managing LLM models in EREN.

Philosophy:
    Providers offer models. The Cognitive Kernel never knows specific models.
    All decisions about models are made through the Model Registry.

Key Concepts:
    - ModelDescriptor: Contains all model metadata
    - ModelRegistry: Manages model registration and discovery
    - ModelSelector: Implements selection strategies
    - ModelCatalog: Pre-defined model descriptors

Example:
    >>> from core.PHASE_1.domain.models import ModelRegistry, ModelCatalog
    >>> 
    >>> registry = ModelRegistry()
    >>> 
    >>> # Register models from catalog
    >>> registry.register_from_catalog()
    >>> 
    >>> # Get a model
    >>> model = registry.get("gpt-5-mini")
    >>> 
    >>> # Find best model for task
    >>> best = registry.find_best(ModelSelectionPolicy.REASONING)
"""

from __future__ import annotations

from core.PHASE_1.domain.models.catalog import ModelCatalog

# Core
from core.PHASE_1.domain.models.descriptor import ModelDescriptor

# Exceptions
from core.PHASE_1.domain.models.exceptions import (
    ModelAlreadyRegisteredError,
    ModelCapabilityError,
    ModelConfigurationError,
    ModelDiscoveryError,
    ModelNotFoundError,
    ModelNotRegisteredError,
    ModelRegistryException,
    ModelSelectionError,
    ModelUnavailableError,
    ProviderNotFoundError,
)
from core.PHASE_1.domain.models.registry import (
    ModelRegistry,
    get_model_registry,
    reset_model_registry,
)
from core.PHASE_1.domain.models.selector import ModelSelector

# Types
from core.PHASE_1.domain.models.types import (
    ModelAvailability,
    ModelCapabilities,
    ModelCategory,
    ModelMetrics,
    ModelPricing,
    ModelSelectionPolicy,
    ModelState,
)

__all__ = [
    # Core
    "ModelDescriptor",
    "ModelRegistry",
    "get_model_registry",
    "reset_model_registry",
    "ModelSelector",
    "ModelCatalog",
    # Types
    "ModelCategory",
    "ModelState",
    "ModelSelectionPolicy",
    "ModelCapabilities",
    "ModelPricing",
    "ModelAvailability",
    "ModelMetrics",
    # Exceptions
    "ModelRegistryException",
    "ModelNotFoundError",
    "ModelAlreadyRegisteredError",
    "ModelNotRegisteredError",
    "ModelUnavailableError",
    "ModelConfigurationError",
    "ModelCapabilityError",
    "ProviderNotFoundError",
    "ModelSelectionError",
    "ModelDiscoveryError",
]
