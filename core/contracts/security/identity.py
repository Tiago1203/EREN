"""
Identity Capability Contract.

Philosophy: EREN must know who is interacting with the system.
Every action must be traceable to an authenticated identity.
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

    HUMAN = "human"  # Physicians, nurses, patients
    DEVICE = "device"  # Medical devices, sensors
    SYSTEM = "system"  # EREN internal, integrations
    SERVICE = "service"  # Microservices, APIs


class IdentityStatus(Enum):
    """Status of an identity."""

    ACTIVE = "active"
    SUSPENDED = "suspended"
    REVOKED = "revoked"
    EXPIRED = "expired"


class CredentialType(Enum):
    """Types of credentials."""

    PASSWORD = "password"
    API_KEY = "api_key"
    CERTIFICATE = "certificate"
    TOKEN = "token"  # JWT, OAuth
    BIOMETRIC = "biometric"
    SSO = "sso"  # SAML, OAuth2


@dataclass(frozen=True)
class Principal:
    """Represents an authenticated identity.

    This is the core identity object that flows through EREN.
    Every operation must be associated with a Principal.
    """

    principal_id: str  # Unique identifier
    identity_type: IdentityType
    display_name: str
    email: str | None = None
    roles: tuple[str, ...] = field(default_factory=tuple)
    attributes: tuple[tuple[str, str], ...] = field(default_factory=tuple)  # key-value pairs
    authenticated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    expires_at: datetime | None = None
    metadata: tuple[tuple[str, str], ...] = field(default_factory=tuple)

    def is_expired(self) -> bool:
        """Check if identity has expired."""
        if self.expires_at is None:
            return False
        return datetime.now(UTC) > self.expires_at

    def has_role(self, role: str) -> bool:
        """Check if identity has a specific role."""
        return role in self.roles

    def get_attribute(self, key: str) -> str | None:
        """Get an identity attribute."""
        for k, v in self.attributes:
            if k == key:
                return v
        return None


@dataclass(frozen=True)
class Credential:
    """Represents a credential for authentication."""

    credential_id: str
    principal_id: str
    credential_type: CredentialType
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    expires_at: datetime | None = None
    last_used_at: datetime | None = None
    metadata: tuple[tuple[str, str], ...] = field(default_factory=tuple)
    is_active: bool = True


@dataclass(frozen=True)
class Session:
    """Represents an authenticated session."""

    session_id: str
    principal: Principal
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    last_activity: datetime = field(default_factory=lambda: datetime.now(UTC))
    expires_at: datetime | None = None
    ip_address: str | None = None
    user_agent: str | None = None
    metadata: tuple[tuple[str, str], ...] = field(default_factory=tuple)

    def is_expired(self) -> bool:
        """Check if session has expired."""
        if self.expires_at is None:
            return False
        return datetime.now(UTC) > self.expires_at


@dataclass(frozen=True)
class AuthenticationResult:
    """Result of an authentication attempt."""

    success: bool
    principal: Principal | None = None
    session: Session | None = None
    error_code: str | None = None
    error_message: str | None = None
    factors_verified: tuple[str, ...] = field(default_factory=tuple)
    authentication_method: str | None = None
    authenticated_at: datetime = field(default_factory=lambda: datetime.now(UTC))


# =============================================================================
# Provider Interface
# =============================================================================


class IdentityProvider(Protocol):
    """Contract for identity and authentication services.

    EREN supports multiple identity providers:
    - Supabase Auth
    - Keycloak
    - Azure AD
    - Hospital LDAP
    - Custom implementations

    The runtime never knows which provider is being used.
    """

    @property
    def provider_id(self) -> str:
        """Unique identifier for this provider."""
        ...

    @property
    def provider_type(self) -> str:
        """Type of provider (supabase, keycloak, azure_ad, ldap)."""
        ...

    async def authenticate(
        self,
        credentials: dict,
    ) -> AuthenticationResult:
        """Authenticate using credentials.

        Args:
            credentials: Provider-specific credentials
                Common formats:
                - password: {"email": "...", "password": "..."}
                - api_key: {"api_key": "..."}
                - token: {"token": "..."}

        Returns:
            AuthenticationResult with principal if successful
        """
        ...

    async def verify_token(self, token: str) -> Principal | None:
        """Verify an authentication token.

        Args:
            token: JWT or other authentication token

        Returns:
            Principal if token is valid, None otherwise
        """
        ...

    async def get_principal(self, principal_id: str) -> Principal | None:
        """Get a principal by ID.

        Args:
            principal_id: Unique principal identifier

        Returns:
            Principal if found, None otherwise
        """
        ...

    async def create_principal(
        self,
        identity_type: IdentityType,
        display_name: str,
        email: str | None = None,
        roles: list[str] | None = None,
        attributes: dict[str, str] | None = None,
    ) -> Principal:
        """Create a new principal.

        Args:
            identity_type: Type of identity
            display_name: Human-readable name
            email: Email address
            roles: Initial roles
            attributes: Additional attributes

        Returns:
            Created principal
        """
        ...

    async def update_principal(
        self,
        principal_id: str,
        display_name: str | None = None,
        roles: list[str] | None = None,
        attributes: dict[str, str] | None = None,
    ) -> Principal:
        """Update a principal.

        Args:
            principal_id: Principal to update
            display_name: New display name
            roles: New roles
            attributes: New attributes

        Returns:
            Updated principal
        """
        ...

    async def suspend_principal(self, principal_id: str) -> bool:
        """Suspend a principal.

        Args:
            principal_id: Principal to suspend

        Returns:
            True if suspended successfully
        """
        ...

    async def revoke_principal(self, principal_id: str) -> bool:
        """Permanently revoke a principal.

        Args:
            principal_id: Principal to revoke

        Returns:
            True if revoked successfully
        """
        ...

    async def create_session(self, principal: Principal) -> Session:
        """Create a new session for a principal.

        Args:
            principal: Authenticated principal

        Returns:
            New session
        """
        ...

    async def get_session(self, session_id: str) -> Session | None:
        """Get a session by ID.

        Args:
            session_id: Session identifier

        Returns:
            Session if found, None otherwise
        """
        ...

    async def refresh_session(self, session_id: str) -> Session:
        """Refresh an existing session.

        Args:
            session_id: Session to refresh

        Returns:
            Refreshed session
        """
        ...

    async def invalidate_session(self, session_id: str) -> bool:
        """Invalidate a session.

        Args:
            session_id: Session to invalidate

        Returns:
            True if invalidated successfully
        """
        ...

    async def invalidate_all_sessions(self, principal_id: str) -> int:
        """Invalidate all sessions for a principal.

        Args:
            principal_id: Principal whose sessions to invalidate

        Returns:
            Number of sessions invalidated
        """
        ...


# =============================================================================
# Events
# =============================================================================


@dataclass(frozen=True)
class IdentityEvent:
    """Base class for identity events."""

    event_id: str
    principal_id: str | None
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    correlation_id: str | None = None


@dataclass(frozen=True)
class AuthenticationSucceeded(IdentityEvent):
    """Fired when authentication succeeds."""

    session_id: str | None = None
    method: str | None = None


@dataclass(frozen=True)
class AuthenticationFailed(IdentityEvent):
    """Fired when authentication fails."""

    error_code: str | None = None
    error_message: str | None = None
    ip_address: str | None = None


@dataclass(frozen=True)
class PrincipalCreated(IdentityEvent):
    """Fired when a new principal is created."""

    identity_type: IdentityType
    display_name: str


@dataclass(frozen=True)
class PrincipalSuspended(IdentityEvent):
    """Fired when a principal is suspended."""


@dataclass(frozen=True)
class PrincipalRevoked(IdentityEvent):
    """Fired when a principal is permanently revoked."""


@dataclass(frozen=True)
class SessionCreated(IdentityEvent):
    """Fired when a new session is created."""

    session_id: str


@dataclass(frozen=True)
class SessionInvalidated(IdentityEvent):
    """Fired when a session is invalidated."""

    session_id: str
    reason: str | None = None
