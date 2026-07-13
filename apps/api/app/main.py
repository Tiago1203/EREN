"""EREN API — FastAPI application factory.

Clean-architecture skeleton only: wiring (config, logging, middleware, error
handlers, routers) is in place, but no business endpoints are implemented.

Run locally (from ``apps/api``)::

    uv run uvicorn app.main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.config.settings import get_settings
from app.core.exceptions import install_exception_handlers
from app.core.logging import configure_logging
from app.middleware import RequestContextMiddleware
from app.routers import api_router


def create_app() -> FastAPI:
    """Build and configure the FastAPI application."""
    settings = get_settings()
    configure_logging()

    app = FastAPI(
        title=settings.app_name,
        version=__version__,
        debug=settings.debug,
        description="Programmatic gateway into the EREN Cognitive Operating System.",
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
