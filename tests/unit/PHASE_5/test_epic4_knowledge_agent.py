"""
Tests for EPIC 4: Knowledge Agent

Test suite for the Knowledge Agent.
"""

import pytest
from datetime import UTC, datetime

# =============================================================================
# IMPORTS FROM PHASE 5
# =============================================================================

from core.PHASE_5.foundation import (
    AgentType,
    AgentState,
    AgentTask,
    AgentResult,
)

from core.PHASE_5.epic4_knowledge_agent import (
    KnowledgeAgent,
    KnowledgeAgentConfig,
)

from core.PHASE_5.epic4_knowledge_agent.domain import (
    KnowledgeQuery,
    QueryType,
    KnowledgeSource,
    KnowledgePackage,
    KnowledgeItem,
    SourceType,
    Citation,
    CitationBundle,
)

from core.PHASE_5.epic4_knowledge_agent.engines import (
    KnowledgeRetriever,
    RetrievalResult,
    CitationCollector,
    CitationResult,
    KnowledgeSearchEngine,
    LiteratureSearchEngine,
    StandardsSearchEngine,
)


# =============================================================================
# TEST FIXTURES
# =============================================================================

@pytest.fixture
def agent_config():
    """Create agent config."""
    return KnowledgeAgentConfig(
        enable_knowledge_retriever=True,
        enable_citation_collector=True,
        enable_literature_search=True,
        enable_standards_search=True,
    )


@pytest.fixture
def knowledge_agent(agent_config):
    """Create knowledge agent."""
    return KnowledgeAgent(
        agent_id="knowledge_test_1",
        config=agent_config,
    )


# =============================================================================
# TEST KNOWLEDGE AGENT
# =============================================================================

class TestKnowledgeAgent:
    """Tests for KnowledgeAgent."""
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self, knowledge_agent, agent_config):
        """Test agent initializes correctly."""
        assert knowledge_agent.agent_id == "knowledge_test_1"
        assert knowledge_agent.agent_type == AgentType.KNOWLEDGE
        assert knowledge_agent.config == agent_config
        
        # Engines should be initialized
        assert knowledge_agent._knowledge_retriever is not None
        assert knowledge_agent._citation_collector is not None
        assert knowledge_agent._literature_engine is not None
        assert knowledge_agent._standards_engine is not None
    
    @pytest.mark.asyncio
    async def test_agent_initialize(self, knowledge_agent):
        """Test agent initialization method."""
        await knowledge_agent.initialize()
        assert knowledge_agent.state == AgentState.IDLE
    
    @pytest.mark.asyncio
    async def test_execute_factual_query(self, knowledge_agent):
        """Test factual query execution."""
        task = AgentTask(
            task_id="task_1",
            agent_id="knowledge_test_1",
            task_type="knowledge_query",
            input_data={
                "query_type": "factual",
                "question": "How to perform PM on infusion pumps?",
                "max_results": 5,
            },
        )
        
        result = await knowledge_agent.execute(task)
        
        assert result is not None
        assert result.success is True
        assert result.agent_id == "knowledge_test_1"
        assert result.output["query_type"] == "factual"
    
    @pytest.mark.asyncio
    async def test_execute_regulatory_query(self, knowledge_agent):
        """Test regulatory query execution."""
        task = AgentTask(
            task_id="task_2",
            agent_id="knowledge_test_1",
            task_type="knowledge_query",
            input_data={
                "query_type": "regulatory",
                "question": "Medical device regulations",
            },
        )
        
        result = await knowledge_agent.execute(task)
        
        assert result is not None
        assert result.success is True
        assert result.output["query_type"] == "regulatory"
    
    @pytest.mark.asyncio
    async def test_execute_literature_query(self, knowledge_agent):
        """Test literature query execution."""
        task = AgentTask(
            task_id="task_3",
            agent_id="knowledge_test_1",
            task_type="knowledge_query",
            input_data={
                "query_type": "literature",
                "question": "Clinical evidence on device safety",
            },
        )
        
        result = await knowledge_agent.execute(task)
        
        assert result is not None
        assert result.success is True
        assert result.output["query_type"] == "literature"
    
    @pytest.mark.asyncio
    async def test_execute_standards_query(self, knowledge_agent):
        """Test standards query execution."""
        task = AgentTask(
            task_id="task_4",
            agent_id="knowledge_test_1",
            task_type="knowledge_query",
            input_data={
                "query_type": "regulatory",
                "question": "Electrical safety standards",
                "sources": ["standards"],
            },
        )
        
        result = await knowledge_agent.execute(task)
        
        assert result is not None
        assert result.success is True
    
    @pytest.mark.asyncio
    async def test_metrics(self, knowledge_agent):
        """Test agent metrics."""
        metrics = knowledge_agent.get_metrics()
        
        assert "queries_processed" in metrics
        assert "packages_generated" in metrics
        assert "engines_enabled" in metrics
        
        assert metrics["engines_enabled"]["knowledge_retriever"] is True
        assert metrics["engines_enabled"]["citation_collector"] is True


