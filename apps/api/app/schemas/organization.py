"""Pydantic v2 schemas for Organization and Hospital API."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class OrganizationCreate(BaseModel):
    legal_name: str = Field(min_length=1, max_length=255)
    doing_business_as: str | None = Field(default=None, max_length=255)
    tax_id: str | None = Field(default=None, max_length=50)
    ownership_type: str = Field(default="private", max_length=20)


class OrganizationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    organization_id: str
    legal_name: str
    doing_business_as: str | None = None
    ownership_type: str
    status: str


class HospitalCreate(BaseModel):
    hospital_code: str = Field(min_length=1, max_length=20)
    hospital_name: str = Field(min_length=1, max_length=200)
    hospital_type: str = Field(min_length=1, max_length=20)
    license_number: str | None = Field(default=None, max_length=100)
    contact_email: str | None = Field(default=None, max_length=255)
    contact_phone: str | None = Field(default=None, max_length=20)


class HospitalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    hospital_id: str
    organization_id: str
    hospital_code: str
    hospital_name: str
    hospital_type: str
    license_number: str | None = None
    accreditation_status: str
    contact_email: str | None = None
    contact_phone: str | None = None
    status: str
