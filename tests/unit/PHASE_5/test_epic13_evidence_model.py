"""
Tests para EPIC 13: Evidence Lifecycle Model
"""

import pytest
from datetime import datetime

from core.PHASE_5.epic13_evidence_model.domain import (
    Evidence,
    EvidenceBundle,
    EvidenceQuality,
    EvidenceSource,
    EvidenceCitation,
    EvidenceType,
    QualityLevel,
    SourceType,
    EvidenceContent,
    RelevanceScore,
    ApplicabilityScore,
)
from core.PHASE_5.epic13_evidence_model.agent import EvidenceLifecycleAgent


class TestEvidence:
    """Tests para Evidence."""
    
    def test_evidence_creation(self):
        """Test creación de evidencia."""
        evidence = Evidence(
            evidence_id="ev_1",
            evidence_type=EvidenceType.CLINICAL_TRIAL,
            source=EvidenceSource(
                source_type=SourceType.PUBMED,
                name="PubMed",
                doi="10.1234/test",
            ),
            content=EvidenceContent(
                title="Test Study",
                abstract="Abstract...",
                findings="Findings...",
                conclusions="Conclusions...",
            ),
            quality=EvidenceQuality(
                quality_level=QualityLevel.MODERATE,
                score=0.7,
                methodology_score=0.8,
                sample_size_score=0.6,
                consistency_score=0.7,
                publication_bias_score=0.2,
            ),
            relevance=RelevanceScore(
                score=0.75,
                relevance_to_query="test query",
                population_match=0.8,
                outcome_match=0.7,
            ),
            applicability=ApplicabilityScore(
                score=0.7,
                clinical_setting_match=0.8,
                patient_population_match=0.7,
                resource_availability=0.6,
            ),
            citation=EvidenceCitation(citation_text="Test citation"),
        )
        
        assert evidence.evidence_id == "ev_1"
        assert evidence.evidence_type == EvidenceType.CLINICAL_TRIAL
        assert evidence.quality.quality_level == QualityLevel.MODERATE
    
    def test_get_confidence_level(self):
        """Test obtener nivel de confianza."""
        evidence = Evidence(
            evidence_id="ev_1",
            evidence_type=EvidenceType.CLINICAL_TRIAL,
            source=EvidenceSource(source_type=SourceType.PUBMED, name="Test"),
            content=EvidenceContent("Title", "Abstract", "Findings", "Conclusions"),
            quality=EvidenceQuality(QualityLevel.MODERATE, 0.7, 0.8, 0.6, 0.7, 0.2),
            relevance=RelevanceScore(0.75, "query", 0.8, 0.7),
            applicability=ApplicabilityScore(0.7, 0.8, 0.7, 0.6),
            citation=EvidenceCitation("Citation"),
        )
        
        confidence = evidence.get_confidence_level()
        assert 0 <= confidence <= 1
    
    def test_is_strong_evidence(self):
        """Test verificar si es evidencia fuerte."""
        evidence = Evidence(
            evidence_id="ev_1",
            evidence_type=EvidenceType.CLINICAL_TRIAL,
            source=EvidenceSource(source_type=SourceType.PUBMED, name="Test"),
            content=EvidenceContent("Title", "Abstract", "Findings", "Conclusions"),
            quality=EvidenceQuality(QualityLevel.HIGH, 0.9, 0.9, 0.8, 0.9, 0.1),
            relevance=RelevanceScore(0.8, "query", 0.8, 0.8),
            applicability=ApplicabilityScore(0.8, 0.8, 0.8, 0.8),
            citation=EvidenceCitation("Citation"),
        )
        
        assert evidence.is_strong() is True


class TestEvidenceQuality:
    """Tests para EvidenceQuality."""
    
    def test_is_high_quality(self):
        """Test verificar si es alta calidad."""
        quality = EvidenceQuality(
            quality_level=QualityLevel.HIGH,
            score=0.9,
            methodology_score=0.9,
            sample_size_score=0.8,
            consistency_score=0.9,
            publication_bias_score=0.1,
        )
        
        assert quality.is_high_quality() is True
    
    def test_get_limitations(self):
        """Test obtener limitaciones."""
        quality = EvidenceQuality(
            quality_level=QualityLevel.LOW,
            score=0.4,
            methodology_score=0.4,
            sample_size_score=0.3,
            consistency_score=0.5,
            publication_bias_score=0.4,
        )
        
        limitations = quality.get_limitations()
        assert len(limitations) > 0
        assert "Methodology concerns" in limitations


class TestEvidenceBundle:
    """Tests para EvidenceBundle."""
    
    def test_bundle_creation(self):
        """Test creación de bundle."""
        bundle = EvidenceBundle(
            bundle_id="bundle_1",
            query="test query",
            evidence_list=[],
        )
        
        assert bundle.bundle_id == "bundle_1"
        assert bundle.query == "test query"
        assert len(bundle.evidence_list) == 0
    
    def test_get_average_quality(self):
        """Test obtener calidad promedio."""
        bundle = EvidenceBundle(
            bundle_id="bundle_1",
            query="test",
            evidence_list=[],
        )
        
        assert bundle.get_average_quality() == 0.0


class TestEvidenceSource:
    """Tests para EvidenceSource."""
    
    def test_is_peer_reviewed(self):
        """Test verificar si es peer-reviewed."""
        source = EvidenceSource(
            source_type=SourceType.PUBMED,
            name="PubMed",
        )
        
        assert source.is_peer_reviewed() is True


class TestEvidenceLifecycleAgent:
    """Tests para EvidenceLifecycleAgent."""
    
    @pytest.mark.asyncio
    async def test_retrieve_evidence(self):
        """Test recuperar evidencia."""
        from core.PHASE_5.foundation import AgentTask
        
        agent = EvidenceLifecycleAgent(agent_id="test_agent")
        
        task = AgentTask(
            task_id="task_1",
            agent_id="test_agent",
            task_type="evidence",
            input={
                "action": "retrieve",
                "query": "ventilator maintenance",
            },
        )
        
        result = await agent.execute(task)
        
        assert "evidence" in result
        assert result["evidence_count"] >= 0
    
    @pytest.mark.asyncio
    async def test_synthesize_evidence(self):
        """Test sintetizar evidencia."""
        from core.PHASE_5.foundation import AgentTask
        
        agent = EvidenceLifecycleAgent(agent_id="test_agent")
        
        task = AgentTask(
            task_id="task_2",
            agent_id="test_agent",
            task_type="evidence",
            input={
                "action": "synthesize",
                "evidence_ids": ["ev_1", "ev_2", "ev_3"],
            },
        )
        
        result = await agent.execute(task)
        
        assert "synthesis" in result
        assert "confidence" in result
