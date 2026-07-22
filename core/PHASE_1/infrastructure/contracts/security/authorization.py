"""
Authorization Capability Contract.

Philosophy: EREN controls what each identity can do.
Authorization follows authentication - no access without identity.
"""

from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from core.PHASE_1.infrastructure.contracts.security.identity import Principal


# =============================================================================
# Types
# =============================================================================


class ResourceType(Enum):
    """Types of resources that can be protected."""

    PATIENT = "patient"
    DEVICE = "device"
    CLINICAL_DATA = "clinical_data"
    DEVICE_DATA = "device_data"
    CONFIGURATION = "configuration"
    AUDIT_LOG = "audit_log"
    REPORT = "report"
    POLICY = "policy"
    USER = "user"
    SESSION = "session"
    KNOWLEDGE = "knowledge"
    ALERT = "alert"
    MAINTENANCE = "maintenance"


class Action(Enum):
    """Actions that can be performed on resources."""

    # CRUD actions
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"

    # Clinical actions
    VIEW_PATIENT = "view_patient"
    EDIT_PATIENT = "edit_patient"
    VIEW_CLINICAL_DATA = "view_clinical_data"
    ADD_CLINICAL_DATA = "add_clinical_data"

    # Device actions
    VIEW_DEVICE = "view_device"
    CONFIGURE_DEVICE = "configure_device"
    CONTROL_DEVICE = "control_device"
    VIEW_DEVICE_DATA = "view_device_data"

    # Administrative actions
    MANAGE_USERS = "manage_users"
    MANAGE_ROLES = "manage_roles"
    VIEW_AUDIT = "view_audit"
    CONFIGURE_SYSTEM = "configure_system"

    # Biomedical actions
    SCHEDULE_MAINTENANCE = "schedule_maintenance"
    PERFORM_MAINTENANCE = "perform_maintenance"
    VIEW_MAINTENANCE_HISTORY = "view_maintenance_history"


class Effect(Enum):
    """Effect of an authorization decision."""

    ALLOW = "allow"
    DENY = "deny"


@dataclass(frozen=True)
class Resource:
    """Represents a resource that can be protected."""

    resource_type: ResourceType
    resource_id: str | None = None  # None means all resources of this type
    attributes: tuple[tuple[str, str], ...] = field(default_factory=tuple)

    def matches(self, other: Resource) -> bool:
        """Check if this resource matches another resource."""
        if self.resource_type != other.resource_type:
            return False
        if self.resource_id is None:
            return True  # Matches all resources of this type
        return self.resource_id == other.resource_id


@dataclass(frozen=True)
class AuthorizationRequest:
    """Request for authorization decision."""

    principal: "Principal"
    action: Action
    resource: Resource
    context: tuple[tuple[str, str], ...] = field(default_factory=tuple)  # Additional context
    requested_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True)
class AuthorizationDecision:
    """Decision from the authorization engine."""

    request: AuthorizationRequest
    effect: Effect
    reason: str
    obligations: tuple[str, ...] = field(default_factory=tuple)  # e.g., "audit", "notify"
    evaluated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    decision_id: str | None = None

    @property
    def is_allowed(self) -> bool:
        """Check if the decision allows the action."""
        return self.effect == Effect.ALLOW


