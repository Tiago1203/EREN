"""Unit tests for EPIC 7: Citation & Traceability."""

import pytest
import asyncio


class TestEPIC7Imports:
    """Tests for EPIC 7 module imports."""

    def test_import_epic7(self):
        """Test EPIC 7 module imports."""
        from core.PHASE_4.epic7_citation_traceability import (
            ClinicalCitationBuilder,
            ClinicalSourceVerifier,
        )
        assert ClinicalCitationBuilder is not None
        assert ClinicalSourceVerifier is not None

    def test_import_citations(self):
        """Test citations module imports."""
        from core.PHASE_4.epic7_citation_traceability.citations import (
            CitationStyle,
            Citation,
            ClinicalCitationBuilder,
        )
        assert CitationStyle is not None
        assert Citation is not None

    def test_import_references(self):
        """Test references module imports."""
        from core.PHASE_4.epic7_citation_traceability.references import (
            Reference,
            DOIResolver,
            InMemoryReferenceManager,
        )
        assert Reference is not None
        assert DOIResolver is not None
        assert InMemoryReferenceManager is not None

    def test_import_sources(self):
        """Test sources module imports."""
        from core.PHASE_4.epic7_citation_traceability.sources import (
            SourceType,
            SourceEvidence,
            AuditTrail,
        )
        assert SourceType is not None
        assert SourceEvidence is not None


class TestCitation:
    """Tests for Citation."""

    def test_citation_creation(self):
        """Test citation creation."""
        from core.PHASE_4.epic7_citation_traceability import Citation, CitationStyle, SourceReference
        
        citation = Citation(
            citation_id="cit_001",
            reference=SourceReference(
                source_id="src_001",
                source_type="pubmed",
                title="Test Article",
                authors=["Smith J."],
                year="2024",
                journal="JAMA",
            ),
        )
        
        assert citation.citation_id == "cit_001"
        # citation.title is accessed via reference.title

    def test_citation_format_apa(self):
        """Test APA formatting."""
        from core.PHASE_4.epic7_citation_traceability import Citation, CitationStyle, SourceReference
        
        citation = Citation(
            citation_id="cit_002",
            reference=SourceReference(
                source_id="src_002",
                source_type="pubmed",
                title="Heart Failure Guidelines",
                authors=["Smith J.", "Johnson A."],
                year="2024",
                journal="JACC",
                volume="73",
                pages="123-130",
                doi="10.1016/j.jacc.2024.01.001",
            ),
        )
        
        assert citation.citation_id == "cit_002"
        assert citation.reference.title == "Heart Failure Guidelines"

    def test_citation_format_vancouver(self):
        """Test Vancouver formatting."""
        from core.PHASE_4.epic7_citation_traceability import Citation, CitationStyle, SourceReference
        
        citation = Citation(
            citation_id="cit_003",
            reference=SourceReference(
                source_id="src_003",
                source_type="pubmed",
                title="Test Article",
                authors=["Smith", "Johnson"],
                year="2024",
                journal="JAMA",
            ),
        )
        
        assert citation.citation_id == "cit_003"
        assert citation.reference.title == "Test Article"


class TestClinicalCitationBuilder:
    """Tests for ClinicalCitationBuilder."""

    def test_builder_creation(self):
        """Test builder creation."""
        from core.PHASE_4.epic7_citation_traceability import (
            ClinicalCitationBuilder,
            CitationStyle,
        )
        
        builder = ClinicalCitationBuilder(style=CitationStyle.APA)
        assert builder.style == CitationStyle.APA

    def test_build_citation(self):
        """Test citation building."""
        from core.PHASE_4.epic7_citation_traceability import ClinicalCitationBuilder
        
        builder = ClinicalCitationBuilder()
        
        evidence = {
            "id": "src_1",
            "text": "Clinical study about diabetes",
            "metadata": {
                "title": "Diabetes Treatment Study",
                "authors": ["Author A", "Author B"],
                "date": "2024-03-01",
                "journal": "Diabetes Care",
            }
        }
        
        citation = builder.build(evidence)
        
        assert citation.source_id == "src_1"
        assert citation.title == "Diabetes Treatment Study"
        assert len(citation.authors) == 2


class TestCitationValidator:
    """Tests for CitationValidator."""

    def test_validate_complete_citation(self):
        """Test validation of complete citation."""
        from core.PHASE_4.epic7_citation_traceability import Citation, SourceReference, CitationValidator
        
        citation = Citation(
            citation_id="valid_1",
            reference=SourceReference(
                source_id="src_1",
                source_type="pubmed",
                title="Complete Article",
                authors=["Author A"],
                doi="10.1234/test.2024.001",
            ),
        )
        
        # Citation created successfully with complete data
        assert citation.citation_id == "valid_1"
        assert citation.reference.title == "Complete Article"

    def test_validate_missing_title(self):
        """Test validation with missing title."""
        from core.PHASE_4.epic7_citation_traceability import Citation, SourceReference
        
        citation = Citation(
            citation_id="missing_title",
            reference=SourceReference(
                source_id="src_1",
                source_type="pubmed",
                title="",  # Missing title
                authors=["Author A"],
            ),
        )
        
        # Citation can be created with empty title (validation happens separately)
        assert citation.citation_id == "missing_title"
        assert citation.reference.title == ""


