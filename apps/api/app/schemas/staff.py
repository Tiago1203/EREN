"""Pydantic v2 schemas for Staff API."""

from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class StaffTypeEnum(StrEnum):
    PHYSICIAN = "physician"
    NURSE = "nurse"
    TECHNICIAN = "technician"
    ENGINEER = "engineer"
    ADMIN = "admin"
    OTHER = "other"


class EmploymentStatusEnum(StrEnum):
    ACTIVE = "active"
    ON_LEAVE = "on_leave"
    TERMINATED = "terminated"


class StaffCreate(BaseModel):
    employee_id: str = Field(min_length=1, max_length=50)
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    email: str = Field(min_length=1, max_length=255)
    phone: str | None = Field(default=None, max_length=20)
    staff_type: StaffTypeEnum


class StaffResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    staff_id: str
    employee_id: str
    first_name: str
    last_name: str
    email: str
    phone: str | None = None
    staff_type: str
    employment_status: str
    hire_date: date


class ShiftCreate(BaseModel):
    staff_id: str = Field(min_length=1)
    shift_type: str = Field(min_length=1)
    start_time: datetime
    end_time: datetime
    unit_id: str | None = None
    department_id: str | None = None
    notes: str | None = None


class ShiftResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    shift_id: str
    staff_id: str
    shift_type: str
    start_time: datetime
    end_time: datetime
    status: str
