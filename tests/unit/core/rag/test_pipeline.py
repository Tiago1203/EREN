"""Unit tests for EREN Cognitive RAG Pipeline."""

import pytest

from core.rag.types import (
    RetrievalStrategy,
    ResponseFormat,
    ConfidenceLevel,
    RAGQuery,
    RetrievedChunk,
    RetrievalResult,
    RAGContext,
    RAGPrompt,
    Citation,
    RAGResponse,
    RAGResult,
    PipelineStatistics,
)
from core.rag.exceptions import (
    RAGError,
    RetrievalError,
    NoContextError,
    TokenBudgetExceededError,
)
from core.rag.planner import RetrievalPlanner, RetrievalPlan
from core.rag.context_builder import ContextBuilder, Deduplicator
from core.rag.prompt_builder import PromptBuilder
from core.rag.response_builder import ResponseBuilder
from core.rag.citation_builder import CitationBuilder
from core.rag.token_budget import TokenBudget, get_default_budget, reset_default_budget
from core.rag.pipeline import CognitiveRAGPipeline


class TestRAGTypes:
    """Tests for RAG types."""

    def test_rag_query_creation(self):
        """Test RAG query creation."""
        query = RAGQuery(
            query_id="q-123",
            question="What is diabetes?",
        )
        assert query.query_id == "q-123"
        assert query.question == "What is diabetes?"
        assert query.top_k == 10

    def test_retrieved_chunk(self):
        """Test retrieved chunk."""
        chunk = RetrievedChunk(
            chunk_id="c-123",
            content="Diabetes is a chronic condition...",
            document_id="doc-456",
            relevance_score=0.9,
        )
        assert chunk.relevance_score == 0.9

    def test_retrieval_result(self):
        """Test retrieval result."""
        result = RetrievalResult(
            query_id="q-123",
            chunks=[],
            total_chunks=0,
        )
        assert result.total_chunks == 0

    def test_citation_creation(self):
        """Test citation creation."""
        citation = Citation(
            citation_id="cite-123",
            text="Some relevant text",
            chunk_id="c-123",
            document_id="doc-456",
            title="Medical Guidelines",
        )
        assert citation.title == "Medical Guidelines"


class TestRetrievalPlanner:
    """Tests for retrieval planner."""

    @pytest.fixture
    def planner(self):
        """Create test planner."""
        return RetrievalPlanner()

    @pytest.mark.asyncio
    async def test_plan_retrieval_default(self, planner):
        """Test default retrieval planning."""
        query = RAGQuery(
            query_id="q-123",
            question="What is diabetes?",
        )
        plan = await planner.plan_retrieval(query)

        assert isinstance(plan, RetrievalPlan)
        assert plan.top_k == 5  # Simple question

    @pytest.mark.asyncio
    async def test_plan_complex_query(self, planner):
        """Test planning for complex query."""
        query = RAGQuery(
            query_id="q-123",
            question="Explain in detail the pathophysiology of type 2 diabetes mellitus and its complications",
        )
        plan = await planner.plan_retrieval(query)

        assert plan.top_k >= 10  # Complex question needs more context


class TestContextBuilder:
    """Tests for context builder."""

    @pytest.fixture
    def builder(self):
        """Create test builder."""
        return ContextBuilder()

    @pytest.mark.asyncio
    async def test_build_empty_context(self, builder):
        """Test building empty context."""
        query = RAGQuery(query_id="q-123", question="Test?")
        context = await builder.build_context(query)

        assert isinstance(context, RAGContext)
        assert context.context_text == ""

    @pytest.mark.asyncio
    async def test_build_context_with_chunks(self, builder):
        """Test building context with chunks."""
        query = RAGQuery(query_id="q-123", question="Test?")
        chunks = [
            RetrievedChunk(
                chunk_id="c-1",
                content="First chunk",
                document_id="doc-1",
                title="Doc 1",
            ),
            RetrievedChunk(
                chunk_id="c-2",
                content="Second chunk",
                document_id="doc-2",
                title="Doc 2",
            ),
        ]
        result = RetrievalResult(
            query_id="q-123",
            chunks=chunks,
            total_chunks=2,
        )

        context = await builder.build_context(query, result)

        assert len(context.retrieved_chunks) == 2


