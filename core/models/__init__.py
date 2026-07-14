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
    >>> from core.models import ModelRegistry, ModelCatalog
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

# Core
from core.models.descriptor import ModelDescriptor
from core.models.registry import (
    ModelRegistry,
    get_model_registry,
    reset_model_registry,
)
from core.models.selector import ModelSelector
from core.models.catalog import ModelCatalog

# Types
from core.models.types import (
    ModelCategory,
    ModelState,
    ModelSelectionPolicy,
    ModelCapabilities,
    ModelPricing,
    ModelAvailability,
    ModelMetrics,
)

# Exceptions
from core.models.exceptions import (
    ModelRegistryException,
    ModelNotFoundError,
    ModelAlreadyRegisteredError,
    ModelNotRegisteredError,
    ModelUnavailableError,
    ModelConfigurationError,
    ModelCapabilityError,
    ProviderNotFoundError,
    ModelSelectionError,
    ModelDiscoveryError,
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
