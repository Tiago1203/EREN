"""System/health router.

This is the only endpoint in the skeleton — a liveness probe used to verify the
service is wired correctly. No business endpoints are implemented yet.
"""

from fastapi import APIRouter

from app import __version__
from app.config.settings import get_settings
from app.schemas.health import HealthResponse

router = APIRouter(tags=["system"])


@router.get("/health", response_model=HealthResponse, summary="Liveness probe")
async def health() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(status="ok", service=settings.app_name, version=__version__)
