"""Conflict resolver for EREN Multi-Agent Collaboration Engine.

Resolves conflicts between agents.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass


class ConflictType(str):
    """Types of conflicts."""
    RESOURCE = "resource"
    DATA = "data"
    DECISION = "decision"
    PRIORITY = "priority"
    TIMING = "timing"
    COMPETING = "competing"


@dataclass
class Conflict:
    """A conflict between agents."""

    conflict_id: str
    session_id: str
    conflict_type: ConflictType
    description: str

    # Parties involved
    parties: list[str] = field(default_factory=list)

    # Context
    context: dict = field(default_factory=dict)

    # Resolution
    resolution: Any = None
    resolved_by: str = ""
    resolved_at: datetime | None = None

    # Status
    is_resolved: bool = False

    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def create(
        cls,
        session_id: str,
        conflict_type: ConflictType,
        description: str,
        parties: list[str],
        context: dict | None = None,
    ) -> Conflict:
        """Create a new conflict."""
        return cls(
            conflict_id=str(uuid.uuid4()),
            session_id=session_id,
            conflict_type=conflict_type,
            description=description,
            parties=parties,
            context=context or {},
        )


@dataclass
class Resolution:
    """A conflict resolution."""

    resolution_id: str
    conflict_id: str
    strategy: str
    result: Any

    # Metadata
    metadata: dict = field(default_factory=dict)

    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class ConflictResolver:
    """Resolves conflicts between agents.

    The Conflict Resolver does NOT:
    - Execute tasks
    - Know about implementations

    It ONLY:
    - Detects conflicts
    - Applies resolution strategies
    - Tracks resolutions
    """

    def __init__(self):
        """Initialize conflict resolver."""
        self._conflicts: dict[str, Conflict] = {}
        self._resolutions: dict[str, Resolution] = {}

    def create_conflict(
        self,
        session_id: str,
        conflict_type: ConflictType,
        description: str,
        parties: list[str],
        context: dict | None = None,
    ) -> Conflict:
        """Create a new conflict.

        Args:
            session_id: Session ID.
            conflict_type: Type of conflict.
            description: Conflict description.
            parties: List of party agent IDs.
            context: Additional context.

        Returns:
            Created conflict.
        """
        conflict = Conflict.create(
            session_id=session_id,
            conflict_type=conflict_type,
            description=description,
            parties=parties,
            context=context,
        )

        self._conflicts[conflict.conflict_id] = conflict
        return conflict

    def get_conflict(
        self,
        conflict_id: str,
    ) -> Conflict | None:
        """Get a conflict by ID.

        Args:
            conflict_id: Conflict ID.

        Returns:
            Conflict or None.
        """
        return self._conflicts.get(conflict_id)

    def get_session_conflicts(
        self,
        session_id: str,
        unresolved_only: bool = False,
    ) -> list[Conflict]:
        """Get all conflicts for a session.

        Args:
            session_id: Session ID.
            unresolved_only: Only return unresolved conflicts.

        Returns:
            List of conflicts.
        """
        conflicts = [
            c for c in self._conflicts.values()
            if c.session_id == session_id
        ]

        if unresolved_only:
            conflicts = [c for c in conflicts if not c.is_resolved]

        return conflicts

    def resolve(
        self,
        conflict_id: str,
        resolution: Any,
        resolved_by: str,
        strategy: str = "default",
    ) -> bool:
        """Resolve a conflict.

        Args:
            conflict_id: Conflict ID.
            resolution: Resolution value.
            resolved_by: Resolver agent ID.
            strategy: Resolution strategy used.

        Returns:
            True if resolved.
        """
        conflict = self._conflicts.get(conflict_id)
        if not conflict:
            return False

        conflict.resolution = resolution
        conflict.resolved_by = resolved_by
        conflict.resolved_at = datetime.now(timezone.utc)
        conflict.is_resolved = True

        # Record resolution
        self._resolutions[conflict_id] = Resolution(
            resolution_id=str(uuid.uuid4()),
            conflict_id=conflict_id,
            strategy=strategy,
            result=resolution,
        )

        return True

    def resolve_by_priority(
        self,
        conflict_id: str,
        priorities: dict[str, int],
        resolved_by: str = "system",
    ) -> bool:
        """Resolve by agent priority.

        Args:
            conflict_id: Conflict ID.
            priorities: Agent ID -> priority (higher = more important).
            resolved_by: Resolver agent ID.

        Returns:
            True if resolved.
        """
        conflict = self._conflicts.get(conflict_id)
        if not conflict:
            return False

        # Find highest priority party
        winner = max(conflict.parties, key=lambda p: priorities.get(p, 0))

        return self.resolve(
            conflict_id=conflict_id,
            resolution={"winner": winner, "losers": [p for p in conflict.parties if p != winner]},
            resolved_by=resolved_by,
            strategy="priority",
        )

    def resolve_by_majority(
        self,
        conflict_id: str,
        votes: dict[str, str],
        resolved_by: str = "system",
    ) -> bool:
        """Resolve by majority vote.

        Args:
            conflict_id: Conflict ID.
            votes: Agent ID -> vote.
            resolved_by: Resolver agent ID.

        Returns:
            True if resolved.
        """
        # Count votes
        vote_counts: dict[str, int] = {}
        for vote in votes.values():
            vote_counts[vote] = vote_counts.get(vote, 0) + 1

        # Find majority
        winner = max(vote_counts, key=vote_counts.get)

        return self.resolve(
            conflict_id=conflict_id,
            resolution={"winner": winner, "vote_counts": vote_counts},
            resolved_by=resolved_by,
            strategy="majority",
        )

    def resolve_by_first_come(
        self,
        conflict_id: str,
        timestamps: dict[str, datetime],
        resolved_by: str = "system",
    ) -> bool:
        """Resolve by first come first served.

        Args:
            conflict_id: Conflict ID.
            timestamps: Agent ID -> timestamp.
            resolved_by: Resolver agent ID.

        Returns:
            True if resolved.
        """
        conflict = self._conflicts.get(conflict_id)
        if not conflict:
            return False

        # Find earliest
        winner = min(
            conflict.parties,
            key=lambda p: timestamps.get(p, datetime.max).timestamp()
        )

        return self.resolve(
            conflict_id=conflict_id,
            resolution={"winner": winner},
            resolved_by=resolved_by,
            strategy="first_come",
        )

    def merge_results(
        self,
        results: list[Any],
        strategy: str = "combine",
    ) -> Any:
        """Merge conflicting results.

        Args:
            results: List of conflicting results.
            strategy: Merge strategy.

        Returns:
            Merged result.
        """
        if not results:
            return None

        if strategy == "first":
            return results[0]

        if strategy == "last":
            return results[-1]

        if strategy == "combine":
            if all(isinstance(r, dict) for r in results):
                merged = {}
                for r in results:
                    merged.update(r)
                return merged
            return results

        if strategy == "concat":
            if all(isinstance(r, (list, str)) for r in results):
                return sum((r if isinstance(r, list) else [r] for r in results), [])
            return results

        return results[0]

    def get_resolution(
        self,
        conflict_id: str,
    ) -> Resolution | None:
        """Get resolution for a conflict.

        Args:
            conflict_id: Conflict ID.

        Returns:
            Resolution or None.
        """
        return self._resolutions.get(conflict_id)

    def get_unresolved_count(
        self,
        session_id: str,
    ) -> int:
        """Get count of unresolved conflicts.

        Args:
            session_id: Session ID.

        Returns:
            Count of unresolved conflicts.
        """
        return len(self.get_session_conflicts(session_id, unresolved_only=True))

    def clear_session(
        self,
        session_id: str,
    ) -> tuple[int, int]:
        """Clear all conflicts for a session.

        Args:
            session_id: Session ID.

        Returns:
            Tuple of (conflicts_cleared, resolutions_cleared).
        """
        conflicts = [
            c_id for c_id, c in self._conflicts.items()
            if c.session_id == session_id
        ]

        for c_id in conflicts:
            self._resolutions.pop(c_id, None)
            del self._conflicts[c_id]

        return len(conflicts), len(conflicts)


# Global conflict resolver
_global_conflict_resolver: ConflictResolver | None = None
_resolver_lock = __import__("threading").Lock()


def get_conflict_resolver() -> ConflictResolver:
    """Get the global conflict resolver.

    Returns:
        Global ConflictResolver instance.
    """
    global _global_conflict_resolver
    with _resolver_lock:
        if _global_conflict_resolver is None:
            _global_conflict_resolver = ConflictResolver()
        return _global_conflict_resolver


def reset_conflict_resolver() -> None:
    """Reset the global conflict resolver."""
    global _global_conflict_resolver
    with _resolver_lock:
        _global_conflict_resolver = None
