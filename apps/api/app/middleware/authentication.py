"""JWT Authentication Middleware.

Validates JWT tokens and extracts principal context.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from fastapi import HTTPException, Request, status
from starlette.middleware.base import BaseHTTPMiddleware

from app.middleware.request_context import (
    get_request_context,
    set_request_context,
)

if TYPE_CHECKING:
    from core.contracts.security.authentication import AuthenticationProvider, Principal

logger = logging.getLogger(__name__)


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """Validates JWT and attaches principal to request context."""

    # Paths that don't require authentication
    PUBLIC_PATHS: frozenset[str] = frozenset({
        "/",
        "/health",
        "/api/v1/health",
        "/docs",
        "/openapi.json",
        "/redoc",
    })

    def __init__(self, app, auth_provider: AuthenticationProvider):
        super().__init__(app)
        self._auth_provider = auth_provider

    async def dispatch(self, request: Request, call_next):
        """Validate JWT and set principal context."""
        # Skip authentication for public paths
        if self._is_public_path(request.url.path):
            return await call_next(request)

        # Get authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing Authorization header",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Extract token
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Authorization header format",
                headers={"WWW-Authenticate": "Bearer"},
            )

        token = parts[1]

        # Verify token
        principal = await self._auth_provider.verify_token(token)
        if principal is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Extract tenant_id from principal attributes
        tenant_id = None
        for key, value in principal.attributes:
            if key == "tenant_id":
                tenant_id = value
                break

        # Set request context
        context = get_request_context()
        context.principal = principal
        context.tenant_id = tenant_id
        set_request_context(context)

        # Add principal to request state
        request.state.principal = principal
        request.state.tenant_id = tenant_id

        return await call_next(request)

    def _is_public_path(self, path: str) -> bool:
        """Check if path is public (no auth required)."""
        return path in self.PUBLIC_PATHS or path.startswith("/api/v1/auth/")


def get_current_principal(request: Request) -> Principal:
    """FastAPI dependency to get current principal."""
    if not hasattr(request.state, "principal"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    return request.state.principal


def get_current_tenant_id(request: Request) -> str | None:
    """FastAPI dependency to get current tenant_id."""
    return getattr(request.state, "tenant_id", None)
