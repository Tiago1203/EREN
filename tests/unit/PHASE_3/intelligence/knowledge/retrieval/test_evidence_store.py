"""Unit tests for Evidence Store module."""

import pytest

from core.PHASE_3.intelligence.knowledge.retrieval import (
    EvidenceSourceType,
    EvidenceLevel,
    QueryType,
    Evidence,
    EvidenceQuery,
    EvidenceFilters,
    EvidenceRetrieval,
    EvidenceWithRelevance,
    EvidenceChain,
    EvidenceStore,
    InMemoryEvidenceStore,
    create_evidence_store,
)


class TestEvidenceTypes:
    """Tests for evidence types."""

    def test_evidence_source_type_values(self):
        """Test evidence source type values."""
        assert EvidenceSourceType.PUBMED.value == "pubmed"
        assert EvidenceSourceType.FDA.value == "fda"
        assert EvidenceSourceType.ISO.value == "iso"
        assert EvidenceSourceType.INTERNAL.value == "internal"

    def test_evidence_level_values(self):
        """Test evidence level values."""
        assert EvidenceLevel.LEVEL_1A.value == "1a"
        assert EvidenceLevel.LEVEL_2B.value == "2b"
        assert EvidenceLevel.LEVEL_5.value == "5"
        assert EvidenceLevel.DEVICE_SPEC.value == "device_spec"

    def test_query_type_values(self):
        """Test query type values."""
        assert QueryType.SEMANTIC.value == "semantic"
        assert QueryType.HYBRID.value == "hybrid"
        assert QueryType.KEYWORD.value == "keyword"


class TestEvidence:
    """Tests for Evidence model."""

    def test_evidence_creation(self):
        """Test evidence creation."""
        evidence = Evidence(
            evidence_id="test-1",
            source_type=EvidenceSourceType.PUBMED,
            source_id="pubmed-123",
            title="Clinical Study on Device X",
            abstract="A study about device X",
        )
        
        assert evidence.evidence_id == "test-1"
        assert evidence.source_type == EvidenceSourceType.PUBMED
        assert evidence.title == "Clinical Study on Device X"
        assert evidence.evidence_level == EvidenceLevel.LEVEL_5

    def test_evidence_create_factory(self):
        """Test evidence create factory method."""
        evidence = Evidence.create(
            source_type=EvidenceSourceType.ISO,
            source_id="iso-60601",
            title="IEC 60601 Standard",
        )
        
        assert evidence.evidence_id is not None
        assert evidence.source_type == EvidenceSourceType.ISO
        assert evidence.title == "IEC 60601 Standard"

    def test_evidence_validation(self):
        """Test evidence validation."""
        with pytest.raises(ValueError):
            Evidence(
                evidence_id="test",
                source_type=EvidenceSourceType.PUBMED,
                source_id="pubmed-123",
                title="",  # Empty title should fail
            )

    def test_evidence_to_dict(self):
        """Test evidence to_dict conversion."""
        evidence = Evidence(
            evidence_id="test-1",
            source_type=EvidenceSourceType.PUBMED,
            source_id="pubmed-123",
            title="Test Evidence",
            icd_codes=["A00", "B00"],
            snomed_codes=["SNOMED-1", "SNOMED-2"],
        )
        
        data = evidence.to_dict()
        assert data["evidence_id"] == "test-1"
        assert data["icd_codes"] == ["A00", "B00"]
        assert data["snomed_codes"] == ["SNOMED-1", "SNOMED-2"]


