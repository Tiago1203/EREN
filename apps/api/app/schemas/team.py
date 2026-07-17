"""Pydantic v2 schemas for Team and Role API."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class TeamCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = None
    team_type: str = Field(min_length=1, max_length=20)
    department_id: str | None = None


class TeamResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    team_id: str
    name: str
    description: str | None = None
    team_type: str
    department_id: str | None = None
    is_active: bool


class RoleCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = None
    role_type: str = Field(min_length=1, max_length=20)


class RoleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    role_id: str
    name: str
    description: str | None = None
    role_type: str
    is_active: bool
