"""Application error types and FastAPI exception handlers.

Raise :class:`AppError` (or a subclass) from services; the handler installed by
:func:`install_exception_handlers` turns it into a consistent JSON response.
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class AppError(Exception):
    """Base class for expected, domain-level errors.

    Subclass this in ``services``/``core`` to represent specific failure modes.
    """

    status_code: int = 400
    code: str = "app_error"

    def __init__(self, message: str, *, status_code: int | None = None, code: str | None = None):
        super().__init__(message)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        if code is not None:
            self.code = code


def install_exception_handlers(app: FastAPI) -> None:
    """Register application-wide exception handlers on the FastAPI app."""

    @app.exception_handler(AppError)
    async def _handle_app_error(_: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": {"code": exc.code, "message": exc.message}},
        )
