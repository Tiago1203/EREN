"""Enhanced Provider Manager with resilience patterns (PR-056).

Extends the base ProviderManager with:
- Circuit Breaker
- Retry Policy
- Rate Limiting
- Load Balancing
- Caching
- Streaming Support
"""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Callable

from core.providers.manager import ProviderManager
from core.providers.provider import BaseProvider
from core.providers.registry import ProviderRegistry, get_provider_registry
from core.providers.resilience import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitState,
    CacheConfig,
    LoadBalancer,
    LoadBalancingStrategy,
    RateLimitConfig,
    RetryPolicy,
    RetryStrategy,
    SimpleCache,
    TokenBucketRateLimiter,
)
from core.providers.selector import ProviderSelector
from core.providers.streaming import (
    CollectingStreamHandler,
    GeneratorStreamHandler,
    StreamChunk,
    StreamHandler,
)
from core.providers.types import (
    GenerationRequest,
    GenerationResponse,
    ProviderConfig,
    ProviderHealth,
    ProviderMetrics,
    SelectionPolicy,
)


# =============================================================================
# Enhanced Manager
# =============================================================================


@dataclass
class EnhancedManagerConfig:
    """Configuration for enhanced manager."""
    enable_circuit_breaker: bool = True
    enable_retry: bool = True
    enable_rate_limiting: bool = True
    enable_load_balancing: bool = True
    enable_caching: bool = True
    
    circuit_breaker: CircuitBreakerConfig = field(default_factory=CircuitBreakerConfig)
    retry_policy: RetryPolicy = field(default_factory=lambda: RetryPolicy())
    rate_limit: RateLimitConfig = field(default_factory=RateLimitConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)
    load_balancing: LoadBalancingStrategy = LoadBalancingStrategy.ROUND_ROBIN


