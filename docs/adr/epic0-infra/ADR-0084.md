# ADR-0084: Row-Level Security in Alembic Migrations

**Status:** ACCEPTED

**Date:** 2026-07-16

**Deciders:** Architecture Board

---

## Context

EREN is a multi-tenant SaaS application. Every table in PostgreSQL must enforce tenant isolation at the database level — not just at the application layer.

Epic 0 (`EREN_MULTITENANCY_STRATEGY.md`) defines the strategy:
> "Shared DB + tenant_id in all tables + RLS (PostgreSQL Row-Level Security) + Application enforcement"

The gap: **how do we implement RLS in Alembic migrations?**

We evaluated:
1. **Alembic migrations with inline RLS** — RLS policies created via Alembic
2. **Application-level enforcement only** — No RLS, only application checks
3. **Separate schema per tenant** — One schema per tenant (rejected in Epic 0 strategy)

---

## Decision

**We will implement Row-Level Security in Alembic migrations.**

Every Alembic migration that creates or modifies a table will:
1. Add `tenant_id UUID NOT NULL` column (if not already present)
2. Create a default value for new records
3. Create RLS policies for SELECT, INSERT, UPDATE, DELETE
4. Enable RLS on the table

A shared Alembic helper library (`eren.migration.rls`) will provide standard migration functions.

---

## Reasons

### RLS + Alembic (Chosen)

1. **Defense in depth:** RLS is a database-level guarantee. Even if application code has a bug, cross-tenant access is impossible at the DB level
2. **HIPAA compliance:** Audit requirements benefit from DB-enforced isolation
3. **Standard migration:** All tenant enforcement is version-controlled in Alembic — reproducible, reviewable
4. **Shared library:** DRY principle — one standard implementation across all bounded contexts
5. **Epic 0 alignment:** `EREN_MULTITENANCY_STRATEGY.md` explicitly calls for RLS

### Application-Level Only (Rejected)

- Single point of failure: if any query forgets the tenant filter, cross-tenant data leaks
- Security risk: human error in application code
- No DB-level audit trail for cross-tenant access attempts

### Separate Schema Per Tenant (Rejected)

- Already rejected in Epic 0 strategy (too many schemas, migration overhead)
- Not considered further

---

## Consequences

### Positive

- Database guarantees tenant isolation — application bugs cannot cause cross-tenant leaks
- All RLS policies version-controlled in Alembic
- Reproducible environment setup
- Consistent enforcement across all bounded contexts

### Negative

- **Migration complexity:** Every migration must call RLS helpers
- **Testing:** RLS policies must be tested in migrations (integration tests)
- **Performance:** Minimal overhead per query (RLS is evaluated per-row, negligible)
- **Superuser bypass:** PostgreSQL superusers bypass RLS — must not use superuser for application connections

### Mitigations

- Shared Alembic helper library (DRY, reduces chance of errors)
- Linting: `alembic-guardrails` checks that migrations include RLS setup
- CI: Integration tests verify RLS enforcement
- Application connections use unprivileged user (not postgres superuser)

---

## Implementation

### 1. RLS Helper Library

```python
# eren/migration/rls.py

def enable_rls(table_name: str) -> list[str]:
    """Returns SQL statements to enable RLS on a table."""
    return [
        # Enable RLS
        f"ALTER TABLE {table_name} ENABLE ROW LEVEL SECURITY;",
        # Force RLS even for owners
        f"ALTER TABLE {table_name} FORCE ROW LEVEL SECURITY;",
    ]

def create_tenant_policy(
    table_name: str,
    role: str = "app_user",
) -> list[str]:
    """Creates RLS policies for a tenant-scoped table."""
    return [
        # SELECT: Can only see rows where tenant_id matches session variable
        f"""
        CREATE POLICY tenant_select_{table_name} ON {table_name}
        FOR SELECT
        USING (tenant_id = current_setting('app.tenant_id', true)::uuid);
        """,
        # INSERT: Must set tenant_id (or use default)
        f"""
        CREATE POLICY tenant_insert_{table_name} ON {table_name}
        FOR INSERT
        WITH CHECK (tenant_id = current_setting('app.tenant_id', true)::uuid);
        """,
        # UPDATE: Can only update rows in own tenant
        f"""
        CREATE POLICY tenant_update_{table_name} ON {table_name}
        FOR UPDATE
        USING (tenant_id = current_setting('app.tenant_id', true)::uuid)
        WITH CHECK (tenant_id = current_setting('app.tenant_id', true)::uuid);
        """,
        # DELETE: Can only delete rows in own tenant
        f"""
        CREATE POLICY tenant_delete_{table_name} ON {table_name}
        FOR DELETE
        USING (tenant_id = current_setting('app.tenant_id', true)::uuid);
        """,
    ]

def add_tenant_column(
    table_name: str,
    column_name: str = "tenant_id",
    with_default: bool = True,
) -> list[str]:
    """Returns SQL to add tenant_id column with index."""
    stmts = [
        f"""
        ALTER TABLE {table_name}
        ADD COLUMN IF NOT EXISTS {column_name} UUID NOT NULL
        {"DEFAULT current_setting('app.tenant_id', true)::uuid" if with_default else ""};
        """,
    ]
    # Index on tenant_id for performance
    stmts.append(
        f"CREATE INDEX IF NOT EXISTS idx_{table_name}_tenant "
        f"ON {table_name}({column_name});"
    )
    return stmts
```

### 2. Alembic Migration Template

