"""Exceptions for the Cognitive Lifecycle Manager."""


class LifecycleError(Exception):
    """Base exception for lifecycle errors."""

    def __init__(self, message: str = "", **kwargs):
        super().__init__(message)
        self.message = message
        self.context = kwargs


class InvalidTransitionError(LifecycleError):
    """Raised when an invalid transition is attempted."""

    def __init__(self, session_id: str = "", from_state: str = "", to_state: str = ""):
        super().__init__(
            f"Invalid transition for '{session_id}' from '{from_state}' to '{to_state}'"
        )
        self.session_id = session_id
        self.from_state = from_state
        self.to_state = to_state


class TerminalStateError(LifecycleError):
    """Raised when attempting to transition from a terminal state."""

    def __init__(self, session_id: str = ""):
        super().__init__(f"Session '{session_id}' is in a terminal state")
        self.session_id = session_id


class LifecycleNotFoundError(LifecycleError):
    """Raised when lifecycle is not found."""

    def __init__(self, session_id: str = ""):
        super().__init__(f"Lifecycle '{session_id}' not found")
        self.session_id = session_id
