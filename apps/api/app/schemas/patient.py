"""Patient schemas (Pydantic models)."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class PatientBase(BaseModel):
    """Base patient schema."""

    mrn: Annotated[
        str, Field(min_length=1, max_length=50, description="Medical Record Number")
    ]
    given_name: Annotated[
        str, Field(min_length=1, max_length=100, description="Patient given name")
    ]
    family_name: Annotated[
        str, Field(min_length=1, max_length=100, description="Patient family name")
    ]
    date_of_birth: datetime | None = Field(default=None, description="Date of birth")
    gender: str | None = Field(default=None, max_length=20, description="Gender")
    email: EmailStr | None = Field(default=None, description="Contact email")
    phone: str | None = Field(default=None, max_length=50, description="Contact phone")
    blood_type: str | None = Field(default=None, max_length=10, description="Blood type")
    allergies: str | None = Field(
        default=None, max_length=500, description="Known allergies"
    )


class PatientCreate(PatientBase):
    """Schema for creating a patient."""

    model_config = ConfigDict(str_strip_whitespace=True)


class PatientUpdate(BaseModel):
    """Schema for updating a patient (all fields optional)."""

    mrn: str | None = Field(default=None, min_length=1, max_length=50)
    given_name: str | None = Field(default=None, min_length=1, max_length=100)
    family_name: str | None = Field(default=None, min_length=1, max_length=100)
    date_of_birth: datetime | None = None
    gender: str | None = Field(default=None, max_length=20)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=50)
    blood_type: str | None = Field(default=None, max_length=10)
    allergies: str | None = Field(default=None, max_length=500)
    is_active: bool | None = None


class PatientResponse(PatientBase):
    """Schema for patient response."""

    id: str
    tenant_id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    created_by: str | None

    model_config = ConfigDict(from_attributes=True)


class PatientListResponse(BaseModel):
    """Schema for paginated patient list."""

    items: list[PatientResponse]
    total: int
    page: int
    page_size: int
