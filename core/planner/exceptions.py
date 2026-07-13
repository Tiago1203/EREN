"""Exception types for the Planner engine.

Scaffolding only — type declarations, no logic. One base error plus a subclass
per responsibility so callers can handle planning failures granularly.
"""

from __future__ import annotations


class PlannerError(Exception):
    """Base class for all planner-related errors."""

    def __init__(self, message: str = "", **kwargs: object) -> None:
        super().__init__(message)
        self.message = message
        self.context = kwargs


class InvalidIntentionError(PlannerError):
    """Raised when a raw request cannot be normalized into an ``Intention``.

    This includes:
    - Empty or whitespace-only goals
    - Unsupported input types
    - Goals that fail validation
    """


class IntentionError(PlannerError):
    """Raised when a raw request cannot be normalized into an ``Intention``."""

    def __init__(self, message: str = "") -> None:
        super().__init__(message)


class PlanCreationError(PlannerError):
    """Raised when a plan cannot be created from an ``Intention``.

    This includes:
    - Strategy decomposition failures
    - Step validation failures
    - Maximum step limit exceeded
    """

    def __init__(self, message: str = "") -> None:
        super().__init__(message)


class EngineSelectionError(PlannerError):
    """Raised when no suitable engine can be selected for a step.

    This includes:
    - No engine matching the step requirements
    - Engine not registered in the system
    - Permission denied for the required engine
    """

    def __init__(self, message: str = "") -> None:
        super().__init__(message)


class StepOrderingError(PlannerError):
    """Raised when steps cannot be ordered into a valid execution sequence.

    This includes:
    - Cyclic dependencies detected
    - Missing dependency references
    - Circular dependency chain
    """

    def __init__(self, message: str = "") -> None:
        super().__init__(message)


class ExecutionOrderError(PlannerError):
    """Raised when steps cannot be ordered (e.g. cyclic dependencies)."""

    def __init__(self, message: str = "") -> None:
        super().__init__(message)
