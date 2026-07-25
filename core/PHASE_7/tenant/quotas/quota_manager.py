"""
PHASE 7 - EPIC 2: Quota Manager

Gestión de cuotas de recursos por tenant:
- Resource quotas
- Usage tracking
- Enforcement
- Alerts
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
import uuid


class ResourceType(str, Enum):
    """Tipos de recursos."""
    USERS = "users"
    ESTABLISHMENTS = "establishments"
    STORAGE_MB = "storage_mb"
    API_CALLS = "api_calls"
    REPORTS = "reports"
    AUDIT_EXPORTS = "audit_exports"
    MAINtenances = "maintenances"
    EQUIPMENT = "equipment"


@dataclass
class ResourceQuota:
    """Cuota de un recurso."""
    resource_type: ResourceType
    limit: float
    used: float = 0.0
    unit: str = "count"
    soft_limit_percent: float = 80.0   # Alertar al 80%
    hard_limit: float = 0.0            # Bloquear al 100%

    def usage_percent(self) -> float:
        """Porcentaje de uso."""
        if self.limit == 0:
            return 0.0
        return (self.used / self.limit) * 100

    def is_over_limit(self) -> bool:
        """Está sobre el límite hard?"""
        if self.hard_limit > 0:
            return self.used >= self.hard_limit
        return self.used >= self.limit

    def is_soft_limit(self) -> bool:
        """Está en zona de alerta (soft limit)?"""
        return self.usage_percent() >= self.soft_limit_percent

    def remaining(self) -> float:
        """Recursos restantes."""
        return max(0, self.limit - self.used)


@dataclass
class TenantQuota:
    """Colección de cuotas de un tenant."""
    tenant_id: str
    quotas: dict[str, ResourceQuota] = field(default_factory=dict)

    def get(self, resource_type: ResourceType) -> Optional[ResourceQuota]:
        return self.quotas.get(resource_type.value)

    def add_quota(self, quota: ResourceQuota) -> None:
        self.quotas[quota.resource_type.value] = quota


class QuotaManager:
    """Gestor de cuotas de recursos."""

    # Límites por defecto por tier
    DEFAULT_QUOTAS = {
        "starter": {
            ResourceType.USERS: 50,
            ResourceType.ESTABLISHMENTS: 1,
            ResourceType.STORAGE_MB: 10240,      # 10GB
            ResourceType.API_CALLS: 10000,       # /day
            ResourceType.REPORTS: 100,           # /month
            ResourceType.AUDIT_EXPORTS: 10,     # /month
            ResourceType.EQUIPMENT: 100,
            ResourceType.MAINtenances: 50,
        },
        "professional": {
            ResourceType.USERS: 500,
            ResourceType.ESTABLISHMENTS: 5,
            ResourceType.STORAGE_MB: 102400,     # 100GB
            ResourceType.API_CALLS: 100000,
            ResourceType.REPORTS: 1000,
            ResourceType.AUDIT_EXPORTS: 100,
            ResourceType.EQUIPMENT: 1000,
            ResourceType.MAINtenances: 500,
        },
        "enterprise": {
            ResourceType.USERS: 100000,
            ResourceType.ESTABLISHMENTS: 100,
            ResourceType.STORAGE_MB: 1048576,    # 1TB
            ResourceType.API_CALLS: float("inf"),
            ResourceType.REPORTS: float("inf"),
            ResourceType.AUDIT_EXPORTS: float("inf"),
            ResourceType.EQUIPMENT: float("inf"),
            ResourceType.MAINtenances: float("inf"),
        },
        "trial": {
            ResourceType.USERS: 10,
            ResourceType.ESTABLISHMENTS: 1,
            ResourceType.STORAGE_MB: 1024,
            ResourceType.API_CALLS: 1000,
            ResourceType.REPORTS: 10,
            ResourceType.AUDIT_EXPORTS: 2,
            ResourceType.EQUIPMENT: 20,
            ResourceType.MAINtenances: 10,
        },
    }

    def __init__(self):
        self._quotas: dict[str, TenantQuota] = {}

    def create_tenant_quotas(
        self,
        tenant_id: str,
        tier: str,
    ) -> TenantQuota:
        """Crea cuotas por defecto para un tenant."""
        tier_limits = self.DEFAULT_QUOTAS.get(tier, self.DEFAULT_QUOTAS["starter"])
        tenant_quota = TenantQuota(tenant_id=tenant_id)

        for resource_type, limit in tier_limits.items():
            quota = ResourceQuota(
                resource_type=resource_type,
                limit=limit,
                hard_limit=limit,
            )
            tenant_quota.add_quota(quota)

        self._quotas[tenant_id] = tenant_quota
        return tenant_quota

    def get_tenant_quotas(self, tenant_id: str) -> Optional[TenantQuota]:
        """Obtiene cuotas del tenant."""
        return self._quotas.get(tenant_id)

    def check_quota(
        self,
        tenant_id: str,
        resource_type: ResourceType,
        amount: float = 1.0,
    ) -> tuple[bool, str, float]:
        """
        Check si tenant puede consumir recursos.
        Returns (allowed, reason, remaining).
        """
        tenant_quota = self._quotas.get(tenant_id)
        if not tenant_quota:
            return True, "No quota configured", float("inf")

        quota = tenant_quota.get(resource_type)
        if not quota:
            return True, "Resource not quota-limited", float("inf")

        remaining = quota.remaining()
        if quota.is_over_limit():
            return False, f"Quota exceeded for {resource_type.value}: {quota.used}/{quota.limit}", 0

        if remaining < amount:
            return False, f"Insufficient quota: need {amount}, have {remaining}", remaining

        return True, "OK", remaining - amount

    def consume_quota(
        self,
        tenant_id: str,
        resource_type: ResourceType,
        amount: float = 1.0,
    ) -> bool:
        """
        Consume cuota de recurso.
        Returns True si se pudo consumir.
        """
        allowed, reason, _ = self.check_quota(tenant_id, resource_type, amount)
        if not allowed:
            return False

        tenant_quota = self._quotas.get(tenant_id)
        if not tenant_quota:
            return False

        quota = tenant_quota.get(resource_type)
        if quota:
            quota.used += amount

        return True

    def release_quota(
        self,
        tenant_id: str,
        resource_type: ResourceType,
        amount: float = 1.0,
    ) -> None:
        """Libera cuota (undo consume)."""
        tenant_quota = self._quotas.get(tenant_id)
        if not tenant_quota:
            return

        quota = tenant_quota.get(resource_type)
        if quota:
            quota.used = max(0, quota.used - amount)

    def update_quota_limit(
        self,
        tenant_id: str,
        resource_type: ResourceType,
        new_limit: float,
    ) -> ResourceQuota:
        """Actualiza límite de cuota."""
        tenant_quota = self._quotas.get(tenant_id)
        if not tenant_quota:
            raise ValueError(f"No quota found for tenant {tenant_id}")

        quota = tenant_quota.get(resource_type)
        if not quota:
            quota = ResourceQuota(resource_type=resource_type, limit=new_limit)
            tenant_quota.add_quota(quota)
        else:
            quota.limit = new_limit

        return quota

    def get_usage_report(self, tenant_id: str) -> dict:
        """Genera reporte de uso de cuotas."""
        tenant_quota = self._quotas.get(tenant_id)
        if not tenant_quota:
            return {"tenant_id": tenant_id, "quotas": {}}

        quotas_report = {}
        for resource_type, quota in tenant_quota.quotas.items():
            quotas_report[resource_type] = {
                "used": quota.used,
                "limit": quota.limit,
                "remaining": quota.remaining(),
                "usage_percent": round(quota.usage_percent(), 1),
                "is_over_limit": quota.is_over_limit(),
                "is_soft_limit": quota.is_soft_limit(),
            }

        return {
            "tenant_id": tenant_id,
            "quotas": quotas_report,
            "any_over_limit": any(q["is_over_limit"] for q in quotas_report.values()),
            "any_soft_limit": any(q["is_soft_limit"] for q in quotas_report.values()),
        }

    def get_alert_report(self, tenant_id: str) -> list[dict]:
        """Genera lista de alertas de cuotas."""
        tenant_quota = self._quotas.get(tenant_id)
        if not tenant_quota:
            return []

        alerts = []
        for resource_type, quota in tenant_quota.quotas.items():
            if quota.is_over_limit():
                alerts.append({
                    "alert_type": "quota_exceeded",
                    "resource": resource_type,
                    "severity": "critical",
                    "message": f"Quota exceeded for {resource_type}: {quota.used}/{quota.limit}",
                    "usage_percent": round(quota.usage_percent(), 1),
                })
            elif quota.is_soft_limit():
                alerts.append({
                    "alert_type": "quota_warning",
                    "resource": resource_type,
                    "severity": "warning",
                    "message": f"Quota at {quota.usage_percent():.0f}% for {resource_type}",
                    "usage_percent": round(quota.usage_percent(), 1),
                })

        return alerts
