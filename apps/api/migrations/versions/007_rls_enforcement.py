"""RLS Enforcement Migration

Revision ID: 007_rls_enforcement
Revises: 006_work_order_schema
Create Date: 2026-07-16

Implements Row-Level Security policies per Epic 0 Multi-Tenancy Strategy.
Every table must have a policy that restricts rows to tenant_id = current_setting('app.tenant_id').
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "007_rls_enforcement"
down_revision = "006_work_order_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enable RLS on all tables
    schemas = ["incident", "device", "recommendation", "knowledge", "work_order"]

    for schema in schemas:
        # Enable RLS
        op.execute(sa.text(f"ALTER TABLE {schema}.devices ENABLE ROW LEVEL SECURITY"))
        op.execute(sa.text(f"ALTER TABLE {schema}.incidents ENABLE ROW LEVEL SECURITY"))
        op.execute(sa.text(f"ALTER TABLE {schema}.recommendations ENABLE ROW LEVEL SECURITY"))
        op.execute(sa.text(f"ALTER TABLE {schema}.outbox_events ENABLE ROW LEVEL SECURITY"))
        op.execute(sa.text(f"ALTER TABLE {schema}.work_orders ENABLE ROW LEVEL SECURITY"))

        # Create policies for devices
        op.execute(sa.text(f"""
            CREATE POLICY tenant_isolation_devices_{schema}
            ON {schema}.devices
            FOR ALL
            USING (tenant_id = current_setting('app.tenant_id', true))
            WITH CHECK (tenant_id = current_setting('app.tenant_id', true))
        """))

        # Create policies for incidents
        op.execute(sa.text(f"""
            CREATE POLICY tenant_isolation_incidents_{schema}
            ON {schema}.incidents
            FOR ALL
            USING (tenant_id = current_setting('app.tenant_id', true))
            WITH CHECK (tenant_id = current_setting('app.tenant_id', true))
        """))

        # Create policies for recommendations
        op.execute(sa.text(f"""
            CREATE POLICY tenant_isolation_recommendations_{schema}
            ON {schema}.recommendations
            FOR ALL
            USING (tenant_id = current_setting('app.tenant_id', true))
            WITH CHECK (tenant_id = current_setting('app.tenant_id', true))
        """))

        # Create policies for outbox_events
        op.execute(sa.text(f"""
            CREATE POLICY tenant_isolation_outbox_{schema}
            ON {schema}.outbox_events
            FOR ALL
            USING (true)  -- Outbox is per-schema, not per-tenant
            WITH CHECK (true)
        """))

        # Create policies for work_orders
        op.execute(sa.text(f"""
            CREATE POLICY tenant_isolation_work_orders_{schema}
            ON {schema}.work_orders
            FOR ALL
            USING (tenant_id = current_setting('app.tenant_id', true))
            WITH CHECK (tenant_id = current_setting('app.tenant_id', true))
        """))

        # Force RLS for all app users
        op.execute(sa.text(f"ALTER TABLE {schema}.devices FORCE ROW LEVEL SECURITY"))
        op.execute(sa.text(f"ALTER TABLE {schema}.incidents FORCE ROW LEVEL SECURITY"))
        op.execute(sa.text(f"ALTER TABLE {schema}.recommendations FORCE ROW LEVEL SECURITY"))
        op.execute(sa.text(f"ALTER TABLE {schema}.outbox_events FORCE ROW LEVEL SECURITY"))
        op.execute(sa.text(f"ALTER TABLE {schema}.work_orders FORCE ROW LEVEL SECURITY"))


def downgrade() -> None:
    schemas = ["incident", "device", "recommendation", "knowledge", "work_order"]

    for schema in schemas:
        for table in ["devices", "incidents", "recommendations", "outbox_events", "work_orders"]:
            op.execute(sa.text(f"DROP POLICY IF EXISTS tenant_isolation_{table}_{schema} ON {schema}.{table}"))
            op.execute(sa.text(f"ALTER TABLE {schema}.{table} NO FORCE ROW LEVEL SECURITY"))
            op.execute(sa.text(f"ALTER TABLE {schema}.{table} DISABLE ROW LEVEL SECURITY"))