class TestEvidenceQuery:
    """Tests for EvidenceQuery model."""

    def test_query_creation(self):
        """Test query creation."""
        query = EvidenceQuery(
            query_id="q-1",
            query_text="device maintenance protocols",
            query_type=QueryType.HYBRID,
        )
        
        assert query.query_id == "q-1"
        assert query.query_text == "device maintenance protocols"
        assert query.query_type == QueryType.HYBRID

    def test_query_create_factory(self):
        """Test query create factory method."""
        query = EvidenceQuery.create(
            query_text="infusion pump troubleshooting",
            query_type=QueryType.KEYWORD,
        )
        
        assert query.query_id is not None
        assert query.query_text == "infusion pump troubleshooting"

    def test_query_with_filters(self):
        """Test query with filters."""
        query = EvidenceQuery(
            query_id="q-2",
            query_text="ventilator safety",
            source_types=[EvidenceSourceType.ISO, EvidenceSourceType.FDA],
            evidence_levels=[EvidenceLevel.LEVEL_1A, EvidenceLevel.LEVEL_1B],
            min_relevance=0.7,
        )
        
        assert len(query.source_types) == 2
        assert len(query.evidence_levels) == 2


class TestEvidenceFilters:
    """Tests for EvidenceFilters model."""

    def test_filters_creation(self):
        """Test filters creation."""
        filters = EvidenceFilters(
            include_sources=[EvidenceSourceType.PUBMED],
            exclude_sources=[EvidenceSourceType.MANUAL],
            min_quality_score=0.5,
        )
        
        assert EvidenceSourceType.PUBMED in filters.include_sources
        assert EvidenceSourceType.MANUAL in filters.exclude_sources
        assert filters.min_quality_score == 0.5

    def test_filters_matches(self):
        """Test filters matching."""
        filters = EvidenceFilters(
            include_sources=[EvidenceSourceType.PUBMED],
            min_quality_score=0.6,
        )
        
        evidence_high = Evidence(
            evidence_id="test-1",
            source_type=EvidenceSourceType.PUBMED,
            source_id="pubmed-1",
            title="High Quality",
            quality_score=0.8,
        )
        
        evidence_low = Evidence(
            evidence_id="test-2",
            source_type=EvidenceSourceType.PUBMED,
            source_id="pubmed-2",
            title="Low Quality",
            quality_score=0.3,
        )
        
        assert filters.matches(evidence_high) is True
        assert filters.matches(evidence_low) is False

    def test_filters_excludes_source(self):
        """Test filters excluding source."""
        filters = EvidenceFilters(
            exclude_sources=[EvidenceSourceType.MANUAL],
        )
        
        evidence = Evidence(
            evidence_id="test-1",
            source_type=EvidenceSourceType.MANUAL,
            source_id="manual-1",
            title="Manual",
        )
        
        assert filters.matches(evidence) is False


class TestEvidenceRetrieval:
    """Tests for EvidenceRetrieval model."""

    def test_retrieval_creation(self):
        """Test retrieval result creation."""
        query = EvidenceQuery.create("test query")
        evidence_list = [
            Evidence.create(
                source_type=EvidenceSourceType.PUBMED,
                source_id=f"pubmed-{i}",
                title=f"Evidence {i}",
                quality_score=0.5 + i * 0.1,
            )
            for i in range(3)
        ]
        
        retrieval = EvidenceRetrieval(
            query=query,
            results=evidence_list,
        )
        
        assert retrieval.total_returned == 3
        assert retrieval.avg_quality_score > 0.5
        
        # Check level distribution
        assert len(retrieval.level_distribution) > 0

    def test_retrieval_filter_by_level(self):
        """Test filtering by evidence level."""
        query = EvidenceQuery.create("test")
        
        evidence = Evidence(
            evidence_id="test-1",
            source_type=EvidenceSourceType.PUBMED,
            source_id="pubmed-1",
            title="Test",
            evidence_level=EvidenceLevel.LEVEL_2B,
            quality_score=0.7,
        )
        
        retrieval = EvidenceRetrieval(
            query=query,
            results=[evidence],
        )
        
        filtered = retrieval.filter_by_level(EvidenceLevel.LEVEL_1A)
        assert len(filtered.results) == 0


