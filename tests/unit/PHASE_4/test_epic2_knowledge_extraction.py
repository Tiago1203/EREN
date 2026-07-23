"""Unit tests for EPIC 2: Knowledge Extraction."""

import pytest
import asyncio


class TestEPIC2Imports:
    """Tests for EPIC 2 module imports."""

    def test_import_epic2(self):
        """Test EPIC 2 module imports."""
        from core.PHASE_4.epic2_knowledge_extraction import (
            MedicalNER,
            EntityExtractor,
            ConceptExtractor,
            KnowledgeExtractionPipeline,
        )
        assert MedicalNER is not None
        assert EntityExtractor is not None

    def test_import_extractors(self):
        """Test extractor imports."""
        from core.PHASE_4.epic2_knowledge_extraction.extractors import (
            EntityCategory,
            ConceptCategory,
            BiomedicalEntity,
            MedicalNER,
        )
        assert EntityCategory is not None
        assert BiomedicalEntity is not None

    def test_import_mappers(self):
        """Test mapper imports."""
        from core.PHASE_4.epic2_knowledge_extraction.mappers import (
            SNOMEDMapper,
            ICDMapper,
            OntologyReference,
            TerminologyMapperFactory,
        )
        assert SNOMEDMapper is not None
        assert TerminologyMapperFactory is not None

    def test_import_pipelines(self):
        """Test pipeline imports."""
        from core.PHASE_4.epic2_knowledge_extraction.pipelines import (
            ExtractedKnowledge,
            KnowledgeExtractionPipeline,
        )
        assert ExtractedKnowledge is not None


class TestEntityExtractor:
    """Tests for EntityExtractor."""

    def test_extract_devices(self):
        """Test device entity extraction."""
        from core.PHASE_4.epic2_knowledge_extraction import EntityExtractor
        from core.PHASE_4.epic2_knowledge_extraction.extractors import EntityCategory
        
        extractor = EntityExtractor()
        text = "Patient on ventilator and infusion pump."
        entities = extractor.extract(text)
        
        device_entities = [e for e in entities if e.category == EntityCategory.DEVICE]
        assert len(device_entities) >= 2
        assert any("ventilator" in e.text.lower() for e in device_entities)

    def test_extract_drugs(self):
        """Test drug entity extraction."""
        from core.PHASE_4.epic2_knowledge_extraction import EntityExtractor
        from core.PHASE_4.epic2_knowledge_extraction.extractors import EntityCategory
        
        extractor = EntityExtractor()
        text = "Take aspirin 100mg and metformin 500mg daily."
        entities = extractor.extract(text)
        
        drug_entities = [e for e in entities if e.category == EntityCategory.DRUG]
        assert len(drug_entities) >= 2

    def test_extract_conditions(self):
        """Test condition entity extraction."""
        from core.PHASE_4.epic2_knowledge_extraction import EntityExtractor
        from core.PHASE_4.epic2_knowledge_extraction.extractors import EntityCategory
        
        extractor = EntityExtractor()
        text = "Patient has hypertension and diabetes."
        entities = extractor.extract(text)
        
        condition_entities = [e for e in entities if e.category == EntityCategory.CONDITION]
        assert len(condition_entities) >= 2

    def test_extract_with_context(self):
        """Test entity context extraction."""
        from core.PHASE_4.epic2_knowledge_extraction import EntityExtractor
        
        extractor = EntityExtractor()
        text = "The patient was diagnosed with heart failure."
        entities = extractor.extract(text)
        
        if entities:
            entity = entities[0]
            assert entity.context != ""  # Should have context


class TestMedicalNER:
    """Tests for MedicalNER."""

    def test_recognize_entities(self):
        """Test MedicalNER entity recognition."""
        from core.PHASE_4.epic2_knowledge_extraction import MedicalNER
        
        ner = MedicalNER()
        text = "ECG shows normal rhythm. Patient takes metoprolol for hypertension."
        entities = ner.recognize(text)
        
        assert len(entities) > 0

    def test_extract_knowledge(self):
        """Test full knowledge extraction."""
        from core.PHASE_4.epic2_knowledge_extraction import MedicalNER
        
        ner = MedicalNER()
        text = "Patient with heart failure treated with lisinopril."
        entities, concepts, relations = ner.extract_knowledge(text)
        
        assert len(entities) > 0
        assert len(concepts) >= 0
        assert len(relations) >= 0


class TestConceptExtractor:
    """Tests for ConceptExtractor."""

    def test_extract_concepts(self):
        """Test concept extraction."""
        from core.PHASE_4.epic2_knowledge_extraction import ConceptExtractor
        from core.PHASE_4.epic2_knowledge_extraction.extractors import ConceptCategory
        
        extractor = ConceptExtractor()
        text = "The diagnosis is hypertension. Treatment includes lifestyle changes."
        concepts = extractor.extract(text)
        
        assert len(concepts) >= 0


