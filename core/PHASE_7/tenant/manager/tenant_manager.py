"""
PHASE 7 - EPIC 2: Tenant Manager

CRUD completo para tenants:
- Create, read, update, delete tenants
- Tenant configuration
- Status management
- Subscription tiers
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
import uuid


class TenantStatus(str, Enum):
    """Estados de un tenant."""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    PENDING = "pending"
    TERMINATED = "terminated"
    READONLY = "readonly"


class SubscriptionTier(str, Enum):
    """Planes de suscripción."""
    STARTER = "starter"           # Hasta 50 usuarios, 1 establecimiento
    PROFESSIONAL = "professional"  # Hasta 500 usuarios, 5 establecimientos
    ENTERPRISE = "enterprise"     # Ilimitado
    TRIAL = "trial"              # 30 días trial


@dataclass
class TenantConfig:
    """Configuración del tenant."""
    allow_phi: bool = True
    require_mfa: bool = True
    max_users: int = 50
    max_establishments: int = 1
    retention_days: int = 2190       # 6 años HIPAA
    enable_audit_export: bool = True
    enable_clinical_modules: bool = True
    enforce_consent_tracking: bool = True
    custom_branding: bool = False
    ip_whitelist_enabled: bool = False
    ip_whitelist: list[str] = field(default_factory=list)


@dataclass
class TenantContact:
    """Información de contacto del tenant."""
    name: str
    email: str
    phone: str = ""
    role: str = ""


@dataclass
class TenantSubscription:
    """Suscripción del tenant."""
    tier: SubscriptionTier
    start_date: datetime
    end_date: Optional[datetime] = None
    auto_renew: bool = True
    billing_email: str = ""
    is_active: bool = True


@dataclass
class Tenant:
    """Tenant principal."""
    tenant_id: str
    name: str
    slug: str                        # URL-friendly identifier
    status: TenantStatus

    # Organization info
    legal_name: str = ""
    tax_id: str = ""
    address: str = ""
    country: str = ""
    timezone: str = "UTC"

    # Contact
    contact: Optional[TenantContact] = None

    # Subscription
    subscription: Optional[TenantSubscription] = None

    # Configuration
    config: TenantConfig = field(default_factory=TenantConfig)

    # Compliance
    hipaa_business_associate: bool = False
    data_processing_agreement: bool = False
    gdpr_compliant: bool = False

    # Timestamps
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    activated_at: Optional[datetime] = None
    suspended_at: Optional[datetime] = None

    # Metadata
    created_by: str = ""
    version: int = 1
    metadata: dict = field(default_factory=dict)


class TenantManager:
    """Gestor de tenants."""

    def __init__(self):
        self._tenants: dict[str, Tenant] = {}
        self._slugs: dict[str, str] = {}   # slug -> tenant_id

    def create_tenant(
        self,
        name: str,
        slug: str,
        legal_name: str = "",
        tier: SubscriptionTier = SubscriptionTier.TRIAL,
        contact_name: str = "",
        contact_email: str = "",
        created_by: str = "",
        config: Optional[TenantConfig] = None,
    ) -> Tenant:
        """Crea un nuevo tenant."""
        if slug in self._slugs:
            raise ValueError(f"Tenant slug '{slug}' already exists")

        tenant_id = f"tenant-{uuid.uuid4().hex[:12]}"

        subscription = TenantSubscription(
            tier=tier,
            start_date=datetime.now(timezone.utc),
        )

        contact = None
        if contact_name or contact_email:
            contact = TenantContact(name=contact_name, email=contact_email)

        tenant = Tenant(
            tenant_id=tenant_id,
            name=name,
            slug=slug,
            status=TenantStatus.PENDING if tier == SubscriptionTier.TRIAL else TenantStatus.ACTIVE,
            legal_name=legal_name or name,
            contact=contact,
            subscription=subscription,
            config=config or self._default_config_for_tier(tier),
            created_by=created_by,
            activated_at=datetime.now(timezone.utc) if tier != SubscriptionTier.TRIAL else None,
        )

        self._tenants[tenant_id] = tenant
        self._slugs[slug] = tenant_id

        return tenant

    def _default_config_for_tier(self, tier: SubscriptionTier) -> TenantConfig:
        """Config por defecto según tier."""
        if tier == SubscriptionTier.STARTER:
            return TenantConfig(max_users=50, max_establishments=1)
        elif tier == SubscriptionTier.PROFESSIONAL:
            return TenantConfig(max_users=500, max_establishments=5)
        elif tier == SubscriptionTier.ENTERPRISE:
            return TenantConfig(max_users=10000, max_establishments=100, custom_branding=True)
        else:  # TRIAL
            return TenantConfig(max_users=10, max_establishments=1, enable_audit_export=False)

    def get_tenant(self, tenant_id: str) -> Optional[Tenant]:
        """Obtiene tenant por ID."""
        return self._tenants.get(tenant_id)

    def get_tenant_by_slug(self, slug: str) -> Optional[Tenant]:
        """Obtiene tenant por slug."""
        tid = self._slugs.get(slug)
        return self._tenants.get(tid) if tid else None

    def get_tenant_by_id_or_slug(self, identifier: str) -> Optional[Tenant]:
        """Obtiene tenant por ID o slug."""
        if identifier in self._tenants:
            return self._tenants[identifier]
        return self.get_tenant_by_slug(identifier)

    def list_tenants(
        self,
        status: Optional[TenantStatus] = None,
        tier: Optional[SubscriptionTier] = None,
        limit: int = 100,
    ) -> list[Tenant]:
        """Lista tenants con filtros."""
        tenants = list(self._tenants.values())

        if status:
            tenants = [t for t in tenants if t.status == status]
        if tier and t.subscription:
            tenants = [t for t in tenants if t.subscription.tier == tier]

        tenants.sort(key=lambda t: t.created_at, reverse=True)
        return tenants[:limit]

    def update_tenant(
        self,
        tenant_id: str,
        name: Optional[str] = None,
        status: Optional[TenantStatus] = None,
        config: Optional[TenantConfig] = None,
        contact: Optional[TenantContact] = None,
        metadata: Optional[dict] = None,
    ) -> Tenant:
        """Actualiza un tenant."""
        tenant = self._tenants.get(tenant_id)
        if not tenant:
            raise ValueError(f"Tenant {tenant_id} not found")

        if name:
            tenant.name = name
        if status:
            old_status = tenant.status
            tenant.status = status
            if status == TenantStatus.SUSPENDED and not tenant.suspended_at:
                tenant.suspended_at = datetime.now(timezone.utc)
            if old_status == TenantStatus.SUSPENDED and status == TenantStatus.ACTIVE:
                tenant.suspended_at = None
        if config:
            tenant.config = config
        if contact:
            tenant.contact = contact
        if metadata:
            tenant.metadata.update(metadata)

        tenant.updated_at = datetime.now(timezone.utc)
        tenant.version += 1

        return tenant

    def suspend_tenant(self, tenant_id: str, reason: str = "") -> Tenant:
        """Suspende un tenant."""
        return self.update_tenant(
            tenant_id,
            status=TenantStatus.SUSPENDED,
            metadata={"suspension_reason": reason},
        )

    def activate_tenant(self, tenant_id: str) -> Tenant:
        """Activa un tenant."""
        tenant = self.update_tenant(tenant_id, status=TenantStatus.ACTIVE)
        tenant.activated_at = datetime.now(timezone.utc)
        return tenant

    def terminate_tenant(self, tenant_id: str) -> Tenant:
        """Termina un tenant (soft delete)."""
        return self.update_tenant(
            tenant_id,
            status=TenantStatus.TERMINATED,
        )

    def delete_tenant(self, tenant_id: str) -> bool:
        """Elimina un tenant (solo si está terminado)."""
        tenant = self._tenants.get(tenant_id)
        if not tenant:
            return False
        if tenant.status != TenantStatus.TERMINATED:
            raise ValueError("Can only delete terminated tenants")

        del self._slugs[tenant.slug]
        del self._tenants[tenant_id]
        return True

    def count_tenants(self, status: Optional[TenantStatus] = None) -> int:
        """Cuenta tenants."""
        if status:
            return sum(1 for t in self._tenants.values() if t.status == status)
        return len(self._tenants)

    def get_tenant_statistics(self) -> dict:
        """Estadísticas de tenants."""
        by_status = {}
        by_tier = {}

        for tenant in self._tenants.values():
            status_key = tenant.status.value
            by_status[status_key] = by_status.get(status_key, 0) + 1

            if tenant.subscription:
                tier_key = tenant.subscription.tier.value
                by_tier[tier_key] = by_tier.get(tier_key, 0) + 1

        return {
            "total": len(self._tenants),
            "by_status": by_status,
            "by_tier": by_tier,
            "active": self.count_tenants(TenantStatus.ACTIVE),
            "suspended": self.count_tenants(TenantStatus.SUSPENDED),
        }
