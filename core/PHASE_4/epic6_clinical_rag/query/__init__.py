"""
PHASE 4 - EPIC 6: Query Module

Procesamiento de queries clínicas:
- Query understanding
- Query expansion
- Query classification
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import re


class ClinicalQueryType(str, Enum):
    """Tipos de query clínica."""
    DIAGNOSIS = "diagnosis"
    TREATMENT = "treatment"
    DEVICE_USAGE = "device_usage"
    TROUBLESHOOTING = "troubleshooting"
    SAFETY_ALERT = "safety_alert"
    REGULATORY = "regulatory"
    PROGNOSIS = "prognosis"
    ETIOLOGY = "etiology"
    GENERAL = "general"


@dataclass
class QueryIntent:
    """Intención de la query."""
    query_type: ClinicalQueryType
    confidence: float
    entities: list[str] = field(default_factory=list)
    medical_terms: list[str] = field(default_factory=list)


@dataclass
class ProcessedQuery:
    """Query procesada."""
    original: str
    normalized: str
    intent: QueryIntent
    expanded_terms: list[str] = field(default_factory=list)
    filters: dict = field(default_factory=dict)


class BaseQueryProcessor(ABC):
    """Clase base para procesador de queries."""
    
    @abstractmethod
    def process(self, query: str) -> ProcessedQuery:
        """Procesa query."""
        ...


class ClinicalQueryProcessor(BaseQueryProcessor):
    """Procesador de queries clínicas."""
    
    def __init__(self):
        self._patterns = self._init_patterns()
    
    def _init_patterns(self) -> dict:
        """Inicializa patrones de clasificación."""
        return {
            ClinicalQueryType.DIAGNOSIS: [
                r"\b(diagnos|diagnostic)\b",
                r"\bwhat is\b.*\bcondition\b",
                r"\bpatient.*\bsymptoms\b",
                r"\bdifferential\b",
            ],
            ClinicalQueryType.TREATMENT: [
                r"\b(treatment|therapy|protocol)\b",
                r"\bhow to treat\b",
                r"\brecommend\w*\s+\w+\s+treatment\b",
                r"\bmedication\b",
            ],
            ClinicalQueryType.DEVICE_USAGE: [
                r"\b(usage|use|operat|setup|configur)\b.*\b(device|equipment|monitor)\b",
                r"\b(device|equipment|monitor).*\b(usage|use|operat)\b",
            ],
            ClinicalQueryType.TROUBLESHOOTING: [
                r"\b(error|problem|issue|fail)\b",
                r"\btroubleshoot|debug\b",
                r"\bnot work|doesn.?t work\b",
            ],
            ClinicalQueryType.SAFETY_ALERT: [
                r"\b(safety|warning|alert|caution)\b",
                r"\bhazard|risk|danger\b",
                r"\brecall\b",
            ],
            ClinicalQueryType.REGULATORY: [
                r"\b(regulation|compliance|fda|ce mark|standard)\b",
                r"\bcertif|bgvv|iso\b",
            ],
            ClinicalQueryType.PROGNOSIS: [
                r"\b(prognos|outcom|survival)\b",
                r"\blife expectancy\b",
            ],
            ClinicalQueryType.ETIOLOGY: [
                r"\b(cause|etiology|origin)\b",
                r"\bwhy does\b",
            ],
        }
    
    def process(self, query: str) -> ProcessedQuery:
        """Procesa query clínica."""
        # Normalize
        normalized = self._normalize(query)
        
        # Classify intent
        intent = self._classify_intent(query)
        
        # Extract entities
        entities = self._extract_entities(query)
        medical_terms = self._extract_medical_terms(query)
        
        # Expand terms
        expanded = self._expand_terms(normalized)
        
        # Extract filters
        filters = self._extract_filters(query)
        
        return ProcessedQuery(
            original=query,
            normalized=normalized,
            intent=intent,
            expanded_terms=expanded,
            filters=filters,
        )
    
    def _normalize(self, query: str) -> str:
        """Normaliza query."""
        # Lowercase
        text = query.lower()
        
        # Remove extra whitespace
        text = re.sub(r"\s+", " ", text)
        
        # Remove special chars but keep medical terms
        text = re.sub(r"[^\w\s\-\.\,\(\)]", " ", text)
        
        return text.strip()
    
    def _classify_intent(self, query: str) -> QueryIntent:
        """Clasifica intención de la query."""
        query_lower = query.lower()
        
        scores = {}
        
        for query_type, patterns in self._patterns.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    score += 1
            if score > 0:
                scores[query_type] = score / len(patterns)
        
        if not scores:
            return QueryIntent(
                query_type=ClinicalQueryType.GENERAL,
                confidence=0.5,
            )
        
        # Get highest scoring type
        best_type = max(scores, key=scores.get)
        confidence = scores[best_type]
        
        return QueryIntent(
            query_type=best_type,
            confidence=confidence,
        )
    
    def _extract_entities(self, query: str) -> list[str]:
        """Extrae entidades de la query."""
        # Extract capitalized words (potential entities)
        entities = re.findall(r"\b[A-Z][a-z]+\b", query)
        return list(set(entities))
    
    def _extract_medical_terms(self, query: str) -> list[str]:
        """Extrae términos médicos."""
        medical_terms = {
            "heart", "cardiac", "cardio", "pulmonary", "respiratory",
            "diabetes", "cancer", "tumor", "fracture", "infection",
            "blood", "pressure", "temperature", "pulse", "oxygen",
            "patient", "device", "equipment", "monitor", "ventilator",
            "ecg", "ekg", "mri", "ct", "xray", "x-ray",
            "medication", "drug", "treatment", "therapy",
            "diagnosis", "symptom", "syndrome", "disease",
        }
        
        query_lower = query.lower()
        found = []
        
        for term in medical_terms:
            if term in query_lower:
                found.append(term)
        
        return found
    
    def _expand_terms(self, query: str) -> list[str]:
        """Expande términos de búsqueda."""
        expansions = {
            "heart failure": ["congestive heart failure", "chf", "cardiac failure"],
            "ecg": ["electrocardiogram", "ekg", "electrocardiography"],
            "mri": ["magnetic resonance imaging"],
            "bp": ["blood pressure", "arterial pressure"],
            "chf": ["congestive heart failure", "heart failure"],
        }
        
        expanded = []
        query_lower = query.lower()
        
        for term, synonyms in expansions.items():
            if term in query_lower:
                expanded.extend(synonyms)
        
        return list(set(expanded))
    
    def _extract_filters(self, query: str) -> dict:
        """Extrae filtros de la query."""
        filters = {}
        
        # Device type
        device_match = re.search(r"\b(monitor|ventilator|pump|ecg|ekg|defibrillator)\b", query, re.I)
        if device_match:
            filters["device_type"] = device_match.group(1).lower()
        
        # Time range
        time_match = re.search(r"\b(last|recent|past)\s+(\d+)\s+(days?|weeks?|months?)\b", query, re.I)
        if time_match:
            filters["time_range"] = f"{time_match.group(2)} {time_match.group(3)}"
        
        # Severity
        if "severe" in query.lower() or "critical" in query.lower():
            filters["severity"] = "high"
        elif "mild" in query.lower() or "minor" in query.lower():
            filters["severity"] = "low"
        
        return filters


__all__ = [
    "ClinicalQueryType",
    "QueryIntent",
    "ProcessedQuery",
    "BaseQueryProcessor",
    "ClinicalQueryProcessor",
]
