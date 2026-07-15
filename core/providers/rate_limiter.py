"""Rate Limiter for EREN OS Multi-Provider Layer.

Implements token bucket rate limiting for providers.
"""

from __future__ import annotations

import threading
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


class RateLimitStrategy(str, Enum):
    """Rate limiting strategies."""

    TOKEN_BUCKET = "token_bucket"
    FIXED_WINDOW = "fixed_window"
    SLIDING_WINDOW = "sliding_window"


@dataclass
class RateLimitConfig:
    """Configuration for rate limiter."""

    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    requests_per_day: int = 10000
    burst_size: int = 10  # Max burst requests
    strategy: RateLimitStrategy = RateLimitStrategy.TOKEN_BUCKET


@dataclass
class RateLimitResult:
    """Result of rate limit check."""

    allowed: bool
    provider_id: str
    remaining_requests: int
    reset_at: datetime
    retry_after_seconds: float = 0.0
    message: str = ""

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "allowed": self.allowed,
            "provider_id": self.provider_id,
            "remaining_requests": self.remaining_requests,
            "reset_at": self.reset_at.isoformat(),
            "retry_after_seconds": self.retry_after_seconds,
            "message": self.message,
        }


@dataclass
class RateLimitStats:
    """Statistics for rate limiter."""

    provider_id: str
    total_requests: int = 0
    allowed_requests: int = 0
    rejected_requests: int = 0
    last_request: datetime | None = None
    last_rejected: datetime | None = None
    tokens_available: float = 0.0

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "provider_id": self.provider_id,
            "total_requests": self.total_requests,
            "allowed_requests": self.allowed_requests,
            "rejected_requests": self.rejected_requests,
            "last_request": self.last_request.isoformat() if self.last_request else None,
            "last_rejected": self.last_rejected.isoformat() if self.last_rejected else None,
            "tokens_available": self.tokens_available,
        }


class TokenBucket:
    """Token bucket implementation for rate limiting."""

    def __init__(
        self,
        capacity: float,
        refill_rate: float,  # tokens per second
    ):
        """Initialize token bucket.

        Args:
            capacity: Maximum number of tokens.
            refill_rate: Number of tokens added per second.
        """
        self._capacity = capacity
        self._refill_rate = refill_rate
        self._tokens = float(capacity)
        self._last_refill = time.time()
        self._lock = threading.Lock()

    def consume(self, tokens: float = 1.0) -> bool:
        """Try to consume tokens.

        Args:
            tokens: Number of tokens to consume.

        Returns:
            True if tokens were consumed.
        """
        with self._lock:
            self._refill()

            if self._tokens >= tokens:
                self._tokens -= tokens
                return True
            return False

    def _refill(self) -> None:
        """Refill tokens based on elapsed time."""
        now = time.time()
        elapsed = now - self._last_refill
        new_tokens = elapsed * self._refill_rate

        self._tokens = min(self._capacity, self._tokens + new_tokens)
        self._last_refill = now

    @property
    def available(self) -> float:
        """Get available tokens."""
        with self._lock:
            self._refill()
            return self._tokens


