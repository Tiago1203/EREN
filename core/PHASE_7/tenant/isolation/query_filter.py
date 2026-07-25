"""
PHASE 7 - EPIC 2: Query Filter

Automatic tenant filtering para ORMs y queries:
- SQLAlchemy filter integration
- Prevents cross-tenant queries
- Audit trail (EPIC 1)
- ORM hooks
"""

from __future__ import annotations

from typing import Any, Optional
from dataclasses import dataclass, field


class CrossTenantQueryError(Exception):
    """Intentó acceder a datos de otro tenant."""
    def __init__(self, attempted_tenant: str, context_tenant: str):
        self.attempted_tenant = attempted_tenant
        self.context_tenant = context_tenant
        super().__init__(
            f"Cross-tenant access denied: attempted to access {attempted_tenant} "
            f"from context of {context_tenant}"
        )


class MissingTenantContextError(Exception):
    """No hay contexto de tenant establecido."""
    pass


class QueryFilter:
    """
    Filtro automático de queries por tenant.
    Previene cross-tenant data access en todos los niveles.
    """

    # Columnas de tenant por tabla
    TENANT_COLUMNS = {
        "users": "tenant_id",
        "establishments": "tenant_id",
        "departments": "tenant_id",
        "equipment": "tenant_id",
        "patients": "tenant_id",
        "medical_records": "tenant_id",
        "maintenances": "tenant_id",
        "kpis": "tenant_id",
        "reports": "tenant_id",
        "notifications": "tenant_id",
        "audit_logs": "tenant_id",
    }

    # Tablas globales (no requieren filtro)
    GLOBAL_TABLES = {
        "tenants",
        "tenant_configs",
        "system_settings",
        "countries",
        "timezones",
    }

    def __init__(self, context_manager: Any):
        self._context = context_manager
        self._bypass_enabled = False
        self._bypass_reason = ""

    def enable_bypass(self, reason: str = "") -> None:
        """Habilita bypass (solo para super_admin operations)."""
        ctx = self._context.get_context()
        if not ctx or not ctx.is_super_admin:
            raise PermissionError("Only super admins can enable tenant bypass")
        self._bypass_enabled = True
        self._bypass_reason = reason

    def disable_bypass(self) -> None:
        """Deshabilita bypass."""
        self._bypass_enabled = False
        self._bypass_reason = ""

    def get_tenant_filter(self, table_name: str) -> Optional[dict]:
        """
        Retorna filtro de tenant para tabla.
        None = tabla global, no requiere filtro.
        Dict = {column: tenant_id} para filtrar.
        """
        if table_name in self.GLOBAL_TABLES:
            return None

        col = self.TENANT_COLUMNS.get(table_name)
        if not col:
            return None  # Unknown table, assume global

        if self._bypass_enabled:
            return {}  # Bypass: no filter

        tenant_id = self._get_current_tenant_id()
        return {col: tenant_id}

    def filter_query(self, table_name: str, query: dict) -> dict:
        """
        Filtra query dict por tenant.
        Retorna query modificado con tenant_id filter.
        """
        tenant_filter = self.get_tenant_filter(table_name)
        if tenant_filter is None:
            return query  # Global table

        # Merge with existing filters
        if "filters" not in query:
            query["filters"] = {}

        query["filters"].update(tenant_filter)
        return query

    def validate_access(
        self,
        table_name: str,
        target_tenant_id: Optional[str] = None,
    ) -> bool:
        """
        Valida que el acceso a la tabla/tenant sea válido.
        Raises CrossTenantQueryError si intenta cross-tenant.
        """
        if table_name in self.GLOBAL_TABLES:
            return True

        if self._bypass_enabled:
            return True

        ctx = self._context.get_context()
        if not ctx:
            raise MissingTenantContextError(
                f"No tenant context for access to {table_name}"
            )

        if ctx.is_super_admin:
            return True

        if target_tenant_id and target_tenant_id != ctx.tenant_id:
            # Log audit event (EPIC 1)
            self._log_cross_tenant_attempt(
                ctx.tenant_id,
                target_tenant_id,
                table_name,
            )
            raise CrossTenantQueryError(target_tenant_id, ctx.tenant_id)

        return True

    def _get_current_tenant_id(self) -> str:
        """Obtiene tenant_id del contexto actual."""
        ctx = self._context.get_context()
        if not ctx:
            raise MissingTenantContextError("No tenant context set")
        return ctx.tenant_id

    def _log_cross_tenant_attempt(
        self,
        from_tenant: str,
        to_tenant: str,
        table_name: str,
    ) -> None:
        """Log intento de acceso cross-tenant (EPIC 1)."""
        try:
            from core.PHASE_7.audit import get_audit_logger
            logger = get_audit_logger()
            if logger:
                ctx = self._context.get_context()
                logger.log_security_event(
                    actor_id=ctx.user_id if ctx else "unknown",
                    actor_name=ctx.user_id if ctx else "unknown",
                    actor_role="system",
                    event_type="CROSS_TENANT_ACCESS_ATTEMPT",
                    details={
                        "from_tenant": from_tenant,
                        "to_tenant": to_tenant,
                        "table": table_name,
                    },
                )
        except Exception:
            pass  # Don't fail on audit errors


# SQLAlchemy integration helpers

def apply_tenant_filter(query: Any, model_class: Any, tenant_id: str) -> Any:
    """
    Aplica filtro de tenant a query SQLAlchemy.
    Uso: apply_tenant_filter(query, Equipment, tenant_id)
    """
    if hasattr(model_class, "tenant_id"):
        return query.filter(model_class.tenant_id == tenant_id)
    return query


def add_tenant_id_to_insert(data: dict, tenant_id: str) -> dict:
    """Añade tenant_id a datos de INSERT."""
    return {**data, "tenant_id": tenant_id}


def assert_tenant_match(record: Any, expected_tenant_id: str) -> None:
    """Assert que registro pertenece al tenant esperado."""
    if hasattr(record, "tenant_id") and record.tenant_id != expected_tenant_id:
        raise CrossTenantQueryError(record.tenant_id, expected_tenant_id)
