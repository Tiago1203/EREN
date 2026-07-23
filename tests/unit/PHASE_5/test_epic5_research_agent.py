"""
Tests for EPIC 5: Research Agent

Test suite for the Research Agent.
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

from core.PHASE_5.epic5_research_agent import (
    ResearchAgent,
    ResearchAgentConfig,
)

from core.PHASE_5.epic5_research_agent.domain import (
    ResearchRequest,
    ResearchType,
    ResearchScope,
    ResearchResult,
    ResearchFinding,
    EvidenceStrength,
    LiteratureReview,
    PaperComparison,
    ComparisonType,
    SummarySection,
)

from core.PHASE_5.epic5_research_agent.engines import (
    ResearchPlanner,
    ResearchPlan,
    EvidenceComparator,
    ComparisonResult,
    PaperAnalyzer,
    AnalysisResult,
    LiteratureReviewer,
    ReviewOutline,
)


# =============================================================================
# TEST FIXTURES
# =============================================================================

@pytest.fixture
def agent_config():
    """Create agent config."""
    return ResearchAgentConfig(
        enable_research_planner=True,
        enable_evidence_comparator=True,
        enable_paper_analyzer=True,
        enable_literature_reviewer=True,
    )


@pytest.fixture
def research_agent(agent_config):
    """Create research agent."""
    return ResearchAgent(
        agent_id="research_test_1",
        config=agent_config,
    )


# =============================================================================
# TEST RESEARCH AGENT
# =============================================================================

class TestResearchAgent:
    """Tests for ResearchAgent."""
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self, research_agent, agent_config):
        """Test agent initializes correctly."""
        assert research_agent.agent_id == "research_test_1"
        assert research_agent.agent_type == AgentType.RESEARCH
        assert research_agent.config == agent_config
        
        # Engines should be initialized
        assert research_agent._research_planner is not None
        assert research_agent._evidence_comparator is not None
        assert research_agent._paper_analyzer is not None
        assert research_agent._literature_reviewer is not None
    
    @pytest.mark.asyncio
    async def test_agent_initialize(self, research_agent):
        """Test agent initialization method."""
        await research_agent.initialize()
        assert research_agent.state == AgentState.IDLE
    
    @pytest.mark.asyncio
    async def test_execute_systematic_review(self, research_agent):
        """Test systematic review execution."""
        task = AgentTask(
            task_id="task_1",
            agent_id="research_test_1",
            task_type="research",
            input_data={
                "research_type": "systematic_review",
                "research_question": "Effectiveness of PM protocols?",
                "scope": "comprehensive",
            },
        )
        
        result = await research_agent.execute(task)
        
        assert result is not None
        assert result.success is True
        assert result.agent_id == "research_test_1"
        assert result.output["research_type"] == "systematic_review"
    
    @pytest.mark.asyncio
    async def test_execute_meta_analysis(self, research_agent):
        """Test meta-analysis execution."""
        task = AgentTask(
            task_id="task_2",
            agent_id="research_test_1",
            task_type="research",
            input_data={
                "research_type": "meta_analysis",
                "research_question": "Impact of training on device reliability",
            },
        )
        
        result = await research_agent.execute(task)
        
        assert result is not None
        assert result.success is True
        assert result.output["research_type"] == "meta_analysis"
    
    @pytest.mark.asyncio
    async def test_execute_technical_review(self, research_agent):
        """Test technical review execution."""
        task = AgentTask(
            task_id="task_3",
            agent_id="research_test_1",
            task_type="research",
            input_data={
                "research_type": "technical_review",
                "research_question": "Device calibration standards",
            },
        )
        
        result = await research_agent.execute(task)
        
        assert result is not None
        assert result.success is True
        assert result.output["research_type"] == "technical_review"
    
    @pytest.mark.asyncio
    async def test_metrics(self, research_agent):
        """Test agent metrics."""
        metrics = research_agent.get_metrics()
        
        assert "research_completed" in metrics
        assert "reviews_generated" in metrics
        assert "engines_enabled" in metrics
        
        assert metrics["engines_enabled"]["research_planner"] is True
        assert metrics["engines_enabled"]["evidence_comparator"] is True


# =============================================================================
# TEST DOMAIN OBJECTS
# =============================================================================

class TestResearchRequest:
    """Tests for ResearchRequest."""
    
    def test_request_creation(self):
        """Test request creation."""
        request = ResearchRequest(
            request_id="req_1",
            research_type=ResearchType.SYSTEMATIC_REVIEW,
            research_question="Test question",
        )
        
        assert request.request_id == "req_1"
        assert request.research_type == ResearchType.SYSTEMATIC_REVIEW
    
    def test_request_auto_id(self):
        """Test automatic ID generation."""
        request = ResearchRequest(
            research_type=ResearchType.SYSTEMATIC_REVIEW,
        )
        
        assert request.request_id != ""
        assert len(request.request_id) > 0


class TestResearchFinding:
    """Tests for ResearchFinding."""
    
    def test_finding_creation(self):
        """Test finding creation."""
        finding = ResearchFinding(
            finding_id="find_1",
            description="Test finding",
            evidence_strength=EvidenceStrength.MODERATE,
        )
        
        assert finding.finding_id == "find_1"
        assert finding.evidence_strength == EvidenceStrength.MODERATE


class TestResearchResult:
    """Tests for ResearchResult."""
    
    def test_result_creation(self):
        """Test result creation."""
        result = ResearchResult(
            result_id="res_1",
            request_id="req_1",
            articles_reviewed=10,
            articles_included=5,
        )
        
        assert result.result_id == "res_1"
        assert result.articles_reviewed == 10
    
    def test_add_finding(self):
        """Test adding findings."""
        result = ResearchResult(request_id="req_1")
        
        result.add_finding(ResearchFinding(description="Finding 1"))
        assert len(result.findings) == 1


class TestLiteratureReview:
    """Tests for LiteratureReview."""
    
    def test_review_creation(self):
        """Test review creation."""
        review = LiteratureReview(
            review_id="rev_1",
            request_id="req_1",
            title="Test Review",
        )
        
        assert review.review_id == "rev_1"
        assert review.title == "Test Review"
        assert review.references_count == 0
    
    def test_add_section(self):
        """Test adding sections."""
        review = LiteratureReview(request_id="req_1")
        
        review.add_section(SummarySection(
            title="Introduction",
            content="Test",
            section_type="introduction",
            order=1,
        ))
        
        assert len(review.sections) == 1
    
    def test_to_markdown(self):
        """Test markdown conversion."""
        review = LiteratureReview(
            request_id="req_1",
            title="Test Review",
        )
        
        review.add_section(SummarySection(
            title="Introduction",
            content="Test content",
            section_type="introduction",
            order=1,
        ))
        
        md = review.to_markdown()
        assert "# Test Review" in md
        assert "## Introduction" in md


class TestPaperComparison:
    """Tests for PaperComparison."""
    
    def test_comparison_creation(self):
        """Test comparison creation."""
        comparison = PaperComparison(
            comparison_id="comp_1",
            paper_1_id="paper_1",
            paper_2_id="paper_2",
            comparison_type=ComparisonType.METHODOLOGY,
        )
        
        assert comparison.comparison_id == "comp_1"
        assert comparison.comparison_type == ComparisonType.METHODOLOGY


# =============================================================================
# TEST ENGINES
# =============================================================================

class TestResearchPlanner:
    """Tests for ResearchPlanner."""
    
    @pytest.mark.asyncio
    async def test_create_plan(self):
        """Test plan creation."""
        planner = ResearchPlanner()
        
        request = ResearchRequest(
            request_id="req_1",
            research_type=ResearchType.SYSTEMATIC_REVIEW,
        )
        
        plan = await planner.create_plan(request)
        
        assert plan.request_id == request.request_id
        assert len(plan.steps) > 0
        assert plan.estimated_duration_minutes > 0


class TestEvidenceComparator:
    """Tests for EvidenceComparator."""
    
    @pytest.mark.asyncio
    async def test_compare(self):
        """Test comparison."""
        comparator = EvidenceComparator()
        
        result = await comparator.compare(
            paper_1_id="paper_1",
            paper_2_id="paper_2",
            comparison_type=ComparisonType.METHODOLOGY,
        )
        
        assert result.paper_1_id == "paper_1"
        assert result.paper_2_id == "paper_2"
        assert len(result.comparisons) == 1
    
    @pytest.mark.asyncio
    async def test_compare_multiple(self):
        """Test multiple comparisons."""
        comparator = EvidenceComparator()
        
        results = await comparator.compare_multiple(
            paper_ids=["paper_1", "paper_2", "paper_3"]
        )
        
        # 3 papers = 3 comparisons (1-2, 1-3, 2-3)
        assert len(results) == 3


class TestPaperAnalyzer:
    """Tests for PaperAnalyzer."""
    
    @pytest.mark.asyncio
    async def test_analyze(self):
        """Test paper analysis."""
        analyzer = PaperAnalyzer()
        
        result = await analyzer.analyze(
            paper_id="paper_1",
            content="Test content",
        )
        
        assert result.paper_id == "paper_1"
        assert result.methodology_score > 0
    
    @pytest.mark.asyncio
    async def test_analyze_batch(self):
        """Test batch analysis."""
        analyzer = PaperAnalyzer()
        
        papers = [
            ("paper_1", "content 1"),
            ("paper_2", "content 2"),
        ]
        
        results = await analyzer.analyze_batch(papers)
        
        assert len(results) == 2


class TestLiteratureReviewer:
    """Tests for LiteratureReviewer."""
    
    @pytest.mark.asyncio
    async def test_create_review(self):
        """Test review creation."""
        reviewer = LiteratureReviewer()
        
        request = ResearchRequest(
            request_id="req_1",
            research_question="Test question",
        )
        
        findings = [
            ResearchFinding(description="Finding 1"),
        ]
        
        review = await reviewer.create_review(request, [], findings)
        
        assert review.request_id == request.request_id
        assert len(review.sections) > 0
    
    @pytest.mark.asyncio
    async def test_create_outline(self):
        """Test outline creation."""
        reviewer = LiteratureReviewer()
        
        outline = await reviewer.create_outline("standard")
        
        assert len(outline.sections) > 0
        assert outline.format_type == "standard"


# =============================================================================
# TEST ENUMS
# =============================================================================

class TestEnums:
    """Tests for enum values."""
    
    def test_research_type_values(self):
        """Test ResearchType enum values."""
        assert ResearchType.SYSTEMATIC_REVIEW.value == "systematic_review"
        assert ResearchType.META_ANALYSIS.value == "meta_analysis"
        assert ResearchType.TECHNICAL_REVIEW.value == "technical_review"
    
    def test_research_scope_values(self):
        """Test ResearchScope enum values."""
        assert ResearchScope.COMPREHENSIVE.value == "comprehensive"
        assert ResearchScope.FOCUSED.value == "focused"
        assert ResearchScope.RAPID.value == "rapid"
    
    def test_evidence_strength_values(self):
        """Test EvidenceStrength enum values."""
        assert EvidenceStrength.STRONG.value == "strong"
        assert EvidenceStrength.MODERATE.value == "moderate"
        assert EvidenceStrength.LIMITED.value == "limited"
    
    def test_comparison_type_values(self):
        """Test ComparisonType enum values."""
        assert ComparisonType.METHODOLOGY.value == "methodology"
        assert ComparisonType.RESULTS.value == "results"
        assert ComparisonType.QUALITY.value == "quality"


# =============================================================================
# TEST RUN
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
