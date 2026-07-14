"""Metadata builder for EREN Knowledge Ingestion Pipeline.

Builds metadata for documents.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from core.ingestion.types import (
    DocumentType,
    DocumentSource,
    IngestionMetadata,
    RawDocument,
    ExtractedDocument,
)

if TYPE_CHECKING:
    pass


class MetadataBuilder:
    """Builds metadata for documents."""

    def __init__(
        self,
        default_language: str = "en",
        default_source: DocumentSource = DocumentSource.UNKNOWN,
    ):
        """Initialize metadata builder.

        Args:
            default_language: Default language.
            default_source: Default source.
        """
        self.default_language = default_language
        self.default_source = default_source

    def build_from_raw(self, raw: RawDocument) -> IngestionMetadata:
        """Build metadata from raw document.

        Args:
            raw: Raw document.

        Returns:
            Built metadata.
        """
        metadata = raw.metadata

        # Generate document ID if not present
        if not metadata.document_id:
            metadata.document_id = str(uuid.uuid4())

        # Set source type based on document type
        if metadata.source_type == DocumentSource.UNKNOWN:
            metadata.source_type = self._infer_source_type(raw)

        # Set language if not present
        if not metadata.language:
            metadata.language = self._detect_language(raw)

        return metadata

    def build_from_extracted(
        self,
        extracted: ExtractedDocument,
    ) -> IngestionMetadata:
        """Build metadata from extracted document.

        Args:
            extracted: Extracted document.

        Returns:
            Built metadata.
        """
        metadata = extracted.metadata

        # Generate document ID if not present
        if not metadata.document_id:
            metadata.document_id = extracted.document_id

        # Extract title from content if not present
        if not metadata.title:
            metadata.title = self._extract_title(extracted.content)

        # Set timestamps
        if metadata.created_at is None:
            metadata.created_at = datetime.now(timezone.utc)

        return metadata

    def _infer_source_type(self, raw: RawDocument) -> DocumentSource:
        """Infer source type from raw document.

        Args:
            raw: Raw document.

        Returns:
            Inferred source type.
        """
        filename = raw.filename.lower()

        # Check filename for hints
        if "manual" in filename:
            return DocumentSource.MANUAL
        if "guideline" in filename or "guide" in filename:
            return DocumentSource.GUIDELINE
        if "protocol" in filename:
            return DocumentSource.PROTOCOL
        if "textbook" in filename:
            return DocumentSource.TEXTBOOK
        if "journal" in filename or "article" in filename:
            return DocumentSource.JOURNAL
        if "fhir" in filename:
            return DocumentSource.FHIR_SERVER
        if "hl7" in filename:
            return DocumentSource.HL7_INTERFACE

        # Infer from document type
        if raw.document_type == DocumentType.FHIR:
            return DocumentSource.FHIR_SERVER
        if raw.document_type == DocumentType.HL7:
            return DocumentSource.HL7_INTERFACE

        return DocumentSource.UNKNOWN

    def _detect_language(self, raw: RawDocument) -> str:
        """Detect language from raw document.

        Args:
            raw: Raw document.

        Returns:
            Detected language code.
        """
        # Try to decode content
        try:
            content = raw.content.decode("utf-8", errors="ignore")
        except Exception:
            content = ""

        # Simple language detection based on common words
        content_lower = content.lower()

        spanish_indicators = ["el", "la", "los", "las", "de", "que", "es", "en", "con", "para"]
        german_indicators = ["der", "die", "das", "und", "ist", "von", "mit", "für"]

        spanish_count = sum(1 for word in spanish_indicators if f" {word} " in content_lower)
        german_count = sum(1 for word in german_indicators if f" {word} " in content_lower)

        if spanish_count > 2:
            return "es"
        if german_count > 2:
            return "de"

        return self.default_language

    def _extract_title(self, content: str) -> str:
        """Extract title from content.

        Args:
            content: Document content.

        Returns:
            Extracted title.
        """
        if not content:
            return "Untitled Document"

        # Get first non-empty line
        lines = content.split("\n")
        for line in lines:
            line = line.strip()
            if line and len(line) > 3:
                # Limit title length
                if len(line) > 100:
                    line = line[:100] + "..."
                return line

        return "Untitled Document"


class MedicalMetadataBuilder(MetadataBuilder):
    """Specialized metadata builder for medical documents."""

    def __init__(self, **kwargs):
        """Initialize medical metadata builder."""
        super().__init__(**kwargs)

        self.specialties = [
            "cardiology",
            "dermatology",
            "endocrinology",
            "gastroenterology",
            "hematology",
            "infectious_disease",
            "nephrology",
            "neurology",
            "oncology",
            "ophthalmology",
            "orthopedics",
            "pathology",
            "pediatrics",
            "psychiatry",
            "pulmonology",
            "radiology",
            "rheumatology",
            "surgery",
            "urology",
        ]

    def build_from_extracted(
        self,
        extracted: ExtractedDocument,
    ) -> IngestionMetadata:
        """Build metadata from extracted medical document.

        Args:
            extracted: Extracted document.

        Returns:
            Built metadata.
        """
        metadata = super().build_from_extracted(extracted)

        # Detect medical specialty if not set
        if not metadata.medical_specialty:
            metadata.medical_specialty = self._detect_medical_specialty(extracted.content)

        # Add medical tags
        if not metadata.tags:
            metadata.tags = self._extract_medical_tags(extracted.content)

        return metadata

    def _detect_medical_specialty(self, content: str) -> str:
        """Detect medical specialty from content.

        Args:
            content: Document content.

        Returns:
            Detected specialty.
        """
        content_lower = content.lower()

        # Specialty indicators
        specialty_indicators = {
            "cardiology": ["heart", "cardiac", "cardiovascular", "myocardial", "coronary"],
            "dermatology": ["skin", "dermal", "cutaneous", "eczema", "psoriasis"],
            "endocrinology": ["thyroid", "diabetes", "hormone", "adrenal", "pituitary"],
            "gastroenterology": ["stomach", "intestinal", "colon", "liver", "digestive"],
            "neurology": ["brain", "neurological", "seizure", "stroke", "cognitive"],
            "oncology": ["cancer", "tumor", "malignant", "chemotherapy", "carcinoma"],
            "pediatrics": ["child", "pediatric", "infant", "neonatal", "adolescent"],
            "pulmonology": ["lung", "pulmonary", "respiratory", "asthma", "copd"],
        }

        for specialty, indicators in specialty_indicators.items():
            score = sum(1 for ind in indicators if ind in content_lower)
            if score >= 2:
                return specialty

        return ""

    def _extract_medical_tags(self, content: str) -> list[str]:
        """Extract medical tags from content.

        Args:
            content: Document content.

        Returns:
            List of tags.
        """
        tags = []
        content_lower = content.lower()

        # Common medical terms
        medical_terms = {
            "diagnosis": ["diagnosis", "diagnosed", "diagnosis:"],
            "treatment": ["treatment", "therapy", "medication", "prescription"],
            "symptoms": ["symptoms", "symptom", "presented with", "complained of"],
            "laboratory": ["lab", "laboratory", "test result", "blood test"],
            "imaging": ["x-ray", "mri", "ct scan", "ultrasound", "imaging"],
            "surgery": ["surgery", "surgical", "operative", "procedure"],
            "emergency": ["emergency", "urgent", "acute", "critical"],
            "chronic": ["chronic", "long-term", "recurrent"],
        }

        for tag, terms in medical_terms.items():
            if any(term in content_lower for term in terms):
                tags.append(tag)

        return tags
