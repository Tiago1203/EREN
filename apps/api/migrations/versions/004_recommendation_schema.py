"""Create recommendation schema — recommendations.

Revision ID: 004
Revises: 003
Create Date: 2026-07-16

Tables:
- recommendation.recommendations
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute('CREATE SCHEMA IF NOT EXISTS "recommendation"')

    op.create_table(
        "recommendations",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("incident_id", sa.String(36), nullable=False),
        sa.Column("device_id", sa.String(36), nullable=True),
        sa.Column("recommendation_type", sa.String(50), nullable=False),
        sa.Column("priority", sa.String(20), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("rationale", sa.Text(), nullable=True),
        sa.Column("expected_outcome", sa.Text(), nullable=True),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("confidence_score", sa.Float(), nullable=True),
        sa.Column("model_name", sa.String(100), nullable=True),
        sa.Column("model_version", sa.String(100), nullable=False),
        sa.Column("risk_level", sa.String(20), nullable=True),
        sa.Column("risk_factors", sa.JSON(), nullable=True),
        sa.Column("contraindications", sa.JSON(), nullable=True),
        sa.Column("applied_by", sa.String(36), nullable=True),
        sa.Column("applied_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("effectiveness_rating", sa.Integer(), nullable=True),
        sa.Column("superseded_by", sa.String(36), nullable=True),
        sa.Column("supersedes", sa.ARRAY(sa.String), nullable=True),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        schema="recommendation",
    )
    op.create_index("ix_recommendations_tenant_id", "recommendations", ["tenant_id"], schema="recommendation")
    op.create_index("ix_recommendations_incident_id", "recommendations", ["incident_id"], schema="recommendation")
    op.create_index("ix_recommendations_device_id", "recommendations", ["device_id"], schema="recommendation")
    op.create_index("ix_recommendations_status", "recommendations", ["status"], schema="recommendation")
    op.create_index("ix_recommendations_priority", "recommendations", ["priority"], schema="recommendation")
    op.create_index("ix_recommendations_type", "recommendations", ["recommendation_type"], schema="recommendation")
    op.create_index("ix_recommendations_confidence", "recommendations", ["confidence_score"], schema="recommendation")
    op.create_index("ix_recommendations_created_at", "recommendations", ["created_at"], schema="recommendation")


def downgrade() -> None:
    op.drop_index("ix_recommendations_created_at", table_name="recommendations", schema="recommendation")
    op.drop_index("ix_recommendations_confidence", table_name="recommendations", schema="recommendation")
    op.drop_index("ix_recommendations_type", table_name="recommendations", schema="recommendation")
    op.drop_index("ix_recommendations_priority", table_name="recommendations", schema="recommendation")
    op.drop_index("ix_recommendations_status", table_name="recommendations", schema="recommendation")
    op.drop_index("ix_recommendations_device_id", table_name="recommendations", schema="recommendation")
    op.drop_index("ix_recommendations_incident_id", table_name="recommendations", schema="recommendation")
    op.drop_index("ix_recommendations_tenant_id", table_name="recommendations", schema="recommendation")
    op.drop_table("recommendations", schema="recommendation")
    op.execute('DROP SCHEMA IF EXISTS "recommendation" CASCADE')
