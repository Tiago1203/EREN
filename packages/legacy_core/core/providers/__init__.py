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
    TaskType,
    ProviderCapabilities,
    ProviderMetadata,
    SelectionCriteria,
    CostEstimate,
    StreamChunk,
)

# Health Monitoring
from core.providers.health_monitor import (
    HealthMonitor,
    HealthStatus,
    HealthCheckResult,
    HealthMetrics,
)

# Resilience
from core.providers.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerRegistry,
    CircuitBreakerConfig,
    CircuitBreakerStats,
    CircuitState,
)
from core.providers.rate_limiter import (
    RateLimiter,
    RateLimitConfig,
    RateLimitResult,
    RateLimitStats,
    RateLimitStrategy,
)

# Intelligence
from core.providers.scoring_engine import (
    ScoringEngine,
    ScoringWeights,
    ProviderScore,
)
from core.providers.policy_engine import (
    PolicyEngine,
    PolicyType,
    PolicyPriority,
    PolicyConfig,
    PolicyRule,
)

# Infrastructure
from core.providers.cache import (
    Cache,
    CacheStats,
    CacheStrategy,
    CacheEntry,
    ProviderCache,
)
from core.providers.tracing import (
    Tracer,
    Span,
    SpanStatus,
    SpanKind,
    TraceContext,
    get_tracer,
    reset_tracer,
)
from core.providers.events import (
    EventBus,
    Event,
    EventType,
    get_event_bus,
    reset_event_bus,
    emit_event,
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
    "TaskType",
    "ProviderCapabilities",
    "ProviderMetadata",
    "SelectionCriteria",
    "CostEstimate",
    "StreamChunk",
    # Health
    "HealthMonitor",
    "HealthStatus",
    "HealthCheckResult",
    "HealthMetrics",
    # Resilience
    "CircuitBreaker",
    "CircuitBreakerRegistry",
    "CircuitBreakerConfig",
    "CircuitBreakerStats",
    "CircuitState",
    "RateLimiter",
    "RateLimitConfig",
    "RateLimitResult",
    "RateLimitStats",
    "RateLimitStrategy",
    # Intelligence
    "ScoringEngine",
    "ScoringWeights",
    "ProviderScore",
    "PolicyEngine",
    "PolicyType",
    "PolicyPriority",
    "PolicyConfig",
    "PolicyRule",
    # Infrastructure
    "Cache",
    "CacheStats",
    "CacheStrategy",
    "CacheEntry",
    "ProviderCache",
    "Tracer",
    "Span",
    "SpanStatus",
    "SpanKind",
    "TraceContext",
    "get_tracer",
    "reset_tracer",
    "EventBus",
    "Event",
    "EventType",
    "get_event_bus",
    "reset_event_bus",
    "emit_event",
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
