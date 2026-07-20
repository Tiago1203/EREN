"""
Caching Module for EREN Production

Multi-level caching strategy implementation.
"""
from typing import Any, Optional, Dict, Callable
import hashlib
import json
from datetime import datetime, timedelta
import redis.asyncio as redis


class CacheManager:
    """Multi-level cache manager."""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self._client: Optional[redis.Redis] = None
        self.local_cache: Dict[str, tuple[Any, datetime]] = {}
    
    async def connect(self):
        """Connect to Redis."""
        self._client = await redis.from_url(self.redis_url)
    
    async def disconnect(self):
        """Disconnect from Redis."""
        if self._client:
            await self._client.close()
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        # Check local cache first
        if key in self.local_cache:
            value, expiry = self.local_cache[key]
            if datetime.utcnow() < expiry:
                return value
            del self.local_cache[key]
        
        # Check Redis
        if self._client:
            value = await self._client.get(key)
            if value:
                return json.loads(value)
        
        return None
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl: int = 300,
        local_ttl: int = 60
    ):
        """Set value in cache."""
        # Store in local cache
        self.local_cache[key] = (
            value, 
            datetime.utcnow() + timedelta(seconds=local_ttl)
        )
        
        # Store in Redis
        if self._client:
            await self._client.setex(
                key,
                ttl,
                json.dumps(value)
            )
    
    async def invalidate(self, key: str):
        """Invalidate cache key."""
        if key in self.local_cache:
            del self.local_cache[key]
        
        if self._client:
            await self._client.delete(key)
    
    async def invalidate_pattern(self, pattern: str):
        """Invalidate all keys matching pattern."""
        if self._client:
            keys = await self._client.keys(pattern)
            if keys:
                await self._client.delete(*keys)
        
        # Clear local cache
        self.local_cache = {
            k: v for k, v in self.local_cache.items()
            if not k.startswith(pattern.replace("*", ""))
        }


# Cache strategies
CACHE_STRATEGIES = {
    "device_list": {"ttl": 300, "local_ttl": 60, "invalidate": "on_update"},
    "device_detail": {"ttl": 600, "local_ttl": 120, "invalidate": "on_change"},
    "dashboard_metrics": {"ttl": 60, "local_ttl": 15, "invalidate": "on_event"},
    "user_session": {"ttl": 3600, "local_ttl": 300, "invalidate": "on_logout"},
}
