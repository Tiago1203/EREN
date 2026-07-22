"""
Session Contract.

Philosophy: EREN must track active interactions.
Sessions are separate from authentication and principal management.
"""

from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from core.PHASE_1.infrastructure.contracts.security.authentication import Principal


# =============================================================================
# Types
# =============================================================================


class SessionStatus(Enum):
    """Status of a session."""

    ACTIVE = "active"
    EXPIRED = "expired"
    INVALIDATED = "invalidated"
    LOCKED = "locked"


class SessionType(Enum):
    """Types of sessions."""

    USER = "user"
    API = "api"
    DEVICE = "device"
    SYSTEM = "system"


@dataclass(frozen=True)
class Session:
    """Represents an active session.

    A session is a temporary state of authenticated interaction.
    Sessions are created from authenticated Principals.
    """

    session_id: str
    principal_id: str
    session_type: SessionType
    status: SessionStatus

    # Temporal
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    last_activity: datetime = field(default_factory=lambda: datetime.now(UTC))
    expires_at: datetime | None = None

    # Context
    ip_address: str | None = None
    user_agent: str | None = None
    device_id: str | None = None
    location: str | None = None

    # Security
    token_id: str | None = None
    refresh_token_id: str | None = None

    # Metadata
    metadata: tuple[tuple[str, str], ...] = field(default_factory=tuple)

    def is_active(self) -> bool:
        """Check if session is still active."""
        if self.status != SessionStatus.ACTIVE:
            return False
        if self.expires_at and datetime.now(UTC) > self.expires_at:
            return False
        return True

    def is_expired(self) -> bool:
        """Check if session has expired."""
        if self.expires_at is None:
            return False
        return datetime.now(UTC) > self.expires_at

    def time_until_expiry(self) -> float | None:
        """Get seconds until expiry. None if no expiry."""
        if self.expires_at is None:
            return None
        delta = self.expires_at - datetime.now(UTC)
        return max(0, delta.total_seconds())


@dataclass(frozen=True)
class SessionQuery:
    """Query parameters for searching sessions."""

    principal_id: str | None = None
    session_type: SessionType | None = None
    status: SessionStatus | None = None
    ip_address: str | None = None
    created_after: datetime | None = None
    created_before: datetime | None = None
    active_within_seconds: int | None = None
    limit: int = 100
    offset: int = 0


@dataclass(frozen=True)
class SessionQueryResult:
    """Result of a session query."""

    sessions: tuple[Session, ...]
    total_count: int
    offset: int
    limit: int


@dataclass(frozen=True)
class SessionMetrics:
    """Metrics about session usage."""

    total_sessions: int
    active_sessions: int
    expired_sessions: int
    invalidated_sessions: int
    average_duration_seconds: float | None
    concurrent_sessions: int


# =============================================================================
# Provider Interface
# =============================================================================


class SessionProvider(Protocol):
    """Contract for session management services.

    This contract is RESPONSIBLE ONLY for:
    - Creating sessions from authenticated principals
    - Tracking active sessions
    - Refreshing sessions
    - Invalidating sessions
    - Session lifecycle management

    This contract is NOT responsible for:
    - Authentication (see AuthenticationProvider)
    - Principal data (it receives Principal, stores only session data)
    - Authorization (see AuthorizationProvider)

    Philosophy: Sessions are state, not identity. They come and go.
    """

    @property
    def provider_id(self) -> str:
        """Unique identifier for this provider."""
        ...

    @property
    def default_ttl_seconds(self) -> int:
        """Default session TTL in seconds."""
        ...

    async def create_session(
        self,
        principal: "Principal",
        session_type: SessionType = SessionType.USER,
        ttl_seconds: int | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> Session:
        """Create a new session from an authenticated principal.

        Args:
            principal: Authenticated principal from AuthenticationProvider
            session_type: Type of session
            ttl_seconds: Time to live (uses default if None)
            ip_address: Client IP address
            user_agent: Client user agent

        Returns:
            New session
        """
        ...

    async def get_session(
        self,
        session_id: str,
    ) -> Session | None:
        """Get a session by ID.

        Args:
            session_id: Session identifier

        Returns:
            Session if found and active, None otherwise
        """
        ...

    async def get_session_by_token(
        self,
        token_id: str,
    ) -> Session | None:
        """Get a session by its token ID.

        Args:
            token_id: Token identifier

        Returns:
            Session if found, None otherwise
        """
        ...

    async def refresh_session(
        self,
        session_id: str,
        extend_ttl: bool = True,
    ) -> Session:
        """Refresh an existing session.

        Args:
            session_id: Session to refresh
            extend_ttl: Whether to extend the TTL

        Returns:
            Refreshed session

        Raises:
            SessionNotFoundError: If session doesn't exist
            SessionExpiredError: If session has expired
        """
        ...

    async def update_activity(
        self,
        session_id: str,
    ) -> Session:
        """Update last activity timestamp.

        This should be called on every request to track session usage.

        Args:
            session_id: Session to update

        Returns:
            Updated session
        """
        ...

    async def invalidate_session(
        self,
        session_id: str,
        reason: str | None = None,
    ) -> bool:
        """Invalidate a session.

        Args:
            session_id: Session to invalidate
            reason: Reason for invalidation

        Returns:
            True if invalidated successfully
        """
        ...

    async def invalidate_all_principal_sessions(
        self,
        principal_id: str,
        except_session_id: str | None = None,
    ) -> int:
        """Invalidate all sessions for a principal.

        Args:
            principal_id: Principal whose sessions to invalidate
            except_session_id: Keep this session active (e.g., current session)

        Returns:
            Number of sessions invalidated
        """
        ...

    async def query_sessions(
        self,
        query: SessionQuery,
    ) -> SessionQueryResult:
        """Query sessions with filters.

        Args:
            query: Query parameters

        Returns:
            Matching sessions with pagination
        """
        ...

    async def get_active_session_count(
        self,
        principal_id: str | None = None,
    ) -> int:
        """Get count of active sessions.

        Args:
            principal_id: If provided, count for specific principal

        Returns:
            Number of active sessions
        """
        ...

    async def get_session_metrics(
        self,
        since: datetime | None = None,
    ) -> SessionMetrics:
        """Get session usage metrics.

        Args:
            since: Calculate metrics since this time

        Returns:
            Session metrics
        """
        ...

    async def cleanup_expired_sessions(self) -> int:
        """Remove expired sessions from storage.

        This is a maintenance operation.

        Returns:
            Number of sessions cleaned up
        """
        ...


# =============================================================================
# Events
# =============================================================================


@dataclass(frozen=True)
class SessionEvent:
    """Base class for session events."""

    event_id: str
    session_id: str
    principal_id: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True)
class SessionCreated(SessionEvent):
    """Fired when a new session is created."""

    session_type: SessionType
    ip_address: str | None = None


@dataclass(frozen=True)
class SessionRefreshed(SessionEvent):
    """Fired when a session is refreshed."""

    new_expires_at: datetime | None


@dataclass(frozen=True)
class SessionActivityUpdated(SessionEvent):
    """Fired when session activity is updated."""

    pass


@dataclass(frozen=True)
class SessionInvalidated(SessionEvent):
    """Fired when a session is invalidated."""

    reason: str | None = None
    invalidator_type: str | None = None  # "user", "admin", "system", "expired"


@dataclass(frozen=True)
class SessionExpired(SessionEvent):
    """Fired when a session expires."""
