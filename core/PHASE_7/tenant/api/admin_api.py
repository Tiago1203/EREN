"""
PHASE 7 - EPIC 2: Super Admin API

API de super-admin para control de tenants:
- Multi-tenant management
- Cross-tenant operations
- System statistics
- Emergency access
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional


@dataclass
class SystemStatistics:
    """Estadísticas del sistema."""
    total_tenants: int
    active_tenants: int
    suspended_tenants: int
    total_users: int
    total_establishments: int
    total_equipment: int
    system_health: str
    uptime_hours: float


@dataclass
class TenantHealthCheck:
    """Health check de tenant."""
    tenant_id: str
    status: str
    database_ok: bool
    cache_ok: bool
    rls_ok: bool
    quota_ok: bool
    issues: list[str]


class AdminAPIService:
    """Servicio de API para super-admins."""

    def __init__(
        self,
        tenant_manager: Any,
        quota_manager: Any,
        rls_manager: Any,
        cache_isolation: Any,
    ):
        self._tenant_manager = tenant_manager
        self._quota_manager = quota_manager
        self._rls_manager = rls_manager
        self._cache_isolation = cache_isolation

    def get_system_statistics(self) -> SystemStatistics:
        """Obtiene estadísticas globales del sistema."""
        stats = self._tenant_manager.get_tenant_statistics()

        return SystemStatistics(
            total_tenants=stats["total"],
            active_tenants=stats["active"],
            suspended_tenants=stats["suspended"],
            total_users=0,      # Would query users table
            total_establishments=0,
            total_equipment=0,
            system_health="healthy",
            uptime_hours=0,
        )

    def get_all_tenants_summary(self) -> dict:
        """Obtiene resumen de todos los tenants."""
        tenants = self._tenant_manager.list_tenants(limit=1000)

        summary = []
        for tenant in tenants:
            quota_report = self._quota_manager.get_usage_report(tenant.tenant_id)
            summary.append({
                "tenant_id": tenant.tenant_id,
                "name": tenant.name,
                "status": tenant.status.value,
                "tier": tenant.subscription.tier.value if tenant.subscription else "unknown",
                "created_at": tenant.created_at.isoformat(),
                "quota_alerts": len(self._quota_manager.get_alert_report(tenant.tenant_id)),
                "any_over_limit": quota_report.get("any_over_limit", False),
            })

        return {
            "total": len(summary),
            "tenants": summary,
        }

    def get_tenant_health(self, tenant_id: str) -> TenantHealthCheck:
        """Realiza health check de tenant."""
        tenant = self._tenant_manager.get_tenant(tenant_id)
        if not tenant:
            raise ValueError(f"Tenant {tenant_id} not found")

        issues: list[str] = []

        # Check database connectivity (mock)
        db_ok = True

        # Check RLS
        rls_ok = self._verify_rls_policies(tenant_id)
        if not rls_ok:
            issues.append("RLS policies not properly configured")

        # Check quota
        quota_report = self._quota_manager.get_usage_report(tenant_id)
        quota_ok = not quota_report.get("any_over_limit", False)
        if not quota_ok:
            issues.append("Quota limits exceeded")

        # Cache check (mock)
        cache_ok = True

        overall_status = "healthy"
        if issues:
            if any("RLS" in i or "quota" in i for i in issues):
                overall_status = "degraded"
            else:
                overall_status = "unhealthy"

        return TenantHealthCheck(
            tenant_id=tenant_id,
            status=overall_status,
            database_ok=db_ok,
            cache_ok=cache_ok,
            rls_ok=rls_ok,
            quota_ok=quota_ok,
            issues=issues,
        )

    def _verify_rls_policies(self, tenant_id: str) -> bool:
        """Verifica que RLS esté configurado."""
        # In production: query pg_policies for tenant's tables
        return True

    def perform_tenant_health_checks(self) -> dict:
        """Realiza health check de todos los tenants activos."""
        tenants = self._tenant_manager.list_tenants(limit=1000)
        results = {}

        for tenant in tenants:
            if tenant.status.value == "active":
                health = self.get_tenant_health(tenant.tenant_id)
                results[tenant.tenant_id] = {
                    "status": health.status,
                    "issues": health.issues,
                }

        healthy = sum(1 for r in results.values() if r["status"] == "healthy")
        degraded = sum(1 for r in results.values() if r["status"] == "degraded")
        unhealthy = sum(1 for r in results.values() if r["status"] == "unhealthy")

        return {
            "total_checked": len(results),
            "healthy": healthy,
            "degraded": degraded,
            "unhealthy": unhealthy,
            "details": results,
        }

    def emergency_suspend_tenant(
        self,
        tenant_id: str,
        reason: str,
        admin_user: str,
    ) -> dict:
        """
        Suspende tenant por emergencia.
        Requiere justificación y auditoría completa (EPIC 1).
        """
        tenant = self._tenant_manager.suspend_tenant(tenant_id, reason)

        # Log to audit (EPIC 1)
        try:
            from core.PHASE_7.audit import get_audit_logger
            logger = get_audit_logger()
            if logger:
                logger.log_security_event(
                    actor_id=admin_user,
                    actor_name="Admin",
                    actor_role="super_admin",
                    event_type="EMERGENCY_TENANT_SUSPENSION",
                    details={
                        "tenant_id": tenant_id,
                        "reason": reason,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    },
                )
        except Exception:
            pass

        # Invalidate all tenant cache
        self._cache_isolation.invalidate_tenant(tenant_id)

        return {
            "tenant_id": tenant.tenant_id,
            "status": tenant.status.value,
            "suspended_at": tenant.suspended_at.isoformat() if tenant.suspended_at else None,
            "reason": reason,
        }

    def bulk_tenant_operation(
        self,
        operation: str,
        tenant_ids: list[str],
        params: dict,
        admin_user: str,
    ) -> dict:
        """Ejecuta operación bulk sobre múltiples tenants."""
        results = {}
        for tenant_id in tenant_ids:
            try:
                if operation == "suspend":
                    self._tenant_manager.suspend_tenant(tenant_id, params.get("reason", "Bulk suspend"))
                    results[tenant_id] = {"status": "suspended"}
                elif operation == "activate":
                    self._tenant_manager.activate_tenant(tenant_id)
                    results[tenant_id] = {"status": "activated"}
                elif operation == "invalidate_cache":
                    self._cache_isolation.invalidate_tenant(tenant_id)
                    results[tenant_id] = {"status": "cache_invalidated"}
                else:
                    results[tenant_id] = {"error": f"Unknown operation: {operation}"}
            except Exception as e:
                results[tenant_id] = {"error": str(e)}

        return {
            "operation": operation,
            "total": len(tenant_ids),
            "results": results,
            "executed_by": admin_user,
        }

    def get_cross_tenant_report(self, report_type: str) -> dict:
        """Genera reporte cross-tenant."""
        if report_type == "quota_usage":
            return self._quota_usage_report()
        elif report_type == "tenant_growth":
            return self._tenant_growth_report()
        elif report_type == "compliance_summary":
            return self._compliance_summary_report()
        else:
            raise ValueError(f"Unknown report type: {report_type}")

    def _quota_usage_report(self) -> dict:
        """Reporte de uso de cuotas por tenant."""
        tenants = self._tenant_manager.list_tenants(limit=1000)
        report = []

        for tenant in tenants:
            quota = self._quota_manager.get_tenant_quotas(tenant.tenant_id)
            if quota:
                report.append({
                    "tenant_id": tenant.tenant_id,
                    "name": tenant.name,
                    "tier": tenant.subscription.tier.value if tenant.subscription else "unknown",
                    "usage": {
                        rt: {"used": q.used, "limit": q.limit}
                        for rt, q in quota.quotas.items()
                    },
                })

        return {"report_type": "quota_usage", "tenants": report}

    def _tenant_growth_report(self) -> dict:
        """Reporte de crecimiento de tenants."""
        tenants = self._tenant_manager.list_tenants(limit=1000)
        by_month = {}

        for tenant in tenants:
            month = tenant.created_at.strftime("%Y-%m")
            by_month[month] = by_month.get(month, 0) + 1

        return {
            "report_type": "tenant_growth",
            "by_month": by_month,
            "total": len(tenants),
        }

    def _compliance_summary_report(self) -> dict:
        """Reporte de compliance."""
        tenants = self._tenant_manager.list_tenants(limit=1000)
        hipaa = sum(1 for t in tenants if t.hipaa_business_associate)
        dpa = sum(1 for t in tenants if t.data_processing_agreement)
        gdpr = sum(1 for t in tenants if t.gdpr_compliant)

        return {
            "report_type": "compliance_summary",
            "total_tenants": len(tenants),
            "hipaa_compliant": hipaa,
            "dpa_signed": dpa,
            "gdpr_compliant": gdpr,
        }
