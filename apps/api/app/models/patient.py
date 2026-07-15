"""Patient model.

Represents a patient in the Clinical Domain.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base

if TYPE_CHECKING:
    pass


class Patient(Base):
    """Patient aggregate root.

    A Patient is an individual who receives healthcare services.
    """

    __tablename__ = "patients"
    __table_args__ = (
        Index("ix_patients_tenant_id", "tenant_id"),
        Index("ix_patients_mrn", "tenant_id", "mrn", unique=True),
    )

    # Primary key
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        comment="UUID v7 for time-ordered IDs",
    )

    # Tenant isolation (multi-tenancy)
    tenant_id: Mapped[str] = mapped_column(
        String(36),
        nullable=False,
        index=True,
        comment="Hospital/organization identifier",
    )

    # Patient identifier
    mrn: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Medical Record Number",
    )

    # Demographics
    given_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Patient given/first name",
    )
    family_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Patient family/last name",
    )
    date_of_birth: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        comment="Date of birth",
    )
    gender: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        comment="Gender (use controlled vocabulary in production)",
    )

    # Contact
    email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="Contact email",
    )
    phone: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="Contact phone",
    )

    # Medical
    blood_type: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True,
        comment="Blood type (A+, O-, etc.)",
    )
    allergies: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        comment="Known allergies (comma-separated in MVP)",
    )

    # Status
    is_active: Mapped[bool] = mapped_column(
        default=True,
        comment="Is patient currently active",
    )

    # Metadata
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        comment="Record creation timestamp",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        comment="Last update timestamp",
    )
    created_by: Mapped[str | None] = mapped_column(
        String(36),
        nullable=True,
        comment="Principal ID who created this record",
    )
