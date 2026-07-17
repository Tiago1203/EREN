"""Patient endpoints.

CRUD operations for patients.
These endpoints delegate to PatientService for business logic.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.clinical.patient import PatientService, SQLAlchemyPatientRepository
from app.infrastructure.events import EventBus
from app.models.patient import Patient
from app.schemas.patient import (
    PatientCreate,
    PatientListResponse,
    PatientResponse,
    PatientUpdate,
)

router = APIRouter(prefix="/patients", tags=["Patients"])


def get_tenant_id(request: Request) -> str:
    """Extract tenant_id from request context."""
    tenant_id = getattr(request.state, "tenant_id", None)
    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tenant not resolved",
        )
    return tenant_id


def get_current_user_id(request: Request) -> str | None:
    """Extract current user ID from request context."""
    principal = getattr(request.state, "principal", None)
    if principal:
        return principal.principal_id
    return None


def get_correlation_id(request: Request) -> str | None:
    """Extract correlation_id from request context."""
    return getattr(request.state, "request_id", None)


def create_patient_service(db: AsyncSession) -> PatientService:
    """Factory to create PatientService with dependencies."""
    repository = SQLAlchemyPatientRepository(db)
    event_bus = EventBus(db)
    return PatientService(repository=repository, event_bus=event_bus)


@router.post("", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
async def create_patient(
    patient_data: PatientCreate,
    request: Request,
    tenant_id: Annotated[str, Depends(get_tenant_id)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Patient:
    """Create a new patient.

    Requires authentication and valid tenant context.
    Publishes PatientCreated event via outbox pattern.
    """
    service = create_patient_service(db)
    created_by = get_current_user_id(request)
    correlation_id = get_correlation_id(request)

    patient = await service.create_patient(
        tenant_id=tenant_id,
        mrn=patient_data.mrn,
        given_name=patient_data.given_name,
        family_name=patient_data.family_name,
        created_by=created_by,
        correlation_id=correlation_id,
        date_of_birth=patient_data.date_of_birth,
        gender=patient_data.gender,
        email=patient_data.email,
        phone=patient_data.phone,
        blood_type=patient_data.blood_type,
        allergies=patient_data.allergies,
    )

    await db.commit()
    await db.refresh(patient)

    return patient


@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(
    patient_id: str,
    tenant_id: Annotated[str, Depends(get_tenant_id)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Patient:
    """Get a patient by ID.

    Requires authentication and valid tenant context.
    """
    service = create_patient_service(db)
    patient = await service.get_patient(patient_id, tenant_id)

    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )

    return patient


@router.get("", response_model=PatientListResponse)
async def list_patients(
    tenant_id: Annotated[str, Depends(get_tenant_id)],
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = 1,
    page_size: int = 50,
) -> PatientListResponse:
    """List patients for the current tenant.

    Requires authentication and valid tenant context.
    """
    service = create_patient_service(db)
    patients, total = await service.list_patients(tenant_id, page, page_size)

    return PatientListResponse(
        items=patients,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.patch("/{patient_id}", response_model=PatientResponse)
async def update_patient(
    patient_id: str,
    patient_data: PatientUpdate,
    tenant_id: Annotated[str, Depends(get_tenant_id)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Patient:
    """Update a patient.

    Requires authentication and valid tenant context.
    """
    service = create_patient_service(db)
    correlation_id = get_correlation_id(None)

    update_data = patient_data.model_dump(exclude_unset=True)
    patient = await service.update_patient(
        patient_id, tenant_id, correlation_id=correlation_id, **update_data
    )

    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )

    await db.commit()
    await db.refresh(patient)

    return patient


@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_patient(
    patient_id: str,
    tenant_id: Annotated[str, Depends(get_tenant_id)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Soft-delete a patient.

    Requires authentication and valid tenant context.
    """
    service = create_patient_service(db)
    deleted_by = get_current_user_id(None)
    correlation_id = get_correlation_id(None)

    success = await service.delete_patient(
        patient_id, tenant_id, deleted_by=deleted_by, correlation_id=correlation_id
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )

    await db.commit()
