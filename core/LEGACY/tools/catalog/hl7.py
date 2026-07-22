"""Contract for the HL7 tool — governed HL7 v2 messaging.

Parsing and exchange of HL7 v2.x pipe-delimited messages (ADT, ORM, ORU, …)
with clinical systems, through a single controlled capability. Contract only —
no logic.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

from .base import ExternalTool


@dataclass(frozen=True, slots=True)
class Hl7Message:
    """A raw HL7 v2 message and its declared type."""

    raw: str = ""
    message_type: str = ""


@dataclass(frozen=True, slots=True)
class Hl7Segment:
    """A parsed HL7 segment (e.g. ``MSH``, ``PID``) and its fields."""

    name: str
    fields: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class Hl7ParseResult:
    """The segments parsed from a message."""

    segments: Sequence[Hl7Segment] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class Hl7Ack:
    """An HL7 acknowledgement (ACK/NAK) for a sent message."""

    accepted: bool = False
    code: str = ""


@runtime_checkable
class HL7Tool(ExternalTool, Protocol):
    """Governed HL7 v2 messaging."""

    def parse(self, message: Hl7Message) -> Hl7ParseResult:
        """Parse *message* into its segments."""
        ...

    def send(self, message: Hl7Message) -> Hl7Ack:
        """Send *message* to a downstream system and return its acknowledgement."""
        ...