# =============================================================================
# TEST DOMAIN OBJECTS
# =============================================================================

class TestKnowledgeQuery:
    """Tests for KnowledgeQuery."""
    
    def test_query_creation(self):
        """Test query creation."""
        query = KnowledgeQuery(
            query_id="q_1",
            query_type=QueryType.TECHNICAL,
            question="Test question",
        )
        
        assert query.query_id == "q_1"
        assert query.query_type == QueryType.TECHNICAL
        assert query.max_results == 10
    
    def test_query_auto_id(self):
        """Test automatic ID generation."""
        query = KnowledgeQuery(
            query_type=QueryType.FACTUAL,
        )
        
        assert query.query_id != ""
        assert len(query.query_id) > 0


class TestKnowledgePackage:
    """Tests for KnowledgePackage."""
    
    def test_package_creation(self):
        """Test package creation."""
        item = KnowledgeItem(
            title="Test Item",
            relevance_score=0.8,
        )
        
        package = KnowledgePackage(
            package_id="pkg_1",
            query_id="q_1",
            items=[item],
        )
        
        assert package.package_id == "pkg_1"
        assert package.total_items == 1
        assert package.avg_relevance == 0.8
    
    def test_add_item(self):
        """Test adding items."""
        package = KnowledgePackage(query_id="q_1")
        
        package.add_item(KnowledgeItem(
            title="Item 1",
            relevance_score=0.9,
        ))
        
        assert package.total_items == 1
        assert package.avg_relevance == 0.9
    
    def test_get_top_items(self):
        """Test getting top items."""
        items = [
            KnowledgeItem(title=f"Item {i}", relevance_score=0.5 + i * 0.1)
            for i in range(5)
        ]
        
        package = KnowledgePackage(query_id="q_1", items=items)
        
        top = package.get_top_items(3)
        assert len(top) == 3
        assert top[0].relevance_score >= top[1].relevance_score


class TestCitation:
    """Tests for Citation."""
    
    def test_citation_creation(self):
        """Test citation creation."""
        citation = Citation(
            citation_id="cit_1",
            title="Test Article",
            authors=["Author 1", "Author 2"],
            year=2024,
        )
        
        assert citation.citation_id == "cit_1"
        assert len(citation.authors) == 2
    
    def test_format_apa(self):
        """Test APA formatting."""
        citation = Citation(
            title="Test Article",
            authors=["Smith, J.", "Doe, A."],
            year=2024,
            publication="Journal of Testing",
        )
        
        apa = citation.format_apa()
        assert "Smith" in apa
        assert "2024" in apa
        assert "Test Article" in apa
    
    def test_format_vancouver(self):
        """Test Vancouver formatting."""
        citation = Citation(
            title="Test Article",
            authors=["Smith, J.", "Doe, A."],
            year=2024,
            publication="J Test",
            volume="10",
            issue="2",
            pages="100-110",
        )
        
        vancouver = citation.format_vancouver()
        assert "Smith" in vancouver
        assert "10" in vancouver


