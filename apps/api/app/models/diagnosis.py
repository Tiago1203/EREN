"""Diagnosis model.

Represents a diagnosis in the Clinical Domain.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Index, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base

if TYPE_CHECKING:
    pass


class Diagnosis(Base):
    """Diagnosis aggregate root.

    A Diagnosis is a clinical judgment documented about a patient's condition.
    """

    __tablename__ = "diagnoses"
    __table_args__ = (
        # ix_diagnoses_tenant_id and ix_diagnoses_patient_id are created by
        # mapped_column(index=True) on those columns — do NOT duplicate here.
        Index(
            "ix_diagnoses_patient_code",
            "patient_id",
            "diagnosis_code",
            unique=True,
        ),
    )

    # Primary key
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        comment="UUID for entity identification",
    )

    # Tenant isolation (multi-tenancy)
    tenant_id: Mapped[str] = mapped_column(
        String(36),
        nullable=False,
        index=True,
        comment="Hospital/organization identifier",
    )

    # Identity relationship (NOT dependency)
    patient_id: Mapped[str] = mapped_column(
        String(36),
        nullable=False,
        index=True,
        comment="Reference to patient (identity only, not dependency)",
    )

    # Clinical information
    diagnosis_code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Diagnosis code (ICD-10 or other standard)",
    )
    diagnosis_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Descriptive name of diagnosis",
    )
    description: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
        comment="Additional clinical notes",
    )

    # Optimistic locking
    version: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
        comment="Version for optimistic locking",
    )

    # Soft delete (replaces is_active)
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Timestamp when diagnosis was deleted",
    )
    deleted_by: Mapped[str | None] = mapped_column(
        String(36),
        nullable=True,
        comment="Principal ID who deleted this record",
    )
    delete_reason: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        comment="Reason for deletion",
    )

    # Metadata
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        comment="When the diagnosis was recorded",
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

    @property
    def is_deleted(self) -> bool:
        """Check if diagnosis is soft-deleted."""
        return self.deleted_at is not None

    @classmethod
    def create(
        cls,
        diagnosis_id: str,
        tenant_id: str,
        patient_id: str,
        diagnosis_code: str,
        diagnosis_name: str,
        created_by: str | None = None,
        description: str | None = None,
    ) -> Diagnosis:
        """Factory method to create a new diagnosis.

        This is the preferred way to create diagnoses,
        as it ensures all required fields are set.
        """
        return cls(
            id=diagnosis_id,
            tenant_id=tenant_id,
            patient_id=patient_id,
            diagnosis_code=diagnosis_code,
            diagnosis_name=diagnosis_name,
            created_by=created_by,
            description=description,
            version=1,
        )