@dataclass(frozen=True)
class Role:
    """Represents a role with associated permissions."""

    role_id: str
    name: str
    description: str
    permissions: tuple["Permission", ...] = field(default_factory=tuple)
    parent_role: str | None = None  # Role inheritance
    metadata: tuple[tuple[str, str], ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class Permission:
    """Represents a permission to perform an action on a resource."""

    permission_id: str
    action: Action
    resource_type: ResourceType
    resource_id_pattern: str | None = None  # Glob pattern for resource IDs
    conditions: tuple[str, ...] = field(default_factory=tuple)  # e.g., "own_only", "department_only"
    metadata: tuple[tuple[str, str], ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class Policy:
    """Represents an authorization policy."""

    policy_id: str
    name: str
    description: str
    priority: int = 0  # Higher priority policies evaluated first
    rules: tuple["PolicyRule", ...] = field(default_factory=tuple)
    target_roles: tuple[str, ...] | None = None  # None means all roles
    enabled: bool = True
    metadata: tuple[tuple[str, str], ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class PolicyRule:
    """A single rule within a policy."""

    rule_id: str
    effect: Effect
    actions: tuple[Action, ...] | None = None  # None means all actions
    resource_types: tuple[ResourceType, ...] | None = None  # None means all types
    conditions: tuple[str, ...] = field(default_factory=tuple)  # e.g., "time_between_8_18"


# =============================================================================
# Provider Interface
# =============================================================================


class AuthorizationProvider(Protocol):
    """Contract for authorization services.

    EREN uses RBAC + ABAC:
    - RBAC: Roles with permissions
    - ABAC: Context-aware policies

    The runtime checks authorization by calling can_perform().
    """

    @property
    def provider_id(self) -> str:
        """Unique identifier for this provider."""
        ...

    async def can_perform(
        self,
        request: AuthorizationRequest,
    ) -> AuthorizationDecision:
        """Check if a principal can perform an action on a resource.

        This is the main authorization check.

        Args:
            request: The authorization request

        Returns:
            AuthorizationDecision with effect (ALLOW or DENY)
        """
        ...

    async def get_role(self, role_id: str) -> Role | None:
        """Get a role by ID.

        Args:
            role_id: Role identifier

        Returns:
            Role if found, None otherwise
        """
        ...

    async def get_principal_roles(self, principal_id: str) -> tuple[Role, ...]:
        """Get all roles assigned to a principal.

        Args:
            principal_id: Principal identifier

        Returns:
            Tuple of assigned roles
        """
        ...

    async def assign_role(self, principal_id: str, role_id: str) -> bool:
        """Assign a role to a principal.

        Args:
            principal_id: Principal to assign role to
            role_id: Role to assign

        Returns:
            True if assigned successfully
        """
        ...

    async def remove_role(self, principal_id: str, role_id: str) -> bool:
        """Remove a role from a principal.

        Args:
            principal_id: Principal to remove role from
            role_id: Role to remove

        Returns:
            True if removed successfully
        """
        ...

    async def create_role(
        self,
        name: str,
        description: str,
        permissions: list[Permission] | None = None,
        parent_role: str | None = None,
    ) -> Role:
        """Create a new role.

        Args:
            name: Role name
            description: Role description
            permissions: Initial permissions
            parent_role: Parent role for inheritance

        Returns:
            Created role
        """
        ...

    async def update_role(
        self,
        role_id: str,
        name: str | None = None,
        description: str | None = None,
        permissions: list[Permission] | None = None,
    ) -> Role:
        """Update a role.

        Args:
            role_id: Role to update
            name: New name
            description: New description
            permissions: New permissions

        Returns:
            Updated role
        """
        ...

    async def delete_role(self, role_id: str) -> bool:
        """Delete a role.

        Args:
            role_id: Role to delete

        Returns:
            True if deleted successfully
        """
        ...

    async def get_policy(self, policy_id: str) -> Policy | None:
        """Get a policy by ID.

        Args:
            policy_id: Policy identifier

        Returns:
            Policy if found, None otherwise
        """
        ...

    async def evaluate_policy(
        self,
        policy_id: str,
        request: AuthorizationRequest,
    ) -> AuthorizationDecision:
        """Evaluate a specific policy for a request.

        Args:
            policy_id: Policy to evaluate
            request: Authorization request

        Returns:
            Decision from this policy
        """
        ...

    async def create_policy(
        self,
        name: str,
        description: str,
        rules: list[PolicyRule],
        priority: int = 0,
        target_roles: list[str] | None = None,
    ) -> Policy:
        """Create a new policy.

        Args:
            name: Policy name
            description: Policy description
            rules: Policy rules
            priority: Policy priority
            target_roles: Roles this policy applies to

        Returns:
            Created policy
        """
        ...

    async def enable_policy(self, policy_id: str) -> bool:
        """Enable a policy.

        Args:
            policy_id: Policy to enable

        Returns:
            True if enabled successfully
        """
        ...

    async def disable_policy(self, policy_id: str) -> bool:
        """Disable a policy.

        Args:
            policy_id: Policy to disable

        Returns:
            True if disabled successfully
        """
        ...


# =============================================================================
# Default Roles (Hospital-specific)
# =============================================================================


@dataclass(frozen=True)
class DefaultRoles:
    """Standard roles for hospital environments."""

    PHYSICIAN = "physician"
    NURSE = "nurse"
    RESIDENT = "resident"
    BIOMEDICAL_ENGINEER = "biomedical_engineer"
    ADMINISTRATOR = "administrator"
    PATIENT = "patient"
    VISITOR = "visitor"
    SYSTEM_ADMIN = "system_admin"
    AUDITOR = "auditor"


# =============================================================================
# Events
# =============================================================================


@dataclass(frozen=True)
class AuthorizationEvent:
    """Base class for authorization events."""

    event_id: str
    principal_id: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    correlation_id: str | None = None


@dataclass(frozen=True)
class AuthorizationGranted(AuthorizationEvent):
    """Fired when authorization is granted."""

    action: Action
    resource_type: ResourceType
    resource_id: str | None


@dataclass(frozen=True)
class AuthorizationDenied(AuthorizationEvent):
    """Fired when authorization is denied."""

    action: Action
    resource_type: ResourceType
    resource_id: str | None
    reason: str


@dataclass(frozen=True)
class RoleAssigned(AuthorizationEvent):
    """Fired when a role is assigned to a principal."""

    role_id: str


@dataclass(frozen=True)
class RoleRemoved(AuthorizationEvent):
    """Fired when a role is removed from a principal."""

    role_id: str


@dataclass(frozen=True)
class PolicyCreated(AuthorizationEvent):
    """Fired when a new policy is created."""

    policy_id: str
    policy_name: str