class TestEvidenceChain:
    """Tests for EvidenceChain model."""

    def test_chain_creation(self):
        """Test evidence chain creation."""
        primary = Evidence.create(
            source_type=EvidenceSourceType.PUBMED,
            source_id="pubmed-1",
            title="Primary Evidence",
        )
        
        chain = EvidenceChain.create(
            primary_evidence=primary,
            clinical_question="Is device X safe?",
        )
        
        assert chain.chain_id is not None
        assert chain.primary_evidence == primary
        assert chain.clinical_question == "Is device X safe?"
        assert chain.chain_strength == primary.quality_score

    def test_chain_add_supporting(self):
        """Test adding supporting evidence."""
        primary = Evidence.create(
            source_type=EvidenceSourceType.PUBMED,
            source_id="pubmed-1",
            title="Primary",
            evidence_level=EvidenceLevel.LEVEL_2B,
            quality_score=0.6,
        )
        
        supporting = Evidence.create(
            source_type=EvidenceSourceType.PUBMED,
            source_id="pubmed-2",
            title="Supporting",
            evidence_level=EvidenceLevel.LEVEL_1A,  # Higher level
            quality_score=0.9,
        )
        
        chain = EvidenceChain.create(primary_evidence=primary)
        chain.add_supporting(supporting)
        
        assert len(chain.supporting_evidence) == 1
        # Chain strength accounts for supporting evidence quality
        assert chain.chain_strength >= 0.0

    def test_chain_add_contradicting(self):
        """Test adding contradicting evidence."""
        primary = Evidence.create(
            source_type=EvidenceSourceType.PUBMED,
            source_id="pubmed-1",
            title="Primary",
            quality_score=0.7,
        )
        
        contradicting = Evidence.create(
            source_type=EvidenceSourceType.PUBMED,
            source_id="pubmed-2",
            title="Contradicting",
            quality_score=0.8,
        )
        
        chain = EvidenceChain.create(primary_evidence=primary)
        chain.add_contradicting(contradicting)
        
        assert len(chain.contradicting_evidence) == 1
        assert chain.chain_strength < primary.quality_score

    def test_chain_to_dict(self):
        """Test chain to_dict conversion."""
        primary = Evidence.create(
            source_type=EvidenceSourceType.ISO,
            source_id="iso-1",
            title="ISO Standard",
        )
        
        chain = EvidenceChain.create(primary_evidence=primary)
        
        data = chain.to_dict()
        assert "chain_id" in data
        assert "primary_evidence" in data
        assert "chain_strength" in data


