"""Unit tests for EPIC 6: Clinical RAG."""

import pytest


class TestEPIC6Imports:
    """Tests for EPIC 6 module imports."""

    def test_import_epic6(self):
        """Test EPIC 6 module imports."""
        from core.PHASE_4.epic6_clinical_rag import (
            ClinicalQueryProcessor,
            ClinicalContextBuilder,
            ClinicalEvidenceBuilder,
        )
        assert ClinicalQueryProcessor is not None
        assert ClinicalContextBuilder is not None

    def test_import_query(self):
        """Test query module imports."""
        from core.PHASE_4.epic6_clinical_rag.query import (
            ClinicalQueryType,
            ProcessedQuery,
            ClinicalQueryProcessor,
        )
        assert ClinicalQueryType is not None
        assert ProcessedQuery is not None

    def test_import_context(self):
        """Test context module imports."""
        from core.PHASE_4.epic6_clinical_rag.context import (
            ClinicalContext,
            ClinicalContextBuilder,
            ContextOptimizer,
        )
        assert ClinicalContext is not None
        assert ClinicalContextBuilder is not None

    def test_import_evidence(self):
        """Test evidence module imports."""
        from core.PHASE_4.epic6_clinical_rag.evidence import (
            EvidencePackage,
            EvidenceItem,
            EvidenceQuality,
        )
        assert EvidencePackage is not None
        assert EvidenceQuality is not None


class TestClinicalQueryProcessor:
    """Tests for ClinicalQueryProcessor."""

    def test_processor_creation(self):
        """Test processor creation."""
        from core.PHASE_4.epic6_clinical_rag import ClinicalQueryProcessor
        
        processor = ClinicalQueryProcessor()
        assert processor is not None

    def test_process_diagnosis_query(self):
        """Test processing diagnosis query."""
        from core.PHASE_4.epic6_clinical_rag import ClinicalQueryProcessor
        from core.PHASE_4.epic6_clinical_rag.query import ClinicalQueryType
        
        processor = ClinicalQueryProcessor()
        result = processor.process("What is the diagnosis for chest pain?")
        
        assert result.original == "What is the diagnosis for chest pain?"
        assert result.normalized is not None
        assert result.intent is not None

    def test_process_treatment_query(self):
        """Test processing treatment query."""
        from core.PHASE_4.epic6_clinical_rag import ClinicalQueryProcessor
        
        processor = ClinicalQueryProcessor()
        result = processor.process("How to treat heart failure?")
        
        assert result.original == "How to treat heart failure?"
        assert result.intent.confidence > 0

    def test_normalize_query(self):
        """Test query normalization."""
        from core.PHASE_4.epic6_clinical_rag import ClinicalQueryProcessor
        
        processor = ClinicalQueryProcessor()
        normalized = processor._normalize("  What is  the diagnosis??  ")
        
        assert normalized == "what is the diagnosis"

    def test_extract_medical_terms(self):
        """Test medical term extraction."""
        from core.PHASE_4.epic6_clinical_rag import ClinicalQueryProcessor
        
        processor = ClinicalQueryProcessor()
        terms = processor._extract_medical_terms("Patient has heart failure with high blood pressure")
        
        assert "heart" in terms
        assert "pressure" in terms


class TestClinicalContextBuilder:
    """Tests for ClinicalContextBuilder."""

    def test_builder_creation(self):
        """Test builder creation."""
        from core.PHASE_4.epic6_clinical_rag import ClinicalContextBuilder
        
        builder = ClinicalContextBuilder()
        assert builder is not None

    def test_build_context(self):
        """Test context building."""
        from core.PHASE_4.epic6_clinical_rag import ClinicalContextBuilder
        
        builder = ClinicalContextBuilder()
        context = builder.build(
            query="Heart failure treatment",
            retrieved_chunks=[
                {"id": "1", "text": "ACE inhibitors are recommended", "score": 0.9},
                {"id": "2", "text": "Beta blockers help", "score": 0.8},
            ]
        )
        
        assert context.query == "Heart failure treatment"
        assert len(context.retrieved_chunks) == 2
        assert context.total_sources >= 1

    def test_context_to_prompt_text(self):
        """Test context to prompt conversion."""
        from core.PHASE_4.epic6_clinical_rag import ClinicalContextBuilder
        
        builder = ClinicalContextBuilder()
        context = builder.build(
            query="Test",
            retrieved_chunks=[
                {"id": "1", "text": "First chunk", "score": 0.9},
                {"id": "2", "text": "Second chunk", "score": 0.8},
            ]
        )
        
        prompt_text = context.to_prompt_text()
        assert "First chunk" in prompt_text
        assert "Second chunk" in prompt_text