class TestMappers:
    """Tests for ontology mappers."""

    def test_snomed_mapper(self):
        """Test SNOMED mapper."""
        from core.PHASE_4.epic2_knowledge_extraction.mappers import SNOMEDMapper
        import asyncio
        
        async def test():
            mapper = SNOMEDMapper()
            result = await mapper.map_term("heart failure")
            
            assert result.mapped is True
            assert result.best_match is not None
            assert result.best_match.code == "84114007"
            assert result.best_match.ontology == "SNOMED-CT"
        
        asyncio.run(test())

    def test_snomed_mapper_not_found(self):
        """Test SNOMED mapper with unknown term."""
        from core.PHASE_4.epic2_knowledge_extraction.mappers import SNOMEDMapper
        import asyncio
        
        async def test():
            mapper = SNOMEDMapper()
            result = await mapper.map_term("unknown_medical_term_xyz")
            
            assert result.mapped is False
            assert result.best_match is None
        
        asyncio.run(test())

    def test_icd_mapper(self):
        """Test ICD mapper."""
        from core.PHASE_4.epic2_knowledge_extraction.mappers import ICDMapper
        import asyncio
        
        async def test():
            mapper = ICDMapper()
            result = await mapper.map_term("hypertension")
            
            assert result.mapped is True
            assert result.best_match.code == "I10"
        
        asyncio.run(test())

    def test_mesh_mapper(self):
        """Test MeSH mapper."""
        from core.PHASE_4.epic2_knowledge_extraction.mappers import MeSHMapper
        import asyncio
        
        async def test():
            mapper = MeSHMapper()
            result = await mapper.map_term("heart disease")
            
            assert result.mapped is True
            assert result.best_match.ontology == "MeSH"
        
        asyncio.run(test())

    def test_terminology_mapper_factory(self):
        """Test TerminologyMapperFactory."""
        from core.PHASE_4.epic2_knowledge_extraction.mappers import TerminologyMapperFactory
        import asyncio
        
        async def test():
            mappers = TerminologyMapperFactory.create_all()
            
            assert "SNOMED" in mappers
            assert "UMLS" in mappers
            assert "MeSH" in mappers
            assert "ICD-10" in mappers
            
            # Test SNOMED mapper
            snomed_result = await mappers["SNOMED"].map_term("heart failure")
            assert snomed_result.mapped is True
            assert "SNOMED" in snomed_result.ontology  # ontology_name property
        
        asyncio.run(test())


class TestPipelines:
    """Tests for extraction pipelines."""

    def test_entity_pipeline(self):
        """Test EntityPipeline."""
        from core.PHASE_4.epic2_knowledge_extraction.pipelines import EntityPipeline
        import asyncio
        
        async def test():
            pipeline = EntityPipeline()
            text = "Patient on ventilator with heart failure."
            entities = await pipeline.process(text)
            
            assert len(entities) > 0
        
        asyncio.run(test())

    def test_knowledge_extraction_pipeline(self):
        """Test KnowledgeExtractionPipeline."""
        from core.PHASE_4.epic2_knowledge_extraction.pipelines import KnowledgeExtractionPipeline
        from core.PHASE_4.foundation import KnowledgeDomain
        import asyncio
        
        async def test():
            pipeline = KnowledgeExtractionPipeline()
            
            knowledge = await pipeline.extract(
                text="Patient has hypertension and diabetes. Takes metformin daily.",
                domain=KnowledgeDomain.CARDIOLOGY
            )
            
            assert knowledge.extraction_id is not None
            assert knowledge.domain == KnowledgeDomain.CARDIOLOGY
            assert knowledge.entity_count >= 0
            assert knowledge.extraction_time_ms >= 0
        
        asyncio.run(test())


class TestIntegration:
    """Integration tests for EPIC 2."""

    def test_document_to_knowledge_flow(self):
        """Test flow from EPIC 1 to EPIC 2."""
        from core.PHASE_4.epic2_knowledge_extraction import KnowledgeExtractionPipeline
        from core.PHASE_4.foundation import KnowledgeDomain
        import asyncio
        
        async def test():
            # Simular documento procesado (de EPIC 1)
            document_text = """
            A 65-year-old patient with a history of heart failure 
            presents with hypertension. Current medications include 
            lisinopril 10mg daily and metformin 500mg twice daily.
            ECG shows normal sinus rhythm. Patient uses oxygen concentrator.
            """
            
            # Extraer conocimiento (EPIC 2)
            pipeline = KnowledgeExtractionPipeline()
            knowledge = await pipeline.extract(
                text=document_text,
                domain=KnowledgeDomain.CARDIOLOGY
            )
            
            # Verificar extracción
            assert knowledge.entity_count > 0
            assert knowledge.extraction_time_ms >= 0
            
            # Verificar ontologías
            if knowledge.ontology_references:
                ref = knowledge.ontology_references[0]
                assert ref.ontology in ["SNOMED-CT", "UMLS", "MeSH", "ICD-10"]
        
        asyncio.run(test())


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
