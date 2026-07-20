"""
Principal Contract.

Philosophy: EREN must manage identity data.
Principals are separate from authentication and sessions.
"""

from __future__ import annotations

from abc import abstractmethod
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


class PrincipalStatus(Enum):
    """Status of a principal."""

    ACTIVE = "active"
    SUSPENDED = "suspended"
    PENDING = "pending"
    REVOKED = "revoked"


class PrincipalType(Enum):
    """Subtypes for human principals."""

    PHYSICIAN = "physician"
    NURSE = "nurse"
    RESIDENT = "resident"
    ADMINISTRATOR = "administrator"
    PATIENT = "patient"
    VISITOR = "visitor"
    BIOMEDICAL_ENGINEER = "biomedical_engineer"
    OTHER = "other"


@dataclass(frozen=True)
class Principal:
    """Represents an identity in the system.

    Principal is the core identity data model.
    It does NOT contain authentication state (tokens, sessions).
    It does NOT contain authorization data (roles are references only).

    Philosophy: Principals are identity facts, not session state.
    """

    # Core identity
    principal_id: str
    identity_type: IdentityType
    status: PrincipalStatus

    # Display information
    display_name: str
    email: str | None = None
    phone: str | None = None
    avatar_url: str | None = None

    # Human-specific
    principal_type: PrincipalType | None = None  # physician, nurse, etc.
    department: str | None = None
    specialization: str | None = None  # cardiology, neurology, etc.
    license_number: str | None = None  # medical license

    # Device-specific
    device_type: str | None = None
    manufacturer: str | None = None
    model: str | None = None
    serial_number: str | None = None

    # System-specific
    service_name: str | None = None
    api_version: str | None = None

    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    last_login: datetime | None = None
    created_by: str | None = None

    # Attributes (flexible key-value pairs)
    attributes: tuple[tuple[str, str], ...] = field(default_factory=tuple)

    # Roles (references only, actual role data is in AuthorizationProvider)
    roles: tuple[str, ...] = field(default_factory=tuple)

    # External identifiers
    external_ids: tuple[tuple[str, str], ...] = field(
        default_factory=tuple
    )  # (provider, id) pairs

    # Trust and risk
    trust_level: str | None = None  # "verified", "pending", "unverified"
    risk_flags: tuple[str, ...] = field(default_factory=tuple)

    def is_active(self) -> bool:
        """Check if principal is active."""
        return self.status == PrincipalStatus.ACTIVE

    def is_human(self) -> bool:
        """Check if principal is a human."""
        return self.identity_type == IdentityType.HUMAN

    def is_device(self) -> bool:
        """Check if principal is a device."""
        return self.identity_type == IdentityType.DEVICE

    def has_role(self, role_id: str) -> bool:
        """Check if principal has a specific role."""
        return role_id in self.roles


@dataclass(frozen=True)
class PrincipalQuery:
    """Query parameters for searching principals."""

    identity_type: IdentityType | None = None
    principal_type: PrincipalType | None = None
    status: PrincipalStatus | None = None
    department: str | None = None
    search: str | None = None  # Search in name, email
    role: str | None = None
    created_after: datetime | None = None
    created_before: datetime | None = None
    limit: int = 100
    offset: int = 0


@dataclass(frozen=True)
class PrincipalQueryResult:
    """Result of a principal query."""

    principals: tuple[Principal, ...]
    total_count: int
    offset: int
    limit: int


@dataclass(frozen=True)
class PrincipalProfile:
    """Extended profile information for a principal."""

    principal: Principal
    permissions: tuple[str, ...]  # Resolved from roles
    groups: tuple[str, ...]
    recent_activity: tuple[dict, ...]  # Activity summary
    risk_assessment: dict | None


# =============================================================================
# Provider Interface
# =============================================================================


