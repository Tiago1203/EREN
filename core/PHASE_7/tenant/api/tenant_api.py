"""
PHASE 7 - EPIC 2: Tenant API

REST API para gestión de tenants:
- CRUD endpoints
- Status management
- Configuration
- Quotas
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
import uuid


@dataclass
class TenantListRequest:
    """Request para listar tenants."""
    status: Optional[str] = None
    tier: Optional[str] = None
    limit: int = 100
    offset: int = 0


@dataclass
class TenantCreateRequest:
    """Request para crear tenant."""
    name: str
    slug: str
    contact_name: str
    contact_email: str
    tier: str = "trial"
    timezone: str = "UTC"
    country: str = ""
    hipaa_business_associate: bool = False
    data_processing_agreement: bool = False
    gdpr_compliant: bool = False


@dataclass
class TenantUpdateRequest:
    """Request para actualizar tenant."""
    name: Optional[str] = None
    status: Optional[str] = None
    timezone: Optional[str] = None
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    metadata: dict = field(default_factory=dict)


@dataclass
class TenantResponse:
    """Response de tenant."""
    tenant_id: str
    name: str
    slug: str
    status: str
    tier: str
    plan_limits: dict
    usage: dict
    created_at: str
    activated_at: Optional[str] = None


class TenantAPIService:
    """Servicio de API para gestión de tenants."""

    def __init__(
        self,
        tenant_manager: Any,
        quota_manager: Any,
        usage_tracker: Any,
        quota_enforcer: Any,
    ):
        self._manager = tenant_manager
        self._quota_manager = quota_manager
        self._usage_tracker = usage_tracker
        self._enforcer = quota_enforcer

    def list_tenants(self, request: TenantListRequest) -> dict:
        """Lista tenants."""
        from core.PHASE_7.tenant.manager.tenant_manager import TenantStatus

        status = TenantStatus(request.status) if request.status else None

        tenants = self._manager.list_tenants(
            status=status,
            limit=request.limit,
        )

        return {
            "total": len(tenants),
            "offset": request.offset,
            "limit": request.limit,
            "tenants": [
                self._format_tenant(t) for t in tenants
            ],
        }

    def get_tenant(self, tenant_id: str) -> Optional[TenantResponse]:
        """Obtiene un tenant."""
        tenant = self._manager.get_tenant(tenant_id)
        if not tenant:
            return None
        return self._format_tenant(tenant)

    def create_tenant(self, request: TenantCreateRequest) -> TenantResponse:
        """Crea un nuevo tenant."""
        from core.PHASE_7.tenant.manager.tenant_manager import SubscriptionTier

        tier = SubscriptionTier(request.tier)

        tenant = self._manager.create_tenant(
            name=request.name,
            slug=request.slug,
            contact_name=request.contact_name,
            contact_email=request.contact_email,
            tier=tier,
        )

        # Update compliance flags
        tenant.hipaa_business_associate = request.hipaa_business_associate
        tenant.data_processing_agreement = request.data_processing_agreement
        tenant.gdpr_compliant = request.gdpr_compliant
        tenant.country = request.country
        tenant.timezone = request.timezone

        # Create quotas
        self._quota_manager.create_tenant_quotas(tenant.tenant_id, request.tier)

        return self._format_tenant(tenant)

    def update_tenant(
        self,
        tenant_id: str,
        request: TenantUpdateRequest,
    ) -> TenantResponse:
        """Actualiza un tenant."""
        from core.PHASE_7.tenant.manager.tenant_manager import TenantStatus, TenantContact

        update_kwargs = {}

        if request.name:
            update_kwargs["name"] = request.name
        if request.status:
            update_kwargs["status"] = TenantStatus(request.status)
        if request.timezone:
            update_kwargs["metadata"] = {**request.metadata, "timezone": request.timezone}
        if request.contact_name or request.contact_email:
            update_kwargs["contact"] = TenantContact(
                name=request.contact_name or "",
                email=request.contact_email or "",
            )

        tenant = self._manager.update_tenant(tenant_id, **update_kwargs)
        return self._format_tenant(tenant)

    def suspend_tenant(self, tenant_id: str, reason: str) -> TenantResponse:
        """Suspende un tenant."""
        tenant = self._manager.suspend_tenant(tenant_id, reason)
        return self._format_tenant(tenant)

    def activate_tenant(self, tenant_id: str) -> TenantResponse:
        """Activa un tenant."""
        tenant = self._manager.activate_tenant(tenant_id)
        return self._format_tenant(tenant)

    def terminate_tenant(self, tenant_id: str) -> TenantResponse:
        """Termina un tenant."""
        tenant = self._manager.terminate_tenant(tenant_id)
        return self._format_tenant(tenant)

    def get_tenant_quotas(self, tenant_id: str) -> dict:
        """Obtiene cuotas del tenant."""
        return self._quota_manager.get_usage_report(tenant_id)

    def get_tenant_usage(self, tenant_id: str) -> dict:
        """Obtiene uso del tenant."""
        from core.PHASE_7.tenant.quotas.quota_manager import ResourceType

        usage = {}
        for res_type in ResourceType:
            usage[res_type.value] = {
                "current": self._usage_tracker.get_current_usage(tenant_id, res_type.value),
                "daily": self._usage_tracker.get_daily_usage(tenant_id, res_type.value),
                "monthly": self._usage_tracker.get_monthly_usage(tenant_id, res_type.value),
            }

        return usage

    def get_quota_alerts(self, tenant_id: str) -> list[dict]:
        """Obtiene alertas de cuotas."""
        return self._quota_manager.get_alert_report(tenant_id)

    def _format_tenant(self, tenant) -> TenantResponse:
        """Formatea tenant para response."""
        plan_limits = {}
        if tenant.subscription:
            tier = tenant.subscription.tier.value
            # Get from quota manager
            quotas = self._quota_manager.get_tenant_quotas(tenant.tenant_id)
            if quotas:
                for res_type, quota in quotas.quotas.items():
                    plan_limits[res_type] = {
                        "limit": quota.limit,
                        "used": quota.used,
                        "remaining": quota.remaining(),
                    }

        return TenantResponse(
            tenant_id=tenant.tenant_id,
            name=tenant.name,
            slug=tenant.slug,
            status=tenant.status.value,
            tier=tenant.subscription.tier.value if tenant.subscription else "unknown",
            plan_limits=plan_limits,
            usage={},
            created_at=tenant.created_at.isoformat(),
            activated_at=tenant.activated_at.isoformat() if tenant.activated_at else None,
        )


class TenantMiddleware:
    """
    Middleware para resolver tenant automáticamente.
    Integrable con FastAPI/Starlette.
    """

    def __init__(
        self,
        resolver: Any,
        context_manager: Any,
        query_filter: Any,
    ):
        self._resolver = resolver
        self._context = context_manager
        self._filter = query_filter

    async def resolve_and_set_context(
        self,
        headers: Optional[dict] = None,
        host: Optional[str] = None,
        path: Optional[str] = None,
        user: Optional[dict] = None,
    ) -> bool:
        """
        Resuelve tenant y establece contexto.
        Returns True si se resolvió correctamente.
        """
        jwt_claims = user or {}
        result = self._resolver.resolve(
            headers=headers,
            host=host,
            path=path,
            jwt_claims=jwt_claims,
        )

        if not result:
            return False

        # Set context
        from core.PHASE_7.tenant.manager.tenant_context import TenantContext

        ctx = TenantContext(
            tenant_id=result.tenant_id,
            user_id=jwt_claims.get("user_id", "anonymous"),
            user_role=jwt_claims.get("role", "user"),
            is_super_admin=jwt_claims.get("role") == "super_admin",
            purpose_of_use=jwt_claims.get("purpose_of_use", "treatment"),
            session_id=jwt_claims.get("session_id", ""),
            ip_address=jwt_claims.get("ip_address", ""),
        )

        self._context.set_context(ctx)
        return True

    def clear_context(self) -> None:
        """Limpia contexto después del request."""
        self._context.clear_context()
