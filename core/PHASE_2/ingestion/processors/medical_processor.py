"""Medical text processor for EREN Knowledge Ingestion Pipeline.

Responsible only for medical-specific text processing.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from core.PHASE_2.ingestion.types import CleanedDocument

if TYPE_CHECKING:
    pass


class MedicalProcessor:
    """Processes medical text specifically.

    Single Responsibility: Only handle medical text processing.
    Does NOT clean or normalize - only medical-specific transformations.
    """

    def __init__(self):
        """Initialize medical processor."""
        # Medical abbreviations to expand
        self._abbreviations = {
            r"\bBID\b": "twice daily",
            r"\bTID\b": "three times daily",
            r"\bQID\b": "four times daily",
            r"\bPRN\b": "as needed",
            r"\bPO\b": "by mouth",
            r"\bIV\b": "intravenous",
            r"\bIM\b": "intramuscular",
            r"\bSC\b": "subcutaneous",
            r"\bSQ\b": "subcutaneous",
            r"\bAC\b": "before meals",
            r"\bPC\b": "after meals",
            r"\bHS\b": "at bedtime",
            r"\bOD\b": "right eye",
            r"\bOS\b": "left eye",
            r"\bOU\b": "both eyes",
            r"\bAD\b": "right ear",
            r"\bAS\b": "left ear",
            r"\bAU\b": "both ears",
            r"\bSTAT\b": "immediately",
            r"\bNPO\b": "nothing by mouth",
            r"\bSOB\b": "shortness of breath",
            r"\bCPK\b": "creatine phosphokinase",
            r"\bAST\b": "aspartate aminotransferase",
            r"\bALT\b": "alanine aminotransferase",
            r"\bBUN\b": "blood urea nitrogen",
            r"\bCBC\b": "complete blood count",
            r"\bCT\b": "computed tomography",
            r"\bMRI\b": "magnetic resonance imaging",
            r"\bECG\b": "electrocardiogram",
            r"\bEKG\b": "electrocardiogram",
            r"\bGERD\b": "gastroesophageal reflux disease",
            r"\bCOPD\b": "chronic obstructive pulmonary disease",
            r"\bCHF\b": "congestive heart failure",
            r"\bUTI\b": "urinary tract infection",
            r"\bURI\b": "upper respiratory infection",
            r"\bDVT\b": "deep vein thrombosis",
            r"\bPE\b": "pulmonary embolism",
            r"\bMI\b": "myocardial infarction",
            r"\bCVA\b": "cerebrovascular accident",
            r"\bHTN\b": "hypertension",
            r"\bDM\b": "diabetes mellitus",
            r"\bCAD\b": "coronary artery disease",
            r"\bGFR\b": "glomerular filtration rate",
            r"\bINR\b": "international normalized ratio",
            r"\bPT\b": "prothrombin time",
            r"\bPTT\b": "partial thromboplastin time",
        }

        # Dosage patterns to normalize
        self._dosage_patterns = [
            (r"(\d+)\s*mg\s*/\s*kg", r"\1 mg/kg"),
            (r"(\d+)\s*ml\s*/\s*hr", r"\1 mL/hr"),
            (r"(\d+)\s*mcg\s*/\s*min", r"\1 mcg/min"),
        ]

        # Medical unit patterns
        self._medical_units = [
            "mg/kg",
            "mg/dL",
            "mmHg",
            "bpm",
            "mL/min",
            "kg/m²",
            "mEq/L",
            "g/dL",
        ]

    async def process(self, cleaned: CleanedDocument) -> CleanedDocument:
        """Process medical text.

        Args:
            cleaned: Already cleaned document.

        Returns:
            Medically processed document.
        """
        text = cleaned.content
        actions = []

        # Expand abbreviations
        for pattern, replacement in self._abbreviations.items():
            new_text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
            if new_text != text:
                text = new_text
                actions.append(f"Expanded abbreviation: {pattern}")

        # Normalize dosage patterns
        for pattern, replacement in self._dosage_patterns:
            new_text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
            if new_text != text:
                text = new_text
                actions.append("Normalized dosage format")

        # Update cleaned document
        cleaned.content = text
        cleaned.cleaning_actions.extend(actions)
        cleaned.cleaned_length = len(text)
        cleaned.removed_chars = cleaned.original_length - cleaned.cleaned_length

        return cleaned


class MedicalTerminologyNormalizer:
    """Normalizes medical terminology.

    Single Responsibility: Only normalize medical terms.
    """

    def __init__(self):
        """Initialize terminology normalizer."""
        # Common term normalizations
        self._term_mappings = {
            "heart attack": "myocardial infarction",
            "high blood pressure": "hypertension",
            "stroke": "cerebrovascular accident",
            "chest pain": "angina",
            "trouble breathing": "dyspnea",
            "blood sugar": "glucose",
            "blood clot": "thrombus",
            "lung clot": "pulmonary embolism",
        }

    async def normalize(self, text: str) -> str:
        """Normalize medical terminology.

        Args:
            text: Text to normalize.

        Returns:
            Normalized text.
        """
        for old_term, new_term in self._term_mappings.items():
            text = re.sub(
                old_term,
                new_term,
                text,
                flags=re.IGNORECASE
            )
        return text
