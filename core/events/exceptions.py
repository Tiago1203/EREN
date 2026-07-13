"""Exceptions for EREN's event system.

Declarative exception types only — no logic.
"""

from __future__ import annotations


class EventError(Exception):
    """Base class for all event-system errors."""


class PublishError(EventError):
    """Raised when an event cannot be published."""


class SubscriptionError(EventError):
    """Raised when a subscription/unsubscription cannot be completed."""
