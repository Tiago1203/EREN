"""Unit tests for EREN Cognitive RAG Pipeline with CCE."""

import pytest

from core.PHASE_2.rag.types import (
    RetrievalStrategy,
    ResponseFormat,
    RAGQuery,
    RAGResponse,
    RAGResult,
    PipelineStatistics,
)
from core.PHASE_2.rag.exceptions import RAGError
from core.PHASE_2.rag.prompt_builder import PromptBuilder
from core.PHASE_2.rag.citation_builder import CitationBuilder
from core.PHASE_2.rag.pipeline import CognitiveRAGPipeline

# Import CCE types
from core.PHASE_2.context.engine.types import (
    ContextItem,
    ContextPackage,
    ContextSource,
    ContextPriority,
)
from core.PHASE_2.context.engine.engine import CognitiveContextEngine
from core.PHASE_2.context.engine.deduplicator import ContextDeduplicator
from core.PHASE_2.context.engine.merger import ContextMerger
from core.PHASE_2.context.engine.compressor import ContextCompressor
from core.PHASE_2.context.engine.ranking import ContextRanker


class TestContextTypes:
    """Tests for context types."""

    def test_context_item_creation(self):
        """Test context item creation."""
        item = ContextItem(
            item_id="item-123",
            source=ContextSource.KNOWLEDGE,
            content="Some knowledge content",
            relevance_score=0.9,
        )
        assert item.item_id == "item-123"
        assert item.relevance_score == 0.9
        assert item.tokens > 0

    def test_context_package_creation(self):
        """Test context package creation."""
        package = ContextPackage(
            package_id="pkg-123",
            query="Test query",
            items=[],
            context_text="Context text",
            context_tokens=100,
        )
        assert package.package_id == "pkg-123"
        assert package.total_items == 0


class TestContextDeduplicator:
    """Tests for context deduplicator."""

    def test_deduplicate_empty(self):
        """Test deduplicating empty list."""
        dedup = ContextDeduplicator()
        items, duplicates = dedup.deduplicate([])
        assert items == []
        assert duplicates == 0

    def test_deduplicate_similar(self):
        """Test deduplicating similar items."""
        dedup = ContextDeduplicator()
        items = [
            ContextItem(
                item_id="i-1",
                source=ContextSource.KNOWLEDGE,
                content="Same content",
                relevance_score=0.9,
            ),
            ContextItem(
                item_id="i-2",
                source=ContextSource.KNOWLEDGE,
                content="Same content",
                relevance_score=0.8,
            ),
        ]
        unique, duplicates = dedup.deduplicate(items)
        assert len(unique) == 1
        assert duplicates == 1


class TestContextMerger:
    """Tests for context merger."""

    def test_merge_empty(self):
        """Test merging empty lists."""
        merger = ContextMerger()
        result = merger.merge()
        assert result == []


class TestContextCompressor:
    """Tests for context compressor."""

    def test_compress_empty(self):
        """Test compressing empty list."""
        compressor = ContextCompressor()
        result = compressor.compress([], 1000)
        assert result == []

    def test_compress_with_items(self):
        """Test compressing items."""
        compressor = ContextCompressor()
        items = [
            ContextItem(
                item_id="i-1",
                source=ContextSource.KNOWLEDGE,
                content="A" * 100,
                relevance_score=0.9,
            ),
            ContextItem(
                item_id="i-2",
                source=ContextSource.KNOWLEDGE,
                content="B" * 200,
                relevance_score=0.8,
            ),
        ]
        result = compressor.compress(items, 1000)
        assert len(result) >= 1


class TestContextRanker:
    """Tests for context ranker."""

    def test_rank_empty(self):
        """Test ranking empty list."""
        ranker = ContextRanker()
        result = ranker.rank([])
        assert result == []

    def test_rank_with_priority(self):
        """Test ranking with priorities."""
        ranker = ContextRanker()
        items = [
            ContextItem(
                item_id="i-1",
                source=ContextSource.KNOWLEDGE,
                content="Low priority content",
                relevance_score=0.5,
                priority=ContextPriority.LOW,
            ),
            ContextItem(
                item_id="i-2",
                source=ContextSource.CLINICAL,
                content="High priority content",
                relevance_score=0.9,
                priority=ContextPriority.HIGH,
            ),
        ]
        result = ranker.rank(items, prioritize_clinical=True)
        # Clinical should be prioritized
        assert len(result) == 2


