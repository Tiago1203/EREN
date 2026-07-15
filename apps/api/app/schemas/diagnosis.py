"""Diagnosis schemas (Pydantic models)."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class DiagnosisBase(BaseModel):
    """Base diagnosis schema."""

    patient_id: Annotated[
        str, Field(min_length=1, max_length=36, description="Patient ID")
    ]
    diagnosis_code: Annotated[
        str, Field(min_length=1, max_length=50, description="Diagnosis code (ICD-10)")
    ]
    diagnosis_name: Annotated[
        str, Field(min_length=1, max_length=255, description="Diagnosis name")
    ]
    description: str | None = Field(
        default=None, max_length=1000, description="Additional notes"
    )


class DiagnosisCreate(DiagnosisBase):
    """Schema for recording a diagnosis."""

    model_config = ConfigDict(str_strip_whitespace=True)


class DiagnosisUpdate(BaseModel):
    """Schema for amending a diagnosis."""

    diagnosis_code: str | None = Field(
        default=None, max_length=50, description="Diagnosis code"
    )
    diagnosis_name: str | None = Field(
        default=None, max_length=255, description="Diagnosis name"
    )
    description: str | None = Field(
        default=None, max_length=1000, description="Additional notes"
    )
    version: Annotated[int, Field(description="Expected version for optimistic locking")]


class DiagnosisResponse(DiagnosisBase):
    """Schema for diagnosis response."""

    id: str
    tenant_id: str
    version: int
    recorded_at: datetime
    updated_at: datetime
    created_by: str | None = None
    is_deleted: bool

    model_config = ConfigDict(from_attributes=True)


class DiagnosisListResponse(BaseModel):
    """Schema for paginated diagnosis list."""

    items: list[DiagnosisResponse]
    total: int
    page: int
    page_size: int