```python
# alembic/versions/2026_07_16_create_incidents.py

from alembic import op
from eren.migration.rls import enable_rls, create_tenant_policy, add_tenant_column

revision = "abc123"
down_revision = "previous_revision"
migration_script = True

def upgrade():
    # 1. Create table
    op.execute("""
        CREATE TABLE incidents (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            device_id UUID NOT NULL,
            priority VARCHAR(20) NOT NULL,
            description TEXT,
            status VARCHAR(20) NOT NULL DEFAULT 'open',
            occurred_at TIMESTAMPTZ NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ,
            deleted_at TIMESTAMPTZ,
            tenant_id UUID NOT NULL
        );
    """)

    # 2. Add tenant_id column (with index)
    # Note: column already in CREATE TABLE above

    # 3. Add indexes
    op.execute("""
        CREATE INDEX idx_incidents_tenant_id ON incidents(tenant_id);
        CREATE INDEX idx_incidents_device_id ON incidents(device_id);
        CREATE INDEX idx_incidents_status ON incidents(status);
    """)

    # 4. Enable RLS
    for stmt in enable_rls("incidents"):
        op.execute(stmt)

    # 5. Create RLS policies
    for stmt in create_tenant_policy("incidents", "app_user"):
        op.execute(stmt)


def downgrade():
    op.execute("DROP TABLE IF EXISTS incidents CASCADE")
```

### 3. Application: Setting Tenant Context

```python
# eren/infrastructure/database.py
from contextvars import ContextVar
from uuid import UUID

_current_tenant_id: ContextVar[UUID | None] = ContextVar("tenant_id", default=None)

async def set_tenant_context(conn, tenant_id: UUID):
    """Sets the tenant context for all queries on this connection."""
    await conn.execute(
        f"SET LOCAL app.tenant_id = '{tenant_id}'"
    )

async def get_connection() -> asyncpg.Connection:
    conn = await asyncpg.connect(
        host=settings.POSTGRES_HOST,
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        database=settings.POSTGRES_DB,
    )
    return conn

class TenantUnitOfWork:
    def __init__(self, tenant_id: UUID):
        self.tenant_id = tenant_id

    async def __aenter__(self):
        self._conn = await get_connection()
        await set_tenant_context(self._conn, self.tenant_id)
        self._transaction = self._conn.transaction()
        await self._transaction.start()
        return self

    async def commit(self):
        await self._transaction.commit()

    async def rollback(self):
        await self._transaction.rollback()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._conn:
            await self._conn.close()
```

### 4. FastAPI Dependency

```python
# eren/api/dependencies.py
from fastapi import Depends, HTTPException
from uuid import UUID

async def get_current_tenant(
    security_token: str = Depends(get_security_token),
) -> UUID:
    """Extracts tenant_id from the security token."""
    payload = verify_jwt(security_token)
    tenant_id = payload.get("tenant_id")
    if not tenant_id:
        raise HTTPException(403, "Missing tenant context")
    return UUID(tenant_id)

# Usage in routes
@router.post("/incidents")
async def create_incident(
    incident: IncidentCreate,
    tenant_id: UUID = Depends(get_current_tenant),
    uow: TenantUnitOfWork = Depends(get_uow),
):
    async with uow:
        result = await uow.incidents.create(incident)
        await uow.commit()
        return result
```

### 5. RLS Testing (Integration Test)

```python
# tests/integration/test_rls.py
import pytest
import asyncpg

async def test_rls_blocks_cross_tenant_access():
    tenant_a_conn = await asyncpg.connect(DSN)
    tenant_b_conn = await asyncpg.connect(DSN)

    try:
        # Tenant A creates an incident
        await tenant_a_conn.execute("SET app.tenant_id = $1", TENANT_A_ID)
        incident_id = await tenant_a_conn.fetchval("""
            INSERT INTO incidents (device_id, priority, tenant_id)
            VALUES ($1, 'high', $2) RETURNING id
        """, DEVICE_ID, TENANT_A_ID)

        # Tenant B cannot see Tenant A's incident
        await tenant_b_conn.execute("SET app.tenant_id = $1", TENANT_B_ID)
        result = await tenant_b_conn.fetchrow(
            "SELECT * FROM incidents WHERE id = $1", incident_id
        )
        assert result is None  # RLS blocks access ✓

        # Tenant B gets zero rows (not an error)
        all_incidents = await tenant_b_conn.fetch("SELECT * FROM incidents")
        assert len(all_incidents) == 0  # Only sees own tenant ✓

    finally:
        await tenant_a_conn.close()
        await tenant_b_conn.close()
```

---

## Alembic Configuration

```ini
# alembic.ini
[post_write_hooks]
# Lint: Check that migrations include RLS setup
hooks = ruff
ruff.type = console_scripts
ruff.entrypoint = eren-alembic-check

# eren-alembic-check: custom script that validates migration
# Exits non-zero if a table is created without RLS
```

---

## Superuser Restriction

```python
# Database connection — NEVER use postgres superuser
async def create_app_user():
    """Creates the app_user role that all application connections use."""
    await conn.execute("""
        CREATE ROLE app_user NOLOGIN;
        GRANT CONNECT ON DATABASE eren TO app_user;
        GRANT USAGE ON SCHEMA public TO app_user;
    """)

    # app_user cannot bypass RLS
    await conn.execute("""
        ALTER ROLE app_user NOBYPASSRLS;
    """)
```

---

*Architecture Board - 2026-07-16*
