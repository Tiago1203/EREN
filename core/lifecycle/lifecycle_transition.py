"""Lifecycle transition for the Cognitive Lifecycle Manager."""

from datetime import datetime, timezone


class LifecycleTransition:
    """Represents a lifecycle transition."""

    def __init__(
        self,
        transition_id: str,
        session_id: str,
        correlation_id: str,
        from_state: str,
        to_state: str,
        event: str,
        reason: str = "",
        actor: str = "",
        timestamp: str = "",
        metadata: dict = None,
    ):
        self.transition_id = transition_id
        self.session_id = session_id
        self.correlation_id = correlation_id
        self.from_state = from_state
        self.to_state = to_state
        self.event = event
        self.reason = reason
        self.actor = actor
        self.timestamp = timestamp or datetime.now(timezone.utc).isoformat()
        self.metadata = metadata or {}

    def to_dict(self):
        return {
            "transition_id": self.transition_id,
            "session_id": self.session_id,
            "correlation_id": self.correlation_id,
            "from_state": self.from_state,
            "to_state": self.to_state,
            "event": self.event,
            "reason": self.reason,
            "actor": self.actor,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }
