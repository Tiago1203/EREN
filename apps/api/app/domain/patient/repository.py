"""Patient repository.

Repository pattern: abstracts database access from domain.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from app.models.patient import Patient


class PatientRepository(Protocol):
    """Protocol for patient persistence operations."""

    async def save(
        self,
        tenant_id: str,
        patient_id: str,
        mrn: str,
        given_name: str,
        family_name: str,
        created_by: str | None = None,
        **kwargs,
    ) -> Patient:
        """Save a patient to the database."""
        ...

    async def get_by_id(self, patient_id: str, tenant_id: str) -> Patient | None:
        """Get a patient by ID within tenant."""
        ...

    async def list_by_tenant(
        self, tenant_id: str, page: int = 1, page_size: int = 50
    ) -> tuple[list[Patient], int]:
        """List patients for a tenant with pagination."""
        ...

    async def update(self, patient: Patient, **updates) -> Patient | None:
        """Update an existing patient."""
        ...

    async def soft_delete(self, patient_id: str, tenant_id: str) -> bool:
        """Soft delete a patient."""
        ...


@dataclass
class SQLAlchemyPatientRepository:
    """SQLAlchemy implementation of PatientRepository."""

    def __init__(self, db: AsyncSession):
        self._db = db

    async def save(
        self,
        tenant_id: str,
        patient_id: str,
        mrn: str,
        given_name: str,
        family_name: str,
        created_by: str | None = None,
        **kwargs,
    ) -> Patient:
        """Save a patient to the database using factory method."""
        from app.models.patient import Patient

        patient = Patient.create(
            patient_id=patient_id,
            tenant_id=tenant_id,
            mrn=mrn,
            given_name=given_name,
            family_name=family_name,
            created_by=created_by,
            **kwargs,
        )
        self._db.add(patient)
        await self._db.flush()
        return patient

    async def get_by_id(self, patient_id: str, tenant_id: str) -> Patient | None:
        """Get a patient by ID within tenant."""
        from sqlalchemy import select

        from app.models.patient import Patient

        result = await self._db.execute(
            select(Patient).where(
                Patient.id == patient_id,
                Patient.tenant_id == tenant_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_by_tenant(
        self, tenant_id: str, page: int = 1, page_size: int = 50
    ) -> tuple[list[Patient], int]:
        """List patients for a tenant with pagination."""
        from sqlalchemy import func, select

        from app.models.patient import Patient

        # Count total
        count_result = await self._db.execute(
            select(func.count(Patient.id)).where(Patient.tenant_id == tenant_id)
        )
        total = count_result.scalar() or 0

        # Get patients
        offset = (page - 1) * page_size
        result = await self._db.execute(
            select(Patient)
            .where(Patient.tenant_id == tenant_id)
            .order_by(Patient.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        patients = list(result.scalars().all())

        return patients, total

    async def update(self, patient: Patient, **updates) -> Patient | None:
        """Update an existing patient."""
        for field, value in updates.items():
            if value is not None and hasattr(patient, field):
                setattr(patient, field, value)
        await self._db.flush()
        return patient

    async def soft_delete(self, patient_id: str, tenant_id: str) -> bool:
        """Soft delete a patient."""
        patient = await self.get_by_id(patient_id, tenant_id)
        if patient is None:
            return False
        patient.is_active = False
        await self._db.flush()
        return True