class TestCognitiveContextEngine:
    """Tests for Cognitive Context Engine."""

    @pytest.fixture
    def engine(self):
        """Create test engine."""
        return CognitiveContextEngine()

    @pytest.mark.asyncio
    async def test_build_context_empty(self, engine):
        """Test building empty context."""
        package = await engine.build_context(query="Test query")
        assert isinstance(package, ContextPackage)
        assert package.package_id is not None

    @pytest.mark.asyncio
    async def test_build_context_with_items(self, engine):
        """Test building context with items."""
        # Add items manually for testing
        item = ContextItem(
            item_id="item-1",
            source=ContextSource.KNOWLEDGE,
            content="Medical guideline content",
            relevance_score=0.9,
            priority=ContextPriority.HIGH,
        )
        engine._builder._retrieve_knowledge = lambda *args, **kwargs: [item]

        package = await engine.build_context(
            query="Test query",
            include_knowledge=True,
        )
        assert isinstance(package, ContextPackage)


class TestPromptBuilder:
    """Tests for prompt builder."""

    @pytest.fixture
    def builder(self):
        """Create test builder."""
        return PromptBuilder()

    def test_build_prompt_from_package(self, builder):
        """Test building prompt from context package."""
        query = RAGQuery(
            query_id="q-123",
            question="What is diabetes?",
        )
        package = ContextPackage(
            package_id="pkg-123",
            query="What is diabetes?",
            items=[],
            context_text="Diabetes is a condition...",
            context_tokens=10,
        )

        prompt = builder.build_prompt_from_package(query, package)

        assert prompt.system_prompt is not None
        assert "What is diabetes?" in prompt.user_prompt


class TestCitationBuilder:
    """Tests for citation builder."""

    @pytest.fixture
    def builder(self):
        """Create test builder."""
        return CitationBuilder()

    def test_build_citations_from_package(self, builder):
        """Test building citations from context package."""
        package = ContextPackage(
            package_id="pkg-123",
            query="Test",
            items=[
                ContextItem(
                    item_id="i-1",
                    source=ContextSource.KNOWLEDGE,
                    content="Some medical content",
                    title="Medical Guide",
                    author="Dr. Smith",
                ),
            ],
        )

        citations = builder.build_citations_from_package(package)

        assert len(citations) == 1
        assert citations[0].title == "Medical Guide"


class TestCognitiveRAGPipeline:
    """Tests for cognitive RAG pipeline."""

    @pytest.fixture
    def pipeline(self):
        """Create test pipeline."""
        return CognitiveRAGPipeline()

    @pytest.mark.asyncio
    async def test_query_basic(self, pipeline):
        """Test basic query processing."""
        result = await pipeline.query(
            question="What is diabetes?",
        )

        assert isinstance(result, RAGResult)
        assert result.query.question == "What is diabetes?"
        assert result.success is True
        assert result.response is not None

    @pytest.mark.asyncio
    async def test_query_with_context(self, pipeline):
        """Test query with context."""
        result = await pipeline.query(
            question="Treatment options?",
            context={"medical_specialty": "endocrinology"},
        )

        assert result.success is True
        assert result.response is not None

    @pytest.mark.asyncio
    async def test_query_with_conversation(self, pipeline):
        """Test query with conversation ID."""
        result = await pipeline.query(
            question="Tell me more",
            conversation_id="conv-123",
            user_id="user-456",
        )

        assert result.success is True
        assert result.query.conversation_id == "conv-123"

    def test_statistics(self, pipeline):
        """Test statistics tracking."""
        stats = pipeline.get_statistics()
        assert isinstance(stats, PipelineStatistics)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