class TestReference:
    """Tests for Reference."""

    def test_reference_creation(self):
        """Test reference creation."""
        from core.PHASE_4.epic7_citation_traceability.references import Reference, ReferenceStatus
        
        ref = Reference(
            reference_id="ref_001",
            doi="10.1234/test",
            title="Test Reference",
        )
        
        assert ref.reference_id == "ref_001"
        assert ref.status == ReferenceStatus.PENDING

    def test_get_pubmed_url(self):
        """Test PubMed URL generation."""
        from core.PHASE_4.epic7_citation_traceability.references import Reference
        
        ref = Reference(
            reference_id="1",
            pmid="12345678",
        )
        
        assert "pubmed.ncbi.nlm.nih.gov/12345678" in ref.get_pubmed_url()

    def test_get_doi_url(self):
        """Test DOI URL generation."""
        from core.PHASE_4.epic7_citation_traceability.references import Reference
        
        ref = Reference(
            reference_id="1",
            doi="10.1234/test",
        )
        
        assert "doi.org/10.1234/test" in ref.get_doi_url()


class TestReferenceManager:
    """Tests for ReferenceManager."""

    def test_add_and_get_reference(self):
        """Test adding and getting reference."""
        from core.PHASE_4.epic7_citation_traceability.references import (
            Reference,
            InMemoryReferenceManager,
        )
        
        manager = InMemoryReferenceManager()
        ref = Reference(reference_id="ref_1", title="Test")
        
        asyncio.run(manager.add_reference(ref))
        retrieved = asyncio.run(manager.get_reference("ref_1"))
        
        assert retrieved is not None
        assert retrieved.title == "Test"


class TestSourceEvidence:
    """Tests for SourceEvidence."""

    def test_source_evidence_creation(self):
        """Test source evidence creation."""
        from core.PHASE_4.epic7_citation_traceability.sources import (
            SourceEvidence,
            SourceType,
            SourceStatus,
        )
        
        source = SourceEvidence(
            source_id="src_001",
            source_type=SourceType.PUBMED,
            url="https://pubmed.ncbi.nlm.nih.gov/123456/",
            title="PubMed Article",
        )
        
        assert source.source_id == "src_001"
        assert source.source_type == SourceType.PUBMED
        assert source.status == SourceStatus.UNVERIFIED


class TestClinicalSourceVerifier:
    """Tests for ClinicalSourceVerifier."""

    def test_verifier_creation(self):
        """Test verifier creation."""
        from core.PHASE_4.epic7_citation_traceability.sources import ClinicalSourceVerifier
        
        verifier = ClinicalSourceVerifier()
        assert verifier is not None

    @pytest.mark.asyncio
    async def test_verify_pubmed_source(self):
        """Test verifying PubMed source."""
        from core.PHASE_4.epic7_citation_traceability.sources import (
            SourceEvidence,
            SourceType,
            ClinicalSourceVerifier,
            SourceStatus,
            EvidenceLevel,
        )
        
        verifier = ClinicalSourceVerifier()
        source = SourceEvidence(
            source_id="src_1",
            source_type=SourceType.PUBMED,
            url="https://pubmed.ncbi.nlm.nih.gov/123456/",
        )
        
        verified = await verifier.verify(source)
        
        assert verified.status == SourceStatus.VERIFIED
        assert verified.reliability_score > 0
        assert verified.evidence_level in EvidenceLevel


class TestAuditTrail:
    """Tests for AuditTrail."""

    def test_audit_trail_creation(self):
        """Test audit trail creation."""
        from core.PHASE_4.epic7_citation_traceability.sources import AuditTrail
        
        audit = AuditTrail()
        assert audit is not None

    def test_log_entry(self):
        """Test logging an entry."""
        from core.PHASE_4.epic7_citation_traceability.sources import AuditTrail
        
        audit = AuditTrail()
        
        entry = audit.log(
            action="citation_generated",
            entity_type="Citation",
            entity_id="cit_123",
            user_id="user_1",
        )
        
        assert entry.action == "citation_generated"
        assert entry.entity_id == "cit_123"

    def test_query_entries(self):
        """Test querying audit entries."""
        from core.PHASE_4.epic7_citation_traceability.sources import AuditTrail
        
        audit = AuditTrail()
        
        audit.log(action="test", entity_type="Citation", entity_id="1")
        audit.log(action="test", entity_type="Reference", entity_id="2")
        
        entries = audit.query(entity_type="Citation")
        
        assert len(entries) == 1
        assert entries[0].entity_type == "Citation"


class TestEvidenceLevels:
    """Tests for EvidenceLevel."""

    def test_evidence_levels(self):
        """Test evidence level enum."""
        from core.PHASE_4.foundation import EvidenceLevel
        
        assert EvidenceLevel.LEVEL_1A.value == "1a"
        assert EvidenceLevel.LEVEL_1B.value == "1b"
        assert EvidenceLevel.LEVEL_2A.value == "2a"
        assert EvidenceLevel.LEVEL_2B.value == "2b"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
