"""Cache for EREN OS Multi-Provider Layer.

Implements caching for provider responses.
"""

from __future__ import annotations

import hashlib
import threading
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass


class CacheStrategy(str, Enum):
    """Caching strategies."""

    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    FIFO = "fifo"  # First In First Out
    TTL = "ttl"  # Time To Live


@dataclass
class CacheEntry:
    """A cache entry."""

    key: str
    value: Any
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    last_accessed: datetime = field(default_factory=lambda: datetime.now(UTC))
    access_count: int = 0
    size_bytes: int = 0
    tags: list[str] = field(default_factory=list)

    def is_expired(self, ttl_seconds: float) -> bool:
        """Check if entry is expired.

        Args:
            ttl_seconds: TTL in seconds.

        Returns:
            True if expired.
        """
        if ttl_seconds <= 0:
            return False
        age = (datetime.now(UTC) - self.created_at).total_seconds()
        return age >= ttl_seconds

    def touch(self) -> None:
        """Update last accessed time."""
        self.last_accessed = datetime.now(UTC)
        self.access_count += 1


@dataclass
class CacheStats:
    """Cache statistics."""

    hits: int = 0
    misses: int = 0
    evictions: int = 0
    expirations: int = 0
    total_size_bytes: int = 0
    entries_count: int = 0

    @property
    def hit_rate(self) -> float:
        """Calculate hit rate percentage."""
        total = self.hits + self.misses
        if total == 0:
            return 0.0
        return (self.hits / total) * 100

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": self.hit_rate,
            "evictions": self.evictions,
            "expirations": self.expirations,
            "total_size_bytes": self.total_size_bytes,
            "entries_count": self.entries_count,
        }


class Cache:
    """Cache for provider responses.

    Features:
    - Multiple eviction strategies
    - TTL support
    - Size limits
    - Statistics
    - Tag-based invalidation
    """

    def __init__(
        self,
        max_entries: int = 1000,
        max_size_bytes: int = 100 * 1024 * 1024,  # 100 MB
        default_ttl_seconds: float = 3600,  # 1 hour
        strategy: CacheStrategy = CacheStrategy.LRU,
    ):
        """Initialize cache.

        Args:
            max_entries: Maximum number of entries.
            max_size_bytes: Maximum cache size in bytes.
            default_ttl_seconds: Default TTL in seconds.
            strategy: Eviction strategy.
        """
        self._max_entries = max_entries
        self._max_size_bytes = max_size_bytes
        self._default_ttl = default_ttl_seconds
        self._strategy = strategy

        self._entries: dict[str, CacheEntry] = {}
        self._lock = threading.RLock()
        self._stats = CacheStats()

    @property
    def stats(self) -> CacheStats:
        """Get cache statistics."""
        with self._lock:
            return self._stats

    def _generate_key(self, *args: Any) -> str:
        """Generate cache key from arguments.

        Args:
            *args: Arguments to hash.

        Returns:
            Cache key.
        """
        key_str = "|".join(str(arg) for arg in args)
        return hashlib.sha256(key_str.encode()).hexdigest()

    def get(self, key: str, ttl_seconds: float | None = None) -> Any | None:
        """Get value from cache.

        Args:
            key: Cache key.
            ttl_seconds: Optional TTL override.

        Returns:
            Cached value or None.
        """
        ttl = ttl_seconds if ttl_seconds is not None else self._default_ttl

        with self._lock:
            if key not in self._entries:
                self._stats.misses += 1
                return None

            entry = self._entries[key]

            # Check expiration
            if entry.is_expired(ttl):
                self._remove_entry(key)
                self._stats.misses += 1
                self._stats.expirations += 1
                return None

            # Update access
            entry.touch()
            self._stats.hits += 1

            return entry.value

    def set(
        self,
        key: str,
        value: Any,
        ttl_seconds: float | None = None,
        tags: list[str] | None = None,
    ) -> None:
        """Set value in cache.

        Args:
            key: Cache key.
            value: Value to cache.
            ttl_seconds: Optional TTL override.
            tags: Optional tags for invalidation.
        """
        ttl = ttl_seconds if ttl_seconds is not None else self._default_ttl
        tags = tags or []

        with self._lock:
            # Check size limits and evict if needed
            self._ensure_capacity()

            # Calculate size
            import sys
            size = len(str(value))

            entry = CacheEntry(
                key=key,
                value=value,
                size_bytes=size,
                tags=tags,
            )

            self._entries[key] = entry
            self._stats.entries_count = len(self._entries)
            self._stats.total_size_bytes = sum(e.size_bytes for e in self._entries.values())

    def delete(self, key: str) -> bool:
        """Delete entry from cache.

        Args:
            key: Cache key.

        Returns:
            True if deleted.
        """
        with self._lock:
            return self._remove_entry(key)

    def _remove_entry(self, key: str) -> bool:
        """Remove entry without locking.

        Args:
            key: Cache key.

        Returns:
            True if removed.
        """
        if key in self._entries:
            del self._entries[key]
            self._stats.entries_count = len(self._entries)
            self._stats.total_size_bytes = sum(e.size_bytes for e in self._entries.values())
            return True
        return False

    def _ensure_capacity(self) -> None:
        """Ensure cache has capacity, evicting if needed."""
        # Check entry count
        while len(self._entries) >= self._max_entries:
            self._evict_one()

        # Check size
        while self._stats.total_size_bytes >= self._max_size_bytes and self._entries:
            self._evict_one()

    def _evict_one(self) -> None:
        """Evict one entry based on strategy."""
        if not self._entries:
            return

        if self._strategy == CacheStrategy.LRU:
            # Evict least recently used
            key = min(self._entries, key=lambda k: self._entries[k].last_accessed)
        elif self._strategy == CacheStrategy.LFU:
            # Evict least frequently used
            key = min(self._entries, key=lambda k: self._entries[k].access_count)
        elif self._strategy == CacheStrategy.FIFO:
            # Evict oldest
            key = min(self._entries, key=lambda k: self._entries[k].created_at)
        elif self._strategy == CacheStrategy.TTL:
            # Evict by expiration (already expired first)
            for k, entry in self._entries.items():
                if entry.is_expired(self._default_ttl):
                    key = k
                    break
            else:
                key = min(self._entries, key=lambda k: self._entries[k].created_at)
        else:
            # Default: evict random
            import random
            key = random.choice(list(self._entries.keys()))

        self._remove_entry(key)
        self._stats.evictions += 1

    def invalidate_by_tags(self, tags: list[str]) -> int:
        """Invalidate entries with any of the given tags.

        Args:
            tags: Tags to match.

        Returns:
            Number of entries invalidated.
        """
        count = 0
        with self._lock:
            to_remove = []
            for key, entry in self._entries.items():
                if any(tag in entry.tags for tag in tags):
                    to_remove.append(key)

            for key in to_remove:
                self._remove_entry(key)
                count += 1

            return count

    def clear(self) -> None:
        """Clear all cache entries."""
        with self._lock:
            self._entries.clear()
            self._stats = CacheStats()

    def cleanup_expired(self) -> int:
        """Remove all expired entries.

        Returns:
            Number of entries removed.
        """
        count = 0
        with self._lock:
            to_remove = []
            for key, entry in self._entries.items():
                if entry.is_expired(self._default_ttl):
                    to_remove.append(key)

            for key in to_remove:
                self._remove_entry(key)
                count += 1

            if count > 0:
                self._stats.expirations += count

            return count

    def get_size(self) -> int:
        """Get current cache size in bytes."""
        with self._lock:
            return self._stats.total_size_bytes

    def get_count(self) -> int:
        """Get current number of entries."""
        with self._lock:
            return len(self._entries)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        with self._lock:
            return {
                "max_entries": self._max_entries,
                "max_size_bytes": self._max_size_bytes,
                "default_ttl_seconds": self._default_ttl,
                "strategy": self._strategy.value,
                "stats": self._stats.to_dict(),
                "entries_count": len(self._entries),
            }


