"""Text processor for EREN Knowledge Ingestion Pipeline.

Coordinates text processing: normalization + medical processing.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from core.ingestion.processors.medical_processor import MedicalProcessor
from core.ingestion.processors.normalizer import TextNormalizer
from core.ingestion.types import CleanedDocument, ExtractedDocument

if TYPE_CHECKING:
    pass


class TextProcessor:
    """Coordinates text processing.

    Single Responsibility: Orchestrate normalization and medical processing.
    """

    def __init__(
        self,
        normalizer: TextNormalizer | None = None,
        medical_processor: MedicalProcessor | None = None,
        enable_medical_processing: bool = False,
    ):
        """Initialize text processor.

        Args:
            normalizer: Text normalizer.
            medical_processor: Medical processor.
            enable_medical_processing: Enable medical-specific processing.
        """
        self._normalizer = normalizer or TextNormalizer()
        self._medical_processor = medical_processor
        self._enable_medical = enable_medical_processing

    async def process(self, extracted: ExtractedDocument) -> CleanedDocument:
        """Process text through normalization and medical processing.

        Args:
            extracted: Extracted document.

        Returns:
            Processed document.
        """
        # Step 1: Normalize
        cleaned = await self._normalizer.normalize(extracted)

        # Step 2: Medical processing (optional)
        if self._enable_medical and self._medical_processor:
            cleaned = await self._medical_processor.process(cleaned)

        return cleaned
