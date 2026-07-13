"""Tests for the Cognitive Knowledge Engine."""

from __future__ import annotations

import pytest

from core.knowledge import (
    CognitiveKnowledgeEngine,
    ExhaustiveRouting,
    KnowledgeFilters,
    KnowledgeQuery,
    KnowledgeRegistry,
    KnowledgeResult,
    KnowledgeRouter,
    KnowledgeSource,
    KnowledgeSourceType,
    KnowledgeSession,
    PriorityRouting,
    QueryPriority,
    QueryType,
    ResultConfidence,
    ResultRelevance,
    SOURCE_QUERY_MAPPING,
)


class MockKnowledgeSource:
    """Mock knowledge source for testing."""

    def __init__(
        self,
        source_id: str,
        name: str,
        source_type: KnowledgeSourceType,
        supported_queries: list[QueryType],
    ) -> None:
        self.source_id = source_id
        self.name = name
        self.source_type = source_type
        self._supported = supported_queries

    def supports_query_type(self, query_type: QueryType) -> bool:
        """Check if supports query type."""
        return query_type in self._supported

    async def query(self, query: KnowledgeQuery) -> list[KnowledgeResult]:
        """Mock query."""
        return [
            KnowledgeResult(
                result_id=f"r_{self.source_id}",
                source_id=self.source_id,
                source_type=self.source_type,
                content=f"Result from {self.name}",
                relevance=ResultRelevance.RELEVANT,
                confidence=ResultConfidence.HIGH,
                query_id=query.query_id,
            )
        ]

    async def health_check(self) -> bool:
        """Mock health check."""
        return True


class TestKnowledgeRegistry:
    """Tests for KnowledgeRegistry."""

    def test_register_source(self) -> None:
        """Registering a source should work."""
        registry = KnowledgeRegistry()
        source = MockKnowledgeSource(
            "test_src",
            "Test Source",
            KnowledgeSourceType.KNOWLEDGE_BASE,
            [QueryType.GENERAL],
        )

        registry.register(source)

        assert registry.count() == 1
        assert "test_src" in registry.list_sources()

    def test_unregister_source(self) -> None:
        """Unregistering a source should work."""
        registry = KnowledgeRegistry()
        source = MockKnowledgeSource(
            "test_src",
            "Test Source",
            KnowledgeSourceType.KNOWLEDGE_BASE,
            [QueryType.GENERAL],
        )
        registry.register(source)

        result = registry.unregister("test_src")

        assert result is True
        assert registry.count() == 0

    def test_get_by_type(self) -> None:
        """Getting sources by type should work."""
        registry = KnowledgeRegistry()
        registry.register(
            MockKnowledgeSource(
                "src1",
                "Clinical",
                KnowledgeSourceType.CLINICAL_DATABASE,
                [QueryType.DIAGNOSTIC],
            )
        )
        registry.register(
            MockKnowledgeSource(
                "src2",
                "Manual",
                KnowledgeSourceType.EQUIPMENT_MANUALS,
                [QueryType.TROUBLESHOOTING],
            )
        )

        clinical = registry.get_by_type(KnowledgeSourceType.CLINICAL_DATABASE)
        manuals = registry.get_by_type(KnowledgeSourceType.EQUIPMENT_MANUALS)

        assert len(clinical) == 1
        assert len(manuals) == 1

    def test_get_by_query_type(self) -> None:
        """Getting sources by query type should work."""
        registry = KnowledgeRegistry()
        registry.register(
            MockKnowledgeSource(
                "src1",
                "Clinical",
                KnowledgeSourceType.CLINICAL_DATABASE,
                [QueryType.DIAGNOSTIC, QueryType.TREATMENT],
            )
        )

        diagnostic = registry.get_by_query_type(QueryType.DIAGNOSTIC)

        assert len(diagnostic) == 1


class TestKnowledgeRouter:
    """Tests for KnowledgeRouter."""

    def test_priority_routing(self) -> None:
        """Priority routing should select sources by priority."""
        router = KnowledgeRouter()

        clinical_src = MockKnowledgeSource(
            "clinical",
            "Clinical DB",
            KnowledgeSourceType.CLINICAL_DATABASE,
            [QueryType.DIAGNOSTIC],
        )
        manual_src = MockKnowledgeSource(
            "manual",
            "Manual",
            KnowledgeSourceType.EQUIPMENT_MANUALS,
            [QueryType.DIAGNOSTIC],
        )

        query = KnowledgeQuery(
            query_id="q1",
            query_text="Test",
            query_type=QueryType.DIAGNOSTIC,
        )

        # Register sources in registry
        router._registry.register(clinical_src)
        router._registry.register(manual_src)

        sources = router.get_sources_for_query(query)

        assert len(sources) >= 1

    def test_exhaustive_routing(self) -> None:
        """Exhaustive routing should select all sources."""
        router = KnowledgeRouter(strategy=ExhaustiveRouting())

        src1 = MockKnowledgeSource(
            "src1",
            "Source 1",
            KnowledgeSourceType.KNOWLEDGE_BASE,
            [QueryType.GENERAL],
        )
        src2 = MockKnowledgeSource(
            "src2",
            "Source 2",
            KnowledgeSourceType.INTERNAL_MEMORY,
            [QueryType.GENERAL],
        )

        query = KnowledgeQuery(
            query_id="q1",
            query_text="Test",
            query_type=QueryType.GENERAL,
        )

        router._registry.register(src1)
        router._registry.register(src2)

        sources = router.get_sources_for_query(query)

        assert len(sources) == 2


