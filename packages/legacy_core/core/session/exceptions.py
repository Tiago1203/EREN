"""Exceptions for the Cognitive Session Manager."""

from __future__ import annotations


class SessionError(Exception):
    """Base exception for session errors."""

    def __init__(self, message: str = "", **kwargs) -> None:
        super().__init__(message)
        self.message = message
        self.context = kwargs


class SessionNotFoundError(SessionError):
    """Raised when a session is not found."""

    def __init__(self, session_id: str = "") -> None:
        super().__init__(f"Session '{session_id}' not found")
        self.session_id = session_id


class SessionAlreadyExistsError(SessionError):
    """Raised when a session already exists."""

    def __init__(self, session_id: str = "") -> None:
        super().__init__(f"Session '{session_id}' already exists")
        self.session_id = session_id


class InvalidSessionStateError(SessionError):
    """Raised when a session state transition is invalid."""

    def __init__(
        self,
        session_id: str = "",
        from_state: str = "",
        to_state: str = "",
    ) -> None:
        super().__init__(
            f"Invalid session state transition for '{session_id}' from '{from_state}' to '{to_state}'"
        )
        self.session_id = session_id
        self.from_state = from_state
        self.to_state = to_state


class SessionTimeoutError(SessionError):
    """Raised when a session times out."""

    def __init__(
        self,
        session_id: str = "",
        timeout_ms: int = 0,
    ) -> None:
        super().__init__(
            f"Session '{session_id}' timed out after {timeout_ms}ms"
        )
        self.session_id = session_id
        self.timeout_ms = timeout_ms


class SessionLimitExceededError(SessionError):
    """Raised when session limit is exceeded."""

    def __init__(
        self,
        limit_type: str = "",
        limit: int = 0,
        current: int = 0,
    ) -> None:
        super().__init__(
            f"Session limit exceeded for '{limit_type}' (limit: {limit}, current: {current})"
        )
        self.limit_type = limit_type
        self.limit = limit
        self.current = current


class SessionExpiredError(SessionError):
    """Raised when a session has expired."""

    def __init__(self, session_id: str = "") -> None:
        super().__init__(f"Session '{session_id}' has expired")
        self.session_id = session_id


class SessionRecoveryError(SessionError):
    """Raised when session recovery fails."""

    def __init__(self, session_id: str = "", reason: str = "") -> None:
        super().__init__(
            f"Session '{session_id}' recovery failed: {reason}"
        )
        self.session_id = session_id
        self.reason = reason


class SessionArchivalError(SessionError):
    """Raised when session archival fails."""

    def __init__(self, session_id: str = "", reason: str = "") -> None:
        super().__init__(
            f"Session '{session_id}' archival failed: {reason}"
        )
        self.session_id = session_id
        self.reason = reason
