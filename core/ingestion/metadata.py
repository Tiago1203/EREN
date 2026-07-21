"""Metadata builders for document ingestion."""

from __future__ import annotations

import uuid
import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.ingestion.types import (
        ExtractedDocument,
        IngestionMetadata,
        RawDocument,
    )


# =============================================================================
# Medical Specialties
# =============================================================================

MEDICAL_SPECIALTIES = {
    "cardiology": ["heart", "cardiac", "cardiovascular", "coronary", "myocardial", "angina", "arrhythmia"],
    "neurology": ["brain", "neurological", "stroke", "seizure", "epilepsy", "cognitive", "nervous system"],
    "oncology": ["cancer", "tumor", "malignant", "carcinoma", "chemotherapy", "oncology"],
    "orthopedics": ["bone", "joint", "fracture", "orthopedic", "spine", "musculoskeletal"],
    "pediatrics": ["child", "infant", "pediatric", "neonatal", "adolescent"],
    "psychiatry": ["mental", "psychiatric", "depression", "anxiety", "psychosis", "mental health"],
    "radiology": ["x-ray", "mri", "ct scan", "imaging", "radiological", "ultrasound"],
    "emergency": ["emergency", "trauma", "acute", "urgent", "critical care"],
    "internal_medicine": ["diabetes", "hypertension", "chronic", "metabolic", "internal medicine"],
    "surgery": ["surgical", "operation", "procedure", "postoperative", "intraoperative"],
}


# =============================================================================
# Base Metadata Builder
# =============================================================================

class MetadataBuilder:
    """Builder for document metadata from raw documents."""

    def build_from_raw(self, raw: RawDocument) -> IngestionMetadata:
        """Build metadata from raw document."""
        metadata = raw.metadata or IngestionMetadata()
        
        # Generate document ID if not set
        if not metadata.document_id:
            metadata.document_id = f"doc-{uuid.uuid4().hex[:8]}"
        
        # Extract title from filename
        if not metadata.title and raw.filename:
            metadata.title = self._extract_title_from_filename(raw.filename)
        
        # Set source type based on document type
        if not metadata.source_type:
            metadata.source_type = raw.document_type.value
        
        return metadata

    def build_from_extracted(self, extracted: ExtractedDocument) -> IngestionMetadata:
        """Build metadata from extracted document."""
        metadata = extracted.metadata or IngestionMetadata()
        
        # Generate document ID if not set
        if not metadata.document_id:
            metadata.document_id = extracted.document_id or f"doc-{uuid.uuid4().hex[:8]}"
        
        # Extract title from content
        if not metadata.title:
            metadata.title = self._extract_title_from_content(extracted.content)
        
        # Extract language
        metadata.language = self._detect_language(extracted.content)
        
        # Extract tags
        metadata.tags = self._extract_tags(extracted.content)
        
        return metadata

    def _extract_title_from_filename(self, filename: str) -> str:
        """Extract title from filename."""
        # Remove extension
        name = filename.rsplit(".", 1)[0] if "." in filename else filename
        # Replace underscores and hyphens with spaces
        name = re.sub(r"[-_]", " ", name)
        # Capitalize words
        return name.title()

    def _extract_title_from_content(self, content: str) -> str:
        """Extract title from document content."""
        lines = content.split("\n")
        for line in lines[:10]:  # Check first 10 lines
            line = line.strip()
            if line and len(line) > 3 and len(line) < 100:
                # Return first non-empty line as title
                return line
        return "Untitled Document"

    def _detect_language(self, content: str) -> str:
        """Detect language from content."""
        # Simple heuristic - default to English
        return "en"

    def _extract_tags(self, content: str) -> list[str]:
        """Extract tags from content."""
        tags = []
        content_lower = content.lower()
        
        # Extract common medical terms
        medical_terms = [
            "diagnosis", "treatment", "symptoms", "patient", "clinical",
            "therapy", "medication", "procedure", "examination", "test"
        ]
        
        for term in medical_terms:
            if term in content_lower:
                tags.append(term)
        
        return tags[:10]  # Limit to 10 tags


# =============================================================================
# Medical Metadata Builder
# =============================================================================

class MedicalMetadataBuilder(MetadataBuilder):
    """Specialized metadata builder for medical documents."""

    def build_from_extracted(self, extracted: ExtractedDocument) -> IngestionMetadata:
        """Build metadata from extracted medical document."""
        metadata = super().build_from_extracted(extracted)
        
        # Detect medical specialty
        metadata.medical_specialty = self._detect_medical_specialty(extracted.content)
        
        # Extract medical-specific tags
        metadata.tags = self._extract_medical_tags(extracted.content)
        
        # Set patient info flag
        metadata.patient_info = self._contains_patient_info(extracted.content)
        
        return metadata

    def _detect_medical_specialty(self, content: str) -> str:
        """Detect medical specialty from content."""
        content_lower = content.lower()
        
        # Score each specialty
        scores = {}
        for specialty, keywords in MEDICAL_SPECIALTIES.items():
            score = sum(1 for kw in keywords if kw in content_lower)
            if score > 0:
                scores[specialty] = score
        
        # Return highest scoring specialty
        if scores:
            return max(scores, key=scores.get)
        
        return "general"

    def _extract_medical_tags(self, content: str) -> list[str]:
        """Extract medical-specific tags."""
        tags = []
        content_lower = content.lower()
        
        # Medical condition tags
        medical_conditions = [
            "diagnosis", "prognosis", "treatment", "therapy", "medication",
            "surgery", "examination", "symptoms", "signs", "test results",
            "vital signs", "laboratory", "imaging", "ecg", "ekg", "x-ray",
            "blood pressure", "heart rate", "temperature", "oxygen"
        ]
        
        for tag in medical_conditions:
            if tag in content_lower:
                tags.append(tag)
        
        return list(set(tags))[:15]  # Limit to 15 unique tags

    def _contains_patient_info(self, content: str) -> bool:
        """Check if content contains patient information."""
        patient_indicators = [
            "patient name", "date of birth", "mrn", "medical record",
            "ssn", "social security", "address", "phone number"
        ]
        
        content_lower = content.lower()
        return any(indicator in content_lower for indicator in patient_indicators)
