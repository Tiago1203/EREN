"""SQLAlchemy models for the Knowledge bounded context."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, ClassVar

from sqlalchemy import (
    JSON,
    DateTime,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class KnowledgeArticleModel(Base):
    """SQLAlchemy model for KnowledgeArticle aggregate root."""

    __tablename__ = "knowledge_articles"
    __table_args__ = (
        Index("ix_ka_tenant_id", "tenant_id"),
        Index("ix_ka_article_id", "article_id"),
        Index("ix_ka_status", "status"),
        Index("ix_ka_category", "category"),
        Index("ix_ka_created_at", "created_at"),
        {"schema": "knowledge"},
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False)

    # Human-readable ID
    article_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    # Content
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)

    # Classification
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="draft")

    # Authorship
    author_id: Mapped[str] = mapped_column(String(36), nullable=False)
    author_name: Mapped[str] = mapped_column(String(255), nullable=False)

    # Publication
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Review
    review_comments: Mapped[str | None] = mapped_column(Text, nullable=True)
    reviewed_by: Mapped[str | None] = mapped_column(String(36), nullable=True)

    # Statistics
    view_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    helpful_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    not_helpful_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_accessed: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Version for optimistic locking
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # Audit
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # SQLAlchemy optimistic locking — auto-increments version on UPDATE
    __mapper_args__: ClassVar[dict[str, Any]] = {"version_id_col": version}

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
            "tenant_id": self.tenant_id,
            "article_id": self.article_id,
            "title": self.title,
            "summary": self.summary,
            "body": self.body,
            "tags": self.tags,
            "category": self.category,
            "status": self.status,
            "author_id": self.author_id,
            "author_name": self.author_name,
            "published_at": (self.published_at.isoformat() if self.published_at else None),
            "review_comments": self.review_comments,
            "reviewed_by": self.reviewed_by,
            "view_count": self.view_count,
            "helpful_count": self.helpful_count,
            "not_helpful_count": self.not_helpful_count,
            "last_accessed": self.last_accessed,
            "version": self.version,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class DomainEventModel(Base):
    """SQLAlchemy model for storing domain events (event sourcing)."""

    __tablename__ = "domain_events"
    __table_args__ = (
        Index("ix_de_aggregate_id", "aggregate_id"),
        Index("ix_de_aggregate_type", "aggregate_type"),
        Index("ix_de_event_type", "event_type"),
        Index("ix_de_occurred_at", "occurred_at"),
        {"schema": "knowledge"},
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    aggregate_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    aggregate_type: Mapped[str] = mapped_column(String(255), nullable=False)
    event_type: Mapped[str] = mapped_column(String(255), nullable=False)
    event_data: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    event_metadata: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
