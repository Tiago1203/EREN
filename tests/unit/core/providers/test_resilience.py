"""Tests for resilience patterns (PR-056)."""

import pytest
import time
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


class TestCircuitBreaker:
    """Tests for CircuitBreaker."""

    def test_initial_state(self):
        """Test initial state is closed."""
        cb = CircuitBreaker("test")
        assert cb.state == CircuitState.CLOSED

    def test_allow_request_in_closed_state(self):
        """Test requests allowed in closed state."""
        cb = CircuitBreaker("test")
        assert cb.allow_request() is True

    def test_opens_after_failures(self):
        """Test circuit opens after threshold failures."""
        cb = CircuitBreaker("test", CircuitBreakerConfig(failure_threshold=3))
        
        cb.record_failure()
        assert cb.state == CircuitState.CLOSED
        cb.record_failure()
        assert cb.state == CircuitState.CLOSED
        cb.record_failure()
        assert cb.state == CircuitState.OPEN

    def test_half_open_after_timeout(self):
        """Test circuit goes to half-open after timeout."""
        cb = CircuitBreaker("test", CircuitBreakerConfig(
            failure_threshold=1,
            timeout_seconds=0.1,
        ))
        
        cb.record_failure()
        assert cb.state == CircuitState.OPEN
        
        time.sleep(0.15)
        assert cb.state == CircuitState.HALF_OPEN

    def test_closes_after_successes_in_half_open(self):
        """Test circuit closes after successes in half-open."""
        cb = CircuitBreaker("test", CircuitBreakerConfig(
            failure_threshold=1,
            timeout_seconds=0.01,
            success_threshold=2,
        ))
        
        cb.record_failure()
        time.sleep(0.02)
        assert cb.state == CircuitState.HALF_OPEN
        
        cb.record_success()
        assert cb.state == CircuitState.HALF_OPEN
        cb.record_success()
        assert cb.state == CircuitState.CLOSED

    def test_state_change_callback(self):
        """Test state change callback."""
        changes = []
        def on_change(name, old, new):
            changes.append((name, old, new))
        
        cb = CircuitBreaker("test", on_state_change=on_change)
        # Manually trigger state transition
        cb._transition_to(CircuitState.OPEN)
        
        assert len(changes) == 1
        assert changes[0] == ("test", CircuitState.CLOSED, CircuitState.OPEN)


class TestTokenBucketRateLimiter:
    """Tests for TokenBucketRateLimiter."""

    def test_initial_tokens(self):
        """Test initial token count."""
        limiter = TokenBucketRateLimiter(RateLimitConfig(burst_size=10))
        assert limiter.get_available_tokens() == 10

    def test_acquire_success(self):
        """Test successful token acquisition."""
        limiter = TokenBucketRateLimiter(RateLimitConfig(burst_size=10))
        assert limiter.acquire(5) is True

    def test_acquire_exhausts_tokens(self):
        """Test acquisition exhausts tokens."""
        limiter = TokenBucketRateLimiter(RateLimitConfig(burst_size=5))
        assert limiter.acquire(5) is True
        assert limiter.get_available_tokens() < 5

    def test_non_blocking_returns_false(self):
        """Test non-blocking acquire returns False."""
        limiter = TokenBucketRateLimiter(RateLimitConfig(burst_size=1))
        limiter.acquire(1)
        assert limiter.acquire(1, blocking=False) is False

    def test_refill_after_time(self):
        """Test tokens refill after time."""
        limiter = TokenBucketRateLimiter(RateLimitConfig(
            burst_size=10,
            requests_per_second=100,
        ))
        limiter.acquire(9)
        time.sleep(0.1)
        assert limiter.get_available_tokens() >= 9


