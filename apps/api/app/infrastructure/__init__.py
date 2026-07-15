"""Infrastructure package.

Contains implementations of domain interfaces.
"""

from app.infrastructure.events import EventBus

__all__ = ["EventBus"]
