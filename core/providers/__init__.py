"""EREN OS Multi-Provider Layer (CMPL).

This module implements the Cognitive Multi-Provider Layer, the official
abstraction layer for LLM providers in EREN.

Philosophy:
    The Cognitive Kernel never knows a specific provider. All cognitive
    capabilities use a common provider contract.

Key Concepts:
    - Provider: A concrete LLM provider (OpenAI, Claude, Ollama, etc.)
    - Registry: Manages provider registration
    - Selector: Implements selection strategies
    - Manager: Orchestrates all provider operations

Example:
    >>> from core.providers import ProviderManager, ProviderConfig, ProviderType
    >>> 
    >>> manager = ProviderManager()
    >>> 
    >>> # Add providers
    >>> manager.add_provider(OpenAIProvider(), config)
    >>> manager.add_provider(OllamaProvider(), config)
    >>> 
    >>> # Generate with automatic selection
    >>> response = manager.generate(request)
    >>> 
    >>> # Generate with specific provider
    >>> response = manager.generate(request, policy=SelectionPolicy.PRIORITY)
"""

from __future__ import annotations

# Exceptions
from core.providers.exceptions import (
    ProviderAuthenticationError,
    ProviderConfigurationError,
    ProviderConnectionError,
    ProviderException,
    ProviderFallbackError,
    ProviderHealthCheckError,
    ProviderInitializationError,
    ProviderNotFoundError,
    ProviderNotRegisteredError,
    ProviderPolicyError,
    ProviderRateLimitError,
    ProviderTimeoutError,
    ProviderUnavailableError,
)
from core.providers.manager import (
    ProviderManager,
    get_provider_manager,
    reset_provider_manager,
)

# Core
from core.providers.provider import BaseProvider
from core.providers.registry import (
    ProviderRegistry,
    get_provider_registry,
    reset_provider_registry,
)
from core.providers.selector import ProviderSelector

# Types
from core.providers.types import (
    GenerationRequest,
    GenerationResponse,
    ProviderConfig,
    ProviderHealth,
    ProviderMetrics,
    ProviderState,
    ProviderType,
    SelectionPolicy,
)

__all__ = [
    # Core
    "BaseProvider",
    "ProviderRegistry",
    "get_provider_registry",
    "reset_provider_registry",
    "ProviderSelector",
    "ProviderManager",
    "get_provider_manager",
    "reset_provider_manager",
    # Types
    "ProviderType",
    "ProviderState",
    "SelectionPolicy",
    "ProviderHealth",
    "ProviderMetrics",
    "ProviderConfig",
    "GenerationRequest",
    "GenerationResponse",
    # Exceptions
    "ProviderException",
    "ProviderNotFoundError",
    "ProviderNotRegisteredError",
    "ProviderConfigurationError",
    "ProviderInitializationError",
    "ProviderConnectionError",
    "ProviderAuthenticationError",
    "ProviderRateLimitError",
    "ProviderTimeoutError",
    "ProviderHealthCheckError",
    "ProviderUnavailableError",
    "ProviderPolicyError",
    "ProviderFallbackError",
]
