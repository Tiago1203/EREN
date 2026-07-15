"""Request-context middleware.

Attaches correlation id, tenant context, and timing to every request/response
so logs and clients can trace a single call.
"""

import logging
import uuid
from collections.abc import Awaitable, Callable
from contextvars import ContextVar
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

if TYPE_CHECKING:
    from core.contracts.security.authentication import Principal

REQUEST_ID_HEADER = "X-Request-ID"


@dataclass
class RequestContext:
    """Request context shared across the call chain."""

    request_id: str
    started_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    tenant_id: str | None = None
    principal: "Principal | None" = None
    metadata: dict[str, Any] = field(default_factory=dict)


# Thread-safe context variable
_request_context: ContextVar[RequestContext] = ContextVar("request_context")


def get_request_context() -> RequestContext:
    """Get current request context."""
    return _request_context.get()


def set_request_context(ctx: RequestContext) -> None:
    """Set current request context."""
    _request_context.set(ctx)


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Ensure each request has an ``X-Request-ID`` and request context."""

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        # Generate or extract request ID
        request_id = request.headers.get(REQUEST_ID_HEADER, str(uuid.uuid4()))

        # Create request context
        ctx = RequestContext(request_id=request_id)
        set_request_context(ctx)

        # Store in request state for easy access
        request.state.request_id = request_id
        request.state.request_context = ctx

        # Process request
        response = await call_next(request)

        # Add request ID to response
        response.headers[REQUEST_ID_HEADER] = request_id

        # Calculate duration and log
        duration_ms = (datetime.now(UTC) - ctx.started_at).total_seconds() * 1000

        # This would be structured logging in production
        logger = logging.getLogger("request")
        logger.info(
            "request_completed",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
                "tenant_id": ctx.tenant_id,
            },
        )

        return response
