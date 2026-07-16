"""Create device schema — devices and status_history.

Revision ID: 003
Revises: 002
Create Date: 2026-07-16

Tables:
- device.devices
- device.status_history
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute('CREATE SCHEMA IF NOT EXISTS "device"')

    # ── devices ─────────────────────────────────────────────────────────────────
    op.create_table(
        "devices",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("device_id", sa.String(36), nullable=False),
        sa.Column("serial_number", sa.String(100), nullable=False),
        sa.Column("manufacturer_name", sa.String(200), nullable=True),
        sa.Column("manufacturer_model", sa.String(100), nullable=True),
        sa.Column("manufacturer_country", sa.String(100), nullable=True),
        sa.Column("device_type", sa.String(50), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_critical", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("status", sa.String(50), nullable=False),
        sa.Column("location_building", sa.String(100), nullable=True),
        sa.Column("location_floor", sa.String(20), nullable=True),
        sa.Column("location_room", sa.String(50), nullable=True),
        sa.Column("location_department", sa.String(100), nullable=True),
        sa.Column("calibration_last", sa.DateTime(timezone=True), nullable=True),
        sa.Column("calibration_next", sa.DateTime(timezone=True), nullable=True),
        sa.Column("calibration_interval_days", sa.Integer(), nullable=True),
        sa.Column("maintenance_interval_days", sa.Integer(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("registered_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("registered_by", sa.String(36), nullable=False),
        sa.Column("last_status_change", sa.DateTime(timezone=True), nullable=True),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
        schema="device",
    )
    op.create_index("ix_devices_tenant_id", "devices", ["tenant_id"], schema="device")
    op.create_index("ix_devices_device_id", "devices", ["device_id"], schema="device")
    op.create_index("ix_devices_serial_number", "devices", ["serial_number"], schema="device")
    op.create_index("ix_devices_status", "devices", ["status"], schema="device")
    op.create_index("ix_devices_device_type", "devices", ["device_type"], schema="device")
    op.create_index("ix_devices_location_department", "devices", ["location_department"], schema="device")
    op.create_index("ix_devices_created_at", "devices", ["created_at"], schema="device")

    # ── status_history ─────────────────────────────────────────────────────────
    op.create_table(
        "status_history",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("device_id", sa.UUID(), nullable=False),
        sa.Column("from_status", sa.String(50), nullable=True),
        sa.Column("to_status", sa.String(50), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("changed_by", sa.String(36), nullable=False),
        sa.Column("changed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["device_id"], ["device.devices.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        schema="device",
    )
    op.create_index("ix_status_history_device_id", "status_history", ["device_id"], schema="device")
    op.create_index("ix_status_history_changed_at", "status_history", ["changed_at"], schema="device")


def downgrade() -> None:
    op.drop_index("ix_status_history_changed_at", table_name="status_history", schema="device")
    op.drop_index("ix_status_history_device_id", table_name="status_history", schema="device")
    op.drop_table("status_history", schema="device")
    op.drop_index("ix_devices_created_at", table_name="devices", schema="device")
    op.drop_index("ix_devices_location_department", table_name="devices", schema="device")
    op.drop_index("ix_devices_device_type", table_name="devices", schema="device")
    op.drop_index("ix_devices_status", table_name="devices", schema="device")
    op.drop_index("ix_devices_serial_number", table_name="devices", schema="device")
    op.drop_index("ix_devices_device_id", table_name="devices", schema="device")
    op.drop_index("ix_devices_tenant_id", table_name="devices", schema="device")
    op.drop_table("devices", schema="device")
    op.execute('DROP SCHEMA IF EXISTS "device" CASCADE')