class TestContextOptimizer:
    """Tests for ContextOptimizer."""

    def test_optimizer_creation(self):
        """Test optimizer creation."""
        from core.PHASE_4.epic6_clinical_rag import ContextOptimizer
        
        optimizer = ContextOptimizer(max_tokens=1000)
        assert optimizer.max_tokens == 1000

    def test_optimize_no_truncation(self):
        """Test optimization without truncation needed."""
        from core.PHASE_4.epic6_clinical_rag import ContextOptimizer, ClinicalContext
        
        optimizer = ContextOptimizer(max_tokens=1000)
        context = ClinicalContext(
            query="Test",
            query_type="clinical",
            intent_confidence=0.8,
            context_chunks=["Short text"],
            total_tokens=10,
        )
        
        optimized = optimizer.optimize(context)
        assert optimized.total_tokens == 10


class TestClinicalEvidenceBuilder:
    """Tests for ClinicalEvidenceBuilder."""

    def test_builder_creation(self):
        """Test builder creation."""
        from core.PHASE_4.epic6_clinical_rag import ClinicalEvidenceBuilder
        
        builder = ClinicalEvidenceBuilder()
        assert builder is not None

    def test_build_evidence_package(self):
        """Test evidence package building."""
        from core.PHASE_4.epic6_clinical_rag import ClinicalEvidenceBuilder
        
        builder = ClinicalEvidenceBuilder()
        evidence = builder.build(
            query="Heart failure",
            retrieved_chunks=[
                {"id": "1", "text": "Treatment guidelines", "score": 0.9},
                {"id": "2", "text": "Clinical study", "score": 0.8},
            ]
        )
        
        assert evidence.query == "Heart failure"
        assert evidence.total_evidence == 2
        assert evidence.package_id is not None

    def test_evidence_quality_assessment(self):
        """Test evidence quality assessment."""
        from core.PHASE_4.epic6_clinical_rag import ClinicalEvidenceBuilder
        from core.PHASE_4.epic6_clinical_rag.evidence import EvidenceQuality
        
        builder = ClinicalEvidenceBuilder()
        
        # Peer-reviewed
        quality = builder._assess_quality({
            "metadata": {"peer_reviewed": True}
        })
        assert quality == EvidenceQuality.HIGH
        
        # No metadata
        quality = builder._assess_quality({})
        assert quality == EvidenceQuality.LOW

    def test_evidence_citations(self):
        """Test evidence citations."""
        from core.PHASE_4.epic6_clinical_rag import ClinicalEvidenceBuilder
        
        builder = ClinicalEvidenceBuilder()
        evidence = builder.build(
            query="Test",
            retrieved_chunks=[
                {
                    "id": "1",
                    "text": "Content",
                    "score": 0.9,
                    "metadata": {
                        "title": "Test Title",
                        "authors": ["Smith", "Jones"],
                    }
                }
            ]
        )
        
        citations = evidence.get_citations()
        assert len(citations) == 1
        assert "Test Title" in citations[0]


class TestEvidenceTypes:
    """Tests for evidence types."""

    def test_evidence_types(self):
        """Test evidence type enum."""
        from core.PHASE_4.epic6_clinical_rag.evidence import EvidenceType
        
        assert EvidenceType.PEER_REVIEWED.value == "peer_reviewed"
        assert EvidenceType.CLINICAL_GUIDELINE.value == "clinical_guideline"
        assert EvidenceType.MANUFACTURER.value == "manufacturer"

    def test_evidence_quality(self):
        """Test evidence quality enum."""
        from core.PHASE_4.epic6_clinical_rag.evidence import EvidenceQuality
        
        assert EvidenceQuality.HIGH.value == "high"
        assert EvidenceQuality.MEDIUM.value == "medium"
        assert EvidenceQuality.LOW.value == "low"


class TestPromptContextGenerator:
    """Tests for PromptContextGenerator."""

    def test_generator_creation(self):
        """Test generator creation."""
        from core.PHASE_4.epic6_clinical_rag import PromptContextGenerator
        
        generator = PromptContextGenerator()
        assert generator is not None

    def test_generate_prompt(self):
        """Test prompt generation."""
        from core.PHASE_4.epic6_clinical_rag import PromptContextGenerator, ClinicalContext
        
        generator = PromptContextGenerator()
        context = ClinicalContext(
            query="Test query",
            query_type="clinical",
            intent_confidence=0.8,
            context_chunks=["Context chunk 1", "Context chunk 2"],
            total_tokens=10,
        )
        
        prompt = generator.generate(context)
        assert "Test query" in prompt
        assert "Context chunk 1" in prompt


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
