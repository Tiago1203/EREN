"""Lifecycle types for the Cognitive Lifecycle Manager."""


class LifecycleState:
    """Lifecycle states."""

    CREATED = "created"
    INITIALIZING = "initializing"
    READY = "ready"
    ACTIVE = "active"
    WAITING = "waiting"
    PAUSED = "paused"
    RESUMING = "resuming"
    RECOVERING = "recovering"
    COMPLETING = "completing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    ARCHIVED = "archived"


class LifecycleEvent:
    """Lifecycle events."""

    INITIALIZE = "initialize"
    READY = "ready"
    ACTIVATE = "activate"
    WAIT = "wait"
    PAUSE = "pause"
    RESUME = "resume"
    RECOVER = "recover"
    COMPLETE = "complete"
    FAIL = "fail"
    CANCEL = "cancel"
    ARCHIVE = "archive"


VALID_TRANSITIONS = {
    LifecycleState.CREATED: {
        LifecycleEvent.INITIALIZE: LifecycleState.INITIALIZING,
    },
    LifecycleState.INITIALIZING: {
        LifecycleEvent.READY: LifecycleState.READY,
        LifecycleEvent.CANCEL: LifecycleState.CANCELLED,
    },
    LifecycleState.READY: {
        LifecycleEvent.ACTIVATE: LifecycleState.ACTIVE,
        LifecycleEvent.CANCEL: LifecycleState.CANCELLED,
    },
    LifecycleState.ACTIVE: {
        LifecycleEvent.WAIT: LifecycleState.WAITING,
        LifecycleEvent.PAUSE: LifecycleState.PAUSED,
        LifecycleEvent.COMPLETE: LifecycleState.COMPLETING,
        LifecycleEvent.FAIL: LifecycleState.FAILED,
        LifecycleEvent.CANCEL: LifecycleState.CANCELLED,
    },
    LifecycleState.WAITING: {
        LifecycleEvent.ACTIVATE: LifecycleState.ACTIVE,
        LifecycleEvent.RECOVER: LifecycleState.RECOVERING,
        LifecycleEvent.FAIL: LifecycleState.FAILED,
        LifecycleEvent.CANCEL: LifecycleState.CANCELLED,
    },
    LifecycleState.PAUSED: {
        LifecycleEvent.RESUME: LifecycleState.RESUMING,
        LifecycleEvent.FAIL: LifecycleState.FAILED,
        LifecycleEvent.CANCEL: LifecycleState.CANCELLED,
    },
    LifecycleState.RESUMING: {
        LifecycleEvent.ACTIVATE: LifecycleState.ACTIVE,
        LifecycleEvent.FAIL: LifecycleState.FAILED,
    },
    LifecycleState.RECOVERING: {
        LifecycleEvent.ACTIVATE: LifecycleState.ACTIVE,
        LifecycleEvent.FAIL: LifecycleState.FAILED,
    },
    LifecycleState.COMPLETING: {
        LifecycleEvent.READY: LifecycleState.COMPLETED,
        LifecycleEvent.FAIL: LifecycleState.FAILED,
    },
    LifecycleState.COMPLETED: {
        LifecycleEvent.ARCHIVE: LifecycleState.ARCHIVED,
    },
    LifecycleState.FAILED: {
        LifecycleEvent.ARCHIVE: LifecycleState.ARCHIVED,
    },
    LifecycleState.CANCELLED: {
        LifecycleEvent.ARCHIVE: LifecycleState.ARCHIVED,
    },
    LifecycleState.ARCHIVED: {},
}


TERMINAL_STATES = {
    LifecycleState.COMPLETED,
    LifecycleState.ARCHIVED,
}
