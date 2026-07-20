"""Session definition for the Cognitive Session Manager."""

from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass
class SessionMetadata:
    """Metadata for a session."""

    session_id: str
    correlation_id: str
    context_id: str
    created_at: str = ""
    activated_at: str = ""
    completed_at: str = ""
    last_activity_at: str = ""
    metadata: dict = field(default_factory=dict)

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(UTC).isoformat()


class SessionState:
    """Session states."""

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


@dataclass
class CognitiveSession:
    """A complete cognitive session."""

    metadata: SessionMetadata
    user_id: str = ""
    hospital_id: str = ""
    tenant_id: str = ""
    session_type: str = "general"
    intent: str = ""
    state: str = SessionState.CREATED
    is_active: bool = False
    state_history: list = field(default_factory=list)
    motors_used: dict = field(default_factory=dict)
    capabilities_used: dict = field(default_factory=dict)
    iterations: int = 0
    max_iterations: int = 100
    result: object = None
    error: str = ""
    pause_count: int = 0
    recovery_count: int = 0
    last_activity: str = ""

    def activate(self):
        self.is_active = True
        self.state = SessionState.ACTIVE
        self.state_history.append(SessionState.ACTIVE)
        self.last_activity = datetime.now(UTC).isoformat()

    def pause(self):
        self.state = SessionState.PAUSED
        self.state_history.append(SessionState.PAUSED)
        self.pause_count += 1

    def resume(self):
        self.state = SessionState.ACTIVE
        self.state_history.append(SessionState.ACTIVE)

    def complete(self, result=None):
        self.state = SessionState.COMPLETED
        self.state_history.append(SessionState.COMPLETED)
        self.result = result
        self.is_active = False

    def fail(self, error):
        self.state = SessionState.FAILED
        self.state_history.append(SessionState.FAILED)
        self.error = error
        self.is_active = False

    def cancel(self, reason=""):
        self.state = SessionState.CANCELLED
        self.state_history.append(SessionState.CANCELLED)
        self.error = reason
        self.is_active = False

    def archive(self):
        self.state = SessionState.ARCHIVED
        self.state_history.append(SessionState.ARCHIVED)

    def to_dict(self):
        return {
            "session_id": self.metadata.session_id,
            "correlation_id": self.metadata.correlation_id,
            "user_id": self.user_id,
            "hospital_id": self.hospital_id,
            "state": self.state,
            "is_active": self.is_active,
        }
