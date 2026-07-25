"""
PHASE 7 - EPIC 2: Data Isolation

Aislamiento de datos a nivel de aplicación:
- Tenant boundary enforcement
- Data access patterns
- Import/Export isolation
- GDPR data handling per tenant
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class DataBoundary:
    """Frontera de datos de un tenant."""
    tenant_id: str
    allowed_tables: list[str]
    denied_tables: list[str]
    max_export_size_mb: int = 100
    allow_gdpr_export: bool = False


class DataIsolation:
    """
    Gestor de fronteras de datos por tenant.
    Implementa el principio de mínimo privilegio.
    """

    def __init__(self, context_manager: Any):
        self._context = context_manager
        self._boundaries: dict[str, DataBoundary] = {}

    def register_boundary(self, boundary: DataBoundary) -> None:
        """Registra frontera para tenant."""
        self._boundaries[boundary.tenant_id] = boundary

    def get_boundary(self, tenant_id: Optional[str] = None) -> DataBoundary:
        """Obtiene frontera de un tenant."""
        if tenant_id is None:
            ctx = self._context.get_context()
            tenant_id = ctx.tenant_id if ctx else ""

        boundary = self._boundaries.get(tenant_id)
        if not boundary:
            # Default boundary: todas las tablas permitidas
            return DataBoundary(
                tenant_id=tenant_id,
                allowed_tables=["*"],
                denied_tables=[],
            )
        return boundary

    def can_access_table(self, table_name: str, tenant_id: Optional[str] = None) -> bool:
        """Check si tenant puede acceder a tabla."""
        boundary = self.get_boundary(tenant_id)

        if "*" in boundary.allowed_tables:
            if boundary.denied_tables and table_name in boundary.denied_tables:
                return False
            return True

        return table_name in boundary.allowed_tables

    def can_export_table(self, table_name: str, size_mb: float, tenant_id: Optional[str] = None) -> tuple[bool, str]:
        """Check si tenant puede exportar tabla."""
        boundary = self.get_boundary(tenant_id)

        if not self.can_access_table(table_name, tenant_id):
            return False, f"Access denied to table {table_name}"

        if size_mb > boundary.max_export_size_mb:
            return False, f"Export size ({size_mb}MB) exceeds limit ({boundary.max_export_size_mb}MB)"

        return True, "OK"

    def sanitize_export_data(
        self,
        table_name: str,
        data: list[dict],
        tenant_id: Optional[str] = None,
    ) -> list[dict]:
        """
        Sanitiza datos para exportación.
        Remueve columnas sensibles según GDPR y configuración.
        """
        boundary = self.get_boundary(tenant_id)

        # Columns that should be redacted in exports
        sensitive_columns = {
            "users": ["password_hash", "mfa_secret", "api_key"],
            "patients": ["ssn", "full_address", "phone"],
            "medical_records": ["raw_content"],  # Keep structured, redact raw
        }

        columns_to_redact = sensitive_columns.get(table_name, [])

        sanitized = []
        for row in data:
            clean_row = {k: v for k, v in row.items() if k not in columns_to_redact}
            # Redact tenant_id from export
            clean_row = {k: v for k, v in clean_row.items() if k != "tenant_id"}
            sanitized.append(clean_row)

        return sanitized

    def validate_import(
        self,
        table_name: str,
        data: list[dict],
        tenant_id: Optional[str] = None,
    ) -> tuple[bool, list[str]]:
        """Valida datos antes de importar."""
        errors: list[str] = []

        ctx = self._context.get_context()
        effective_tenant = tenant_id or (ctx.tenant_id if ctx else "")

        if not self.can_access_table(table_name, effective_tenant):
            errors.append(f"Cannot import to table {table_name}: access denied")
            return False, errors

        # Verify all records don't have conflicting tenant_id
        for i, record in enumerate(data):
            record_tenant = record.get("tenant_id")
            if record_tenant and record_tenant != effective_tenant:
                errors.append(
                    f"Row {i}: tenant_id mismatch "
                    f"(got {record_tenant}, expected {effective_tenant})"
                )

        # GDPR: warn about personal data imports
        if table_name in ("patients", "users", "medical_records"):
            errors.append(
                f"GDPR WARNING: Importing {len(data)} records to {table_name} "
                "may contain personal data. Ensure DPA covers this import."
            )

        return len(errors) == 0 or all("GDPR WARNING" in e for e in errors), errors

    def get_isolation_report(self, tenant_id: Optional[str] = None) -> dict:
        """Genera reporte de aislamiento."""
        boundary = self.get_boundary(tenant_id)
        return {
            "tenant_id": boundary.tenant_id,
            "allowed_tables": boundary.allowed_tables,
            "denied_tables": boundary.denied_tables,
            "max_export_mb": boundary.max_export_size_mb,
            "gdpr_export": boundary.allow_gdpr_export,
        }
