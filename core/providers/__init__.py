"""EREN OS Multi-Provider Layer (CMPL) - PR-056.

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
    - Enhanced Manager: Adds resilience patterns

Example:
    >>> from core.providers import EnhancedProviderManager, ProviderType
    >>> 
    >>> manager = EnhancedProviderManager()
    >>> 
    >>> # Add providers
    >>> manager.add_provider(MockProvider("openai", "gpt-4"), weight=1.0)
    >>> manager.add_provider(MockProvider("claude", "claude-3"), weight=2.0)
    >>> 
    >>> # Generate with automatic selection and resilience
    >>> response = await manager.generate(request)
    >>> 
    >>> # Generate streaming
    >>> handler = await manager.generate_stream(request)
    >>> for chunk in handler.stream():
    ...     print(chunk.content, end="")
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

# Core
from core.providers.enhanced_manager import (
    EnhancedManagerConfig,
    EnhancedProviderManager,
    get_enhanced_provider_manager,
    reset_enhanced_provider_manager,
)
from core.providers.manager import (
    ProviderManager,
    get_provider_manager,
    reset_provider_manager,
)
from core.providers.provider import BaseProvider
from core.providers.registry import (
    ProviderRegistry,
    get_provider_registry,
    reset_provider_registry,
)
from core.providers.selector import ProviderSelector

# Mock providers
from core.providers.mock_provider import (
    MockProvider,
    MockProviderFactory,
    MockProviderConfig,
    OpenAIMockProvider,
    ClaudeMockProvider,
    GeminiMockProvider,
    OllamaMockProvider,
    DeepSeekMockProvider,
    MistralMockProvider,
    OpenRouterMockProvider,
    AzureOpenAIMockProvider,
    StreamingMockProvider,
)

# Resilience patterns
from core.providers.resilience import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitState,
    LoadBalancer,
    LoadBalancingStrategy,
    RateLimitConfig,
    RetryPolicy,
    RetryStrategy,
    SimpleCache,
    CacheConfig,
    TokenBucketRateLimiter,
)

# Streaming
from core.providers.streaming import (
    StreamChunk,
    StreamHandler,
    StreamMetrics,
    CallbackStreamHandler,
    CollectingStreamHandler,
    GeneratorStreamHandler,
    StreamAdapter,
    OpenAIStreamAdapter,
    AnthropicStreamAdapter,
    MockStreamAdapter,
)

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
    "EnhancedProviderManager",
    "EnhancedManagerConfig",
    "get_enhanced_provider_manager",
    "reset_enhanced_provider_manager",
    # Mock providers
    "MockProvider",
    "MockProviderConfig",
    "MockProviderFactory",
    "OpenAIMockProvider",
    "ClaudeMockProvider",
    "GeminiMockProvider",
    "OllamaMockProvider",
    "DeepSeekMockProvider",
    "MistralMockProvider",
    "OpenRouterMockProvider",
    "AzureOpenAIMockProvider",
    "StreamingMockProvider",
    # Resilience patterns
    "CircuitBreaker",
    "CircuitBreakerConfig",
    "CircuitState",
    "LoadBalancer",
    "LoadBalancingStrategy",
    "RateLimitConfig",
    "RetryPolicy",
    "RetryStrategy",
    "SimpleCache",
    "CacheConfig",
    "TokenBucketRateLimiter",
    # Streaming
    "StreamChunk",
    "StreamHandler",
    "StreamMetrics",
    "CallbackStreamHandler",
    "CollectingStreamHandler",
    "GeneratorStreamHandler",
    "StreamAdapter",
    "OpenAIStreamAdapter",
    "AnthropicStreamAdapter",
    "MockStreamAdapter",
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
