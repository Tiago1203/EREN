"""Contract for the PDF tool — governed PDF document access.

Text/metadata extraction and page rendering over PDF documents. Contract only —
no logic.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

from .base import ExternalTool


@dataclass(frozen=True, slots=True)
class PdfDocument:
    """A PDF to operate on, referenced by storage location or raw bytes."""

    uri: str = ""
    content: bytes | None = None


@dataclass(frozen=True, slots=True)
class ExtractedText:
    """Text extracted from a document, optionally page by page."""

    text: str = ""
    pages: Sequence[str] = field(default_factory=tuple)
    metadata: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class RenderedPage:
    """A single page rendered to an image."""

    page_number: int
    image: bytes | None = None


@runtime_checkable
class PDFTool(ExternalTool, Protocol):
    """Governed access to PDF documents."""

    def extract_text(self, document: PdfDocument) -> ExtractedText:
        """Extract text and metadata from *document*."""
        ...

    def render_pages(self, document: PdfDocument) -> Sequence[RenderedPage]:
        """Render each page of *document* to an image."""
        ...
