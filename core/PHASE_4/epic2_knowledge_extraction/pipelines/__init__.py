"""
PHASE 4 - EPIC 2: Pipelines Module

Pipelines de extracción de conocimiento:
- Entity Pipeline
- Knowledge Extraction Pipeline
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import uuid

from core.PHASE_4.foundation import (
    KnowledgeDomain,
    MedicalCode,
    InMemoryEventPublisher,
    DomainEvent,
    EventType,
)


@dataclass
class ExtractedKnowledge:
    """Conocimiento extraído completo."""
    extraction_id: str
    source_text: str
    domain: KnowledgeDomain
    
    # Entidades biomédicas
    entities: list = field(default_factory=list)
    entity_count: int = 0
    
    # Conceptos
    concepts: list = field(default_factory=list)
    concept_count: int = 0
    
    # Relaciones
    relations: list = field(default_factory=list)
    relation_count: int = 0
    
    # Códigos médicos
    medical_codes: list[MedicalCode] = field(default_factory=list)
    code_count: int = 0
    
    # Mapeos ontológicos
    ontology_references: list = field(default_factory=list)
    
    # Metadata
    extraction_time_ms: int = 0
    confidence_avg: float = 0.0
    extracted_at: datetime = field(default_factory=lambda: datetime.now())
    
    # Calidad
    coverage_score: float = 0.0
    coherence_score: float = 0.0


class EntityPipeline:
    """Pipeline para extracción de entidades."""
    
    def __init__(self):
        from core.PHASE_4.epic2_knowledge_extraction.extractors import MedicalNER, EntityExtractor
        self.ner = MedicalNER()
        self.entity_extractor = EntityExtractor()
    
    async def extract_entities(self, text: str) -> list:
        """Extrae entidades del texto."""
        return self.ner.recognize(text)
    
    async def process(self, text: str) -> list:
        """Procesa texto y retorna entidades."""
        return await self.extract_entities(text)


class KnowledgeExtractionPipeline:
    """Pipeline completo de extracción de conocimiento."""
    
    def __init__(self):
        from core.PHASE_4.epic2_knowledge_extraction.extractors import MedicalNER
        from core.PHASE_4.epic2_knowledge_extraction.mappers import TerminologyMapperFactory
        
        self.ner = MedicalNER()
        self.ontology_mappers = TerminologyMapperFactory.create_all()
        self.event_publisher = InMemoryEventPublisher()
    
    async def extract(self, text: str, domain: KnowledgeDomain = KnowledgeDomain.GENERAL) -> ExtractedKnowledge:
        """Extrae conocimiento completo del texto."""
        import time
        start = time.time()
        
        extraction_id = str(uuid.uuid4())
        
        # 1. Extraer entidades usando NER
        entities = self.ner.recognize(text)
        
        # 2. Extraer conceptos
        _, concepts, relations = self.ner.extract_knowledge(text)
        
        # 3. Mapear entidades a ontologías
        ontology_refs = await self._map_entities_to_ontologies(entities)
        
        # 4. Extraer códigos médicos
        medical_codes = await self._extract_medical_codes(entities)
        
        # 5. Calcular scores de calidad
        confidence = self._calculate_confidence(entities, concepts)
        
        extraction_time_ms = int((time.time() - start) * 1000)
        
        # 6. Publicar evento
        event = DomainEvent.create(
            event_type=EventType.EXTRACTION_COMPLETED,
            metadata={
                "extraction_id": extraction_id,
                "entity_count": len(entities),
                "concept_count": len(concepts),
                "extraction_time_ms": extraction_time_ms,
            },
        )
        await self.event_publisher.publish(event)
        
        return ExtractedKnowledge(
            extraction_id=extraction_id,
            source_text=text[:500] + "..." if len(text) > 500 else text,
            domain=domain,
            entities=entities,
            entity_count=len(entities),
            concepts=concepts,
            concept_count=len(concepts),
            relations=relations,
            relation_count=len(relations),
            medical_codes=medical_codes,
            code_count=len(medical_codes),
            ontology_references=ontology_refs,
            extraction_time_ms=extraction_time_ms,
            confidence_avg=confidence,
        )
    
    async def _map_entities_to_ontologies(self, entities: list) -> list:
        """Mapea entidades a ontologías."""
        refs = []
        
        for entity in entities:
            for ontology_name, mapper in self.ontology_mappers.items():
                result = await mapper.map_term(entity.text)
                if result.mapped and result.best_match:
                    refs.append(result.best_match)
                    # Agregar código a la entidad
                    entity.medical_codes.append(f"{ontology_name}:{result.best_match.code}")
        
        return refs
    
    async def _extract_medical_codes(self, entities: list) -> list[MedicalCode]:
        """Extrae códigos médicos de entidades."""
        codes = []
        
        for entity in entities:
            for code_str in entity.medical_codes:
                if ":" in code_str:
                    ontology, code = code_str.split(":", 1)
                    codes.append(MedicalCode(
                        system=ontology,
                        code=code,
                        display=entity.text,
                    ))
        
        return codes
    
    def _calculate_confidence(self, entities: list, concepts: list) -> float:
        """Calcula confianza promedio."""
        confidences = [e.confidence for e in entities]
        confidences.extend([c.confidence for c in concepts])
        
        if not confidences:
            return 0.0
        
        return sum(confidences) / len(confidences)


__all__ = [
    "ExtractedKnowledge",
    "EntityPipeline",
    "KnowledgeExtractionPipeline",
]
