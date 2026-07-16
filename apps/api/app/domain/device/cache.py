"""Device-specific caching layer using Redis."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from app.infrastructure.messaging import CacheService, cache_key

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

DEVICE_CACHE_TTL = 300  # 5 minutes


def _device_cache_key(tenant_id: str, device_id: str) -> str:
    return cache_key("device", tenant_id, device_id)


def _serial_cache_key(tenant_id: str, serial: str) -> str:
    return cache_key("device", "serial", tenant_id, serial)


def _list_cache_key(tenant_id: str) -> str:
    return cache_key("device", "list", tenant_id)


class DeviceCacheService:
    """Cache layer for device queries.

    Provides get/set/invalidate for device entities and query results.
    Automatically invalidated on writes.
    """

    def __init__(self, cache: CacheService) -> None:
        self._cache = cache

    async def get_by_id(self, tenant_id: str, device_id: str) -> dict | None:
        """Get cached device by ID."""
        key = _device_cache_key(tenant_id, device_id)
        return await self._cache.get(key)

    async def set_by_id(self, tenant_id: str, device_id: str, data: dict) -> None:
        """Cache device by ID."""
        key = _device_cache_key(tenant_id, device_id)
        await self._cache.set(key, data, ttl=DEVICE_CACHE_TTL)

    async def get_by_serial(self, tenant_id: str, serial: str) -> dict | None:
        """Get cached device by serial number."""
        key = _serial_cache_key(tenant_id, serial)
        return await self._cache.get(key)

    async def set_by_serial(self, tenant_id: str, serial: str, data: dict) -> None:
        """Cache device by serial number."""
        key = _serial_cache_key(tenant_id, serial)
        await self._cache.set(key, data, ttl=DEVICE_CACHE_TTL)

    async def invalidate(
        self,
        tenant_id: str,
        device_id: str,
        serial_number: str | None = None,
    ) -> None:
        """Invalidate all caches for a device after a write operation."""
        key_by_id = _device_cache_key(tenant_id, device_id)
        await self._cache.delete(key_by_id)

        key_list = _list_cache_key(tenant_id)
        await self._cache.delete(key_list)

        if serial_number:
            key_by_serial = _serial_cache_key(tenant_id, serial_number)
            await self._cache.delete(key_by_serial)

        logger.debug(
            "Device cache invalidated",
            extra={"device_id": device_id, "tenant_id": tenant_id},
        )
