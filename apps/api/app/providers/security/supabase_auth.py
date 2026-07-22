"""
Supabase Authentication Provider.

Implements AuthenticationProvider contract using Supabase Auth.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from core.PHASE_1.infrastructure.contracts.security.authentication import (
    AuthenticationFactor,
    AuthenticationMethod,
    AuthenticationResult,
    IdentityType,
    Principal,
    TokenInfo,
)
from supabase import AsyncClient, create_client

from app.config.settings import get_settings

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


@dataclass
class SupabaseAuthConfig:
    """Configuration for Supabase Auth Provider."""

    url: str
    anon_key: str
    service_role_key: str | None = None
    tenant_claim: str = "tenant_id"


class SupabaseAuthenticationProvider:
    """Supabase implementation of AuthenticationProvider.

    Uses Supabase Auth for JWT validation and user management.
    """

    def __init__(self, config: SupabaseAuthConfig):
        self._config = config
        self._client: AsyncClient | None = None
        self._provider_id = "supabase-auth"

    @property
    def provider_id(self) -> str:
        return self._provider_id

    @property
    def supported_methods(self) -> tuple[AuthenticationMethod, ...]:
        return (
            AuthenticationMethod.PASSWORD,
            AuthenticationMethod.TOKEN,
        )

    async def _get_client(self) -> AsyncClient:
        """Lazy initialization of Supabase client."""
        if self._client is None:
            self._client = create_client(self._config.url, self._config.anon_key)
        return self._client

    async def authenticate(
        self,
        credentials: dict,
    ) -> AuthenticationResult:
        """Authenticate using email/password.

        Args:
            credentials: {"email": "...", "password": "..."}

        Returns:
            AuthenticationResult with principal_id if successful
        """
        email = credentials.get("email")
        password = credentials.get("password")

        if not email or not password:
            return AuthenticationResult(
                success=False,
                error_code="AUTH-001",
                error_message="Email and password are required",
            )

        try:
            client = await self._get_client()
            response = await client.auth.sign_in_with_password(
                {"email": email, "password": password}
            )

            if response.user is None:
                return AuthenticationResult(
                    success=False,
                    error_code="AUTH-001",
                    error_message="Authentication failed",
                )

            user = response.user
            metadata = user.user_metadata or {}

            # Extract tenant_id from user metadata
            tenant_id = metadata.get(self._config.tenant_claim, "default")

            principal = Principal(
                principal_id=user.id,
                identity_type=IdentityType.HUMAN,
                display_name=metadata.get("full_name", email),
                email=email,
                roles=(metadata.get("role", "user"),),
                attributes=(
                    ("tenant_id", tenant_id),
                    ("provider", "supabase"),
                ),
            )

            return AuthenticationResult(
                success=True,
                principal_id=principal.principal_id,
                identity_type=IdentityType.HUMAN,
                factors_verified=(AuthenticationFactor.SOMETHING_YOU_KNOW,),
                method=AuthenticationMethod.PASSWORD,
            )

        except Exception as e:
            logger.error(f"Authentication failed for {email}: {e}")
            return AuthenticationResult(
                success=False,
                error_code="AUTH-001",
                error_message="Invalid credentials",
            )

    async def authenticate_multi_factor(
        self,
        factors: list[dict],
    ) -> AuthenticationResult:
        """Multi-factor authentication not implemented in MVP."""
        return AuthenticationResult(
            success=False,
            error_code="AUTH-001",
            error_message="MFA not yet implemented",
        )

    async def verify_token(self, token: str) -> Principal | None:
        """Verify a JWT token.

        Args:
            token: JWT Bearer token

        Returns:
            Principal if token is valid, None otherwise
        """
        if not token:
            return None

        try:
            client = await self._get_client()
            response = await client.auth.get_user(token)

            if response.user is None:
                return None

            user = response.user
            metadata = user.user_metadata or {}

            tenant_id = metadata.get(self._config.tenant_claim, "default")

            return Principal(
                principal_id=user.id,
                identity_type=IdentityType.HUMAN,
                display_name=metadata.get("full_name", user.email or "Unknown"),
                email=user.email,
                roles=(metadata.get("role", "user"),),
                attributes=(
                    ("tenant_id", tenant_id),
                    ("provider", "supabase"),
                ),
            )

        except Exception as e:
            logger.warning(f"Token verification failed: {e}")
            return None

    async def get_token_info(self, token: str) -> TokenInfo | None:
        """Get information about a token without full verification.

        Args:
            token: JWT token to inspect

        Returns:
            TokenInfo if token is parseable, None otherwise
        """
        if not token:
            return None

        try:
            client = await self._get_client()
            response = await client.auth.get_user(token)

            if response.user is None or response.session is None:
                return None

            session = response.session
            expires_at = datetime.fromtimestamp(
                session.expires_at, tz=UTC
            ) if session.expires_at else None

            return TokenInfo(
                token_type="Bearer",
                issued_at=datetime.now(UTC),
                expires_at=expires_at,
                scopes=(),
                issuer=self._config.url,
                audience=self._config.anon_key,
            )

        except Exception:
            return None

    async def refresh_token(self, refresh_token: str) -> AuthenticationResult:
        """Refresh an authentication token.

        Args:
            refresh_token: Token used to get new access token

        Returns:
            New AuthenticationResult with fresh tokens
        """
        try:
            client = await self._get_client()
            response = await client.auth.refresh_session(refresh_token)

            if response.user is None:
                return AuthenticationResult(
                    success=False,
                    error_code="AUTH-003",
                    error_message="Token refresh failed",
                )

            return AuthenticationResult(
                success=True,
                principal_id=response.user.id,
                identity_type=IdentityType.HUMAN,
                method=AuthenticationMethod.TOKEN,
            )

        except Exception as e:
            logger.error(f"Token refresh failed: {e}")
            return AuthenticationResult(
                success=False,
                error_code="AUTH-003",
                error_message="Token expired or invalid",
            )

    async def revoke_token(self, token: str) -> bool:
        """Revoke an authentication token.

        Args:
            token: Token to revoke

        Returns:
            True if revoked successfully
        """
        try:
            client = await self._get_client()
            await client.auth.sign_out()
            return True
        except Exception as e:
            logger.error(f"Token revocation failed: {e}")
            return False

    async def get_principal_from_id(self, principal_id: str) -> Principal | None:
        """Get Principal by ID.

        Note: This requires service role key for admin access.

        Args:
            principal_id: Principal identifier

        Returns:
            Principal if found, None otherwise
        """
        if not self._config.service_role_key:
            logger.warning("Cannot get principal without service role key")
            return None

        try:
            client = await self._get_client()
            response = await client.auth.admin.get_user(principal_id)

            if response.user is None:
                return None

            user = response.user
            metadata = user.user_metadata or {}
            tenant_id = metadata.get(self._config.tenant_claim, "default")

            return Principal(
                principal_id=user.id,
                identity_type=IdentityType.HUMAN,
                display_name=metadata.get("full_name", user.email or "Unknown"),
                email=user.email,
                roles=(metadata.get("role", "user"),),
                attributes=(
                    ("tenant_id", tenant_id),
                    ("provider", "supabase"),
                ),
            )

        except Exception as e:
            logger.error(f"Failed to get principal {principal_id}: {e}")
            return None


def create_supabase_auth_provider() -> SupabaseAuthenticationProvider:
    """Factory function to create Supabase Auth Provider."""
    settings = get_settings()

    config = SupabaseAuthConfig(
        url=settings.supabase_url,
        anon_key=settings.supabase_anon_key,
        service_role_key=settings.supabase_service_role_key,
    )

    return SupabaseAuthenticationProvider(config)