class PrincipalProvider(Protocol):
    """Contract for principal management services.

    This contract is RESPONSIBLE ONLY for:
    - Creating and managing principal identity data
    - Profile information
    - Principal lifecycle (create, update, suspend, revoke)
    - Principal queries

    This contract is NOT responsible for:
    - Authentication (see AuthenticationProvider)
    - Sessions (see SessionProvider)
    - Roles and permissions (see AuthorizationProvider)

    Philosophy: Principals are identity data, not authentication state.
    A principal exists even when not logged in.
    """

    @property
    def provider_id(self) -> str:
        """Unique identifier for this provider."""
        ...

    async def create_principal(
        self,
        identity_type: IdentityType,
        display_name: str,
        email: str | None = None,
        principal_type: PrincipalType | None = None,
        roles: list[str] | None = None,
        attributes: dict[str, str] | None = None,
        created_by: str | None = None,
        **kwargs,
    ) -> Principal:
        """Create a new principal.

        Args:
            identity_type: Type of identity
            display_name: Human-readable name
            email: Email address
            principal_type: Subtype for humans
            roles: Initial roles to assign
            attributes: Additional attributes
            created_by: Principal who created this

        Returns:
            Created principal
        """
        ...

    async def get_principal(
        self,
        principal_id: str,
    ) -> Principal | None:
        """Get a principal by ID.

        Args:
            principal_id: Principal identifier

        Returns:
            Principal if found, None otherwise
        """
        ...

    async def get_principal_by_email(
        self,
        email: str,
    ) -> Principal | None:
        """Get a principal by email.

        Args:
            email: Email address

        Returns:
            Principal if found, None otherwise
        """
        ...

    async def update_principal(
        self,
        principal_id: str,
        display_name: str | None = None,
        email: str | None = None,
        phone: str | None = None,
        avatar_url: str | None = None,
        department: str | None = None,
        specialization: str | None = None,
        attributes: dict[str, str] | None = None,
        **kwargs,
    ) -> Principal:
        """Update principal data.

        Args:
            principal_id: Principal to update
            display_name: New display name
            email: New email
            phone: New phone
            avatar_url: New avatar URL
            department: New department
            specialization: New specialization
            attributes: Updated attributes

        Returns:
            Updated principal
        """
        ...

    async def update_last_login(
        self,
        principal_id: str,
    ) -> bool:
        """Update the last login timestamp.

        Args:
            principal_id: Principal who logged in

        Returns:
            True if updated successfully
        """
        ...

    async def suspend_principal(
        self,
        principal_id: str,
        reason: str | None = None,
        suspended_by: str | None = None,
    ) -> bool:
        """Suspend a principal.

        Suspended principals cannot authenticate but data is preserved.

        Args:
            principal_id: Principal to suspend
            reason: Reason for suspension
            suspended_by: Principal who suspended

        Returns:
            True if suspended successfully
        """
        ...

    async def reactivate_principal(
        self,
        principal_id: str,
        reactivated_by: str | None = None,
    ) -> bool:
        """Reactivate a suspended principal.

        Args:
            principal_id: Principal to reactivate
            reactivated_by: Principal who reactivated

        Returns:
            True if reactivated successfully
        """
        ...

    async def revoke_principal(
        self,
        principal_id: str,
        reason: str | None = None,
        revoked_by: str | None = None,
    ) -> bool:
        """Permanently revoke a principal.

        Revoked principals cannot be reactivated.

        Args:
            principal_id: Principal to revoke
            reason: Reason for revocation
            revoked_by: Principal who revoked

        Returns:
            True if revoked successfully
        """
        ...

    async def assign_role(
        self,
        principal_id: str,
        role_id: str,
    ) -> bool:
        """Assign a role to a principal.

        Role data is managed by AuthorizationProvider.
        This only updates the principal's role references.

        Args:
            principal_id: Principal to assign role to
            role_id: Role to assign

        Returns:
            True if assigned successfully
        """
        ...

    async def remove_role(
        self,
        principal_id: str,
        role_id: str,
    ) -> bool:
        """Remove a role from a principal.

        Args:
            principal_id: Principal to remove role from
            role_id: Role to remove

        Returns:
            True if removed successfully
        """
        ...

    async def query_principals(
        self,
        query: PrincipalQuery,
    ) -> PrincipalQueryResult:
        """Query principals with filters.

        Args:
            query: Query parameters

        Returns:
            Matching principals with pagination
        """
        ...

    async def get_principal_profile(
        self,
        principal_id: str,
    ) -> PrincipalProfile | None:
        """Get extended profile for a principal.

        This resolves roles to permissions and fetches related data.

        Args:
            principal_id: Principal identifier

        Returns:
            Extended profile if found
        """
        ...

    async def add_external_id(
        self,
        principal_id: str,
        provider: str,
        external_id: str,
    ) -> bool:
        """Add an external identity provider ID.

        Args:
            principal_id: Principal identifier
            provider: External provider name
            external_id: ID in that provider

        Returns:
            True if added successfully
        """
        ...

    async def set_trust_level(
        self,
        principal_id: str,
        trust_level: str,
    ) -> bool:
        """Set the trust level for a principal.

        Args:
            principal_id: Principal identifier
            trust_level: New trust level

        Returns:
            True if set successfully
        """
        ...

    async def add_risk_flag(
        self,
        principal_id: str,
        flag: str,
    ) -> bool:
        """Add a risk flag to a principal.

        Args:
            principal_id: Principal identifier
            flag: Risk flag to add

        Returns:
            True if added successfully
        """
        ...


# =============================================================================
# Events
# =============================================================================


@dataclass(frozen=True)
class PrincipalEvent:
    """Base class for principal events."""

    event_id: str
    principal_id: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True)
class PrincipalCreated(PrincipalEvent):
    """Fired when a new principal is created."""

    identity_type: IdentityType
    principal_type: PrincipalType | None
    created_by: str | None


@dataclass(frozen=True)
class PrincipalUpdated(PrincipalEvent):
    """Fired when principal data is updated."""

    changes: tuple[tuple[str, str], ...]  # (field, old_value) pairs


@dataclass(frozen=True)
class PrincipalSuspended(PrincipalEvent):
    """Fired when a principal is suspended."""

    reason: str | None
    suspended_by: str | None


@dataclass(frozen=True)
class PrincipalReactivated(PrincipalEvent):
    """Fired when a suspended principal is reactivated."""

    reactivated_by: str | None


@dataclass(frozen=True)
class PrincipalRevoked(PrincipalEvent):
    """Fired when a principal is permanently revoked."""

    reason: str | None
    revoked_by: str | None


@dataclass(frozen=True)
class RoleAssignedToPrincipal(PrincipalEvent):
    """Fired when a role is assigned to a principal."""

    role_id: str
    assigned_by: str | None


@dataclass(frozen=True)
class RoleRemovedFromPrincipal(PrincipalEvent):
    """Fired when a role is removed from a principal."""

    role_id: str
    removed_by: str | None