class TestCitationBundle:
    """Tests for CitationBundle."""
    
    def test_bundle_creation(self):
        """Test bundle creation."""
        bundle = CitationBundle(
            bundle_id="bundle_1",
            topic="Test topic",
        )
        
        assert bundle.bundle_id == "bundle_1"
        assert bundle.references_count == 0
    
    def test_add_citation(self):
        """Test adding citations."""
        bundle = CitationBundle(topic="Test")
        
        bundle.add_citation(Citation(
            title="Article 1",
            authors=["Author"],
            year=2024,
        ))
        
        assert bundle.references_count == 1
    
    def test_format_references_apa(self):
        """Test formatting references in APA."""
        bundle = CitationBundle(topic="Test")
        
        bundle.add_citation(Citation(
            title="Article 1",
            authors=["Smith"],
            year=2024,
        ))
        
        formatted = bundle.format_references("apa")
        assert "[1]" in formatted
        assert "Article 1" in formatted


# =============================================================================
# TEST ENGINES
# =============================================================================

class TestKnowledgeRetriever:
    """Tests for KnowledgeRetriever."""
    
    @pytest.mark.asyncio
    async def test_retrieve(self):
        """Test knowledge retrieval."""
        retriever = KnowledgeRetriever()
        
        query = KnowledgeQuery(
            question="infusion pump maintenance",
            max_results=5,
        )
        
        result = await retriever.retrieve(query)
        
        assert result.query_id == query.query_id
        assert result.items is not None
    
    @pytest.mark.asyncio
    async def test_retrieve_with_sources(self):
        """Test retrieval with specific sources."""
        retriever = KnowledgeRetriever()
        
        query = KnowledgeQuery(
            question="safety standards",
            sources=[KnowledgeSource.STANDARDS],
        )
        
        result = await retriever.retrieve(query)
        
        assert len(result.items) > 0


class TestCitationCollector:
    """Tests for CitationCollector."""
    
    @pytest.mark.asyncio
    async def test_collect(self):
        """Test citation collection."""
        collector = CitationCollector()
        
        items = [
            KnowledgeItem(
                title="Test Article",
                source_type=SourceType.JOURNAL_ARTICLE,
                source_name="Test Journal",
            )
        ]
        
        query = KnowledgeQuery(question="test")
        result = await collector.collect(query, items)
        
        assert result.query_id == query.query_id
        assert len(result.citations) >= 0
    
    def test_create_bundle(self):
        """Test bundle creation."""
        collector = CitationCollector()
        
        citations = [
            Citation(title="Article 1", authors=["Author"], year=2024),
            Citation(title="Article 2", authors=["Author"], year=2023),
        ]
        
        bundle = collector.create_bundle(citations, "Test topic")
        
        assert bundle.references_count == 2
        assert bundle.topic == "Test topic"


class TestSearchEngines:
    """Tests for search engines."""
    
    @pytest.mark.asyncio
    async def test_knowledge_search(self):
        """Test knowledge search."""
        engine = KnowledgeSearchEngine()
        
        results = await engine.search("test query", limit=5)
        
        assert len(results) > 0
        assert results[0].title is not None
    
    @pytest.mark.asyncio
    async def test_literature_search(self):
        """Test literature search."""
        engine = LiteratureSearchEngine()
        
        results = await engine.search("clinical study", limit=5)
        
        assert len(results) > 0
    
    @pytest.mark.asyncio
    async def test_standards_search(self):
        """Test standards search."""
        engine = StandardsSearchEngine()
        
        results = await engine.search("electrical safety", limit=5)
        
        assert len(results) > 0


# =============================================================================
# TEST ENUMS
# =============================================================================

class TestEnums:
    """Tests for enum values."""
    
    def test_query_type_values(self):
        """Test QueryType enum values."""
        assert QueryType.FACTUAL.value == "factual"
        assert QueryType.REGULATORY.value == "regulatory"
        assert QueryType.TECHNICAL.value == "technical"
    
    def test_knowledge_source_values(self):
        """Test KnowledgeSource enum values."""
        assert KnowledgeSource.MANUALS.value == "manuals"
        assert KnowledgeSource.STANDARDS.value == "standards"
        assert KnowledgeSource.LITERATURE.value == "literature"
    
    def test_source_type_values(self):
        """Test SourceType enum values."""
        assert SourceType.JOURNAL_ARTICLE.value == "journal_article"
        assert SourceType.STANDARD.value == "standard"
        assert SourceType.MANUAL.value == "manual"


# =============================================================================
# TEST RUN
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