class TestKnowledgeQuery:
    """Tests for KnowledgeQuery."""

    def test_query_creation(self) -> None:
        """Creating a query should work."""
        query = KnowledgeQuery(
            query_id="q1",
            query_text="How to calibrate SpO2?",
            query_type=QueryType.MAINTENANCE,
            priority=QueryPriority.HIGH,
        )

        assert query.query_id == "q1"
        assert query.query_type == QueryType.MAINTENANCE
        assert query.priority == QueryPriority.HIGH
        assert query.created_at != ""

    def test_query_filters(self) -> None:
        """Query with filters should work."""
        filters = KnowledgeFilters(
            max_results=5,
            language="es",
        )

        query = KnowledgeQuery(
            query_id="q1",
            query_text="Test",
            query_type=QueryType.GENERAL,
            filters=filters,
        )

        assert query.filters.max_results == 5
        assert query.filters.language == "es"


class TestSourceQueryMapping:
    """Tests for source query type mapping."""

    def test_clinical_database_mappings(self) -> None:
        """Clinical database should support clinical query types."""
        clinical_queries = SOURCE_QUERY_MAPPING.get(
            KnowledgeSourceType.CLINICAL_DATABASE, ()
        )

        assert QueryType.CLINICAL_PROCEDURE in clinical_queries
        assert QueryType.DIAGNOSTIC in clinical_queries
        assert QueryType.TREATMENT in clinical_queries

    def test_equipment_manuals_mappings(self) -> None:
        """Equipment manuals should support technical query types."""
        manual_queries = SOURCE_QUERY_MAPPING.get(
            KnowledgeSourceType.EQUIPMENT_MANUALS, ()
        )

        assert QueryType.TECHNICAL_SPECIFICATION in manual_queries
        assert QueryType.TROUBLESHOOTING in manual_queries
        assert QueryType.MAINTENANCE in manual_queries

    def test_regulatory_standards_mappings(self) -> None:
        """Regulatory standards should support compliance query types."""
        reg_queries = SOURCE_QUERY_MAPPING.get(
            KnowledgeSourceType.REGULATORY_STANDARDS, ()
        )

        assert QueryType.COMPLIANCE in reg_queries
        assert QueryType.CERTIFICATION in reg_queries
        assert QueryType.SAFETY in reg_queries


class TestCognitiveKnowledgeEngine:
    """Tests for CognitiveKnowledgeEngine."""

    def test_engine_creation(self) -> None:
        """Creating engine should work."""
        engine = CognitiveKnowledgeEngine()

        assert engine is not None
        assert engine._registry is not None
        assert engine._router is not None

    def test_register_source(self) -> None:
        """Registering source should work."""
        engine = CognitiveKnowledgeEngine()
        source = MockKnowledgeSource(
            "test_src",
            "Test",
            KnowledgeSourceType.KNOWLEDGE_BASE,
            [QueryType.GENERAL],
        )

        engine.register_source(source)

        assert "test_src" in engine.get_registered_sources()

    def test_capability_registration(self) -> None:
        """Capability registration should work."""
        engine = CognitiveKnowledgeEngine()

        # Should not raise
        engine.register_capabilities()

        # Should not be registered (no registry provided)
        assert not engine.capabilities_registered


class TestKnowledgeTypes:
    """Tests for knowledge types."""

    def test_source_types(self) -> None:
        """All source types should be defined."""
        assert KnowledgeSourceType.CLINICAL_DATABASE
        assert KnowledgeSourceType.EQUIPMENT_MANUALS
        assert KnowledgeSourceType.HOSPITAL_PROTOCOLS
        assert KnowledgeSourceType.REGULATORY_STANDARDS
        assert KnowledgeSourceType.INTERNAL_MEMORY

    def test_query_types(self) -> None:
        """All query types should be defined."""
        assert QueryType.DIAGNOSTIC
        assert QueryType.TROUBLESHOOTING
        assert QueryType.MAINTENANCE
        assert QueryType.COMPLIANCE

    def test_result_relevance(self) -> None:
        """All relevance levels should be defined."""
        assert ResultRelevance.HIGHLY_RELEVANT
        assert ResultRelevance.RELEVANT
        assert ResultRelevance.PARTIALLY_RELEVANT
        assert ResultRelevance.NOT_RELEVANT

    def test_result_confidence(self) -> None:
        """All confidence levels should be defined."""
        assert ResultConfidence.HIGH
        assert ResultConfidence.MEDIUM
        assert ResultConfidence.LOW
        assert ResultConfidence.UNKNOWN
