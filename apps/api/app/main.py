"""EREN API — FastAPI application factory.

Wiring (config, logging, middleware, error handlers, routers) is in place.
Domain layer (core/) is integrated via infrastructure repositories.

Run locally (from ``apps/api``)::

    uv run uvicorn app.main:app --reload

Production::

    docker compose up
"""

from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.config.settings import get_settings
from app.core.database import close_db
from app.core.exceptions import install_exception_handlers
from app.infrastructure.messaging import close_connection, close_redis
from app.infrastructure.observability import configure_logging, setup_instrumentation
from app.middleware import RequestContextMiddleware
from app.routers import api_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> Any:
    """Application lifespan manager for startup/shutdown events."""
    # Startup
    settings = get_settings()
    configure_logging()

    if settings.otel_endpoint:
        setup_instrumentation(app)

    # Create database schemas in development
    if settings.environment == "development":
        try:
            from app.core.database import init_db
            await init_db()
        except Exception:
            pass  # Database may not be available in all environments

    yield

    # Shutdown
    await close_connection()
    await close_redis()
    await close_db()


def create_app() -> FastAPI:
    """Build and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=__version__,
        debug=settings.debug,
        description="Programmatic gateway into the EREN Cognitive Operating System.",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RequestContextMiddleware)

    install_exception_handlers(app)

    app.include_router(api_router, prefix=settings.api_v1_prefix)

    return app


app = create_app()