class TestLoadBalancer:
    """Tests for LoadBalancer."""

    def test_round_robin(self):
        """Test round robin selection."""
        lb = LoadBalancer(LoadBalancingStrategy.ROUND_ROBIN)
        lb.register_provider("p1")
        lb.register_provider("p2")
        lb.register_provider("p3")
        
        selected = [lb.select_provider(["p1", "p2", "p3"]) for _ in range(6)]
        assert selected == ["p1", "p2", "p3", "p1", "p2", "p3"]

    def test_least_loaded(self):
        """Test least loaded selection."""
        lb = LoadBalancer(LoadBalancingStrategy.LEAST_LOADED)
        lb.register_provider("p1")
        lb.register_provider("p2")
        lb.register_provider("p3")
        
        # Simulate load on p1
        lb.record_request_start("p1")
        lb.record_request_start("p1")
        
        selected = lb.select_provider(["p1", "p2", "p3"])
        assert selected == "p2"

    def test_weighted_selection(self):
        """Test weighted random selection."""
        lb = LoadBalancer(LoadBalancingStrategy.WEIGHTED)
        lb.register_provider("heavy", weight=10.0)
        lb.register_provider("light", weight=1.0)
        
        # Should select "heavy" more often
        counts = {"heavy": 0, "light": 0}
        for _ in range(100):
            selected = lb.select_provider(["heavy", "light"])
            counts[selected] += 1
        
        assert counts["heavy"] > counts["light"]

    def test_records_stats(self):
        """Test stats recording."""
        lb = LoadBalancer()
        lb.register_provider("p1")
        lb.record_request_start("p1")
        lb.record_request_end("p1", success=True)
        
        stats = lb.get_stats()
        assert stats["p1"]["completed_requests"] == 1


class TestSimpleCache:
    """Tests for SimpleCache."""

    def test_set_and_get(self):
        """Test set and get."""
        cache = SimpleCache()
        cache.set("key", "value")
        assert cache.get("key") == "value"

    def test_get_missing_returns_none(self):
        """Test missing key returns None."""
        cache = SimpleCache()
        assert cache.get("missing") is None

    def test_ttl_expiration(self):
        """Test TTL expiration."""
        cache = SimpleCache(CacheConfig(ttl_seconds=0.1))
        cache.set("key", "value")
        assert cache.get("key") == "value"
        time.sleep(0.15)
        assert cache.get("key") is None

    def test_eviction_on_max_size(self):
        """Test eviction when max size reached."""
        cache = SimpleCache(CacheConfig(max_size=3))
        cache.set("k1", "v1")
        cache.set("k2", "v2")
        cache.set("k3", "v3")
        cache.set("k4", "v4")  # Should evict k1
        
        assert cache.get("k1") is None
        assert cache.get("k4") == "v4"

    def test_delete(self):
        """Test delete."""
        cache = SimpleCache()
        cache.set("key", "value")
        assert cache.delete("key") is True
        assert cache.get("key") is None

    def test_clear(self):
        """Test clear."""
        cache = SimpleCache()
        cache.set("k1", "v1")
        cache.set("k2", "v2")
        cache.clear()
        assert cache.get("k1") is None
        assert cache.get("k2") is None


class TestRetryPolicy:
    """Tests for RetryPolicy."""

    def test_exponential_delay(self):
        """Test exponential delay calculation."""
        policy = RetryPolicy(
            strategy=RetryStrategy.EXPONENTIAL,
            initial_delay_seconds=1.0,
        )
        
        assert policy.get_delay(1) == 1.0
        assert policy.get_delay(2) == 2.0
        assert policy.get_delay(3) == 4.0

    def test_fixed_delay(self):
        """Test fixed delay."""
        policy = RetryPolicy(
            strategy=RetryStrategy.FIXED,
            initial_delay_seconds=2.0,
        )
        
        assert policy.get_delay(1) == 2.0
        assert policy.get_delay(2) == 2.0
        assert policy.get_delay(3) == 2.0

    def test_should_retry_timeout(self):
        """Test retry decision for timeout errors."""
        policy = RetryPolicy(max_attempts=3)
        
        # Create a timeout error
        class TimeoutError(Exception):
            pass
        
        assert policy.should_retry(0, TimeoutError("timeout")) is True
        assert policy.should_retry(1, TimeoutError("timeout")) is True
        assert policy.should_retry(2, TimeoutError("timeout")) is True
        assert policy.should_retry(3, TimeoutError("timeout")) is False

    def test_should_not_retry_non_retryable(self):
        """Test no retry for non-retryable errors."""
        policy = RetryPolicy(max_attempts=3)
        
        assert policy.should_retry(0, ValueError("invalid")) is False
