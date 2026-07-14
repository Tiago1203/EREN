"""Text cleaner for EREN Knowledge Ingestion Pipeline.

Cleans and normalizes extracted text.
"""

from __future__ import annotations

import re
import time
from typing import TYPE_CHECKING

from core.ingestion.types import ExtractedDocument, CleanedDocument

if TYPE_CHECKING:
    pass


class TextCleaner:
    """Cleans and normalizes text."""

    def __init__(
        self,
        remove_headers_footers: bool = True,
        remove_page_numbers: bool = True,
        remove_extra_whitespace: bool = True,
        normalize_unicode: bool = True,
        remove_special_chars: bool = False,
    ):
        """Initialize text cleaner.

        Args:
            remove_headers_footers: Remove common headers/footers.
            remove_page_numbers: Remove page numbers.
            remove_extra_whitespace: Normalize whitespace.
            normalize_unicode: Normalize unicode characters.
            remove_special_chars: Remove special characters.
        """
        self.remove_headers_footers = remove_headers_footers
        self.remove_page_numbers = remove_page_numbers
        self.remove_extra_whitespace = remove_extra_whitespace
        self.normalize_unicode = normalize_unicode
        self.remove_special_chars = remove_special_chars

        # Common patterns
        self._header_footer_patterns = [
            r"^Page\s+\d+\s+of\s+\d+$",
            r"^©\s*\d{4}.*$",
            r"^Confidential$",
            r"^Draft$",
        ]
        self._page_number_patterns = [
            r"\bPage\s*\d+\b",
            r"\b\d+\s*of\s*\d+\b",
            r"^\d+$",
        ]

    async def clean(self, extracted: ExtractedDocument) -> CleanedDocument:
        """Clean extracted document.

        Args:
            extracted: Extracted document.

        Returns:
            Cleaned document.
        """
        start_time = time.time()
        actions = []

        text = extracted.content
        original_length = len(text)

        # Remove headers and footers
        if self.remove_headers_footers:
            for pattern in self._header_footer_patterns:
                new_text = re.sub(pattern, "", text, flags=re.MULTILINE | re.IGNORECASE)
                if new_text != text:
                    text = new_text
                    actions.append(f"Removed header/footer pattern: {pattern}")

        # Remove page numbers
        if self.remove_page_numbers:
            for pattern in self._page_number_patterns:
                new_text = re.sub(pattern, "", text)
                if new_text != text:
                    text = new_text
                    actions.append(f"Removed page numbers: {pattern}")

        # Normalize whitespace
        if self.remove_extra_whitespace:
            # Replace multiple spaces with single space
            new_text = re.sub(r"[ \t]+", " ", text)
            if new_text != text:
                text = new_text
                actions.append("Normalized spaces")

            # Replace multiple newlines with double newline
            new_text = re.sub(r"\n{3,}", "\n\n", text)
            if new_text != text:
                text = new_text
                actions.append("Normalized newlines")

            # Remove leading/trailing whitespace from lines
            lines = [line.strip() for line in text.split("\n")]
            text = "\n".join(lines)
            actions.append("Trimmed line whitespace")

        # Normalize unicode
        if self.normalize_unicode:
            # Replace common unicode characters
            replacements = {
                "\u2018": "'",  # Left single quote
                "\u2019": "'",  # Right single quote
                "\u201c": '"',  # Left double quote
                "\u201d": '"',  # Right double quote
                "\u2013": "-",  # En dash
                "\u2014": "--",  # Em dash
                "\u00a0": " ",  # Non-breaking space
                "\u00e9": "e",  # é
                "\u00e8": "e",  # è
                "\u00ea": "e",  # ê
                "\u00e0": "a",  # à
                "\u00e1": "a",  # á
                "\u00f3": "o",  # ó
                "\u00fa": "u",  # ú
                "\u00fc": "u",  # ü
            }

            for old, new in replacements.items():
                if old in text:
                    text = text.replace(old, new)
                    actions.append(f"Normalized unicode: {old} -> {new}")

        # Remove special characters
        if self.remove_special_chars:
            # Remove non-printable characters except newlines
            new_text = re.sub(r"[^\x20-\x7E\n]", "", text)
            if new_text != text:
                text = new_text
                actions.append("Removed non-printable characters")

        # Remove very short lines (likely artifacts)
        lines = text.split("\n")
        cleaned_lines = [line for line in lines if len(line) > 2]
        text = "\n".join(cleaned_lines)

        cleaned_length = len(text)
        removed_chars = original_length - cleaned_length
        cleaning_time = int((time.time() - start_time) * 1000)

        return CleanedDocument(
            document_id=extracted.document_id,
            content=text,
            original_length=original_length,
            cleaned_length=cleaned_length,
            removed_chars=removed_chars,
            metadata=extracted.metadata,
            cleaning_time_ms=cleaning_time,
            cleaning_actions=actions,
        )


class MedicalTextCleaner(TextCleaner):
    """Specialized cleaner for medical text."""

    def __init__(self, **kwargs):
        """Initialize medical text cleaner."""
        super().__init__(**kwargs)
        self.medical_units = [
            "mg/kg",
            "mg/dL",
            "mmHg",
            "bpm",
            "mL/min",
            "kg/m²",
        ]

    async def clean(self, extracted: ExtractedDocument) -> CleanedDocument:
        """Clean medical document.

        Args:
            extracted: Extracted document.

        Returns:
            Cleaned document.
        """
        # First, apply standard cleaning
        cleaned = await super().clean(extracted)

        # Additional medical-specific cleaning
        text = cleaned.content

        # Normalize medical abbreviations
        medical_abbreviations = {
            r"\bBID\b": "twice daily",
            r"\bTID\b": "three times daily",
            r"\bQID\b": "four times daily",
            r"\bPRN\b": "as needed",
            r"\bPO\b": "by mouth",
            r"\bIV\b": "intravenous",
            r"\bIM\b": "intramuscular",
            r"\bSC\b": "subcutaneous",
            r"\bAC\b": "before meals",
            r"\bPC\b": "after meals",
            r"\bHS\b": "at bedtime",
            r"\bOD\b": "right eye",
            r"\bOS\b": "left eye",
            r"\bOU\b": "both eyes",
        }

        for pattern, replacement in medical_abbreviations.items():
            new_text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
            if new_text != text:
                text = new_text
                cleaned.cleaning_actions.append(f"Expanded abbreviation: {pattern}")

        # Normalize dosages
        dosage_patterns = [
            (r"(\d+)\s*mg\s*/\s*kg", r"\1 mg/kg"),
            (r"(\d+)\s*ml\s*/\s*hr", r"\1 mL/hr"),
        ]

        for pattern, replacement in dosage_patterns:
            new_text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
            if new_text != text:
                text = new_text
                cleaned.cleaning_actions.append("Normalized dosage format")

        cleaned.content = text
        return cleaned
