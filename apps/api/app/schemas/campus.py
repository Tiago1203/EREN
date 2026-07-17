"""Pydantic v2 schemas for Campus API."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class CampusCreate(BaseModel):
    campus_code: str = Field(min_length=1, max_length=20)
    campus_name: str = Field(min_length=1, max_length=200)
    city: str = Field(min_length=1, max_length=100)
    state: str = Field(min_length=1, max_length=100)
    country: str = Field(min_length=1, max_length=100)
    address: str | None = Field(default=None, max_length=500)
    postal_code: str | None = Field(default=None, max_length=20)
    timezone: str | None = Field(default=None, max_length=50)


class CampusUpdate(BaseModel):
    campus_name: str | None = Field(default=None, max_length=200)
    address: str | None = Field(default=None, max_length=500)
    timezone: str | None = Field(default=None, max_length=50)
    status: str | None = None


class CampusResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    campus_id: str
    campus_code: str
    campus_name: str
    city: str
    state: str
    country: str
    address: str | None = None
    postal_code: str | None = None
    timezone: str | None = None
    status: str