class EnhancedProviderManager(ProviderManager):
    """Enhanced provider manager with resilience patterns.

    Adds:
    - Circuit breaker per provider
    - Automatic retry with configurable policy
    - Rate limiting
    - Load balancing across providers
    - Response caching
    - Streaming support
    - Telemetry and tracing
    """

    def __init__(
        self,
        config: EnhancedManagerConfig | None = None,
        registry: ProviderRegistry | None = None,
    ):
        """Initialize enhanced manager."""
        super().__init__(registry=registry)
        self._config = config or EnhancedManagerConfig()

        # Initialize resilience components
        self._circuit_breakers: dict[str, CircuitBreaker] = {}
        self._rate_limiters: dict[str, TokenBucketRateLimiter] = {}
        self._load_balancer = LoadBalancer(config=self._config.load_balancing)
        self._cache = SimpleCache(self._config.cache)

        # Event handlers
        self._event_handlers: dict[str, list[Callable]] = {}

        # Global rate limiter
        if self._config.enable_rate_limiting:
            self._global_rate_limiter = TokenBucketRateLimiter(self._config.rate_limit)
        else:
            self._global_rate_limiter = None

    # =========================================================================
    # Provider Management
    # =========================================================================

    def add_provider(
        self,
        provider: BaseProvider,
        config: ProviderConfig | None = None,
        weight: float = 1.0,
    ) -> None:
        """Add provider with resilience setup."""
        super().add_provider(provider, config)

        # Setup circuit breaker
        if self._config.enable_circuit_breaker:
            self._circuit_breakers[provider.provider_id] = CircuitBreaker(
                name=provider.provider_id,
                config=self._config.circuit_breaker,
                on_state_change=self._on_circuit_state_change,
            )

        # Setup rate limiter
        if self._config.enable_rate_limiting:
            self._rate_limiters[provider.provider_id] = TokenBucketRateLimiter(
                self._config.rate_limit
            )

        # Register with load balancer
        if self._config.enable_load_balancing:
            self._load_balancer.register_provider(
                provider.provider_id,
                weight=weight,
            )

    # =========================================================================
    # Generate with Resilience
    # =========================================================================

    async def generate(
        self,
        request: GenerationRequest,
        provider_id: str | None = None,
        use_cache: bool = True,
        skip_resilience: bool = False,
    ) -> GenerationResponse:
        """Generate with resilience patterns.

        Args:
            request: Generation request.
            provider_id: Specific provider ID (optional).
            use_cache: Whether to use caching.
            skip_resilience: Skip resilience patterns (for testing).

        Returns:
            Generation response.
        """
        cache_key = self._generate_cache_key(request) if use_cache else None

        # Check cache
        if cache_key and self._config.enable_caching:
            cached = self._cache.get(cache_key)
            if cached:
                self._emit_event("cache_hit", {"provider_id": provider_id})
                return cached

        # Rate limit
        if self._global_rate_limiter and not skip_resilience:
            self._global_rate_limiter.acquire()

        # Select provider
        if not provider_id:
            provider_id = self._select_provider()

        if not provider_id:
            raise Exception("No available providers")

        # Execute with resilience
        response = await self._execute_with_resilience(
            provider_id, request, skip_resilience
        )

        # Cache response
        if cache_key and self._config.enable_caching:
            self._cache.set(cache_key, response)

        # Emit events
        self._emit_event("response_generated", {
            "provider_id": provider_id,
            "tokens": response.tokens_used,
            "duration_ms": response.duration_ms,
        })

        return response

    async def generate_with_fallback(
        self,
        request: GenerationRequest,
        preferred_providers: list[str] | None = None,
    ) -> GenerationResponse:
        """Generate with automatic fallback to other providers."""
        providers = preferred_providers or self._get_available_providers()

        last_error: Exception | None = None
        for provider_id in providers:
            try:
                return await self.generate(request, provider_id)
            except Exception as e:
                last_error = e
                self._emit_event("fallback_triggered", {
                    "from_provider": provider_id,
                    "error": str(e),
                })
                continue

        raise Exception(f"All providers failed. Last error: {last_error}")

    async def generate_stream(
        self,
        request: GenerationRequest,
        provider_id: str | None = None,
        handler: StreamHandler | None = None,
    ) -> GeneratorStreamHandler:
        """Generate streaming response.

        Args:
            request: Generation request.
            provider_id: Specific provider ID.
            handler: Stream handler.

        Returns:
            Stream handler with chunks.
        """
        if handler is None:
            handler = GeneratorStreamHandler()

        if not provider_id:
            provider_id = self._select_provider()

        provider = self._registry.get_provider(provider_id)
        if not provider:
            handler.on_error(Exception(f"Provider not found: {provider_id}"))
            return handler

        # Check circuit breaker
        if self._config.enable_circuit_breaker:
            circuit = self._circuit_breakers.get(provider_id)
            if circuit and not circuit.allow_request():
                handler.on_error(Exception(f"Circuit breaker open for: {provider_id}"))
                return handler

        try:
            await provider.generate_stream(request, handler)
        except Exception as e:
            self._record_failure(provider_id, e)
            handler.on_error(e)

        return handler

    # =========================================================================
    # Resilience Implementation
    # =========================================================================

    async def _execute_with_resilience(
        self,
        provider_id: str,
        request: GenerationRequest,
        skip_resilience: bool,
    ) -> GenerationResponse:
        """Execute request with resilience patterns."""
        if skip_resilience:
            return await self._direct_generate(provider_id, request)

        provider = self._registry.get_provider(provider_id)
        if not provider:
            raise Exception(f"Provider not found: {provider_id}")

        # Check circuit breaker
        circuit = self._circuit_breakers.get(provider_id)
        if circuit and not circuit.allow_request():
            raise Exception(f"Circuit breaker open for: {provider_id}")

        # Execute with retry
        retry_policy = self._config.retry_policy
        last_error: Exception | None = None

        for attempt in range(retry_policy.max_attempts):
            try:
                # Rate limit if enabled
                rate_limiter = self._rate_limiters.get(provider_id)
                if rate_limiter:
                    rate_limiter.acquire()

                # Record request start for load balancer
                if self._config.enable_load_balancing:
                    self._load_balancer.record_request_start(provider_id)

                # Execute
                response = await provider.generate(request)

                # Record success
                self._record_success(provider_id)
                if self._config.enable_load_balancing:
                    self._load_balancer.record_request_end(provider_id, True)

                return response

            except Exception as e:
                last_error = e
                if self._config.enable_load_balancing:
                    self._load_balancer.record_request_end(provider_id, False)

                # Check if should retry
                if not retry_policy.should_retry(attempt, e):
                    break

                # Wait before retry
                delay = retry_policy.get_delay(attempt)
                time.sleep(delay)

        # All retries failed
        self._record_failure(provider_id, last_error)
        raise last_error or Exception("Provider execution failed")

    async def _direct_generate(
        self,
        provider_id: str,
        request: GenerationRequest,
    ) -> GenerationResponse:
        """Direct generate without resilience."""
        provider = self._registry.get_provider(provider_id)
        if not provider:
            raise Exception(f"Provider not found: {provider_id}")
        return await provider.generate(request)

    def _record_success(self, provider_id: str) -> None:
        """Record successful request."""
        circuit = self._circuit_breakers.get(provider_id)
        if circuit:
            circuit.record_success()

    def _record_failure(self, provider_id: str, error: Exception) -> None:
        """Record failed request."""
        circuit = self._circuit_breakers.get(provider_id)
        if circuit:
            circuit.record_failure()

        self._emit_event("provider_error", {
            "provider_id": provider_id,
            "error": str(error),
        })

    # =========================================================================
    # Provider Selection
    # =========================================================================

    def _select_provider(self) -> str | None:
        """Select provider using configured strategy."""
        available = self._get_available_providers()

        if not available:
            return None

        # Filter by circuit breaker
        if self._config.enable_circuit_breaker:
            available = [
                pid for pid in available
                if self._circuit_breakers.get(pid, CircuitBreaker(pid)).state != CircuitState.OPEN
            ]

        if not available:
            return None

        # Use load balancer
        if self._config.enable_load_balancing:
            return self._load_balancer.select_provider(available)

        # Fallback to selector
        return self._selector.select(available)

    def _get_available_providers(self) -> list[str]:
        """Get list of available provider IDs."""
        return list(self._registry.list_providers())

    # =========================================================================
    # Circuit Breaker Events
    # =========================================================================

    def _on_circuit_state_change(
        self,
        name: str,
        old_state: CircuitState,
        new_state: CircuitState,
    ) -> None:
        """Handle circuit breaker state change."""
        self._emit_event("circuit_state_change", {
            "provider_id": name,
            "old_state": old_state.value,
            "new_state": new_state.value,
        })

    # =========================================================================
    # Cache
    # =========================================================================

    def _generate_cache_key(self, request: GenerationRequest) -> str:
        """Generate cache key for request."""
        import hashlib
        content = "".join(m.content for m in request.messages)
        return hashlib.md5(content.encode()).hexdigest()

    def clear_cache(self) -> None:
        """Clear response cache."""
        self._cache.clear()

    def get_cache_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        return self._cache.get_stats()

    # =========================================================================
    # Telemetry
    # =========================================================================

    def get_telemetry(self) -> dict[str, Any]:
        """Get comprehensive telemetry data."""
        providers = {}
        for pid in self._registry.list_providers():
            circuit = self._circuit_breakers.get(pid)
            rate_limiter = self._rate_limiters.get(pid)
            provider = self._registry.get_provider(pid)

            providers[pid] = {
                "circuit_breaker": circuit.get_state() if circuit else None,
                "rate_limit_available": rate_limiter.get_available_tokens() if rate_limiter else None,
                "metrics": provider.get_metrics().__dict__ if provider else None,
            }

        return {
            "providers": providers,
            "load_balancer": self._load_balancer.get_stats(),
            "cache": self._cache.get_stats(),
            "config": {
                "enable_circuit_breaker": self._config.enable_circuit_breaker,
                "enable_retry": self._config.enable_retry,
                "enable_rate_limiting": self._config.enable_rate_limiting,
                "enable_load_balancing": self._config.enable_load_balancing,
                "enable_caching": self._config.enable_caching,
            },
        }

    # =========================================================================
    # Event System
    # =========================================================================

    def _emit_event(self, event_type: str, data: dict[str, Any]) -> None:
        """Emit internal event."""
        handlers = self._event_handlers.get(event_type, [])
        for handler in handlers:
            try:
                handler(data)
            except Exception:
                pass

    def on(self, event_type: str, handler: Callable) -> None:
        """Subscribe to event."""
        if event_type not in self._event_handlers:
            self._event_handlers[event_type] = []
        self._event_handlers[event_type].append(handler)


# =============================================================================
# Singleton
# =============================================================================


_enhanced_manager: EnhancedProviderManager | None = None
_manager_lock = threading.Lock()


def get_enhanced_provider_manager() -> EnhancedProviderManager:
    """Get global enhanced provider manager."""
    global _enhanced_manager
    with _manager_lock:
        if _enhanced_manager is None:
            _enhanced_manager = EnhancedProviderManager()
        return _enhanced_manager


def reset_enhanced_provider_manager() -> None:
    """Reset global enhanced provider manager."""
    global _enhanced_manager
    with _manager_lock:
        _enhanced_manager = None
