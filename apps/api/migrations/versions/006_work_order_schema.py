"""Create work_order schema — work_orders.

Revision ID: 006
Revises: 005
Create Date: 2026-07-16

Tables:
- work_order.work_orders
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "006"
down_revision = "005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute('CREATE SCHEMA IF NOT EXISTS "work_order"')

    # ── work_orders ────────────────────────────────────────────────────────────
    op.create_table(
        "work_orders",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("device_id", sa.UUID(), nullable=False),
        sa.Column("work_order_type", sa.String(20), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("resolution_summary", sa.Text(), nullable=True),
        sa.Column("cancellation_reason", sa.Text(), nullable=True),
        sa.Column("priority", sa.String(20), nullable=False, server_default="medium"),
        sa.Column("status", sa.String(30), nullable=False, server_default="draft"),
        sa.Column("assigned_to", sa.String(36), nullable=True),
        sa.Column("assigned_by", sa.String(36), nullable=True),
        sa.Column("assigned_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("scheduled_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("estimated_duration_hours", sa.Float(), nullable=True),
        sa.Column("actual_labor_hours", sa.Float(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_by", sa.String(36), nullable=True),
        sa.Column("sla_deadline", sa.DateTime(timezone=True), nullable=True),
        sa.Column("sla_breached", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("on_hold_reason", sa.Text(), nullable=True),
        sa.Column("on_hold_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("incident_id", sa.UUID(), nullable=True),
        sa.Column("preventive_schedule_id", sa.String(36), nullable=True),
        sa.Column("parts_used", sa.JSON(), nullable=True),
        sa.Column("next_calibration_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("created_by", sa.String(36), nullable=True),
        sa.Column("cancelled_by", sa.String(36), nullable=True),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.PrimaryKeyConstraint("id"),
        schema="work_order",
    )

    # Indexes
    op.create_index("ix_work_orders_tenant_id", "work_orders", ["tenant_id"], schema="work_order")
    op.create_index("ix_work_orders_device_id", "work_orders", ["device_id"], schema="work_order")
    op.create_index("ix_work_orders_status", "work_orders", ["status"], schema="work_order")
    op.create_index("ix_work_orders_priority", "work_orders", ["priority"], schema="work_order")
    op.create_index("ix_work_orders_assigned_to", "work_orders", ["assigned_to"], schema="work_order")
    op.create_index("ix_work_orders_sla_deadline", "work_orders", ["sla_deadline"], schema="work_order")
    op.create_index("ix_work_orders_tenant_status", "work_orders", ["tenant_id", "status"], schema="work_order")
    op.create_index("ix_work_orders_incident_id", "work_orders", ["incident_id"], schema="work_order")

    # Foreign key to device.devices
    op.create_foreign_key(
        "fk_work_orders_device_id",
        "work_orders", "devices",
        ["device_id"], ["id"],
        source_schema="work_order", referent_schema="device",
    )
    # Foreign key to incident.incidents
    op.create_foreign_key(
        "fk_work_orders_incident_id",
        "work_orders", "incidents",
        ["incident_id"], ["id"],
        source_schema="work_order", referent_schema="incident",
    )

    # PrimaryKeyConstraint for optimistic locking
    op.create_primary_key(
        "pk_work_orders",
        "work_orders",
        ["id"],
        schema="work_order",
    )


def downgrade() -> None:
    op.drop_table("work_orders", schema="work_order")
    op.execute('DROP SCHEMA IF EXISTS "work_order"')