class TestDeduplicator:
    """Tests for deduplicator."""

    def test_deduplicate_empty(self):
        """Test deduplicating empty list."""
        dedup = Deduplicator()
        result = dedup.deduplicate([])
        assert result == []

    def test_deduplicate_similar(self):
        """Test deduplicating similar chunks."""
        dedup = Deduplicator()
        chunks = [
            RetrievedChunk(chunk_id="c-1", content="Same content", document_id="d-1"),
            RetrievedChunk(chunk_id="c-2", content="Same content", document_id="d-1"),
        ]
        result = dedup.deduplicate(chunks)
        assert len(result) == 1


class TestPromptBuilder:
    """Tests for prompt builder."""

    @pytest.fixture
    def builder(self):
        """Create test builder."""
        return PromptBuilder()

    def test_build_prompt(self, builder):
        """Test building prompt."""
        query = RAGQuery(
            query_id="q-123",
            question="What is diabetes?",
        )
        context = RAGContext(
            query=query,
            context_text="Diabetes is a condition...",
            context_tokens=10,
        )

        prompt = builder.build_prompt(query, context)

        assert isinstance(prompt, RAGPrompt)
        assert "EREN" in prompt.system_prompt
        assert "What is diabetes?" in prompt.user_prompt


class TestResponseBuilder:
    """Tests for response builder."""

    @pytest.fixture
    def builder(self):
        """Create test builder."""
        return ResponseBuilder()

    def test_build_text_response(self, builder):
        """Test building text response."""
        query = RAGQuery(
            query_id="q-123",
            question="What is diabetes?",
        )
        prompt = RAGPrompt(
            system_prompt="You are EREN.",
            user_prompt="Question",
            context="Context",
            total_tokens=100,
        )

        response = builder.build_response(
            query=query,
            prompt=prompt,
            llm_output="Diabetes is a chronic condition.",
        )

        assert isinstance(response, RAGResponse)
        assert "diabetes" in response.answer.lower()

    def test_format_markdown(self, builder):
        """Test markdown formatting."""
        text = "## Title\n\nContent"
        formatted = builder._format_markdown(text)
        assert formatted == text


class TestCitationBuilder:
    """Tests for citation builder."""

    @pytest.fixture
    def builder(self):
        """Create test builder."""
        return CitationBuilder()

    def test_build_citations(self, builder):
        """Test building citations."""
        chunks = [
            RetrievedChunk(
                chunk_id="c-1",
                content="First chunk content",
                document_id="doc-1",
                title="Medical Guide",
                author="Dr. Smith",
            ),
        ]

        citations = builder.build_citations(chunks)

        assert len(citations) == 1
        assert citations[0].title == "Medical Guide"
        assert citations[0].author == "Dr. Smith"


class TestTokenBudget:
    """Tests for token budget."""

    def test_default_budget(self):
        """Test default budget values."""
        budget = TokenBudget()
        assert budget.max_tokens == 4000
        assert budget.reserved_tokens == 500
        assert budget.available_tokens == 3500

    def test_custom_budget(self):
        """Test custom budget."""
        budget = TokenBudget(max_tokens=5000, reserved_tokens=1000)
        assert budget.available_tokens == 4000

    def test_fits_budget(self):
        """Test budget fitting."""
        budget = TokenBudget(max_tokens=1000, reserved_tokens=100)
        assert budget.fits_budget(500) is True
        assert budget.fits_budget(1000) is False

    def test_allocate(self):
        """Test chunk allocation."""
        budget = TokenBudget(max_tokens=1000, reserved_tokens=100)
        chunks = [
            RetrievedChunk(chunk_id="c-1", content="A" * 100, document_id="d-1"),
            RetrievedChunk(chunk_id="c-2", content="B" * 200, document_id="d-1"),
        ]

        allocated = budget.allocate(chunks)
        assert len(allocated) >= 1


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