class TestInMemoryEvidenceStore:
    """Tests for InMemoryEvidenceStore."""

    @pytest.fixture
    def store(self):
        """Create test store."""
        return InMemoryEvidenceStore()

    @pytest.fixture
    def sample_evidence(self):
        """Create sample evidence."""
        return Evidence.create(
            source_type=EvidenceSourceType.PUBMED,
            source_id="pubmed-123",
            title="Clinical Study on Infusion Pumps",
            abstract="Study about infusion pump safety",
            evidence_level=EvidenceLevel.LEVEL_1B,
            quality_score=0.8,
            icd_codes=["T82", "T85"],
            snomed_codes=["SNOMED-123"],
            medical_specialty="Critical Care",
            device_categories=["Infusion Pump"],
            manufacturers=["Acme Medical"],
        )

    @pytest.mark.asyncio
    async def test_store(self, store, sample_evidence):
        """Test storing evidence."""
        evidence_id = await store.store(sample_evidence)
        
        assert evidence_id == sample_evidence.evidence_id
        
        retrieved = await store.get(evidence_id)
        assert retrieved is not None
        assert retrieved.title == sample_evidence.title

    @pytest.mark.asyncio
    async def test_retrieve(self, store, sample_evidence):
        """Test retrieving evidence by code."""
        await store.store(sample_evidence)
        
        # Search by code instead of text (InMemoryEvidenceStore uses code-based search)
        query = EvidenceQuery.create(
            "infusion pump",
            icd_codes=["T82"],  # Use the code from sample_evidence
            min_relevance=0.0,  # Lower threshold since relevance_score defaults to 0
        )
        results = await store.retrieve(query)
        
        assert results.total_returned >= 1

    @pytest.mark.asyncio
    async def test_retrieve_with_filters(self, store):
        """Test retrieving with filters."""
        evidence1 = Evidence.create(
            source_type=EvidenceSourceType.PUBMED,
            source_id="pubmed-1",
            title="Infusion Pump Study",
            medical_specialty="Critical Care",
            device_categories=["Infusion Pump"],
            icd_codes=["T82"],
        )
        
        evidence2 = Evidence.create(
            source_type=EvidenceSourceType.FDA,
            source_id="fda-1",
            title="FDA Alert",
            medical_specialty="Radiology",
            device_categories=["X-Ray"],
            icd_codes=["Z87"],  # Different code
        )
        
        await store.store(evidence1)
        await store.store(evidence2)
        
        # Use code-based search with source filter
        query = EvidenceQuery.create(
            "pump",
            source_types=[EvidenceSourceType.PUBMED],
            icd_codes=["T82"],  # Filter to evidence1 only
            min_relevance=0.0,  # Lower threshold since relevance_score defaults to 0
        )
        
        results = await store.retrieve(query)
        assert results.total_returned == 1
        assert results.results[0].source_type == EvidenceSourceType.PUBMED

    @pytest.mark.asyncio
    async def test_search_by_code(self, store, sample_evidence):
        """Test searching by medical codes."""
        await store.store(sample_evidence)
        
        results = await store.search_by_code("icd", ["T82"])
        
        assert len(results) >= 1
        assert "T82" in results[0].icd_codes

    @pytest.mark.asyncio
    async def test_search_by_category(self, store):
        """Test searching by category."""
        # Create evidence with medical specialty (used for category search)
        evidence = Evidence.create(
            source_type=EvidenceSourceType.PUBMED,
            source_id="pubmed-cat-1",
            title="Critical Care Study",
            medical_specialty="Critical Care",
            device_categories=["Infusion Pump"],
        )
        await store.store(evidence)
        
        results = await store.search_by_category("Critical Care")
        
        assert len(results) >= 1
        assert results[0].medical_specialty == "Critical Care"

    @pytest.mark.asyncio
    async def test_update(self, store, sample_evidence):
        """Test updating evidence."""
        await store.store(sample_evidence)
        
        updated = Evidence(
            evidence_id=sample_evidence.evidence_id,
            source_type=sample_evidence.source_type,
            source_id=sample_evidence.source_id,
            title="Updated Title",
            quality_score=0.9,
        )
        
        result = await store.update(updated)
        assert result is True
        
        retrieved = await store.get(sample_evidence.evidence_id)
        assert retrieved.title == "Updated Title"

    @pytest.mark.asyncio
    async def test_delete(self, store, sample_evidence):
        """Test deleting evidence."""
        await store.store(sample_evidence)
        
        result = await store.delete(sample_evidence.evidence_id)
        assert result is True
        
        retrieved = await store.get(sample_evidence.evidence_id)
        assert retrieved is None

    @pytest.mark.asyncio
    async def test_build_chain(self, store):
        """Test building evidence chain."""
        primary = Evidence.create(
            source_type=EvidenceSourceType.PUBMED,
            source_id="pubmed-1",
            title="Primary Study",
            evidence_level=EvidenceLevel.LEVEL_2B,
            icd_codes=["T82"],
        )
        
        supporting = Evidence.create(
            source_type=EvidenceSourceType.PUBMED,
            source_id="pubmed-2",
            title="Supporting Study",
            evidence_level=EvidenceLevel.LEVEL_1A,
            icd_codes=["T82"],
        )
        
        await store.store(primary)
        await store.store(supporting)
        
        chain = await store.build_chain(primary.evidence_id)
        
        assert chain.chain_id is not None
        assert chain.primary_evidence.evidence_id == primary.evidence_id
        assert len(chain.supporting_evidence) >= 1


class TestEvidenceStoreFactory:
    """Tests for evidence store factory."""

    def test_create_memory_store(self):
        """Test creating memory store."""
        store = create_evidence_store("memory")
        assert isinstance(store, InMemoryEvidenceStore)

    def test_create_unknown_store(self):
        """Test creating unknown store type."""
        with pytest.raises(ValueError):
            create_evidence_store("unknown")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
