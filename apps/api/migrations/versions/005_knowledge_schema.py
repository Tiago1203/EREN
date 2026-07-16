"""Create knowledge schema — knowledge_articles and domain_events.

Revision ID: 005
Revises: 004
Create Date: 2026-07-16

Tables:
- knowledge.knowledge_articles
- knowledge.domain_events
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "005"
down_revision = "004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute('CREATE SCHEMA IF NOT EXISTS "knowledge"')

    # ── knowledge_articles ──────────────────────────────────────────────────────
    op.create_table(
        "knowledge_articles",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("article_id", sa.String(36), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("tags", sa.ARRAY(sa.String), nullable=True),
        sa.Column("category", sa.String(100), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("author_id", sa.String(36), nullable=False),
        sa.Column("author_name", sa.String(100), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("view_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("helpful_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("not_helpful_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_accessed", sa.String(50), nullable=True),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
        schema="knowledge",
    )
    op.create_index("ix_ka_tenant_id", "knowledge_articles", ["tenant_id"], schema="knowledge")
    op.create_index("ix_ka_article_id", "knowledge_articles", ["article_id"], schema="knowledge")
    op.create_index("ix_ka_status", "knowledge_articles", ["status"], schema="knowledge")
    op.create_index("ix_ka_category", "knowledge_articles", ["category"], schema="knowledge")
    op.create_index("ix_ka_author_id", "knowledge_articles", ["author_id"], schema="knowledge")
    op.create_index("ix_ka_created_at", "knowledge_articles", ["created_at"], schema="knowledge")
    op.create_index("ix_ka_view_count", "knowledge_articles", ["view_count"], schema="knowledge")

    # ── domain_events ───────────────────────────────────────────────────────────
    op.create_table(
        "domain_events",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("aggregate_id", sa.UUID(), nullable=False),
        sa.Column("aggregate_type", sa.String(255), nullable=False),
        sa.Column("event_type", sa.String(255), nullable=False),
        sa.Column("event_data", sa.JSON(), nullable=False),
        sa.Column("event_metadata", sa.JSON(), nullable=True),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.PrimaryKeyConstraint("id"),
        schema="knowledge",
    )
    op.create_index("ix_de_aggregate_id", "domain_events", ["aggregate_id"], schema="knowledge")
    op.create_index("ix_de_aggregate_type", "domain_events", ["aggregate_type"], schema="knowledge")
    op.create_index("ix_de_event_type", "domain_events", ["event_type"], schema="knowledge")
    op.create_index("ix_de_occurred_at", "domain_events", ["occurred_at"], schema="knowledge")


def downgrade() -> None:
    op.drop_index("ix_de_occurred_at", table_name="domain_events", schema="knowledge")
    op.drop_index("ix_de_event_type", table_name="domain_events", schema="knowledge")
    op.drop_index("ix_de_aggregate_type", table_name="domain_events", schema="knowledge")
    op.drop_index("ix_de_aggregate_id", table_name="domain_events", schema="knowledge")
    op.drop_table("domain_events", schema="knowledge")
    op.drop_index("ix_ka_view_count", table_name="knowledge_articles", schema="knowledge")
    op.drop_index("ix_ka_created_at", table_name="knowledge_articles", schema="knowledge")
    op.drop_index("ix_ka_author_id", table_name="knowledge_articles", schema="knowledge")
    op.drop_index("ix_ka_category", table_name="knowledge_articles", schema="knowledge")
    op.drop_index("ix_ka_status", table_name="knowledge_articles", schema="knowledge")
    op.drop_index("ix_ka_article_id", table_name="knowledge_articles", schema="knowledge")
    op.drop_index("ix_ka_tenant_id", table_name="knowledge_articles", schema="knowledge")
    op.drop_table("knowledge_articles", schema="knowledge")
    op.execute('DROP SCHEMA IF EXISTS "knowledge" CASCADE')
