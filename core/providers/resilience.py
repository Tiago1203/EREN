"""Resilience patterns for EREN OS Multi-Provider Layer (PR-056).

Implements:
- Circuit Breaker
- Retry Policy
- Rate Limiter
- Load Balancer
- Cache

Philosophy:
    Providers are fallible. The system must handle failures gracefully
    and maintain resilience through these patterns.
"""

from __future__ import annotations

import threading
import time
from collections import deque
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any, Callable


# =============================================================================
# Circuit Breaker
# =============================================================================


class CircuitState(str, Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, rejecting requests
    HALF_OPEN = "half_open"  # Testing if recovered


@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration."""
    failure_threshold: int = 5       # Failures before opening
    success_threshold: int = 3       # Successes to close
    timeout_seconds: float = 60.0    # Time before trying again
    half_open_max_calls: int = 3     # Max calls in half-open


class CircuitBreaker:
    """Circuit breaker pattern implementation."""

    def __init__(
        self,
        name: str,
        config: CircuitBreakerConfig | None = None,
        on_state_change: Callable[[str, CircuitState, CircuitState], None] | None = None,
    ):
        """Initialize circuit breaker."""
        self._name = name
        self._config = config or CircuitBreakerConfig()
        self._on_state_change = on_state_change
        
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time: float | None = None
        self._half_open_calls = 0
        self._lock = threading.RLock()

    @property
    def name(self) -> str:
        """Get circuit breaker name."""
        return self._name

    @property
    def state(self) -> CircuitState:
        """Get current state."""
        with self._lock:
            return self._evaluate_state()

    def _evaluate_state(self) -> CircuitState:
        """Evaluate state based on conditions."""
        if self._state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self._transition_to(CircuitState.HALF_OPEN)
        return self._state

    def _should_attempt_reset(self) -> bool:
        """Check if should attempt reset."""
        if self._last_failure_time is None:
            return True
        elapsed = time.time() - self._last_failure_time
        return elapsed >= self._config.timeout_seconds

    def _transition_to(self, new_state: CircuitState) -> None:
        """Transition to a new state."""
        old_state = self._state
        self._state = new_state
        
        if new_state == CircuitState.CLOSED:
            self._failure_count = 0
            self._success_count = 0
        elif new_state == CircuitState.HALF_OPEN:
            self._half_open_calls = 0
        
        if self._on_state_change:
            self._on_state_change(self._name, old_state, new_state)

    def allow_request(self) -> bool:
        """Check if request should be allowed."""
        with self._lock:
            self._evaluate_state()
            
            if self._state == CircuitState.CLOSED:
                return True
            
            if self._state == CircuitState.HALF_OPEN:
                if self._half_open_calls < self._config.half_open_max_calls:
                    self._half_open_calls += 1
                    return True
                return False
            
            return False

    def record_success(self) -> None:
        """Record a successful call."""
        with self._lock:
            if self._state == CircuitState.HALF_OPEN:
                self._success_count += 1
                if self._success_count >= self._config.success_threshold:
                    self._transition_to(CircuitState.CLOSED)
            elif self._state == CircuitState.CLOSED:
                self._failure_count = 0

    def record_failure(self) -> None:
        """Record a failed call."""
        with self._lock:
            self._failure_count += 1
            self._last_failure_time = time.time()
            
            if self._state == CircuitState.HALF_OPEN:
                self._transition_to(CircuitState.OPEN)
            elif self._state == CircuitState.CLOSED:
                if self._failure_count >= self._config.failure_threshold:
                    self._transition_to(CircuitState.OPEN)

    def get_state(self) -> dict[str, Any]:
        """Get circuit breaker state."""
        with self._lock:
            return {
                "name": self._name,
                "state": self._state.value,
                "failure_count": self._failure_count,
                "success_count": self._success_count,
                "last_failure_time": self._last_failure_time,
            }


# =============================================================================
# Retry Policy
# =============================================================================


class RetryStrategy(str, Enum):
    """Retry strategies."""
    FIXED = "fixed"
    EXPONENTIAL = "exponential"
    LINEAR = "linear"


@dataclass
class RetryPolicy:
    """Retry policy configuration."""
    max_attempts: int = 3
    initial_delay_seconds: float = 1.0
    max_delay_seconds: float = 30.0
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL
    retryable_errors: tuple[str, ...] = ("timeout", "rate_limit", "server_error")

    def get_delay(self, attempt: int) -> float:
        """Calculate delay for attempt."""
        if self.strategy == RetryStrategy.FIXED:
            return self.initial_delay_seconds
        elif self.strategy == RetryStrategy.EXPONENTIAL:
            delay = self.initial_delay_seconds * (2 ** (attempt - 1))
        else:  # LINEAR
            delay = self.initial_delay_seconds * attempt
        
        return min(delay, self.max_delay_seconds)

    def should_retry(self, attempt: int, error: Exception) -> bool:
        """Check if should retry."""
        if attempt >= self.max_attempts:
            return False
        
        error_type = type(error).__name__.lower()
        return any(re in error_type for re in self.retryable_errors)


# =============================================================================
# Rate Limiter
# =============================================================================


@dataclass
class RateLimitConfig:
    """Rate limit configuration."""
    requests_per_minute: int = 60
    requests_per_second: int = 10
    burst_size: int = 20


class TokenBucketRateLimiter:
    """Token bucket rate limiter implementation."""

    def __init__(self, config: RateLimitConfig | None = None):
        """Initialize rate limiter."""
        self._config = config or RateLimitConfig()
        self._tokens = self._config.burst_size
        self._last_refill = time.time()
        self._lock = threading.Lock()

    def _refill(self) -> None:
        """Refill tokens based on elapsed time."""
        now = time.time()
        elapsed = now - self._last_refill
        
        tokens_to_add = elapsed * (self._config.requests_per_second)
        self._tokens = min(
            self._config.burst_size,
            self._tokens + tokens_to_add
        )
        self._last_refill = now

    def acquire(self, tokens: int = 1, blocking: bool = True, timeout: float = 30.0) -> bool:
        """Acquire tokens."""
        start = time.time()
        
        while True:
            with self._lock:
                self._refill()
                
                if self._tokens >= tokens:
                    self._tokens -= tokens
                    return True
                
                if not blocking:
                    return False
            
            if not blocking or (time.time() - start) >= timeout:
                return False
            
            time.sleep(0.1)

    def get_available_tokens(self) -> float:
        """Get available tokens."""
        with self._lock:
            self._refill()
            return self._tokens

    def get_wait_time(self, tokens: int = 1) -> float:
        """Get estimated wait time for tokens."""
        with self._lock:
            self._refill()
            if self._tokens >= tokens:
                return 0.0
            tokens_needed = tokens - self._tokens
            return tokens_needed / self._config.requests_per_second


# =============================================================================
# Load Balancer
# =============================================================================


class LoadBalancingStrategy(str, Enum):
    """Load balancing strategies."""
    ROUND_ROBIN = "round_robin"
    LEAST_LOADED = "least_loaded"
    WEIGHTED = "weighted"
    RANDOM = "random"
    PRIORITY = "priority"


@dataclass
class LoadBalancerConfig:
    """Load balancer configuration."""
    strategy: LoadBalancingStrategy = LoadBalancingStrategy.ROUND_ROBIN
    health_check_interval: float = 30.0
    unhealthy_threshold: int = 3


class LoadBalancer:
    """Load balancer for providers."""

    def __init__(
        self,
        config: LoadBalancingStrategy | None = None,
    ):
        """Initialize load balancer."""
        self._config = config or LoadBalancingStrategy.ROUND_ROBIN
        self._providers: dict[str, dict[str, Any]] = {}
        self._round_robin_index: int = 0
        self._lock = threading.RLock()

    def register_provider(
        self,
        provider_id: str,
        weight: float = 1.0,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Register a provider."""
        with self._lock:
            self._providers[provider_id] = {
                "weight": weight,
                "active_requests": 0,
                "completed_requests": 0,
                "failed_requests": 0,
                "metadata": metadata or {},
            }

    def unregister_provider(self, provider_id: str) -> bool:
        """Unregister a provider."""
        with self._lock:
            if provider_id in self._providers:
                del self._providers[provider_id]
                return True
            return False

    def select_provider(self, available_providers: list[str]) -> str | None:
        """Select a provider based on strategy."""
        if not available_providers:
            return None

        available = {pid: self._providers[pid] for pid in available_providers if pid in self._providers}
        
        if not available:
            return None

        if self._config == LoadBalancingStrategy.ROUND_ROBIN:
            return self._round_robin_select(available)
        elif self._config == LoadBalancingStrategy.LEAST_LOADED:
            return self._least_loaded_select(available)
        elif self._config == LoadBalancingStrategy.WEIGHTED:
            return self._weighted_select(available)
        elif self._config == LoadBalancingStrategy.RANDOM:
            import random
            return random.choice(list(available.keys()))
        else:
            return list(available.keys())[0]

    def _round_robin_select(self, providers: dict[str, dict[str, Any]]) -> str:
        """Select using round robin."""
        keys = list(providers.keys())
        while self._round_robin_index >= len(keys):
            self._round_robin_index = 0
        selected = keys[self._round_robin_index]
        self._round_robin_index += 1
        return selected

    def _least_loaded_select(self, providers: dict[str, dict[str, Any]]) -> str:
        """Select least loaded provider."""
        return min(providers.keys(), key=lambda p: providers[p]["active_requests"])

    def _weighted_select(self, providers: dict[str, dict[str, Any]]) -> str:
        """Select using weighted random."""
        import random
        weights = [p["weight"] for p in providers.values()]
        total = sum(weights)
        if total == 0:
            return list(providers.keys())[0]
        r = random.random() * total
        cumulative = 0
        for pid, p in providers.items():
            cumulative += p["weight"]
            if r <= cumulative:
                return pid
        return list(providers.keys())[-1]

    def record_request_start(self, provider_id: str) -> None:
        """Record request start."""
        with self._lock:
            if provider_id in self._providers:
                self._providers[provider_id]["active_requests"] += 1

    def record_request_end(self, provider_id: str, success: bool = True) -> None:
        """Record request end."""
        with self._lock:
            if provider_id in self._providers:
                self._providers[provider_id]["active_requests"] -= 1
                if success:
                    self._providers[provider_id]["completed_requests"] += 1
                else:
                    self._providers[provider_id]["failed_requests"] += 1

    def get_stats(self) -> dict[str, dict[str, Any]]:
        """Get load balancer stats."""
        with self._lock:
            return dict(self._providers)


# =============================================================================
# Simple Cache
# =============================================================================


@dataclass
class CacheConfig:
    """Cache configuration."""
    max_size: int = 1000
    ttl_seconds: float = 3600.0


class SimpleCache:
    """Simple in-memory cache with TTL."""

    def __init__(self, config: CacheConfig | None = None):
        """Initialize cache."""
        self._config = config or CacheConfig()
        self._cache: dict[str, tuple[Any, float]] = {}
        self._access_order: deque = deque()
        self._lock = threading.RLock()

    def get(self, key: str) -> Any | None:
        """Get value from cache."""
        with self._lock:
            if key not in self._cache:
                return None
            
            value, expiry = self._cache[key]
            if time.time() > expiry:
                del self._cache[key]
                if key in self._access_order:
                    self._access_order.remove(key)
                return None
            
            return value

    def set(self, key: str, value: Any, ttl: float | None = None) -> None:
        """Set value in cache."""
        with self._lock:
            if len(self._cache) >= self._config.max_size:
                self._evict_oldest()
            
            ttl = ttl or self._config.ttl_seconds
            expiry = time.time() + ttl
            self._cache[key] = (value, expiry)
            
            if key in self._access_order:
                self._access_order.remove(key)
            self._access_order.append(key)

    def _evict_oldest(self) -> None:
        """Evict oldest entry."""
        if self._access_order:
            oldest = self._access_order.popleft()
            if oldest in self._cache:
                del self._cache[oldest]

    def delete(self, key: str) -> bool:
        """Delete entry from cache."""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                if key in self._access_order:
                    self._access_order.remove(key)
                return True
            return False

    def clear(self) -> None:
        """Clear all cache."""
        with self._lock:
            self._cache.clear()
            self._access_order.clear()

    def get_stats(self) -> dict[str, Any]:
        """Get cache stats."""
        with self._lock:
            return {
                "size": len(self._cache),
                "max_size": self._config.max_size,
                "ttl_seconds": self._config.ttl_seconds,
            }
