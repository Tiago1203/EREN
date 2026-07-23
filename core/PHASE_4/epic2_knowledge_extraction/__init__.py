"""
PHASE 4 - EPIC 2: Biomedical Knowledge Extraction Engine

Extrae conocimiento estructurado de documentos biomédicos:
- Entidades médicas (dispositivos, drogas, condiciones)
- Conceptos clínicos (diagnósticos, tratamientos)
- Relaciones entre entidades
- Ontologías y terminología clínica
- Códigos médicos (ICD, SNOMED, LOINC)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Optional
import uuid

from core.PHASE_4.foundation import (
    ProcessedDocument,
    ExtractedKnowledge,
    ExtractedEntity,
    ExtractedConcept,
    ExtractedRelation,
    MedicalCode,
    KnowledgeDomain,
)


class EntityType(str, Enum):
    """Tipos de entidades médicas."""
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
    ORGANIZATION = "ORGANIZATION"
    PERSON = "PERSON"
    LOCATION = "LOCATION"
    DATE = "DATE"
    QUANTITY = "QUANTITY"


class ConceptCategory(str, Enum):
    """Categorías de conceptos clínicos."""
    DIAGNOSIS = "DIAGNOSIS"
    TREATMENT = "TREATMENT"
    SYMPTOM = "SYMPTOM"
    ANATOMY = "ANATOMY"
    ETIOLOGY = "ETIOLOGY"
    PROGNOSIS = "PROGNOSIS"
    PREVENTION = "PREVENTION"
    COMPLICATION = "COMPLICATION"
    CONTRAINDICATION = "CONTRAINDICATION"
    INDICATION = "INDICATION"
    SIDE_EFFECT = "SIDE_EFFECT"
    INTERACTION = "INTERACTION"


class RelationType(str, Enum):
    """Tipos de relaciones entre entidades."""
    TREATS = "TREATS"
    CAUSES = "CAUSES"
    INTERACTS_WITH = "INTERACTS_WITH"
    IS_A = "IS_A"
    PART_OF = "PART_OF"
    LOCATED_IN = "LOCATED_IN"
    DIAGNOSES = "DIAGNOSES"
    MANIFESTS_AS = "MANIFESTS_AS"
    PREVENTS = "PREVENTS"
    COMPLICATES = "COMPLICATES"
    ASSESSES = "ASSESSES"
    HAS_CONTRAINDICATION = "HAS_CONTRAINDICATION"


class ExtractionModel(str, Enum):
    """Modelos de extracción."""
    SPACY = "spacy"
    TRANSFORMERS = "transformers"
    BIOMEDBERT = "biomedbert"
    PUBMEDBERT = "pubmedbert"
    CLINICALBERT = "clinicalbert"
    RULE_BASED = "rule_based"
    HYBRID = "hybrid"


@dataclass
class EntityCandidate:
    """Candidato de entidad encontrado."""
    text: str
    start_pos: int
    end_pos: int
    entity_type: EntityType
    confidence: float
    normalized_form: str = ""
    linked_codes: list[MedicalCode] = field(default_factory=list)
    context: str = ""


@dataclass
class ConceptCandidate:
    """Candidato de concepto encontrado."""
    text: str
    category: ConceptCategory
    confidence: float
    definition: str = ""
    synonyms: list[str] = field(default_factory=list)
    linked_codes: list[MedicalCode] = field(default_factory=list)


@dataclass
class RelationCandidate:
    """Candidato de relación encontrado."""
    source_text: str
    target_text: str
    relation_type: RelationType
    confidence: float
    evidence: str = ""
    context: str = ""


@dataclass
class ExtractionResult:
    """Resultado de extracción de conocimiento."""
    extraction_id: str
    document_id: str
    
    # Entidades
    entities: list[ExtractedEntity] = field(default_factory=list)
    entity_count: int = 0
    
    # Conceptos
    concepts: list[ExtractedConcept] = field(default_factory=list)
    concept_count: int = 0
    
    # Relaciones
    relations: list[ExtractedRelation] = field(default_factory=list)
    relation_count: int = 0
    
    # Códigos
    medical_codes: list[MedicalCode] = field(default_factory=list)
    
    # Metadatos de extracción
    model_used: str = ""
    extraction_time_ms: int = 0
    confidence_avg: float = 0.0
    
    # Calidad
    coverage_score: float = 0.0  # Qué % del documento fue cubierto
    coherence_score: float = 0.0  # Qué tan coherentes son las extracciones
    
    extracted_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class OntologyMapping:
    """Mapeo a ontologías médicas."""
    original_term: str
    ontology: str  # SNOMED, UMLS, ICD10, etc
    code: str
    display_name: str
    confidence: float
    synonyms: list[str] = field(default_factory=list)


class INamedEntityRecognizer:
    """Protocolo para reconocimiento de entidades nombradas."""
    
    async def recognize(self, text: str) -> list[EntityCandidate]:
        """Reconoce entidades en texto."""
        ...


class IConceptExtractor:
    """Protocolo para extracción de conceptos."""
    
    async def extract(self, text: str, domain: KnowledgeDomain) -> list[ConceptCandidate]:
        """Extrae conceptos clínicos."""
        ...


class IRelationExtractor:
    """Protocolo para extracción de relaciones."""
    
    async def extract_relations(
        self,
        text: str,
        entities: list[ExtractedEntity],
    ) -> list[RelationCandidate]:
        """Extrae relaciones entre entidades."""
        ...


class ICodeLinker:
    """Protocolo para link a códigos médicos."""
    
    async def link_to_icd10(self, term: str) -> list[MedicalCode]:
        """Link término a ICD-10."""
        ...
    
    async def link_to_snomed(self, term: str) -> list[MedicalCode]:
        """Link término a SNOMED CT."""
        ...
    
    async def link_to_loinc(self, term: str) -> list[MedicalCode]:
        """Link término a LOINC."""
        ...


class IOntologyMapper:
    """Protocolo para mapeo a ontologías."""
    
    async def map_term(
        self,
        term: str,
        ontologies: list[str],
    ) -> list[OntologyMapping]:
        """Mapea término a ontologías."""
        ...


class SpacyNerRecognizer:
    """Reconocedor NER usando spaCy."""
    
    def __init__(self, model: str = "en_core_sci_sm"):
        self.model = model
        self._nlp = None
    
    async def recognize(self, text: str) -> list[EntityCandidate]:
        """Reconoce entidades usando spaCy."""
        # Placeholder - would use spaCy model
        return []
    
    def _map_pos_to_entity_type(self, label: str) -> EntityType:
        """Mapea label spaCy a EntityType."""
        mapping = {
            "ORG": EntityType.ORGANIZATION,
            "PERSON": EntityType.PERSON,
            "GPE": EntityType.LOCATION,
            "DATE": EntityType.DATE,
            "QUANTITY": EntityType.QUANTITY,
        }
        return mapping.get(label, EntityType.DEVICE)


class BiomedicalNerRecognizer:
    """Reconocedor NER especializado para biomedicina."""
    
    def __init__(self, model: ExtractionModel = ExtractionModel.BIOMEDBERT):
        self.model = model
        self._recognizer = None
    
    async def recognize(self, text: str) -> list[EntityCandidate]:
        """Reconoce entidades biomédicas."""
        # Placeholder - would use BioBERT, PubMedBERT, etc
        candidates = []
        
        # Common device patterns
        import re
        device_patterns = [
            r'\b(infusion pump|ventilator|defibrillator|monitor|pacemaker)\b',
            r'\b(X-ray|CT|MRI|ultrasound|EKG|ECG)\b',
        ]
        
        for pattern in device_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                candidates.append(EntityCandidate(
                    text=match.group(),
                    start_pos=match.start(),
                    end_pos=match.end(),
                    entity_type=EntityType.DEVICE,
                    confidence=0.9,
                    normalized_form=match.group().lower(),
                ))
        
        return candidates


class ClinicalConceptExtractor:
    """Extractor de conceptos clínicos."""
    
    def __init__(self):
        self._concept_db = {}  # Placeholder for concept database
    
    async def extract(
        self,
        text: str,
        domain: KnowledgeDomain,
    ) -> list[ConceptCandidate]:
        """Extrae conceptos según dominio clínico."""
        candidates = []
        
        # Keyword-based extraction
        domain_keywords = self._get_domain_keywords(domain)
        
        import re
        for keyword, category in domain_keywords:
            pattern = rf'\b{keyword}\b'
            for match in re.finditer(pattern, text, re.IGNORECASE):
                candidates.append(ConceptCandidate(
                    text=match.group(),
                    category=category,
                    confidence=0.85,
                ))
        
        return candidates
    
    def _get_domain_keywords(self, domain: KnowledgeDomain) -> list[tuple]:
        """Obtiene keywords según dominio."""
        keywords = {
            KnowledgeDomain.CARDIOLOGY: [
                ("heart failure", ConceptCategory.DIAGNOSIS),
                ("myocardial infarction", ConceptCategory.DIAGNOSIS),
                ("arrhythmia", ConceptCategory.DIAGNOSIS),
                ("beta blocker", ConceptCategory.TREATMENT),
                ("angina", ConceptCategory.SYMPTOM),
            ],
            KnowledgeDomain.CRITICAL_CARE: [
                ("sepsis", ConceptCategory.DIAGNOSIS),
                ("respiratory failure", ConceptCategory.DIAGNOSIS),
                ("shock", ConceptCategory.DIAGNOSIS),
                ("ventilation", ConceptCategory.TREATMENT),
                ("vasopressor", ConceptCategory.TREATMENT),
            ],
        }
        return keywords.get(domain, [])


class RuleBasedRelationExtractor:
    """Extractor de relaciones basado en reglas."""
    
    def __init__(self):
        self._patterns = self._load_relation_patterns()
    
    def _load_relation_patterns(self) -> dict:
        """Carga patrones de relaciones."""
        return {
            RelationType.TREATS: [
                r'(\w+)\s+(treats?|treated|therapy|treatment)',
                r'(\w+)\s+is\s+indicated\s+for',
            ],
            RelationType.CAUSES: [
                r'(\w+)\s+(causes?|induced|lead\s+to)',
                r'(\w+)\s+may\s+result\s+in',
            ],
            RelationType.INTERACTS_WITH: [
                r'(\w+)\s+interacts?\s+with',
                r'(\w+)\s+and\s+(\w+)\s+interaction',
            ],
        }
    
    async def extract_relations(
        self,
        text: str,
        entities: list[ExtractedEntity],
    ) -> list[RelationCandidate]:
        """Extrae relaciones usando patrones."""
        import re
        candidates = []
        
        entity_texts = {e.text for e in entities}
        
        for rel_type, patterns in self._patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    # Verify entities are in the match
                    match_entities = [e for e in entity_texts if e in match.group()]
                    if len(match_entities) >= 2:
                        candidates.append(RelationCandidate(
                            source_text=match_entities[0],
                            target_text=match_entities[1],
                            relation_type=rel_type,
                            confidence=0.8,
                            evidence=match.group(),
                            context=text[max(0, match.start()-50):match.end()+50],
                        ))
        
        return candidates


class MedicalCodeLinker:
    """Linker de códigos médicos."""
    
    def __init__(self):
        self._icd10_cache = {}
        self._snomed_cache = {}
    
    async def link_to_icd10(self, term: str) -> list[MedicalCode]:
        """Link término a ICD-10."""
        # Placeholder - would call ICD-10 API/database
        return []
    
    async def link_to_snomed(self, term: str) -> list[MedicalCode]:
        """Link término a SNOMED CT."""
        return []
    
    async def link_to_loinc(self, term: str) -> list[MedicalCode]:
        """Link término a LOINC."""
        return []


class KnowledgeExtractionPipeline:
    """Pipeline completo de extracción de conocimiento."""
    
    def __init__(
        self,
        ner: INamedEntityRecognizer | None = None,
        concept_extractor: IConceptExtractor | None = None,
        relation_extractor: IRelationExtractor | None = None,
        code_linker: ICodeLinker | None = None,
    ):
        self.ner = ner or BiomedicalNerRecognizer()
        self.concept_extractor = concept_extractor or ClinicalConceptExtractor()
        self.relation_extractor = relation_extractor or RuleBasedRelationExtractor()
        self.code_linker = code_linker or MedicalCodeLinker()
    
    async def extract(
        self,
        document: ProcessedDocument,
        domain: KnowledgeDomain | None = None,
    ) -> ExtractedKnowledge:
        """Extrae conocimiento de documento procesado."""
        import time
        start = time.time()
        
        extraction_id = str(uuid.uuid4())
        
        # 1. Extract entities
        entities = await self._extract_entities(document.content)
        
        # 2. Extract concepts
        concepts = await self._extract_concepts(
            document.content,
            domain or KnowledgeDomain.GENERAL,
        )
        
        # 3. Extract relations
        relations = await self._extract_relations(document.content, entities)
        
        # 4. Link to medical codes
        medical_codes = await self._link_codes(entities, concepts)
        
        # 5. Calculate quality scores
        confidence_avg = self._calculate_avg_confidence(entities, concepts)
        
        # 6. Generate summary
        summary = self._generate_summary(document.content, entities, concepts)
        
        # 7. Extract keywords
        keywords = self._extract_keywords(entities, concepts)
        
        extraction_time_ms = int((time.time() - start) * 1000)
        
        return ExtractedKnowledge(
            extraction_id=extraction_id,
            document_id=document.document_id,
            entities=entities,
            concepts=concepts,
            relations=relations,
            summary=summary,
            keywords=keywords,
            medical_codes=medical_codes,
            quality_score=confidence_avg,
        )
    
    async def _extract_entities(self, text: str) -> list[ExtractedEntity]:
        """Extrae entidades."""
        candidates = await self.ner.recognize(text)
        
        entities = []
        for candidate in candidates:
            entities.append(ExtractedEntity(
                entity_id=str(uuid.uuid4()),
                text=candidate.text,
                type=candidate.entity_type.value,
                confidence=candidate.confidence,
                start_pos=candidate.start_pos,
                end_pos=candidate.end_pos,
                normalized_form=candidate.normalized_form,
                medical_codes=candidate.linked_codes,
            ))
        
        return entities
    
    async def _extract_concepts(
        self,
        text: str,
        domain: KnowledgeDomain,
    ) -> list[ExtractedConcept]:
        """Extrae conceptos."""
        candidates = await self.concept_extractor.extract(text, domain)
        
        concepts = []
        for candidate in candidates:
            concepts.append(ExtractedConcept(
                concept_id=str(uuid.uuid4()),
                text=candidate.text,
                category=candidate.category.value,
                definition=candidate.definition,
                synonyms=candidate.synonyms,
                medical_codes=candidate.linked_codes,
            ))
        
        return concepts
    
    async def _extract_relations(
        self,
        text: str,
        entities: list[ExtractedEntity],
    ) -> list[ExtractedRelation]:
        """Extrae relaciones."""
        candidates = await self.relation_extractor.extract_relations(text, entities)
        
        relations = []
        for candidate in candidates:
            relations.append(ExtractedRelation(
                relation_id=str(uuid.uuid4()),
                source_entity_id=candidate.source_text,
                target_entity_id=candidate.target_text,
                relation_type=candidate.relation_type.value,
                confidence=candidate.confidence,
                evidence=candidate.evidence,
            ))
        
        return relations
    
    async def _link_codes(
        self,
        entities: list[ExtractedEntity],
        concepts: list[ExtractedConcept],
    ) -> list[MedicalCode]:
        """Link entidades y conceptos a códigos médicos."""
        codes = []
        
        for entity in entities:
            if not entity.medical_codes:
                icd_codes = await self.code_linker.link_to_icd10(entity.text)
                snomed_codes = await self.code_linker.link_to_snomed(entity.text)
                codes.extend(icd_codes + snomed_codes)
        
        for concept in concepts:
            if not concept.medical_codes:
                snomed_codes = await self.code_linker.link_to_snomed(concept.text)
                codes.extend(snomed_codes)
        
        return codes
    
    def _calculate_avg_confidence(
        self,
        entities: list[ExtractedEntity],
        concepts: list[ExtractedConcept],
    ) -> float:
        """Calcula confianza promedio."""
        all_confidences = [e.confidence for e in entities]
        all_confidences.extend([c.confidence for c in concepts])
        
        if not all_confidences:
            return 0.0
        
        return sum(all_confidences) / len(all_confidences)
    
    def _generate_summary(
        self,
        text: str,
        entities: list[ExtractedEntity],
        concepts: list[ExtractedConcept],
    ) -> str:
        """Genera resumen del documento."""
        # Take first 500 chars as summary
        sentences = text.split('.')
        summary_parts = []
        char_count = 0
        
        for sentence in sentences[:5]:
            if char_count + len(sentence) < 500:
                summary_parts.append(sentence)
                char_count += len(sentence)
        
        return '.'.join(summary_parts).strip() + '.'
    
    def _extract_keywords(
        self,
        entities: list[ExtractedEntity],
        concepts: list[ExtractedConcept],
    ) -> list[str]:
        """Extrae keywords del documento."""
        keywords = set()
        
        for entity in entities:
            if entity.confidence > 0.8:
                keywords.add(entity.normalized_form or entity.text.lower())
        
        for concept in concepts:
            if concept.confidence > 0.8:
                keywords.add(concept.text.lower())
        
        return list(keywords)[:20]  # Top 20 keywords


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Enums
    "EntityType",
    "ConceptCategory",
    "RelationType",
    "ExtractionModel",
    # Data Classes
    "EntityCandidate",
    "ConceptCandidate",
    "RelationCandidate",
    "ExtractionResult",
    "OntologyMapping",
    # Protocols
    "INamedEntityRecognizer",
    "IConceptExtractor",
    "IRelationExtractor",
    "ICodeLinker",
    "IOntologyMapper",
    # Implementations
    "SpacyNerRecognizer",
    "BiomedicalNerRecognizer",
    "ClinicalConceptExtractor",
    "RuleBasedRelationExtractor",
    "MedicalCodeLinker",
    # Pipeline
    "KnowledgeExtractionPipeline",
]
