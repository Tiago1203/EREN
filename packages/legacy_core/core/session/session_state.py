"""Session state definitions for the Cognitive Session Manager."""


class SessionState:
    """States of a cognitive session."""

    CREATED = "created"
    ACTIVE = "active"
    IDLE = "idle"
    PAUSED = "paused"
    WAITING = "waiting"
    RECOVERING = "recovering"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    ARCHIVED = "archived"
