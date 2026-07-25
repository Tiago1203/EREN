"""
PHASE 7 - EPIC 2: Cache Isolation

Aislamiento de cache Redis por tenant:
- Key prefixing automático
- TTL management
- Cache invalidation per tenant
- Rate limiting per tenant
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional
import hashlib


@dataclass
class CacheKey:
    """Cache key con prefijo de tenant."""
    tenant_id: str
    namespace: str         # e.g., "equipment", "users", "kpis"
    key: str
    version: int = 1

    def to_string(self) -> str:
        """Convierte a string de key."""
        return f"t:{self.tenant_id}:v{self.version}:{self.namespace}:{self.key}"

    def to_pattern(self) -> str:
        """Convierte a patrón para SCAN/DEL."""
        return f"t:{self.tenant_id}:*:{self.namespace}:*"


class CacheIsolation:
    """
    Gestor de aislamiento de cache para multi-tenant.
    Asegura que cada tenant tenga su propio namespace de cache.
    """

    def __init__(self, context_manager: Any):
        self._context = context_manager
        self._default_ttl: int = 3600  # 1 hour
        self._namespaces_ttl: dict[str, int] = {
            "session": 86400,       # 24h
            "user": 3600,           # 1h
            "equipment": 300,       # 5min
            "kpis": 60,             # 1min
            "establishment": 1800,  # 30min
        }

    def make_key(
        self,
        namespace: str,
        key: str,
        tenant_id: Optional[str] = None,
        version: int = 1,
    ) -> CacheKey:
        """Genera cache key con prefijo de tenant."""
        if tenant_id is None:
            ctx = self._context.get_context()
            tenant_id = ctx.tenant_id if ctx else "global"

        return CacheKey(
            tenant_id=tenant_id,
            namespace=namespace,
            key=key,
            version=version,
        )

    def get_key_string(
        self,
        namespace: str,
        key: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Genera string de key directo."""
        cache_key = self.make_key(namespace, key, tenant_id)
        return cache_key.to_string()

    def get_ttl(self, namespace: str) -> int:
        """Obtiene TTL para namespace."""
        return self._namespaces_ttl.get(namespace, self._default_ttl)

    def set_ttl(self, namespace: str, ttl: int) -> None:
        """Establece TTL para namespace."""
        self._namespaces_ttl[namespace] = ttl

    def make_user_key(self, user_id: str) -> str:
        """Genera key para cache de usuario."""
        return self.get_key_string("user", f"u:{user_id}")

    def make_equipment_key(self, equipment_id: str) -> str:
        """Genera key para cache de equipo."""
        return self.get_key_string("equipment", f"eq:{equipment_id}")

    def make_kpi_key(self, kpi_id: str) -> str:
        """Genera key para cache de KPI."""
        return self.get_key_string("kpis", f"kpi:{kpi_id}")

    def make_session_key(self, session_id: str) -> str:
        """Genera key para cache de sesión."""
        return self.get_key_string("session", f"sess:{session_id}")

    def get_tenant_pattern(self, tenant_id: Optional[str] = None) -> str:
        """Genera patrón para todas las keys de un tenant."""
        if tenant_id is None:
            ctx = self._context.get_context()
            tenant_id = ctx.tenant_id if ctx else "global"
        return f"t:{tenant_id}:*"

    def invalidate_tenant(self, tenant_id: Optional[str] = None) -> None:
        """
        Invalida todo el cache de un tenant.
        WARNING: Esto elimina TODO el cache del tenant.
        Use with caution in production.
        """
        pattern = self.get_tenant_pattern(tenant_id)
        # In production: redis_client.delete(*redis_client.scan_iter(pattern))
        return pattern  # Return pattern for caller to execute

    def invalidate_namespace(
        self,
        namespace: str,
        tenant_id: Optional[str] = None,
    ) -> str:
        """Invalida un namespace específico del tenant."""
        key = self.make_key(namespace, "*", tenant_id, version=0)
        return key.to_pattern()


# Rate limiting per tenant

class TenantRateLimiter:
    """
    Rate limiting por tenant usando Redis sliding window.
    Implementa límites por plan de suscripción.
    """

    def __init__(self):
        self._limits: dict[str, int] = {
            "starter": 1000,         # requests per minute
            "professional": 5000,
            "enterprise": 50000,
            "trial": 100,
               "default": 1000,
        }

    def get_limit(self, tier: str) -> int:
        """Obtiene límite por tier."""
        return self._limits.get(tier, self._limits["default"])

    def check_rate_limit(
        self,
        tenant_id: str,
        tier: str,
        current_usage: int,
    ) -> tuple[bool, int, int]:
        """
        Check rate limit.
        Returns (allowed, remaining, reset_in_seconds).
        """
        limit = self.get_limit(tier)
        remaining = max(0, limit - current_usage)
        allowed = current_usage < limit
        return allowed, remaining, 60  # 60s window

    def generate_rate_limit_headers(
        self,
        tenant_id: str,
        tier: str,
        current_usage: int,
    ) -> dict:
        """Genera headers de rate limiting."""
        allowed, remaining, reset = self.check_rate_limit(tenant_id, tier, current_usage)
        limit = self.get_limit(tier)

        return {
            "X-RateLimit-Limit": str(limit),
            "X-RateLimit-Remaining": str(remaining),
            "X-RateLimit-Reset": str(reset),
            "X-RateLimit-Policy": tier,
        }
