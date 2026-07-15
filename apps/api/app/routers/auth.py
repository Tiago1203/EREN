"""Authentication endpoints.

Public endpoints for login/logout.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr

from app.providers.security.supabase_auth import create_supabase_auth_provider

router = APIRouter(prefix="/auth", tags=["Authentication"])


class LoginRequest(BaseModel):
    """Login credentials."""

    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    """Login response."""

    success: bool
    message: str
    access_token: str | None = None
    token_type: str | None = None
    expires_in: int | None = None


class LogoutResponse(BaseModel):
    """Logout response."""

    success: bool
    message: str


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest) -> LoginResponse:
    """Authenticate user and return JWT token.

    This endpoint is PUBLIC - no authentication required.
    """
    auth_provider = create_supabase_auth_provider()

    result = await auth_provider.authenticate(
        credentials={"email": request.email, "password": request.password}
    )

    if not result.success:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=result.error_message or "Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # In a real implementation, we'd issue our own JWT here
    # For MVP, we return a placeholder
    return LoginResponse(
        success=True,
        message="Login successful",
        access_token="placeholder-jwt-token",
        token_type="Bearer",
        expires_in=3600,
    )


@router.post("/logout", response_model=LogoutResponse)
async def logout() -> LogoutResponse:
    """Logout current user.

    This endpoint requires authentication.
    """
    # In a real implementation, we'd invalidate the session/token here
    return LogoutResponse(success=True, message="Logged out successfully")


@router.post("/refresh", response_model=LoginResponse)
async def refresh_token(refresh_token: str) -> LoginResponse:
    """Refresh access token using refresh token.

    This endpoint is PUBLIC - no authentication required.
    """
    auth_provider = create_supabase_auth_provider()

    result = await auth_provider.refresh_token(refresh_token)

    if not result.success:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=result.error_message or "Token refresh failed",
        )

    return LoginResponse(
        success=True,
        message="Token refreshed",
        access_token="placeholder-jwt-token",
        token_type="Bearer",
        expires_in=3600,
    )
