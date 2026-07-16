"""Redis caching layer."""
from __future__ import annotations

import json
import logging
from typing import Any

from app.config.settings import get_settings

logger = logging.getLogger(__name__)

_redis_client: Any = None


async def get_redis() -> Any:
    """Get or create Redis client."""
    global _redis_client
    if _redis_client is None:
        try:
            import redis.asyncio as redis

            settings = get_settings()
            _redis_client = redis.from_url(
                settings.redis_url,
                decode_responses=True,
            )
        except ImportError:
            logger.warning("Redis not available, caching disabled")
            return None
    return _redis_client


async def close_redis() -> None:
    """Close Redis connection."""
    global _redis_client
    if _redis_client is not None:
        await _redis_client.close()
        _redis_client = None


class CacheService:
    """Redis-backed caching service."""

    def __init__(self, client: Any) -> None:
        self._client = client
        self._settings = get_settings()

    async def get(self, key: str) -> Any | None:
        """Get value from cache."""
        if self._client is None:
            return None
        try:
            value = await self._client.get(key)
            if value is not None:
                try:
                    return json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    return value
        except Exception as e:
            logger.warning("Cache get failed for %s: %s", key, e)
        return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: int | None = None,
    ) -> None:
        """Set value in cache with optional TTL."""
        if self._client is None:
            return
        try:
            ttl = ttl or self._settings.cache_ttl_seconds
            serialized = json.dumps(value) if not isinstance(value, str) else value
            await self._client.set(key, serialized, ex=ttl)
        except Exception as e:
            logger.warning("Cache set failed for %s: %s", key, e)

    async def delete(self, key: str) -> None:
        """Delete key from cache."""
        if self._client is None:
            return
        try:
            await self._client.delete(key)
        except Exception as e:
            logger.warning("Cache delete failed for %s: %s", key, e)

    async def get_or_set(
        self,
        key: str,
        factory: Any,
        ttl: int | None = None,
    ) -> Any:
        """Get from cache or compute and cache value."""
        value = await self.get(key)
        if value is None:
            value = await factory() if callable(factory) else factory
            await self.set(key, value, ttl)
        return value


def cache_key(*parts: str) -> str:
    """Build a cache key from parts."""
    return ":".join(f"eren:{p}" for p in parts)
