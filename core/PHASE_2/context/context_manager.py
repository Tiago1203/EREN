"""Context Manager — manages cognitive contexts lifecycle.

The Context Manager handles:
- Creating new contexts
- Managing context state transitions
- Tracking context history
- Merging contexts
- Cleaning up expired contexts

Architecture only — no business logic, no AI.
"""

from __future__ import annotations

import threading
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

from .cognitive_context import CognitiveContext
from .context_history import ContextHistory
from .context_snapshot import ContextSnapshot
from .context_types import ContextFilter, ContextStatus

if TYPE_CHECKING:
    pass


@dataclass
class ContextStats:
    """Statistics about managed contexts."""

    total: int = 0
    by_status: dict[str, int] = field(default_factory=dict)
    by_user: dict[str, int] = field(default_factory=dict)
    by_hospital: dict[str, int] = field(default_factory=dict)
    average_duration_ms: float = 0.0


class ContextManager:
    """Manages the lifecycle of cognitive contexts.

    The ContextManager is responsible for:
    - Creating and registering contexts
    - Managing context state transitions
    - Providing context lookup
    - Tracking context statistics
    - Cleaning up expired contexts

    Thread-safe and designed for concurrent access.
    """

    def __init__(
        self,
        max_contexts: int = 1000,
        context_ttl_minutes: int = 60,
    ) -> None:
        """Initialize the context manager.

        Args:
            max_contexts: Maximum number of active contexts
            context_ttl_minutes: Time-to-live for contexts in minutes
        """
        self._contexts: dict[str, CognitiveContext] = {}
        self._by_session: dict[str, list[str]] = defaultdict(list)
        self._by_user: dict[str, list[str]] = defaultdict(list)
        self._by_correlation: dict[str, list[str]] = defaultdict(list)
        self._history = ContextHistory()

        self._lock = threading.RLock()
        self._max_contexts = max_contexts
        self._context_ttl = timedelta(minutes=context_ttl_minutes)

    # =========================================================================
    # Context Creation
    # =========================================================================

    def create_context(
        self,
        correlation_id: str = "",
        session_id: str = "",
        **kwargs,
    ) -> CognitiveContext:
        """Create a new cognitive context.

        Args:
            correlation_id: Correlation ID for tracking
            session_id: Session ID
            **kwargs: Additional context parameters

        Returns:
            A new CognitiveContext instance.
        """
        context = CognitiveContext.create(
            correlation_id=correlation_id,
            session_id=session_id,
            **kwargs,
        )

        with self._lock:
            # Check capacity
            if len(self._contexts) >= self._max_contexts:
                self._evict_oldest()

            # Store context
            self._contexts[context.context_id] = context

            # Update indexes
            if session_id:
                self._by_session[session_id].append(context.context_id)
            if context.user.user_id:
                self._by_user[context.user.user_id].append(context.context_id)
            if correlation_id:
                self._by_correlation[correlation_id].append(context.context_id)

        return context

    # =========================================================================
    # Context Access
    # =========================================================================

    def get_context(self, context_id: str) -> CognitiveContext | None:
        """Get a context by ID.

        Args:
            context_id: The context ID

        Returns:
            The context if found, None otherwise.
        """
        with self._lock:
            return self._contexts.get(context_id)

    def update_context(
        self,
        context: CognitiveContext,
    ) -> CognitiveContext:
        """Update a context.

        Args:
            context: The updated context

        Returns:
            The updated context.
        """
        with self._lock:
            if context.context_id not in self._contexts:
                raise ValueError(f"Context {context.context_id} not found")

            # Record in history
            self._history.record_transition(
                context_id=context.context_id,
                from_status=self._contexts[context.context_id].status,
                to_status=context.status,
            )

            # Update
            self._contexts[context.context_id] = context

        return context

    def delete_context(self, context_id: str) -> bool:
        """Delete a context.

        Args:
            context_id: The context ID

        Returns:
            True if deleted, False if not found.
        """
        with self._lock:
            if context_id not in self._contexts:
                return False

            context = self._contexts[context_id]

            # Remove from indexes
            if context.processing.session_id in self._by_session:
                self._by_session[context.processing.session_id].remove(context_id)
            if context.user.user_id in self._by_user:
                self._by_user[context.user.user_id].remove(context_id)
            if context.processing.correlation_id in self._by_correlation:
                self._by_correlation[context.processing.correlation_id].remove(context_id)

            # Remove from storage
            del self._contexts[context_id]

            # Record final state in history
            self._history.record_final_state(context_id, context)

            return True

    # =========================================================================
    # Context Lookup
    # =========================================================================

    def find_by_session(self, session_id: str) -> list[CognitiveContext]:
        """Find contexts by session ID.

        Args:
            session_id: The session ID

        Returns:
            List of contexts for the session.
        """
        with self._lock:
            context_ids = self._by_session.get(session_id, [])
            return [
                self._contexts[cid]
                for cid in context_ids
                if cid in self._contexts
            ]

    def find_by_user(self, user_id: str) -> list[CognitiveContext]:
        """Find contexts by user ID.

        Args:
            user_id: The user ID

        Returns:
            List of contexts for the user.
        """
        with self._lock:
            context_ids = self._by_user.get(user_id, [])
            return [
                self._contexts[cid]
                for cid in context_ids
                if cid in self._contexts
            ]

    def find_by_correlation(self, correlation_id: str) -> list[CognitiveContext]:
        """Find contexts by correlation ID.

        Args:
            correlation_id: The correlation ID

        Returns:
            List of contexts for the correlation.
        """
        with self._lock:
            context_ids = self._by_correlation.get(correlation_id, [])
            return [
                self._contexts[cid]
                for cid in context_ids
                if cid in self._contexts
            ]

    def search(self, filter: ContextFilter) -> list[CognitiveContext]:
        """Search contexts by filter.

        Args:
            filter: The search filter

        Returns:
            List of matching contexts.
        """
        with self._lock:
            results = list(self._contexts.values())

            if filter.status:
                results = [c for c in results if c.status == filter.status]
            if filter.user_id:
                results = [c for c in results if c.user.user_id == filter.user_id]
            if filter.hospital_id:
                results = [c for c in results if c.hospital.hospital_id == filter.hospital_id]
            if filter.device_id:
                results = [c for c in results if c.device.device_id == filter.device_id]
            if filter.session_id:
                results = [c for c in results if c.processing.session_id == filter.session_id]

            return results

    # =========================================================================
    # Context History and Snapshots
    # =========================================================================

    def create_snapshot(self, context_id: str) -> ContextSnapshot | None:
        """Create a snapshot of a context.

        Args:
            context_id: The context ID

        Returns:
            A ContextSnapshot if the context exists, None otherwise.
        """
        with self._lock:
            context = self._contexts.get(context_id)
            if not context:
                return None

            return ContextSnapshot.from_context(context)

    def get_history(self, context_id: str) -> list[dict]:
        """Get the history of a context.

        Args:
            context_id: The context ID

        Returns:
            List of history records.
        """
        return self._history.get_history(context_id)

    # =========================================================================
    # Context Lifecycle
    # =========================================================================

    def complete_context(
        self,
        context_id: str,
        response: str,
    ) -> CognitiveContext | None:
        """Mark a context as completed.

        Args:
            context_id: The context ID
            response: The final response

        Returns:
            The updated context if found.
        """
        from .context_types import ResponseResult
        context = self.get_context(context_id)
        if not context:
            return None

        completed = context.complete(
            response=ResponseResult(content=response),
        )

        return self.update_context(completed)

    def fail_context(self, context_id: str, error: str) -> CognitiveContext | None:
        """Mark a context as failed.

        Args:
            context_id: The context ID
            error: The error message

        Returns:
            The updated context if found.
        """
        context = self.get_context(context_id)
        if not context:
            return None

        failed = context.fail({"error": error, "timestamp": datetime.now(UTC).isoformat()})

        return self.update_context(failed)

    def cancel_context(self, context_id: str, reason: str = "") -> CognitiveContext | None:
        """Cancel a context.

        Args:
            context_id: The context ID
            reason: Cancellation reason

        Returns:
            The updated context if found.
        """
        context = self.get_context(context_id)
        if not context:
            return None

        from dataclasses import replace

        from .context_types import ContextStatus

        cancelled = replace(
            context,
            status=ContextStatus.CANCELLED,
            updated_at=datetime.now(UTC).isoformat(),
        )

        return self.update_context(cancelled)

    # =========================================================================
    # Utility Methods
    # =========================================================================

    def get_statistics(self) -> ContextStats:
        """Get statistics about managed contexts.

        Returns:
            ContextStats with current statistics.
        """
        with self._lock:
            stats = ContextStats(total=len(self._contexts))

            for context in self._contexts.values():
                # By status
                status_name = context.status.name
                stats.by_status[status_name] = stats.by_status.get(status_name, 0) + 1

                # By user
                if context.user.user_id:
                    stats.by_user[context.user.user_id] = (
                        stats.by_user.get(context.user.user_id, 0) + 1
                    )

                # By hospital
                if context.hospital.hospital_id:
                    stats.by_hospital[context.hospital.hospital_id] = (
                        stats.by_hospital.get(context.hospital.hospital_id, 0) + 1
                    )

            return stats

    def cleanup_expired(self) -> int:
        """Clean up expired contexts.

        Returns:
            Number of contexts cleaned up.
        """
        with self._lock:
            now = datetime.now(UTC)
            expired_ids = []

            for context_id, context in self._contexts.items():
                if context.status in (ContextStatus.COMPLETED, ContextStatus.FAILED):
                    updated_at = datetime.fromisoformat(context.updated_at)
                    if now - updated_at > self._context_ttl:
                        expired_ids.append(context_id)

            for context_id in expired_ids:
                self.delete_context(context_id)

            return len(expired_ids)

    def _evict_oldest(self) -> None:
        """Evict the oldest context."""
        if not self._contexts:
            return

        oldest_id = min(
            self._contexts.keys(),
            key=lambda cid: self._contexts[cid].created_at,
        )
        self.delete_context(oldest_id)

    def list_active_contexts(self) -> list[CognitiveContext]:
        """List all active (non-completed) contexts."""
        with self._lock:
            return [
                c for c in self._contexts.values()
                if c.status not in (ContextStatus.COMPLETED, ContextStatus.FAILED)
            ]
