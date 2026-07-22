"""
Authentication Contract.

Philosophy: EREN must verify who is interacting.
Authentication is separate from sessions and identity management.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    pass


# =============================================================================
# Types
# =============================================================================


class IdentityType(Enum):
    """Types of identities in EREN."""

    HUMAN = "human"
    DEVICE = "device"
    SYSTEM = "system"
    SERVICE = "service"


class AuthenticationMethod(Enum):
    """Methods of authentication."""

    PASSWORD = "password"
    API_KEY = "api_key"
    CERTIFICATE = "certificate"
    TOKEN = "token"
    BIOMETRIC = "biometric"
    SSO = "sso"
    MFA = "mfa"


class AuthenticationFactor(Enum):
    """Authentication factors."""

    SOMETHING_YOU_KNOW = "password"
    SOMETHING_YOU_HAVE = "token"
    SOMETHING_YOU_ARE = "biometric"


@dataclass(frozen=True)
class AuthenticationResult:
    """Result of an authentication attempt."""

    success: bool
    principal_id: str | None = None
    identity_type: IdentityType | None = None
    factors_verified: tuple[AuthenticationFactor, ...] = field(default_factory=tuple)
    method: AuthenticationMethod | None = None
    error_code: str | None = None
    error_message: str | None = None
    authenticated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    metadata: tuple[tuple[str, str], ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class Principal:
    """Represents a verified identity.

    This is returned by authentication and passed to session management.
    The Principal is a data carrier, not a service.
    """

    principal_id: str
    identity_type: IdentityType
    display_name: str
    email: str | None = None
    roles: tuple[str, ...] = field(default_factory=tuple)
    attributes: tuple[tuple[str, str], ...] = field(default_factory=tuple)
    authenticated_methods: tuple[AuthenticationMethod, ...] = field(default_factory=tuple)
    authenticated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    expires_at: datetime | None = None


@dataclass(frozen=True)
class TokenInfo:
    """Information about an authentication token."""

    token_type: str  # "Bearer", "JWT", etc.
    issued_at: datetime
    expires_at: datetime | None
    scopes: tuple[str, ...] = field(default_factory=tuple)
    issuer: str | None = None
    audience: str | None = None


# =============================================================================
# Provider Interface
# =============================================================================


class AuthenticationProvider(Protocol):
    """Contract for authentication services.

    This contract is RESPONSIBLE ONLY for:
    - Verifying credentials
    - Issuing tokens
    - Validating tokens
    - Managing authentication factors

    This contract is NOT responsible for:
    - Session management (see SessionProvider)
    - Principal data (it's returned, not managed)
    - Authorization (see AuthorizationProvider)

    Philosophy: Single Responsibility. Authentication is verification, nothing else.
    """

    @property
    def provider_id(self) -> str:
        """Unique identifier for this provider."""
        ...

    @property
    def supported_methods(self) -> tuple[AuthenticationMethod, ...]:
        """Methods this provider supports."""
        ...

    async def authenticate(
        self,
        credentials: dict,
    ) -> AuthenticationResult:
        """Authenticate using credentials.

        Args:
            credentials: Provider-specific credentials
                Examples:
                - Password: {"email": "...", "password": "..."}
                - API Key: {"api_key": "..."}
                - Token: {"token": "..."}

        Returns:
            AuthenticationResult with principal_id if successful
        """
        ...

    async def authenticate_multi_factor(
        self,
        factors: list[dict],
    ) -> AuthenticationResult:
        """Authenticate using multiple factors.

        Args:
            factors: List of credentials for each factor
                Example: [{"password": "..."}, {"totp": "..."}]

        Returns:
            AuthenticationResult if all factors verify
        """
        ...

    async def verify_token(
        self,
        token: str,
    ) -> Principal | None:
        """Verify an authentication token.

        Args:
            token: JWT, Bearer token, or similar

        Returns:
            Principal if token is valid, None otherwise
        """
        ...

    async def get_token_info(
        self,
        token: str,
    ) -> TokenInfo | None:
        """Get information about a token without full verification.

        Args:
            token: Token to inspect

        Returns:
            TokenInfo if token is parseable, None otherwise
        """
        ...

    async def refresh_token(
        self,
        refresh_token: str,
    ) -> AuthenticationResult:
        """Refresh an authentication token.

        Args:
            refresh_token: Token used to get new access token

        Returns:
            New AuthenticationResult with fresh tokens
        """
        ...

    async def revoke_token(
        self,
        token: str,
    ) -> bool:
        """Revoke an authentication token.

        Args:
            token: Token to revoke

        Returns:
            True if revoked successfully
        """
        ...

    async def get_principal_from_id(
        self,
        principal_id: str,
    ) -> Principal | None:
        """Get Principal by ID.

        This is a convenience method to hydrate Principal data.
        It does NOT authenticate - use verify_token for that.

        Args:
            principal_id: Principal identifier

        Returns:
            Principal if found, None otherwise
        """
        ...


# =============================================================================
# Events
# =============================================================================


@dataclass(frozen=True)
class AuthenticationEvent:
    """Base class for authentication events."""

    event_id: str
    principal_id: str | None
    method: AuthenticationMethod | None
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True)
class AuthenticationSucceeded(AuthenticationEvent):
    """Fired when authentication succeeds."""

    factors_verified: tuple[AuthenticationFactor, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class AuthenticationFailed(AuthenticationEvent):
    """Fired when authentication fails."""

    error_code: str | None = None
    error_message: str | None = None
    ip_address: str | None = None


@dataclass(frozen=True)
class TokenIssued(AuthenticationEvent):
    """Fired when a token is issued."""

    token_type: str = ""
    expires_at: datetime | None = None


@dataclass(frozen=True)
class TokenRevoked(AuthenticationEvent):
    """Fired when a token is revoked."""
