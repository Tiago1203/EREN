"""Base Entity for EREN domain.

Entities are objects with a distinct identity that runs through time
and different representations. They are the primary building blocks
of the domain model.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from ..errors import ConcurrencyError
from ..primitives import EntityId

if TYPE_CHECKING:
    from ..events import DomainEvent

    pass


def _default_version() -> int:
    """Default factory for version field — always returns 1."""
    return 1


@dataclass(eq=False)
class BaseEntity:
    """Base class for all entities in EREN domain.

    Entities have a unique identity that persists through changes.
    They track their own state changes and publish domain events.

    Key principles:
    1. Entities are identified by a unique ID
    2. Entities track their own version for optimistic locking
    3. Entities collect domain events until flush
    4. Entities validate their state on initialization and mutation
    5. Entities use private __setattr__ to enforce invariants

    Attributes:
        id: Unique identifier for the entity.
        version: Current version for optimistic locking.
        created_at: When the entity was created.
        updated_at: When the entity was last modified.

    Usage:
        @dataclass(eq=False)
        class Incident(BaseEntity):
            device_id: EntityId
            priority: Priority
            status: IncidentStatus

            def __post_init__(self) -> None:
                super().__init__()
                self._validate()

            def _validate(self) -> None:
                if self.priority is None:
                    raise ValueError("Priority is required")

    Anti-patterns to avoid:
        ❌ Don't expose public setters (use methods)
        ❌ Don't allow direct attribute modification
        ❌ Don't skip validation in __post_init__
        ❌ Don't use entities for value-only concepts (use Value Objects)
        ❌ Don't create entities with circular dependencies
    """

    id: EntityId = field(kw_only=True)
    version: int = field(default_factory=_default_version, kw_only=True)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC), kw_only=True)
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC), kw_only=True)
    _pending_events: list["DomainEvent"] = field(default_factory=list, init=False, repr=False, kw_only=True)

    def __post_init__(self) -> None:
        # Lock the entity after __post_init__
        object.__setattr__(self, "_locked", True)

    def _mark_created(self) -> None:
        """Mark entity as created. Called by factory methods after entity creation."""
        self._unlock_for_mutation()
        self.version = 1
        self.updated_at = datetime.now(UTC)
        self._relock_after_mutation()

    def _mark_updated(self) -> None:
        """Mark entity as updated. Called after any state change."""
        self._unlock_for_mutation()
        self.version += 1
        self.updated_at = datetime.now(UTC)
        self._relock_after_mutation()

    def __setattr__(self, name: str, value: Any) -> None:
        if getattr(self, "_locked", False) and name not in ("version", "updated_at", "_pending_events"):
            msg = f"Cannot modify attribute '{name}' directly. Use entity methods."
            raise AttributeError(msg)
        object.__setattr__(self, name, value)

    def _unlock_for_mutation(self) -> None:
        """Temporarily unlock entity for mutation. Internal use only."""
        object.__setattr__(self, "_locked", False)

    def _relock_after_mutation(self) -> None:
        """Relock entity after mutation. Internal use only."""
        object.__setattr__(self, "_locked", True)
        self.version += 1
        self.updated_at = datetime.now(UTC)

    def _increment_version(self) -> None:
        """Increment version for optimistic locking."""
        self.version += 1
        self.updated_at = datetime.now(UTC)

    def add_event(self, event: DomainEvent) -> None:
        """Add a domain event to be published."""
        self._pending_events.append(event)

    def pop_events(self) -> list[DomainEvent]:
        """Get and clear all pending domain events."""
        events = self._pending_events.copy()
        self._pending_events.clear()
        return events

    def has_pending_events(self) -> bool:
        """Check if entity has pending events."""
        return len(self._pending_events) > 0

    def _assert_version(self, expected_version: int) -> None:
        """Assert that the current version matches expected version."""
        if self.version != expected_version:
            raise ConcurrencyError(
                entity_type=self.__class__.__name__,
                entity_id=str(self.id),
                expected_version=expected_version,
                actual_version=self.version,
            )

    def to_dict(self) -> dict[str, Any]:
        """Convert entity to dictionary for persistence."""
        return {
            "id": str(self.id),
            "version": self.version,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BaseEntity):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)


@dataclass(eq=False)
class AggregateRoot(BaseEntity):
    """Base class for aggregate roots.

    Aggregate roots are the only entities that external components
    can reference. They encapsulate the entire aggregate and ensure
    its consistency.

    Rules:
    1. External components only reference the aggregate root
    2. The aggregate root controls all state changes within the aggregate
    3. All domain events are published through the aggregate root
    4. The aggregate root is responsible for the aggregate's invariants

    Usage:
        @dataclass(eq=False)
        class Incident(AggregateRoot):
            device_id: EntityId
            status: IncidentStatus
            _investigation: Investigation

            def change_priority(self, new_priority: Priority, expected_version: int) -> None:
                self._assert_version(expected_version)
                self._unlock_for_mutation()
                self._priority = new_priority
                self._relock_after_mutation()
                self.add_event(IncidentPriorityChanged(...))
    """

    pass
