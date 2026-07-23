"""
PHASE 4 - EPIC 8: Bias Module

Detección de sesgos:
- Bias Detector
- Bias Types
- Bias Report
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class BiasType(str, Enum):
    """Tipos de sesgo."""
    PUBLICATION = "publication"       # Publication bias
    SELECTION = "selection"         # Selection bias
    CONFIRMATION = "confirmation"   # Confirmation bias
    CITATION = "citation"           # Citation bias
    LANGUAGE = "language"          # Language bias
    GEOGRAPHIC = "geographic"      # Geographic bias
    TEMPORAL = "temporal"         # Temporal bias
    INDUSTRY = "industry"          # Industry funding bias


class BiasSeverity(str, Enum):
    """Severidad del sesgo."""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class BiasIndicator:
    """Indicador de sesgo."""
    bias_type: BiasType
    severity: BiasSeverity
    description: str
    evidence: str = ""
    score: float = 0.0


@dataclass
class BiasReport:
    """Reporte de sesgo."""
    source_id: str
    indicators: list[BiasIndicator] = field(default_factory=list)
    
    overall_severity: BiasSeverity = BiasSeverity.NONE
    bias_score: float = 0.0
    
    is_flagged: bool = False
    created_at: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        
        if self.indicators:
            max_severity = max(self.indicators, key=lambda i: self._severity_value(i.severity))
            self.overall_severity = max_severity.severity
            self.bias_score = sum(i.score for i in self.indicators) / len(self.indicators)
        
        self.is_flagged = self.overall_severity in (BiasSeverity.MEDIUM, BiasSeverity.HIGH)
    
    @staticmethod
    def _severity_value(severity: BiasSeverity) -> int:
        values = {
            BiasSeverity.NONE: 0,
            BiasSeverity.LOW: 1,
            BiasSeverity.MEDIUM: 2,
            BiasSeverity.HIGH: 3,
        }
        return values.get(severity, 0)


class BaseBiasDetector(ABC):
    """Clase base para detectores de sesgo."""
    
    @abstractmethod
    def detect(self, evidence_item: dict) -> BiasReport:
        """Detecta sesgos en evidencia."""
        ...


class ClinicalBiasDetector(BaseBiasDetector):
    """Detector de sesgos clínicos."""
    
    def __init__(self):
        self._industry_keywords = [
            "pharmaceutical", "pharma", "biotech", "medical device company",
            "funded by", "sponsored by", "provided by", "grant from",
        ]
        
        self._publication_bias_indicators = [
            "positive results", "statistically significant",
            "no adverse events", "improved outcomes",
        ]
    
    def detect(self, evidence_item: dict) -> BiasReport:
        """Detecta sesgos en evidencia clínica."""
        source_id = evidence_item.get("id", "unknown")
        text = evidence_item.get("text", "")
        metadata = evidence_item.get("metadata", {})
        
        indicators = []
        
        # Check for industry funding
        industry_bias = self._detect_industry_bias(text, metadata)
        if industry_bias:
            indicators.append(industry_bias)
        
        # Check for publication bias
        publication_bias = self._detect_publication_bias(text)
        if publication_bias:
            indicators.append(publication_bias)
        
        # Check for language bias
        language_bias = self._detect_language_bias(metadata)
        if language_bias:
            indicators.append(language_bias)
        
        # Check for temporal bias
        temporal_bias = self._detect_temporal_bias(metadata)
        if temporal_bias:
            indicators.append(temporal_bias)
        
        return BiasReport(
            source_id=source_id,
            indicators=indicators,
        )
    
    def _detect_industry_bias(
        self,
        text: str,
        metadata: dict,
    ) -> BiasIndicator | None:
        """Detecta sesgo de financiación industrial."""
        text_lower = text.lower()
        
        for keyword in self._industry_keywords:
            if keyword in text_lower:
                return BiasIndicator(
                    bias_type=BiasType.INDUSTRY,
                    severity=BiasSeverity.MEDIUM,
                    description=f"Potential industry funding detected: '{keyword}'",
                    evidence=keyword,
                    score=0.6,
                )
        
        # Check metadata for funding disclosure
        funding = metadata.get("funding", "")
        if funding and any(k in funding.lower() for k in ["industry", "pharma", "company"]):
            return BiasIndicator(
                bias_type=BiasType.INDUSTRY,
                severity=BiasSeverity.MEDIUM,
                description="Industry funding reported in metadata",
                evidence=funding,
                score=0.7,
            )
        
        return None
    
    def _detect_publication_bias(
        self,
        text: str,
    ) -> BiasIndicator | None:
        """Detecta sesgo de publicación."""
        text_lower = text.lower()
        
        positive_count = sum(1 for p in self._publication_bias_indicators if p in text_lower)
        
        if positive_count >= 2:
            return BiasIndicator(
                bias_type=BiasType.PUBLICATION,
                severity=BiasSeverity.LOW,
                description="Multiple positive outcome indicators detected",
                evidence=f"{positive_count} positive indicators found",
                score=0.5,
            )
        
        return None
    
    def _detect_language_bias(
        self,
        metadata: dict,
    ) -> BiasIndicator | None:
        """Detecta sesgo de idioma."""
        language = metadata.get("language", "en").lower()
        
        # Non-English sources may have limited scope
        if language not in ("en", "english"):
            return BiasIndicator(
                bias_type=BiasType.LANGUAGE,
                severity=BiasSeverity.LOW,
                description=f"Non-English source: {language}",
                evidence=f"Language: {language}",
                score=0.3,
            )
        
        return None
    
    def _detect_temporal_bias(
        self,
        metadata: dict,
    ) -> BiasIndicator | None:
        """Detecta sesgo temporal."""
        date = metadata.get("date", "")
        
        if not date:
            return BiasIndicator(
                bias_type=BiasType.TEMPORAL,
                severity=BiasSeverity.LOW,
                description="Publication date not available",
                evidence="Missing date",
                score=0.4,
            )
        
        try:
            year = int(date[:4])
            current_year = datetime.now().year
            
            # Very old sources
            if current_year - year > 15:
                return BiasIndicator(
                    bias_type=BiasType.TEMPORAL,
                    severity=BiasSeverity.MEDIUM,
                    description=f"Outdated source ({year})",
                    evidence=f"Publication year: {year}",
                    score=0.6,
                )
        except (ValueError, IndexError):
            pass
        
        return None


__all__ = [
    "BiasType",
    "BiasSeverity",
    "BiasIndicator",
    "BiasReport",
    "BaseBiasDetector",
    "ClinicalBiasDetector",
]
