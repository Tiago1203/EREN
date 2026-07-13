"""Exception types for the Planner engine.

Scaffolding only — type declarations, no logic. One base error plus a subclass
per responsibility so callers can handle planning failures granularly.
"""

from __future__ import annotations


class PlannerError(Exception):
    """Base class for all planner-related errors."""


class IntentionError(PlannerError):
    """Raised when a raw request cannot be normalized into an ``Intention``."""


class PlanCreationError(PlannerError):
    """Raised when a plan cannot be created from an ``Intention``."""


class EngineSelectionError(PlannerError):
    """Raised when no suitable engine can be selected for a step."""


class ExecutionOrderError(PlannerError):
    """Raised when steps cannot be ordered (e.g. cyclic dependencies)."""
