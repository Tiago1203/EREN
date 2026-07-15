"""Diagnosis API endpoints."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.domain.diagnosis.repository import SQLAlchemyDiagnosisRepository
from app.domain.diagnosis.service import DiagnosisService
from app.infrastructure.events import EventBus
from app.schemas.diagnosis import (
    DiagnosisCreate,
    DiagnosisListResponse,
    DiagnosisResponse,
    DiagnosisUpdate,
)

router = APIRouter(prefix="/api/v1/diagnoses", tags=["Diagnoses"])


async def get_diagnosis_service(
    db: Annotated[AsyncSession, Depends(get_db)]
) -> DiagnosisService:
    """Dependency injection for DiagnosisService."""
    repository = SQLAlchemyDiagnosisRepository(db)
    event_bus = EventBus(db)
    return DiagnosisService(repository=repository, event_bus=event_bus)


@router.post(
    "",
    response_model=DiagnosisResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Record a diagnosis",
    description="Record a new clinical diagnosis for a patient.",
)
async def record_diagnosis(
    diagnosis: DiagnosisCreate,
    service: Annotated[DiagnosisService, Depends(get_diagnosis_service)],
    tenant_id: Annotated[str, Query(description="Tenant ID")],
    created_by: Annotated[str | None, Query(description="Creator principal ID")] = None,
) -> DiagnosisResponse:
    """Record a new diagnosis."""
    result = await service.record_diagnosis(
        tenant_id=tenant_id,
        patient_id=diagnosis.patient_id,
        diagnosis_code=diagnosis.diagnosis_code,
        diagnosis_name=diagnosis.diagnosis_name,
        description=diagnosis.description,
        created_by=created_by,
    )
    return DiagnosisResponse.model_validate(result)


@router.get(
    "/{diagnosis_id}",
    response_model=DiagnosisResponse,
    summary="Get a diagnosis",
    description="Get a diagnosis by ID.",
)
async def get_diagnosis(
    diagnosis_id: str,
    service: Annotated[DiagnosisService, Depends(get_diagnosis_service)],
    tenant_id: Annotated[str, Query(description="Tenant ID")],
) -> DiagnosisResponse:
    """Get a diagnosis by ID."""
    result = await service.get_diagnosis(diagnosis_id, tenant_id)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Diagnosis not found",
        )
    return DiagnosisResponse.model_validate(result)


@router.get(
    "",
    response_model=DiagnosisListResponse,
    summary="List diagnoses",
    description="List diagnoses for a patient or tenant.",
)
async def list_diagnoses(
    service: Annotated[DiagnosisService, Depends(get_diagnosis_service)],
    tenant_id: Annotated[str, Query(description="Tenant ID")],
    patient_id: Annotated[str | None, Query(description="Filter by patient ID")] = None,
    page: Annotated[int, Query(ge=1, description="Page number")] = 1,
    page_size: Annotated[int, Query(ge=1, le=100, description="Page size")] = 50,
) -> DiagnosisListResponse:
    """List diagnoses."""
    if patient_id:
        items, total = await service.list_diagnoses_by_patient(
            patient_id, tenant_id, page, page_size
        )
    else:
        items, total = await service.list_diagnoses_by_tenant(
            tenant_id, page, page_size
        )
    return DiagnosisListResponse(
        items=[DiagnosisResponse.model_validate(i) for i in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.patch(
    "/{diagnosis_id}",
    response_model=DiagnosisResponse,
    summary="Amend a diagnosis",
    description="Amend an existing diagnosis with optimistic locking.",
)
async def amend_diagnosis(
    diagnosis_id: str,
    update: DiagnosisUpdate,
    service: Annotated[DiagnosisService, Depends(get_diagnosis_service)],
    tenant_id: Annotated[str, Query(description="Tenant ID")],
) -> DiagnosisResponse:
    """Amend a diagnosis."""
    updates = update.model_dump(exclude_unset=True, exclude={"version"})
    result = await service.amend_diagnosis(
        diagnosis_id,
        tenant_id,
        expected_version=update.version,
        **updates,
    )
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Diagnosis was modified by another user",
        )
    return DiagnosisResponse.model_validate(result)


@router.delete(
    "/{diagnosis_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a diagnosis",
    description="Soft-delete a diagnosis.",
)
async def delete_diagnosis(
    diagnosis_id: str,
    service: Annotated[DiagnosisService, Depends(get_diagnosis_service)],
    tenant_id: Annotated[str, Query(description="Tenant ID")],
    deleted_by: Annotated[str | None, Query(description="Deleter principal ID")] = None,
    delete_reason: Annotated[
        str | None, Query(max_length=500, description="Reason for deletion")
    ] = None,
) -> None:
    """Soft-delete a diagnosis."""
    success = await service.delete_diagnosis(
        diagnosis_id,
        tenant_id,
        deleted_by=deleted_by,
        delete_reason=delete_reason,
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Diagnosis not found",
        )
