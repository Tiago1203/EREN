"""System/health router with liveness, readiness, and full health checks."""
from __future__ import annotations

import asyncio
import logging
from datetime import UTC, datetime

from fastapi import APIRouter, status
from pydantic import BaseModel

from app import __version__
from app.config.settings import get_settings

logger = logging.getLogger(__name__)
router = APIRouter(tags=["system"])


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str


class LivenessResponse(BaseModel):
    status: str
    timestamp: str


class ReadinessResponse(BaseModel):
    status: str
    timestamp: str
    checks: dict[str, object]


class FullHealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    environment: str
    checks: dict[str, object]


async def _check_database() -> dict[str, object]:
    """Check PostgreSQL connectivity."""
    try:
        from app.core.database import get_engine

        engine = get_engine()
        async with engine.connect() as conn:
            from sqlalchemy import text

            await conn.execute(text("SELECT 1"))
        return {"status": "healthy"}
    except Exception as e:
        logger.warning("Database health check failed: %s", e)
        return {"status": "unhealthy", "error": str(e)}


async def _check_redis() -> dict[str, object]:
    """Check Redis connectivity."""
    try:
        from app.infrastructure.messaging import get_redis

        client = await get_redis()
        if client is None:
            return {"status": "skipped", "reason": "Redis not configured"}
        await client.ping()
        return {"status": "healthy"}
    except Exception as e:
        logger.warning("Redis health check failed: %s", e)
        return {"status": "unhealthy", "error": str(e)}


@router.get("/health", response_model=HealthResponse, summary="Liveness probe")
async def health() -> HealthResponse:
    """Simple liveness probe."""
    settings = get_settings()
    return HealthResponse(status="ok", service=settings.app_name, version=__version__)


@router.get(
    "/health/live",
    response_model=LivenessResponse,
    status_code=status.HTTP_200_OK,
    summary="Liveness probe (Kubernetes)",
)
async def liveness() -> LivenessResponse:
    """Kubernetes liveness probe — checks if the app is running."""
    return LivenessResponse(
        status="alive",
        timestamp=datetime.now(UTC).isoformat(),
    )


@router.get(
    "/health/ready",
    response_model=ReadinessResponse,
    status_code=status.HTTP_200_OK,
    summary="Readiness probe (Kubernetes)",
)
async def readiness() -> ReadinessResponse:
    """Kubernetes readiness probe — checks if the app can serve traffic."""
    db_check, redis_check = await asyncio.gather(
        _check_database(),
        _check_redis(),
    )

    ready = db_check.get("status") == "healthy"
    return ReadinessResponse(
        status="ready" if ready else "not_ready",
        timestamp=datetime.now(UTC).isoformat(),
        checks={"database": db_check, "redis": redis_check},
    )


@router.get(
    "/health/full",
    response_model=FullHealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Full health check",
)
async def full_health() -> FullHealthResponse:
    """Full health check including all dependencies."""
    settings = get_settings()

    db_check, redis_check = await asyncio.gather(
        _check_database(),
        _check_redis(),
    )

    all_healthy = all(
        c.get("status") == "healthy"
        for c in [db_check, redis_check]
        if c.get("status") != "skipped"
    )

    return FullHealthResponse(
        status="healthy" if all_healthy else "degraded",
        timestamp=datetime.now(UTC).isoformat(),
        version=__version__,
        environment=settings.environment,
        checks={"database": db_check, "redis": redis_check},
    )
