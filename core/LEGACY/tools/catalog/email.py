"""Contract for the Email tool — governed outbound email.

Sends transactional/notification email through a single controlled capability.
Contract only — no logic.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

from .base import ExternalTool


@dataclass(frozen=True, slots=True)
class EmailAttachment:
    """A file attached to an email message."""

    filename: str
    content: bytes | None = None
    content_type: str = "application/octet-stream"


@dataclass(frozen=True, slots=True)
class EmailMessage:
    """An email to be sent."""

    to: tuple[str, ...]
    subject: str = ""
    body: str = ""
    cc: tuple[str, ...] = field(default_factory=tuple)
    attachments: Sequence[EmailAttachment] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class EmailReceipt:
    """Provider acknowledgement for a sent message."""

    message_id: str = ""
    accepted: bool = False


@runtime_checkable
class EmailTool(ExternalTool, Protocol):
    """Governed outbound email."""

    def send(self, message: EmailMessage) -> EmailReceipt:
        """Send *message* and return the provider receipt."""
        ...