class RateLimiter:
    """Rate limiter for provider API calls.

    Supports:
    - Token bucket algorithm
    - Multiple time windows (minute, hour, day)
    - Burst handling
    - Callbacks for rejected requests
    """

    def __init__(self, config: RateLimitConfig | None = None):
        """Initialize rate limiter.

        Args:
            config: Rate limit configuration.
        """
        self._config = config or RateLimitConfig()
        self._buckets: dict[str, TokenBucket] = {}
        self._counters: dict[str, dict[str, int]] = {}  # window counters
        self._window_starts: dict[str, datetime] = {}
        self._stats: dict[str, RateLimitStats] = {}
        self._lock = threading.RLock()

        # Callbacks
        self._on_rejected: list[Callable[[str, RateLimitResult], None]] = []

    def _get_bucket(self, provider_id: str) -> TokenBucket:
        """Get or create token bucket for provider."""
        if provider_id not in self._buckets:
            # Calculate refill rate: requests_per_minute / 60
            refill_rate = self._config.requests_per_minute / 60.0
            self._buckets[provider_id] = TokenBucket(
                capacity=float(self._config.burst_size),
                refill_rate=refill_rate,
            )
            self._stats[provider_id] = RateLimitStats(provider_id=provider_id)
            self._counters[provider_id] = {
                "minute": 0,
                "hour": 0,
                "day": 0,
            }
            self._window_starts[provider_id] = datetime.now(UTC)
        return self._buckets[provider_id]

    def _check_window_limit(
        self,
        provider_id: str,
        window: str,
        limit: int,
    ) -> tuple[bool, int, datetime]:
        """Check if request is within window limit.

        Args:
            provider_id: Provider identifier.
            window: Window name (minute, hour, day).
            limit: Maximum requests in window.

        Returns:
            Tuple of (allowed, remaining, reset_time).
        """
        with self._lock:
            now = datetime.now(UTC)

            # Initialize counters if needed
            if provider_id not in self._counters:
                self._counters[provider_id] = {"minute": 0, "hour": 0, "day": 0}
                self._window_starts[provider_id] = now

            window_start = self._window_starts.get(provider_id, now)
            elapsed = (now - window_start).total_seconds()

            # Check if window should reset
            window_seconds = {"minute": 60, "hour": 3600, "day": 86400}[window]

            if elapsed >= window_seconds:
                # Reset window
                self._counters[provider_id][window] = 0
                self._window_starts[provider_id] = now
                return True, limit - 1, now + timedelta(seconds=window_seconds)

            count = self._counters.get(provider_id, {}).get(window, 0)

            if count < limit:
                self._counters[provider_id][window] = count + 1
                remaining = limit - count - 1
                return True, remaining, window_start + timedelta(seconds=window_seconds)

            return False, 0, window_start + timedelta(seconds=window_seconds)

    def check(self, provider_id: str) -> RateLimitResult:
        """Check if request is allowed.

        Args:
            provider_id: Provider identifier.

        Returns:
            Rate limit result.
        """
        now = datetime.now(UTC)

        # Check minute limit
        allowed, remaining, reset_at = self._check_window_limit(
            provider_id, "minute", self._config.requests_per_minute
        )

        if not allowed:
            return self._create_rejected_result(
                provider_id, remaining, reset_at, f"Minute limit exceeded ({self._config.requests_per_minute})"
            )

        # Check hour limit
        allowed, remaining_hour, reset_at_hour = self._check_window_limit(
            provider_id, "hour", self._config.requests_per_hour
        )

        if not allowed:
            return self._create_rejected_result(
                provider_id, remaining, reset_at, f"Hour limit exceeded ({self._config.requests_per_hour})"
            )

        # Check day limit
        allowed, remaining_day, reset_at_day = self._check_window_limit(
            provider_id, "day", self._config.requests_per_day
        )

        if not allowed:
            return self._create_rejected_result(
                provider_id, remaining, reset_at, f"Day limit exceeded ({self._config.requests_per_day})"
            )

        # Check token bucket (for burst handling)
        bucket = self._get_bucket(provider_id)
        if not bucket.consume():
            retry_after = 1.0 / self._config.requests_per_minute * 60.0
            return RateLimitResult(
                allowed=False,
                provider_id=provider_id,
                remaining_requests=0,
                reset_at=now + timedelta(seconds=retry_after),
                retry_after_seconds=retry_after,
                message="Burst limit exceeded",
            )

        # Update stats
        self._update_stats(provider_id, allowed=True)

        return RateLimitResult(
            allowed=True,
            provider_id=provider_id,
            remaining_requests=min(remaining, remaining_hour, remaining_day),
            reset_at=reset_at,
        )

    def _create_rejected_result(
        self,
        provider_id: str,
        remaining: int,
        reset_at: datetime,
        message: str,
    ) -> RateLimitResult:
        """Create a rejected result."""
        retry_after = max(0, (reset_at - datetime.now(UTC)).total_seconds())
        result = RateLimitResult(
            allowed=False,
            provider_id=provider_id,
            remaining_requests=remaining,
            reset_at=reset_at,
            retry_after_seconds=retry_after,
            message=message,
        )

        self._update_stats(provider_id, allowed=False)
        self._notify_rejected(result)

        return result

    def _update_stats(self, provider_id: str, allowed: bool) -> None:
        """Update rate limit statistics."""
        with self._lock:
            if provider_id not in self._stats:
                self._stats[provider_id] = RateLimitStats(provider_id=provider_id)

            stats = self._stats[provider_id]
            stats.total_requests += 1

            if allowed:
                stats.allowed_requests += 1
                stats.last_request = datetime.now(UTC)
                if provider_id in self._buckets:
                    stats.tokens_available = self._buckets[provider_id].available
            else:
                stats.rejected_requests += 1
                stats.last_rejected = datetime.now(UTC)

    def _notify_rejected(self, result: RateLimitResult) -> None:
        """Notify callbacks about rejected request."""
        for callback in self._on_rejected:
            try:
                callback(result.provider_id, result)
            except Exception:
                pass

    def on_rejected(self, callback: Callable[[str, RateLimitResult], None]) -> None:
        """Register a callback for rejected requests.

        Args:
            callback: Callback function(provider_id, result).
        """
        with self._lock:
            if callback not in self._on_rejected:
                self._on_rejected.append(callback)

    def get_stats(self, provider_id: str) -> RateLimitStats | None:
        """Get rate limit stats for a provider.

        Args:
            provider_id: Provider identifier.

        Returns:
            Rate limit stats or None.
        """
        with self._lock:
            # Ensure stats exist for this provider
            if provider_id not in self._stats:
                self._stats[provider_id] = RateLimitStats(provider_id=provider_id)
            return self._stats.get(provider_id)

    def get_all_stats(self) -> dict[str, RateLimitStats]:
        """Get rate limit stats for all providers.

        Returns:
            Dictionary of provider_id -> stats.
        """
        with self._lock:
            return dict(self._stats)

    def reset(self, provider_id: str | None = None) -> None:
        """Reset rate limits.

        Args:
            provider_id: Provider to reset, or None for all.
        """
        with self._lock:
            if provider_id:
                if provider_id in self._buckets:
                    # Create new bucket
                    refill_rate = self._config.requests_per_minute / 60.0
                    self._buckets[provider_id] = TokenBucket(
                        capacity=float(self._config.burst_size),
                        refill_rate=refill_rate,
                    )
                if provider_id in self._counters:
                    self._counters[provider_id] = {"minute": 0, "hour": 0, "day": 0}
                if provider_id in self._stats:
                    self._stats[provider_id] = RateLimitStats(provider_id=provider_id)
            else:
                # Reset all
                self._buckets.clear()
                self._counters.clear()
                self._stats.clear()

    def set_config(self, config: RateLimitConfig) -> None:
        """Update rate limit configuration.

        Args:
            config: New configuration.
        """
        with self._lock:
            self._config = config
            # Reset all buckets with new config
            self.reset()

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        with self._lock:
            return {
                "config": {
                    "requests_per_minute": self._config.requests_per_minute,
                    "requests_per_hour": self._config.requests_per_hour,
                    "requests_per_day": self._config.requests_per_day,
                    "burst_size": self._config.burst_size,
                    "strategy": self._config.strategy.value,
                },
                "tracked_providers": list(self._buckets.keys()),
                "stats": {pid: stats.to_dict() for pid, stats in self._stats.items()},
            }
