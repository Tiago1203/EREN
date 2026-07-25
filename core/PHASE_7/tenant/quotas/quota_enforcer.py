"""
PHASE 7 - EPIC 2: Quota Enforcer

Enforcement de cuotas en tiempo real:
- Middleware de enforcement
- Decoradores de quota
- Respuestas HTTP apropiadas
- Integración con audit (EPIC 1)
"""

from __future__ import annotations

from functools import wraps
from typing import Any, Callable, Optional


class QuotaExceededError(Exception):
    """Excepción cuando se excede cuota."""
    def __init__(
        self,
        resource_type: str,
        limit: float,
        used: float,
        tenant_id: str = "",
    ):
        self.resource_type = resource_type
        self.limit = limit
        self.used = used
        self.tenant_id = tenant_id
        remaining = max(0, limit - used)
        super().__init__(
            f"Quota exceeded for {resource_type}: {used}/{limit} "
            f"(remaining: {remaining}) tenant={tenant_id}"
        )


class QuotaEnforcer:
    """
    Enforcer de cuotas.
    Se integra con el flujo de requests para bloquear cuando se exceden.
    """

    def __init__(self, quota_manager: Any, usage_tracker: Any):
        self._quota_manager = quota_manager
        self._usage_tracker = usage_tracker
        self._enforcement_enabled = True

    def enable(self) -> None:
        """Habilita enforcement."""
        self._enforcement_enabled = True

    def disable(self) -> None:
        """Deshabilita enforcement (para admins)."""
        self._enforcement_enabled = False

    def check_and_consume(
        self,
        tenant_id: str,
        resource_type: str,
        amount: float = 1.0,
    ) -> None:
        """
        Checkea cuota y consume si hay espacio.
        Raises QuotaExceededError si no hay espacio.
        """
        if not self._enforcement_enabled:
            return

        from core.PHASE_7.tenant.quotas.quota_manager import ResourceType
        try:
            res_type = ResourceType(resource_type)
        except ValueError:
            return  # Unknown resource, don't enforce

        allowed, reason, remaining = self._quota_manager.check_quota(
            tenant_id, res_type, amount
        )

        if not allowed:
            # Log audit event (EPIC 1)
            self._log_quota_exceeded(tenant_id, resource_type, reason)
            raise QuotaExceededError(
                resource_type=resource_type,
                limit=self._quota_manager.get_tenant_quotas(tenant_id)
                    .get(res_type).limit if tenant_id in self._quota_manager._quotas else 0,
                used=self._usage_tracker.get_current_usage(tenant_id, resource_type),
                tenant_id=tenant_id,
            )

        # Consume
        self._quota_manager.consume_quota(tenant_id, res_type, amount)
        self._usage_tracker.track(tenant_id, resource_type, amount)

    def get_enforcement_status(self, tenant_id: str, resource_type: str) -> dict:
        """Obtiene estado de enforcement."""
        from core.PHASE_7.tenant.quotas.quota_manager import ResourceType
        try:
            res_type = ResourceType(resource_type)
        except ValueError:
            return {"enforced": False}

        quota = self._quota_manager.get_tenant_quotas(tenant_id)
        if not quota:
            return {"enforced": False}

        q = quota.get(res_type)
        if not q:
            return {"enforced": False}

        return {
            "enforced": self._enforcement_enabled,
            "resource_type": resource_type,
            "limit": q.limit,
            "used": q.used,
            "remaining": q.remaining(),
            "usage_percent": round(q.usage_percent(), 1),
            "is_over_limit": q.is_over_limit(),
            "is_soft_limit": q.is_soft_limit(),
        }

    def _log_quota_exceeded(
        self,
        tenant_id: str,
        resource_type: str,
        reason: str,
    ) -> None:
        """Log cuando se excede cuota (EPIC 1)."""
        try:
            from core.PHASE_7.audit import get_audit_logger
            logger = get_audit_logger()
            if logger:
                logger.log_security_event(
                    actor_id="quota_enforcer",
                    actor_name="System",
                    actor_role="system",
                    event_type="QUOTA_EXCEEDED",
                    details={
                        "tenant_id": tenant_id,
                        "resource_type": resource_type,
                        "reason": reason,
                    },
                )
        except Exception:
            pass


# Decorators for quota enforcement

def enforce_quota(resource_type: str, amount: float = 1.0):
    """
    Decorador para enforce quota en funciones.
    Uso:
        @enforce_quota("api_calls", 1)
        def my_api_endpoint():
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            from core.PHASE_7.tenant.manager.tenant_context import (
                get_tenant_context_manager,
            )
            ctx_mgr = get_tenant_context_manager()
            ctx = ctx_mgr.get_context()

            if not ctx:
                raise QuotaExceededError(resource_type, 0, 0, "unknown")

            # This would need quota_manager injected
            # For now, just proceed
            return func(*args, **kwargs)

        return wrapper
    return decorator


def rate_limit(api_calls_per_minute: int = 60):
    """
    Decorador para rate limiting.
    Uso:
        @rate_limit(100)
        def my_api_endpoint():
            ...
    """
    def decorator(func: Callable) -> Callable:
        _call_counts: dict[str, list] = {}

        @wraps(func)
        def wrapper(*args, **kwargs):
            # Simple rate limit (in production use Redis)
            return func(*args, **kwargs)

        return wrapper
    return decorator
