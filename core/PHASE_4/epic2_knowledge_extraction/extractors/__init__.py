"""
PHASE 4 - EPIC 2: Extractors Module

Extractores especializados para conocimiento biomédico:
- Entity Extractor
- Concept Extractor
- Relation Extractor
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
import re
import uuid


class EntityCategory(str, Enum):
    """Categorías de entidades biomédicas."""
    DEVICE = "DEVICE"
    DRUG = "DRUG"
    CONDITION = "CONDITION"
    PROCEDURE = "PROCEDURE"
    ANATOMY = "ANATOMY"
    ORGANISM = "ORGANISM"
    BIOMARKER = "BIOMARKER"
    GENE = "GENE"
    PROTEIN = "PROTEIN"
    LAB_TEST = "LAB_TEST"
    SPECIMEN = "SPECIMEN"
    VALUE = "VALUE"
    TEMPORAL = "TEMPORAL"


class ConceptCategory(str, Enum):
    """Categorías de conceptos clínicos."""
    DIAGNOSIS = "DIAGNOSIS"
    TREATMENT = "TREATMENT"
    SYMPTOM = "SYMPTOM"
    ETIOLOGY = "ETIOLOGY"
    PROGNOSIS = "PROGNOSIS"
    PREVENTION = "PREVENTION"
    COMPLICATION = "COMPLICATION"
    CONTRAINDICATION = "CONTRAINDICATION"
    INDICATION = "INDICATION"
    SIDE_EFFECT = "SIDE_EFFECT"
    INTERACTION = "INTERACTION"
    ASSESSMENT = "ASSESSMENT"


class RelationCategory(str, Enum):
    """Categorías de relaciones."""
    TREATS = "TREATS"
    CAUSES = "CAUSES"
    PREVENTS = "PREVENTS"
    COMPLICATES = "COMPLICATES"
    DIAGNOSES = "DIAGNOSES"
    MANIFESTS_AS = "MANIFESTS_AS"
    INTERACTS_WITH = "INTERACTS_WITH"
    IS_A = "IS_A"
    PART_OF = "PART_OF"
    LOCATED_IN = "LOCATED_IN"
    ASSESSES = "ASSESSES"
    PRODUCES = "PRODUCES"


@dataclass
class BiomedicalEntity:
    """Entidad biomédica extraída."""
    entity_id: str
    text: str
    category: EntityCategory
    normalized_text: str = ""
    confidence: float = 0.0
    start_pos: int = 0
    end_pos: int = 0
    context: str = ""
    synonyms: list[str] = field(default_factory=list)
    medical_codes: list[str] = field(default_factory=list)
    properties: dict = field(default_factory=dict)


@dataclass
class BiomedicalConcept:
    """Concepto biomédico."""
    concept_id: str
    text: str
    category: ConceptCategory
    definition: str = ""
    confidence: float = 0.0
    synonyms: list[str] = field(default_factory=list)
    related_concepts: list[str] = field(default_factory=list)
    medical_codes: list[str] = field(default_factory=list)


@dataclass
class MedicalRelation:
    """Relación médica entre entidades."""
    relation_id: str
    source_entity_id: str
    target_entity_id: str
    relation_type: RelationCategory
    confidence: float = 0.0
    evidence: str = ""
    context: str = ""
    bidirectional: bool = False


class BaseExtractor(ABC):
    """Clase base para extractores."""
    
    @abstractmethod
    def extract(self, text: str, **kwargs) -> list:
        """Extrae información del texto."""
        ...


class EntityExtractor(BaseExtractor):
    """Extractor de entidades biomédicas."""
    
    # Patrones para diferentes categorías de entidades
    DEVICE_PATTERNS = {
        'infusion pump': EntityCategory.DEVICE,
        'ventilator': EntityCategory.DEVICE,
        'defibrillator': EntityCategory.DEVICE,
        'pacemaker': EntityCategory.DEVICE,
        'monitor': EntityCategory.DEVICE,
        'ecg machine': EntityCategory.DEVICE,
        'ekg machine': EntityCategory.DEVICE,
        'ct scanner': EntityCategory.DEVICE,
        'mri machine': EntityCategory.DEVICE,
        'x-ray': EntityCategory.DEVICE,
        'ultrasound': EntityCategory.DEVICE,
        'dialysis': EntityCategory.DEVICE,
        'insulin pump': EntityCategory.DEVICE,
    }
    
    DRUG_PATTERNS = {
        'aspirin': EntityCategory.DRUG,
        'ibuprofen': EntityCategory.DRUG,
        'metformin': EntityCategory.DRUG,
        'lisinopril': EntityCategory.DRUG,
        'atorvastatin': EntityCategory.DRUG,
        'amoxicillin': EntityCategory.DRUG,
        'omeprazole': EntityCategory.DRUG,
        'metoprolol': EntityCategory.DRUG,
        'losartan': EntityCategory.DRUG,
        'gabapentin': EntityCategory.DRUG,
    }
    
    CONDITION_PATTERNS = {
        'hypertension': EntityCategory.CONDITION,
        'diabetes': EntityCategory.CONDITION,
        'myocardial infarction': EntityCategory.CONDITION,
        'heart failure': EntityCategory.CONDITION,
        'stroke': EntityCategory.CONDITION,
        'arrhythmia': EntityCategory.CONDITION,
        'copd': EntityCategory.CONDITION,
        'asthma': EntityCategory.CONDITION,
        'cancer': EntityCategory.CONDITION,
        'tumor': EntityCategory.CONDITION,
        'infection': EntityCategory.CONDITION,
        'sepsis': EntityCategory.CONDITION,
        'pneumonia': EntityCategory.CONDITION,
        'anemia': EntityCategory.CONDITION,
    }
    
    LAB_TEST_PATTERNS = {
        'glucose': EntityCategory.LAB_TEST,
        'hemoglobin': EntityCategory.LAB_TEST,
        'creatinine': EntityCategory.LAB_TEST,
        'sodium': EntityCategory.LAB_TEST,
        'potassium': EntityCategory.LAB_TEST,
        'wbc': EntityCategory.LAB_TEST,
        'rbc': EntityCategory.LAB_TEST,
        'platelet': EntityCategory.LAB_TEST,
        'troponin': EntityCategory.LAB_TEST,
        'bnp': EntityCategory.LAB_TEST,
        'hba1c': EntityCategory.LAB_TEST,
        'cholesterol': EntityCategory.LAB_TEST,
    }
    
    ALL_PATTERNS = {}
    ALL_PATTERNS.update(DEVICE_PATTERNS)
    ALL_PATTERNS.update(DRUG_PATTERNS)
    ALL_PATTERNS.update(CONDITION_PATTERNS)
    ALL_PATTERNS.update(LAB_TEST_PATTERNS)
    
    def __init__(self, min_confidence: float = 0.5):
        self.min_confidence = min_confidence
    
    def extract(self, text: str, **kwargs) -> list[BiomedicalEntity]:
        """Extrae entidades biomédicas."""
        entities = []
        text_lower = text.lower()
        
        for pattern, category in self.ALL_PATTERNS.items():
            pattern_lower = pattern.lower()
            
            for match in re.finditer(re.escape(pattern_lower), text_lower):
                # Get full match with original case
                start_pos = match.start()
                end_pos = match.end()
                matched_text = text[start_pos:end_pos]
                
                # Get context (50 chars before and after)
                ctx_start = max(0, start_pos - 50)
                ctx_end = min(len(text), end_pos + 50)
                context = text[ctx_start:ctx_end]
                
                entity = BiomedicalEntity(
                    entity_id=str(uuid.uuid4()),
                    text=matched_text,
                    category=category,
                    normalized_text=pattern,
                    confidence=0.85,
                    start_pos=start_pos,
                    end_pos=end_pos,
                    context=context,
                )
                entities.append(entity)
        
        return entities
    
    def extract_with_regex(self, text: str, **kwargs) -> list[BiomedicalEntity]:
        """Extrae entidades usando regex."""
        entities = []
        
        # Unidades de medida
        unit_patterns = [
            (r'\d+\.?\d*\s*(?:mg|mcg|ml|µg|µL|g|kg|mmHg|bpm)', EntityCategory.VALUE),
            (r'\d+\.?\d*\s*(?:°C|°F|K)', EntityCategory.VALUE),
            (r'\d+\.?\d*\s*(?:cm|mm|m)', EntityCategory.VALUE),
        ]
        
        for pattern, category in unit_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                entity = BiomedicalEntity(
                    entity_id=str(uuid.uuid4()),
                    text=match.group(),
                    category=category,
                    confidence=0.9,
                    start_pos=match.start(),
                    end_pos=match.end(),
                )
                entities.append(entity)
        
        return entities


class ConceptExtractor(BaseExtractor):
    """Extractor de conceptos biomédicos."""
    
    CONCEPT_PATTERNS = {
        ConceptCategory.DIAGNOSIS: [
            r'\b(diagnos|diagnosis|diagnosed|diagnostic)\b',
            r'\b(disease|disorder|syndrome)\b',
        ],
        ConceptCategory.TREATMENT: [
            r'\b(treat|therapy|treatment|manage|prescribe)\b',
            r'\b(drug|medication|medicine|surgery)\b',
        ],
        ConceptCategory.SYMPTOM: [
            r'\b(symptom|presenting|complaint)\b',
            r'\b(pain|fever|cough|nausea|dyspnea)\b',
        ],
        ConceptCategory.ETIOLOGY: [
            r'\b(cause|etiology|trigger|risk\s+factor)\b',
            r'\b(due\s+to|result\s+from|leads?\s+to)\b',
        ],
        ConceptCategory.PROGNOSIS: [
            r'\b(prognosis|outcome|survival|progression)\b',
            r'\b(mortality|morbidity|recurrence)\b',
        ],
        ConceptCategory.PREVENTION: [
            r'\b(prevent|prevention|screening|prophylaxis)\b',
            r'\b(vaccin|immuniz)\b',
        ],
    }
    
    def extract(self, text: str, **kwargs) -> list[BiomedicalConcept]:
        """Extrae conceptos biomédicos."""
        concepts = []
        text_lower = text.lower()
        
        for category, patterns in self.CONCEPT_PATTERNS.items():
            for pattern in patterns:
                for match in re.finditer(pattern, text_lower, re.IGNORECASE):
                    concept = BiomedicalConcept(
                        concept_id=str(uuid.uuid4()),
                        text=match.group(),
                        category=category,
                        confidence=0.75,
                    )
                    concepts.append(concept)
        
        return concepts


class RelationExtractor(BaseExtractor):
    """Extractor de relaciones médicas."""
    
    RELATION_PATTERNS = {
        RelationCategory.TREATS: [
            r'(\w+)\s+(treats?|treated\s+with|treatment\s+with)',
            r'(\w+)\s+(is\s+indicated\s+for|indicated\s+in)',
        ],
        RelationCategory.CAUSES: [
            r'(\w+)\s+(causes?|induced|lead\s+to|resulted\s+in)',
            r'(\w+)\s+(due\s+to|caused\s+by|resulting\s+from)',
        ],
        RelationCategory.INTERACTS_WITH: [
            r'(\w+)\s+(interacts?\s+with|interaction\s+with)',
            r'(\w+)\s+and\s+(\w+)\s+(interact|interaction)',
        ],
        RelationCategory.COMPLICATES: [
            r'(\w+)\s+(complicates?|complication\s+of)',
            r'(\w+)\s+(leads?\s+to\s+complications?)',
        ],
    }
    
    def extract(
        self,
        text: str,
        entities: list[BiomedicalEntity],
        **kwargs
    ) -> list[MedicalRelation]:
        """Extrae relaciones entre entidades."""
        relations = []
        entity_texts = {e.text.lower() for e in entities}
        
        for rel_type, patterns in self.RELATION_PATTERNS.items():
            for pattern in patterns:
                for match in re.finditer(pattern, text, re.IGNORECASE):
                    # Find if entities are mentioned
                    matched_entities = []
                    for entity in entities:
                        if entity.text.lower() in text[max(0, match.start()-100):match.end()+100].lower():
                            matched_entities.append(entity)
                    
                    if len(matched_entities) >= 2:
                        relation = MedicalRelation(
                            relation_id=str(uuid.uuid4()),
                            source_entity_id=matched_entities[0].entity_id,
                            target_entity_id=matched_entities[1].entity_id,
                            relation_type=rel_type,
                            confidence=0.7,
                            evidence=match.group(),
                            context=text[max(0, match.start()-50):match.end()+50],
                        )
                        relations.append(relation)
        
        return relations


class MedicalNER:
    """Reconocimiento de entidades médicas (Medical NER)."""
    
    def __init__(self, model_type: str = "rule_based"):
        self.model_type = model_type
        self.entity_extractor = EntityExtractor()
        self.concept_extractor = ConceptExtractor()
    
    def recognize(self, text: str) -> list[BiomedicalEntity]:
        """Reconoce entidades médicas."""
        # Extraer entidades
        entities = self.entity_extractor.extract(text)
        # Agregar entidades de regex
        entities.extend(self.entity_extractor.extract_with_regex(text))
        return entities
    
    def extract_knowledge(
        self,
        text: str,
    ) -> tuple[list[BiomedicalEntity], list[BiomedicalConcept], list[MedicalRelation]]:
        """Extrae conocimiento completo."""
        entities = self.recognize(text)
        concepts = self.concept_extractor.extract(text)
        relations = self._extract_relations(text, entities)
        
        return entities, concepts, relations
    
    def _extract_relations(
        self,
        text: str,
        entities: list[BiomedicalEntity],
    ) -> list[MedicalRelation]:
        """Extrae relaciones."""
        extractor = RelationExtractor()
        return extractor.extract(text, entities=entities)


__all__ = [
    "EntityCategory",
    "ConceptCategory",
    "RelationCategory",
    "BiomedicalEntity",
    "BiomedicalConcept",
    "MedicalRelation",
    "BaseExtractor",
    "EntityExtractor",
    "ConceptExtractor",
    "RelationExtractor",
    "MedicalNER",
]
