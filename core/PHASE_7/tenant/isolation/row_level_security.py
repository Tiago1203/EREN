"""
PHASE 7 - EPIC 2: Row-Level Security

PostgreSQL RLS policies:
- Automatic tenant filtering
- RLS policy generation
- Enforcement hooks
- Audit integration (EPIC 1)
"""

from __future__ import annotations

from dataclasses import dataclass, field

from dataclasses import dataclass
from typing import Optional


@dataclass
class RLSPolicy:
    """Política RLS."""
    table_name: str
    policy_name: str
    cmd: str                    # SELECT, INSERT, UPDATE, DELETE, ALL
    qual: str                  # USING expression
    with_check: str = ""       # WITH CHECK expression
    roles: list[str] = field(default_factory=list)

    def to_sql(self) -> str:
        """Genera SQL de CREATE POLICY."""
        with_check_sql = f"WITH CHECK ({self.with_check})" if self.with_check else ""
        roles_sql = ""
        if self.roles:
            roles_sql = f"FOR {self.roles[0]}" if len(self.roles) == 1 else ""

        return f"""
CREATE POLICY {self.policy_name} ON {self.table_name}
    FOR {self.cmd}
    USING ({self.qual})
    {with_check_sql};
""".strip()


class RowLevelSecurityManager:
    """Gestor de políticas RLS para multi-tenant."""

    # Tablas que requieren RLS
    PROTECTED_TABLES = [
        "users",
        "establishments",
        "departments",
        "equipment",
        "patients",
        "medical_records",
        "maintenances",
        "kpis",
        "reports",
        "notifications",
        "audit_logs",
    ]

    def __init__(self, schema: str = "public"):
        self._schema = schema
        self._policies: dict[str, list[RLSPolicy]] = {}

    def get_tenant_policy(
        self,
        table_name: str,
        tenant_column: str = "tenant_id",
    ) -> RLSPolicy:
        """Genera política de aislamiento por tenant."""
        return RLSPolicy(
            table_name=table_name,
            policy_name=f"{table_name}_tenant_isolation",
            cmd="ALL",
            qual=f"tenant_id = current_setting('app.current_tenant', true)::text",
            with_check=f"tenant_id = current_setting('app.current_tenant', true)::text",
        )

    def get_select_policy(
        self,
        table_name: str,
        tenant_column: str = "tenant_id",
    ) -> RLSPolicy:
        """Política SELECT por tenant."""
        return RLSPolicy(
            table_name=table_name,
            policy_name=f"{table_name}_tenant_select",
            cmd="SELECT",
            qual=f"tenant_id = current_setting('app.current_tenant', true)::text",
        )

    def get_insert_policy(
        self,
        table_name: str,
        tenant_column: str = "tenant_id",
    ) -> RLSPolicy:
        """Política INSERT por tenant."""
        return RLSPolicy(
            table_name=table_name,
            policy_name=f"{table_name}_tenant_insert",
            cmd="INSERT",
            qual="true",
            with_check=f"tenant_id = current_setting('app.current_tenant', true)::text",
        )

    def generate_all_policies(
        self,
        table_name: str,
        tenant_column: str = "tenant_id",
    ) -> list[RLSPolicy]:
        """Genera todas las políticas RLS para una tabla."""
        return [
            self.get_tenant_policy(table_name, tenant_column),
            self.get_select_policy(table_name, tenant_column),
            self.get_insert_policy(table_name, tenant_column),
        ]

    def generate_enable_rls_sql(self, table_name: str) -> str:
        """Genera SQL para habilitar RLS en tabla."""
        return f"""
ALTER TABLE {self._schema}.{table_name} ENABLE ROW LEVEL SECURITY;
ALTER TABLE {self._schema}.{table_name} FORCE ROW LEVEL SECURITY;
""".strip()

    def generate_set_tenant_sql(self, tenant_id: str) -> str:
        """Genera SQL para establecer tenant actual."""
        return f"SET app.current_tenant = '{tenant_id}';"

    def generate_transaction_wrapper(
        self,
        tenant_id: str,
        sql_statements: list[str],
    ) -> str:
        """Genera transacción con SET de tenant."""
        tenant_sql = self.generate_set_tenant_sql(tenant_id)
        stmts = "\n".join(sql_statements)
        return f"""
BEGIN;
{tenant_sql}
SET LOCAL app.current_tenant = '{tenant_id}';
{stmts}
COMMIT;
""".strip()

    def validate_policy(self, policy: RLSPolicy) -> tuple[bool, list[str]]:
        """Valida que una política no tenga bypass peligroso."""
        warnings = []

        # Check for dangerous patterns
        if "1=1" in policy.qual or "true" == policy.qual.strip().lower():
            warnings.append(f"Policy {policy.policy_name} has no tenant filter (qual)")

        if "1=1" in policy.with_check:
            warnings.append(f"Policy {policy.policy_name} has no WITH CHECK constraint")

        # RLS bypass risk
        if "pg_has_role" in policy.qual and "superuser" in policy.qual:
            warnings.append(f"Policy {policy.policy_name} may allow superuser bypass")

        return len(warnings) == 0, warnings

    def get_protected_tables(self) -> list[str]:
        """Lista tablas que requieren RLS."""
        return self.PROTECTED_TABLES.copy()
