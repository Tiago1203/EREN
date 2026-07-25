"""
PHASE 7 - EPIC 2: Tenant Resolver

Resuelve el tenant desde requests HTTP:
- Header X-Tenant-ID
- Subdomain
- Path slug
- JWT claim
- Fallback to default
"""

from __future__ import annotations

from typing import Optional
from dataclasses import dataclass


@dataclass
class ResolveResult:
    """Resultado de resolución de tenant."""
    tenant_id: str
    source: str                    # header, subdomain, path, jwt, default
    confidence: str                # high, medium, low
    validated: bool = False


class TenantResolver:
    """Resuelve tenant desde múltiples fuentes."""

    def __init__(self, tenant_manager: Any):
        self._manager = tenant_manager
        self._default_tenant: Optional[str] = None

    def set_default_tenant(self, tenant_id: str) -> None:
        """Establece tenant por defecto."""
        self._default_tenant = tenant_id

    def resolve_from_header(self, headers: dict) -> Optional[ResolveResult]:
        """Resuelve desde header X-Tenant-ID."""
        tenant_id = headers.get("X-Tenant-ID") or headers.get("x-tenant-id")
        if not tenant_id:
            return None

        tenant = self._manager.get_tenant_by_id_or_slug(tenant_id)
        if not tenant:
            return None

        return ResolveResult(
            tenant_id=tenant.tenant_id,
            source="header",
            confidence="high",
            validated=True,
        )

    def resolve_from_subdomain(self, host: str) -> Optional[ResolveResult]:
        """Resuelve desde subdomain (e.g., hospitallen.orma.systems)."""
        parts = host.split(".")
        if not parts or len(parts) < 2:
            return None

        subdomain = parts[0]
        if subdomain in ("www", "api", "admin", "localhost"):
            return None

        tenant = self._manager.get_tenant_by_slug(subdomain)
        if not tenant:
            return None

        return ResolveResult(
            tenant_id=tenant.tenant_id,
            source="subdomain",
            confidence="high",
            validated=True,
        )

    def resolve_from_path(self, path: str) -> Optional[ResolveResult]:
        """
        Resuelve desde path (e.g., /hospitallen/...).
        Deprecated: path-based routing está en desuso.
        """
        segments = [s for s in path.strip("/").split("/") if s]
        if not segments:
            return None

        first_segment = segments[0]
        if first_segment in ("api", "admin", "docs"):
            return None

        tenant = self._manager.get_tenant_by_slug(first_segment)
        if not tenant:
            return None

        return ResolveResult(
            tenant_id=tenant.tenant_id,
            source="path",
            confidence="medium",
            validated=True,
        )

    def resolve_from_jwt(self, claims: dict) -> Optional[ResolveResult]:
        """Resuelve desde JWT claims."""
        tenant_id = claims.get("tenant_id") or claims.get("tid")
        if not tenant_id:
            return None

        tenant = self._manager.get_tenant_by_id_or_slug(tenant_id)
        if not tenant:
            return None

        return ResolveResult(
            tenant_id=tenant.tenant_id,
            source="jwt",
            confidence="high",
            validated=True,
        )

    def resolve(
        self,
        headers: Optional[dict] = None,
        host: Optional[str] = None,
        path: Optional[str] = None,
        jwt_claims: Optional[dict] = None,
    ) -> Optional[ResolveResult]:
        """
        Resuelve tenant con prioridad:
        1. Header X-Tenant-ID (más específico)
        2. JWT claim
        3. Subdomain
        4. Path slug
        5. Default tenant
        """
        headers = headers or {}

        # Priority 1: Header
        result = self.resolve_from_header(headers)
        if result:
            return result

        # Priority 2: JWT
        if jwt_claims:
            result = self.resolve_from_jwt(jwt_claims)
            if result:
                return result

        # Priority 3: Subdomain
        if host:
            result = self.resolve_from_subdomain(host)
            if result:
                return result

        # Priority 4: Path
        if path:
            result = self.resolve_from_path(path)
            if result:
                return result

        # Priority 5: Default
        if self._default_tenant:
            return ResolveResult(
                tenant_id=self._default_tenant,
                source="default",
                confidence="low",
                validated=False,
            )

        return None
