"""Contract for the OCR tool — governed optical character recognition.

Turns scanned images/pages into machine-readable text. Contract only — no logic.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

from .base import ExternalTool


@dataclass(frozen=True, slots=True)
class OcrImage:
    """An image to recognize, referenced by location or raw bytes."""

    uri: str = ""
    content: bytes | None = None
    language: str = ""


@dataclass(frozen=True, slots=True)
class OcrBlock:
    """A recognized region of text and its confidence."""

    text: str = ""
    confidence: float = 0.0


@dataclass(frozen=True, slots=True)
class OcrResult:
    """Full recognized text plus the per-region breakdown."""

    text: str = ""
    blocks: Sequence[OcrBlock] = field(default_factory=tuple)


@runtime_checkable
class OCRTool(ExternalTool, Protocol):
    """Governed optical character recognition."""

    def recognize(self, image: OcrImage) -> OcrResult:
        """Recognize text within *image*."""
        ...
