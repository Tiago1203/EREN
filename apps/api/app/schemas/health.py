"""Schemas for the health/system endpoints."""

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Response body for the liveness probe."""

    status: str
    service: str
    version: str
