"""Diagnosis repository.

Repository pattern: abstracts database access from domain.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from app.models.diagnosis import Diagnosis


class DiagnosisRepository(Protocol):
    """Protocol for diagnosis persistence operations."""

    async def save(
        self,
        tenant_id: str,
        diagnosis_id: str,
        patient_id: str,
        diagnosis_code: str,
        diagnosis_name: str,
        created_by: str | None = None,
        description: str | None = None,
        **kwargs,
    ) -> Diagnosis:
        """Save a diagnosis to the database."""
        ...

    async def get_by_id(
        self, diagnosis_id: str, tenant_id: str
    ) -> Diagnosis | None:
        """Get a diagnosis by ID within tenant (excludes deleted)."""
        ...

    async def list_by_patient(
        self, patient_id: str, tenant_id: str, page: int = 1, page_size: int = 50
    ) -> tuple[list[Diagnosis], int]:
        """List diagnoses for a patient with pagination (excludes deleted)."""
        ...

    async def list_by_tenant(
        self, tenant_id: str, page: int = 1, page_size: int = 50
    ) -> tuple[list[Diagnosis], int]:
        """List diagnoses for a tenant with pagination (excludes deleted)."""
        ...

    async def update(
        self, diagnosis: Diagnosis, expected_version: int, **updates
    ) -> Diagnosis | None:
        """Update an existing diagnosis with optimistic locking."""
        ...

    async def soft_delete(
        self,
        diagnosis_id: str,
        tenant_id: str,
        deleted_by: str | None = None,
        delete_reason: str | None = None,
    ) -> bool:
        """Soft delete a diagnosis with metadata."""
        ...


@dataclass
class SQLAlchemyDiagnosisRepository:
    """SQLAlchemy implementation of DiagnosisRepository."""

    def __init__(self, db: AsyncSession):
        self._db = db

    async def save(
        self,
        tenant_id: str,
        diagnosis_id: str,
        patient_id: str,
        diagnosis_code: str,
        diagnosis_name: str,
        created_by: str | None = None,
        description: str | None = None,
        **kwargs,
    ) -> Diagnosis:
        """Save a diagnosis to the database using factory method."""
        from app.models.diagnosis import Diagnosis

        diagnosis = Diagnosis.create(
            diagnosis_id=diagnosis_id,
            tenant_id=tenant_id,
            patient_id=patient_id,
            diagnosis_code=diagnosis_code,
            diagnosis_name=diagnosis_name,
            created_by=created_by,
            description=description,
            **kwargs,
        )
        self._db.add(diagnosis)
        await self._db.flush()
        return diagnosis

    async def get_by_id(
        self, diagnosis_id: str, tenant_id: str
    ) -> Diagnosis | None:
        """Get a diagnosis by ID within tenant (excludes deleted)."""
        from sqlalchemy import select

        from app.models.diagnosis import Diagnosis

        result = await self._db.execute(
            select(Diagnosis).where(
                Diagnosis.id == diagnosis_id,
                Diagnosis.tenant_id == tenant_id,
                Diagnosis.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def list_by_patient(
        self, patient_id: str, tenant_id: str, page: int = 1, page_size: int = 50
    ) -> tuple[list[Diagnosis], int]:
        """List diagnoses for a patient with pagination (excludes deleted)."""
        from sqlalchemy import func, select

        from app.models.diagnosis import Diagnosis

        count_result = await self._db.execute(
            select(func.count(Diagnosis.id)).where(
                Diagnosis.patient_id == patient_id,
                Diagnosis.tenant_id == tenant_id,
                Diagnosis.deleted_at.is_(None),
            )
        )
        total = count_result.scalar() or 0

        offset = (page - 1) * page_size
        result = await self._db.execute(
            select(Diagnosis)
            .where(
                Diagnosis.patient_id == patient_id,
                Diagnosis.tenant_id == tenant_id,
                Diagnosis.deleted_at.is_(None),
            )
            .order_by(Diagnosis.recorded_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        diagnoses = list(result.scalars().all())

        return diagnoses, total

    async def list_by_tenant(
        self, tenant_id: str, page: int = 1, page_size: int = 50
    ) -> tuple[list[Diagnosis], int]:
        """List diagnoses for a tenant with pagination (excludes deleted)."""
        from sqlalchemy import func, select

        from app.models.diagnosis import Diagnosis

        count_result = await self._db.execute(
            select(func.count(Diagnosis.id)).where(
                Diagnosis.tenant_id == tenant_id,
                Diagnosis.deleted_at.is_(None),
            )
        )
        total = count_result.scalar() or 0

        offset = (page - 1) * page_size
        result = await self._db.execute(
            select(Diagnosis)
            .where(
                Diagnosis.tenant_id == tenant_id,
                Diagnosis.deleted_at.is_(None),
            )
            .order_by(Diagnosis.recorded_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        diagnoses = list(result.scalars().all())

        return diagnoses, total

    async def update(
        self, diagnosis: Diagnosis, expected_version: int, **updates
    ) -> Diagnosis | None:
        """Update an existing diagnosis with optimistic locking."""
        if diagnosis.version != expected_version:
            return None

        for field, value in updates.items():
            if value is not None and hasattr(diagnosis, field):
                setattr(diagnosis, field, value)

        diagnosis.version = expected_version + 1

        await self._db.flush()
        return diagnosis

    async def soft_delete(
        self,
        diagnosis_id: str,
        tenant_id: str,
        deleted_by: str | None = None,
        delete_reason: str | None = None,
    ) -> bool:
        """Soft delete a diagnosis with metadata."""
        diagnosis = await self.get_by_id(diagnosis_id, tenant_id)
        if diagnosis is None:
            return False

        diagnosis.deleted_at = datetime.now(UTC)
        diagnosis.deleted_by = deleted_by
        diagnosis.delete_reason = delete_reason
        await self._db.flush()
        return True
