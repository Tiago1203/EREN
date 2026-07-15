"""Initial schema - patients and outbox tables.

Revision ID: 001
Revises:
Create Date: 2026-07-15
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

# revision identifiers
revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create patients table."""
    op.create_table(
        "patients",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("mrn", sa.String(50), nullable=False),
        sa.Column("given_name", sa.String(100), nullable=False),
        sa.Column("family_name", sa.String(100), nullable=False),
        sa.Column("date_of_birth", sa.DateTime(), nullable=True),
        sa.Column("gender", sa.String(20), nullable=True),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("phone", sa.String(50), nullable=True),
        sa.Column("blood_type", sa.String(10), nullable=True),
        sa.Column("allergies", sa.String(500), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default="1", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("created_by", sa.String(36), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    # Indexes
    op.create_index("ix_patients_tenant_id", "patients", ["tenant_id"])
    op.create_index("ix_patients_mrn", "patients", ["tenant_id", "mrn"], unique=True)

    # Outbox table for reliable event publishing
    op.create_table(
        "outbox",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("aggregate_type", sa.String(100), nullable=False),
        sa.Column("aggregate_id", sa.String(36), nullable=False),
        sa.Column("event_type", sa.String(100), nullable=False),
        sa.Column("payload", sa.Text(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("retry_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("max_retries", sa.Integer(), nullable=False, server_default="3"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    # Outbox indexes
    op.create_index("ix_outbox_status", "outbox", ["status"])
    op.create_index("ix_outbox_aggregate_type", "outbox", ["aggregate_type"])
    op.create_index("ix_outbox_created_at", "outbox", ["created_at"])


def downgrade() -> None:
    """Drop tables."""
    op.drop_index("ix_outbox_created_at", table_name="outbox")
    op.drop_index("ix_outbox_aggregate_type", table_name="outbox")
    op.drop_index("ix_outbox_status", table_name="outbox")
    op.drop_table("outbox")
    op.drop_index("ix_patients_mrn", table_name="patients")
    op.drop_index("ix_patients_tenant_id", table_name="patients")
    op.drop_table("patients")