class ProviderCache:
    """Cache specialized for provider responses."""

    def __init__(
        self,
        max_entries: int = 1000,
        default_ttl_seconds: float = 300,  # 5 minutes
    ):
        """Initialize provider cache.

        Args:
            max_entries: Maximum entries.
            default_ttl_seconds: Default TTL.
        """
        self._cache = Cache(
            max_entries=max_entries,
            default_ttl_seconds=default_ttl_seconds,
            strategy=CacheStrategy.LRU,
        )

    def get_response(
        self,
        provider_id: str,
        prompt_hash: str,
    ) -> dict | None:
        """Get cached response.

        Args:
            provider_id: Provider identifier.
            prompt_hash: Hash of prompt.

        Returns:
            Cached response or None.
        """
        key = self._cache._generate_key(provider_id, prompt_hash)
        return self._cache.get(key)

    def set_response(
        self,
        provider_id: str,
        prompt_hash: str,
        response: dict,
        ttl_seconds: float | None = None,
    ) -> None:
        """Cache response.

        Args:
            provider_id: Provider identifier.
            prompt_hash: Hash of prompt.
            response: Response to cache.
            ttl_seconds: Optional TTL.
        """
        key = self._cache._generate_key(provider_id, prompt_hash)
        self._cache.set(key, response, ttl_seconds, tags=[provider_id])

    def invalidate_provider(self, provider_id: str) -> int:
        """Invalidate all entries for a provider.

        Args:
            provider_id: Provider identifier.

        Returns:
            Number of entries invalidated.
        """
        return self._cache.invalidate_by_tags([provider_id])

    def clear(self) -> None:
        """Clear all cached responses."""
        self._cache.clear()

    @property
    def stats(self) -> CacheStats:
        """Get cache statistics."""
        return self._cache.stats

    def cleanup(self) -> int:
        """Remove expired entries."""
        return self._cache.cleanup_expired()
