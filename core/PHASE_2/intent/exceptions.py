"""Exceptions for the Intent Engine.

Declarative exception types only.
"""

from __future__ import annotations


class IntentError(Exception):
    """Base class for Intent Engine errors."""


class ClassificationError(IntentError):
    """Raised when intent classification cannot be completed."""
