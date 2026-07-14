"""Text normalizer for EREN Knowledge Ingestion Pipeline.

Responsible only for normalizing text without medical-specific logic.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from core.ingestion.types import ExtractedDocument, CleanedDocument

if TYPE_CHECKING:
    pass


class TextNormalizer:
    """Normalizes text without medical-specific processing.

    Single Responsibility: Only normalize text format.
    """

    def __init__(
        self,
        remove_headers_footers: bool = True,
        remove_page_numbers: bool = True,
        normalize_whitespace: bool = True,
        normalize_unicode: bool = True,
    ):
        """Initialize normalizer.

        Args:
            remove_headers_footers: Remove common headers/footers.
            remove_page_numbers: Remove page numbers.
            normalize_whitespace: Normalize whitespace.
            normalize_unicode: Normalize unicode.
        """
        self.remove_headers_footers = remove_headers_footers
        self.remove_page_numbers = remove_page_numbers
        self.normalize_whitespace = normalize_whitespace
        self.normalize_unicode = normalize_unicode

        # Patterns
        self._header_footer_patterns = [
            r"^Page\s+\d+\s+of\s+\d+$",
            r"^©\s*\d{4}.*$",
            r"^Confidential$",
            r"^Draft$",
            r"^\s*-\s*$",  # Separators
        ]
        self._page_number_patterns = [
            r"\bPage\s*\d+\b",
            r"\b\d+\s*of\s*\d+\b",
            r"^\s*\d+\s*$",  # Standalone numbers
        ]

    async def normalize(self, extracted: ExtractedDocument) -> CleanedDocument:
        """Normalize extracted text.

        Args:
            extracted: Extracted document.

        Returns:
            Normalized document.
        """
        text = extracted.content
        actions = []
        original_length = len(text)

        # Remove headers and footers
        if self.remove_headers_footers:
            for pattern in self._header_footer_patterns:
                new_text = re.sub(pattern, "", text, flags=re.MULTILINE | re.IGNORECASE)
                if new_text != text:
                    text = new_text
                    actions.append(f"Removed header/footer: {pattern[:30]}...")

        # Remove page numbers
        if self.remove_page_numbers:
            for pattern in self._page_number_patterns:
                new_text = re.sub(pattern, "", text)
                if new_text != text:
                    text = new_text
                    actions.append(f"Removed page numbers")

        # Normalize whitespace
        if self.normalize_whitespace:
            # Multiple spaces to single space
            new_text = re.sub(r"[ \t]+", " ", text)
            if new_text != text:
                text = new_text
                actions.append("Normalized spaces")

            # Multiple newlines to double newline
            new_text = re.sub(r"\n{3,}", "\n\n", text)
            if new_text != text:
                text = new_text
                actions.append("Normalized newlines")

            # Trim lines
            lines = [line.strip() for line in text.split("\n")]
            text = "\n".join(lines)
            actions.append("Trimmed line whitespace")

        # Normalize unicode
        if self.normalize_unicode:
            replacements = {
                "\u2018": "'",
                "\u2019": "'",
                "\u201c": '"',
                "\u201d": '"',
                "\u2013": "-",
                "\u2014": "--",
                "\u00a0": " ",
            }
            for old, new in replacements.items():
                if old in text:
                    text = text.replace(old, new)
                    actions.append(f"Normalized unicode: {old}")

        # Remove very short lines
        lines = text.split("\n")
        cleaned_lines = [line for line in lines if len(line) > 2]
        text = "\n".join(cleaned_lines)

        cleaned_length = len(text)
        removed_chars = original_length - cleaned_length

        return CleanedDocument(
            document_id=extracted.document_id,
            content=text,
            original_length=original_length,
            cleaned_length=cleaned_length,
            removed_chars=removed_chars,
            metadata=extracted.metadata,
            cleaning_time_ms=0,
            cleaning_actions=actions,
        )
