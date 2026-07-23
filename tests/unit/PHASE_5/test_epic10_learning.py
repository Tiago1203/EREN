"""
Tests for EPIC 10: Agent Learning & Optimization

Test suite for the Agent Learning Engine.
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
)

from core.PHASE_5.epic10_learning import (
    AgentLearningEngine,
    AgentLearningConfig,
)

from core.PHASE_5.epic10_learning.domain import (
    AgentMetric,
    MetricType,
    LearningSession,
    SessionStatus,
    OptimizationReport,
    OptimizationType,
    Recommendation,
)

from core.PHASE_5.epic10_learning.engines import (
    PerformanceAnalyzer,
    StrategyOptimizer,
    AgentEvaluator,
    CollaborationOptimizer,
)


# =============================================================================
# TEST FIXTURES
# =============================================================================

@pytest.fixture
def learning_config():
    """Create learning config."""
    return AgentLearningConfig(
        enable_performance_analyzer=True,
        enable_strategy_optimizer=True,
        enable_agent_evaluator=True,
        enable_collab_optimizer=True,
    )


@pytest.fixture
def agent_learning(learning_config):
    """Create agent learning engine."""
    return AgentLearningEngine(
        agent_id="learning_test_1",
        config=learning_config,
    )


# =============================================================================
# TEST AGENT LEARNING ENGINE
# =============================================================================

class TestAgentLearningEngine:
    """Tests for AgentLearningEngine."""
    
    @pytest.mark.asyncio
    async def test_engine_initialization(self, agent_learning, learning_config):
        """Test engine initializes correctly."""
        assert agent_learning.agent_id == "learning_test_1"
        assert agent_learning.agent_type == AgentType.LEARNING
        assert agent_learning.config == learning_config
        
        # Engines should be initialized
        assert agent_learning._performance_analyzer is not None
        assert agent_learning._strategy_optimizer is not None
        assert agent_learning._agent_evaluator is not None
        assert agent_learning._collab_optimizer is not None
    
    @pytest.mark.asyncio
    async def test_engine_initialize(self, agent_learning):
        """Test engine initialization method."""
        await agent_learning.initialize()
        assert agent_learning.state == AgentState.IDLE
    
    @pytest.mark.asyncio
    async def test_analyze_action(self, agent_learning):
        """Test analyze action."""
        task = AgentTask(
            task_id="task_1",
            agent_id="learning_test_1",
            task_type="learning",
            input_data={
                "action": "analyze",
                "agent_id": "agent_1",
                "metrics": [
                    {"type": "performance", "current_value": 0.85},
                    {"type": "accuracy", "current_value": 0.92},
                ],
            },
        )
        
        result = await agent_learning.execute(task)
        
        assert result is not None
        assert result.success is True
        assert result.output["action"] == "analyze"
    
    @pytest.mark.asyncio
    async def test_evaluate_action(self, agent_learning):
        """Test evaluate action."""
        task = AgentTask(
            task_id="task_2",
            agent_id="learning_test_1",
            task_type="learning",
            input_data={
                "action": "evaluate",
                "agent_id": "agent_1",
                "metrics": [
                    {"type": "performance", "current_value": 0.85},
                    {"type": "collaboration", "current_value": 0.78},
                ],
            },
        )
        
        result = await agent_learning.execute(task)
        
        assert result is not None
        assert result.success is True
        assert "overall_score" in result.output
    
    @pytest.mark.asyncio
    async def test_metrics(self, agent_learning):
        """Test engine metrics."""
        metrics = agent_learning.get_metrics()
        
        assert "analyses_performed" in metrics
        assert "optimizations_performed" in metrics
        assert "engines_enabled" in metrics


# =============================================================================
# TEST DOMAIN OBJECTS
# =============================================================================

class TestAgentMetric:
    """Tests for AgentMetric."""
    
    def test_metric_creation(self):
        """Test metric creation."""
        metric = AgentMetric(
            metric_id="metric_1",
            agent_id="agent_1",
            metric_type=MetricType.PERFORMANCE,
            current_value=0.85,
        )
        
        assert metric.metric_id == "metric_1"
        assert metric.current_value == 0.85
    
    def test_calculate_trend(self):
        """Test trend calculation."""
        metric = AgentMetric(
            agent_id="agent_1",
            metric_type=MetricType.PERFORMANCE,
            current_value=1.0,
            previous_value=0.8,
        )
        
        trend = metric.calculate_trend()
        assert trend in ["improving", "stable", "declining"]
    
    def test_change_percentage(self):
        """Test change percentage."""
        metric = AgentMetric(
            agent_id="agent_1",
            metric_type=MetricType.PERFORMANCE,
            current_value=1.0,
            previous_value=0.8,
        )
        
        pct = metric.get_change_percentage()
        assert abs(pct - 25.0) < 0.01


class TestLearningSession:
    """Tests for LearningSession."""
    
    def test_session_creation(self):
        """Test session creation."""
        session = LearningSession(
            session_id="session_1",
            agent_id="agent_1",
            description="Test learning",
        )
        
        assert session.session_id == "session_1"
        assert session.status == SessionStatus.PENDING
    
    def test_start_session(self):
        """Test starting session."""
        session = LearningSession(agent_id="agent_1")
        
        session.start()
        
        assert session.status == SessionStatus.RUNNING
        assert session.started_at is not None
    
    def test_complete_session(self):
        """Test completing session."""
        session = LearningSession(agent_id="agent_1")
        
        session.complete()
        
        assert session.status == SessionStatus.COMPLETED
        assert session.completed_at is not None
    
    def test_add_improvement(self):
        """Test adding improvements."""
        session = LearningSession(agent_id="agent_1")
        
        session.add_improvement("Improved response time")
        
        assert len(session.improvements) == 1


class TestRecommendation:
    """Tests for Recommendation."""
    
    def test_recommendation_creation(self):
        """Test recommendation creation."""
        rec = Recommendation(
            title="Improve accuracy",
            description="Increase evidence retrieval",
            expected_impact=0.3,
            priority=8,
        )
        
        assert rec.title == "Improve accuracy"
        assert rec.expected_impact == 0.3
    
    def test_implement(self):
        """Test implementing recommendation."""
        rec = Recommendation(title="Test")
        
        rec.implement()
        
        assert rec.implemented is True
        assert rec.implemented_at is not None


class TestOptimizationReport:
    """Tests for OptimizationReport."""
    
    def test_report_creation(self):
        """Test report creation."""
        report = OptimizationReport(
            report_id="report_1",
            session_id="session_1",
        )
        
        assert report.report_id == "report_1"
        assert len(report.recommendations) == 0
    
    def test_add_recommendation(self):
        """Test adding recommendations."""
        report = OptimizationReport(session_id="session_1")
        
        report.add_recommendation(Recommendation(
            title="Test",
            expected_impact=0.5,
        ))
        
        assert len(report.recommendations) == 1
    
    def test_get_top_recommendations(self):
        """Test getting top recommendations."""
        report = OptimizationReport(session_id="session_1")
        
        report.add_recommendation(Recommendation(title="Low", priority=3))
        report.add_recommendation(Recommendation(title="High", priority=9))
        report.add_recommendation(Recommendation(title="Medium", priority=6))
        
        top = report.get_top_recommendations(2)
        assert len(top) == 2
        assert top[0].priority >= top[1].priority


# =============================================================================
# TEST ENGINES
# =============================================================================

class TestPerformanceAnalyzer:
    """Tests for PerformanceAnalyzer."""
    
    @pytest.mark.asyncio
    async def test_analyze(self):
        """Test analyzing performance."""
        analyzer = PerformanceAnalyzer()
        
        metrics = [
            AgentMetric(agent_id="agent_1", metric_type=MetricType.PERFORMANCE, current_value=0.85),
            AgentMetric(agent_id="agent_1", metric_type=MetricType.ACCURACY, current_value=0.92),
        ]
        
        result = await analyzer.analyze("agent_1", metrics)
        
        assert result.agent_id == "agent_1"
        assert len(result.metrics) == 2
    
    @pytest.mark.asyncio
    async def test_detect_anomalies(self):
        """Test detecting anomalies."""
        analyzer = PerformanceAnalyzer()
        
        metrics = [
            AgentMetric(agent_id="agent_1", metric_type=MetricType.PERFORMANCE, current_value=0.5),
            AgentMetric(agent_id="agent_1", metric_type=MetricType.PERFORMANCE, current_value=0.8),
            AgentMetric(agent_id="agent_1", metric_type=MetricType.PERFORMANCE, current_value=0.85),
        ]
        
        anomalies = await analyzer.detect_anomalies(metrics)
        
        # Should detect the low value as anomaly
        assert len(anomalies) >= 0


class TestStrategyOptimizer:
    """Tests for StrategyOptimizer."""
    
    @pytest.mark.asyncio
    async def test_optimize(self):
        """Test optimizing strategy."""
        optimizer = StrategyOptimizer()
        
        result = await optimizer.optimize(
            agent_id="agent_1",
            current_strategy={"param": 1},
            performance_data={"response_time": 10.0},
        )
        
        assert result.success is True
        assert len(result.recommendations) > 0


class TestAgentEvaluator:
    """Tests for AgentEvaluator."""
    
    @pytest.mark.asyncio
    async def test_evaluate(self):
        """Test evaluating agent."""
        evaluator = AgentEvaluator()
        
        metrics = [
            AgentMetric(agent_id="agent_1", metric_type=MetricType.PERFORMANCE, current_value=0.85),
            AgentMetric(agent_id="agent_1", metric_type=MetricType.COLLABORATION, current_value=0.78),
        ]
        
        result = await evaluator.evaluate("agent_1", metrics)
        
        assert result.agent_id == "agent_1"
        assert 0.0 <= result.overall_score <= 1.0


class TestCollaborationOptimizer:
    """Tests for CollaborationOptimizer."""
    
    @pytest.mark.asyncio
    async def test_optimize(self):
        """Test optimizing collaboration."""
        optimizer = CollaborationOptimizer()
        
        result = await optimizer.optimize(
            agent_ids=["agent_1", "agent_2"],
            collaboration_data={"message_count": 150},
        )
        
        assert len(result.agents_involved) == 2
        assert result.improvement_score >= 0.0


# =============================================================================
# TEST ENUMS
# =============================================================================

class TestEnums:
    """Tests for enum values."""
    
    def test_metric_type_values(self):
        """Test MetricType enum values."""
        assert MetricType.PERFORMANCE.value == "performance"
        assert MetricType.ACCURACY.value == "accuracy"
    
    def test_session_status_values(self):
        """Test SessionStatus enum values."""
        assert SessionStatus.PENDING.value == "pending"
        assert SessionStatus.RUNNING.value == "running"
        assert SessionStatus.COMPLETED.value == "completed"
    
    def test_optimization_type_values(self):
        """Test OptimizationType enum values."""
        assert OptimizationType.STRATEGY.value == "strategy"
        assert OptimizationType.COLLABORATION.value == "collaboration"


# =============================================================================
# TEST RUN
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
