"""Create incident schema — incidents, investigations, evidence, actions, messages, outbox_events.

Revision ID: 002
Revises: 001
Create Date: 2026-07-16

Tables:
- incident.incidents
- incident.investigations
- incident.evidence
- incident.actions
- incident.conversation_messages
- incident.outbox_events
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── Schema ──────────────────────────────────────────────────────────────────
    op.execute('CREATE SCHEMA IF NOT EXISTS "incident"')

    # ── incidents ─────────────────────────────────────────────────────────────
    op.create_table(
        "incidents",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("device_id", sa.String(36), nullable=False),
        sa.Column("reported_by", sa.String(36), nullable=False),
        sa.Column("symptom_description", sa.Text(), nullable=False),
        sa.Column("symptom_category", sa.String(100), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("priority", sa.String(50), nullable=False),
        sa.Column("status", sa.String(50), nullable=False),
        sa.Column("safety_classification", sa.String(50), nullable=False),
        sa.Column("assigned_to", sa.String(36), nullable=True),
        sa.Column("triage_notes", sa.Text(), nullable=True),
        sa.Column("estimated_resolution_hours", sa.Integer(), nullable=True),
        sa.Column("resolution_description", sa.Text(), nullable=True),
        sa.Column("resolution_root_cause", sa.Text(), nullable=True),
        sa.Column("resolution_time_minutes", sa.Integer(), nullable=True),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("closed_by", sa.String(36), nullable=True),
        sa.Column("feedback_type", sa.String(50), nullable=True),
        sa.Column("feedback_content", sa.Text(), nullable=True),
        sa.Column("correlation_id", sa.String(36), nullable=True),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        schema="incident",
    )
    op.create_index("ix_incidents_tenant_id", "incidents", ["tenant_id"], schema="incident")
    op.create_index("ix_incidents_device_id", "incidents", ["device_id"], schema="incident")
    op.create_index("ix_incidents_status", "incidents", ["status"], schema="incident")
    op.create_index("ix_incidents_priority", "incidents", ["priority"], schema="incident")
    op.create_index("ix_incidents_assigned_to", "incidents", ["assigned_to"], schema="incident")
    op.create_index("ix_incidents_created_at", "incidents", ["created_at"], schema="incident")

    # ── investigations ─────────────────────────────────────────────────────────
    op.create_table(
        "investigations",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("incident_id", sa.UUID(), nullable=False),
        sa.Column("investigator_id", sa.String(36), nullable=False),
        sa.Column("investigator_name", sa.String(100), nullable=False),
        sa.Column("status", sa.String(50), nullable=False),
        sa.Column("findings", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["incident_id"], ["incident.incidents.id"], ondelete="CASCADE"),
        schema="incident",
    )
    op.create_index("ix_investigations_incident_id", "investigations", ["incident_id"], schema="incident")
    op.create_index("ix_investigations_status", "investigations", ["status"], schema="incident")

    # ── evidence ───────────────────────────────────────────────────────────────
    op.create_table(
        "evidence",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("investigation_id", sa.UUID(), nullable=False),
        sa.Column("evidence_type", sa.String(50), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("source", sa.String(100), nullable=True),
        sa.Column("collected_by", sa.String(36), nullable=False),
        sa.Column("collected_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("relevance", sa.String(20), nullable=False, server_default="medium"),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["investigation_id"], ["incident.investigations.id"], ondelete="CASCADE"),
        schema="incident",
    )
    op.create_index("ix_evidence_investigation_id", "evidence", ["investigation_id"], schema="incident")

    # ── actions ─────────────────────────────────────────────────────────────────
    op.create_table(
        "actions",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("investigation_id", sa.UUID(), nullable=False),
        sa.Column("action_type", sa.String(50), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("priority", sa.String(20), nullable=False),
        sa.Column("assigned_to", sa.String(36), nullable=True),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("result", sa.Text(), nullable=True),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["investigation_id"], ["incident.investigations.id"], ondelete="CASCADE"),
        schema="incident",
    )
    op.create_index("ix_actions_investigation_id", "actions", ["investigation_id"], schema="incident")
    op.create_index("ix_actions_status", "actions", ["status"], schema="incident")

    # ── conversation_messages ───────────────────────────────────────────────────
    op.create_table(
        "conversation_messages",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("investigation_id", sa.UUID(), nullable=False),
        sa.Column("sender_type", sa.String(20), nullable=False),
        sa.Column("sender_id", sa.String(36), nullable=False),
        sa.Column("sender_name", sa.String(100), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("ai_confidence", sa.Float(), nullable=True),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["investigation_id"], ["incident.investigations.id"], ondelete="CASCADE"),
        schema="incident",
    )
    op.create_index("ix_conv_investigation_id", "conversation_messages", ["investigation_id"], schema="incident")

    # ── outbox_events (Transactional Outbox) ────────────────────────────────────
    op.create_table(
        "outbox_events",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("aggregate_type", sa.String(255), nullable=False),
        sa.Column("event_type", sa.String(255), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("correlation_id", sa.String(255), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("retry_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_error", sa.String(1000), nullable=True),
        schema="incident",
    )
    op.create_index("ix_outbox_events_created_at", "outbox_events", ["created_at"], schema="incident")
    op.create_index("ix_outbox_events_status_created", "outbox_events", ["status", "created_at"], schema="incident")


def downgrade() -> None:
    op.drop_index("ix_outbox_events_status_created", table_name="outbox_events", schema="incident")
    op.drop_index("ix_outbox_events_created_at", table_name="outbox_events", schema="incident")
    op.drop_table("outbox_events", schema="incident")
    op.drop_index("ix_conv_investigation_id", table_name="conversation_messages", schema="incident")
    op.drop_table("conversation_messages", schema="incident")
    op.drop_index("ix_actions_status", table_name="actions", schema="incident")
    op.drop_index("ix_actions_investigation_id", table_name="actions", schema="incident")
    op.drop_table("actions", schema="incident")
    op.drop_index("ix_evidence_investigation_id", table_name="evidence", schema="incident")
    op.drop_table("evidence", schema="incident")
    op.drop_index("ix_investigations_status", table_name="investigations", schema="incident")
    op.drop_index("ix_investigations_incident_id", table_name="investigations", schema="incident")
    op.drop_table("investigations", schema="incident")
    op.drop_index("ix_incidents_created_at", table_name="incidents", schema="incident")
    op.drop_index("ix_incidents_assigned_to", table_name="incidents", schema="incident")
    op.drop_index("ix_incidents_priority", table_name="incidents", schema="incident")
    op.drop_index("ix_incidents_status", table_name="incidents", schema="incident")
    op.drop_index("ix_incidents_device_id", table_name="incidents", schema="incident")
    op.drop_index("ix_incidents_tenant_id", table_name="incidents", schema="incident")
    op.drop_table("incidents", schema="incident")
    op.execute('DROP SCHEMA IF EXISTS "incident" CASCADE')
