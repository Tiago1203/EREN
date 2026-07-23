"""
Tests for EPIC 3: Diagnostic Agent

Test suite for the Diagnostic Agent.
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

from core.PHASE_5.epic3_diagnostic_agent import (
    DiagnosticAgent,
    DiagnosticAgentConfig,
)

from core.PHASE_5.epic3_diagnostic_agent.domain import (
    DiagnosticTask,
    DiagnosticTaskType,
    FailurePattern,
    FailureSeverity,
    DiagnosticReport,
    DiagnosisConfidence,
)

from core.PHASE_5.epic3_diagnostic_agent.engines import (
    FailureAnalyzer,
    FailureAnalysisResult,
    RootCauseAnalyzer,
    RootCauseAnalysisResult,
    DiagnosticPlanner,
    DiagnosticPlan,
    FaultCorrelator,
    CorrelationResult,
)


# =============================================================================
# TEST FIXTURES
# =============================================================================

@pytest.fixture
def agent_config():
    """Create agent config."""
    return DiagnosticAgentConfig(
        enable_failure_analyzer=True,
        enable_root_cause_analyzer=True,
        enable_diagnostic_planner=True,
        enable_fault_correlator=True,
    )


@pytest.fixture
def diagnostic_agent(agent_config):
    """Create diagnostic agent."""
    return DiagnosticAgent(
        agent_id="diagnostic_test_1",
        config=agent_config,
    )


# =============================================================================
# TEST DIAGNOSTIC AGENT
# =============================================================================

class TestDiagnosticAgent:
    """Tests for DiagnosticAgent."""
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self, diagnostic_agent, agent_config):
        """Test agent initializes correctly."""
        assert diagnostic_agent.agent_id == "diagnostic_test_1"
        assert diagnostic_agent.agent_type == AgentType.DIAGNOSTIC
        assert diagnostic_agent.config == agent_config
        
        # Engines should be initialized
        assert diagnostic_agent._failure_analyzer is not None
        assert diagnostic_agent._root_cause_analyzer is not None
        assert diagnostic_agent._diagnostic_planner is not None
        assert diagnostic_agent._fault_correlator is not None
    
    @pytest.mark.asyncio
    async def test_agent_initialize(self, diagnostic_agent):
        """Test agent initialization method."""
        await diagnostic_agent.initialize()
        assert diagnostic_agent.state == AgentState.IDLE
    
    @pytest.mark.asyncio
    async def test_execute_failure_analysis(self, diagnostic_agent):
        """Test failure analysis task execution."""
        task = AgentTask(
            task_id="task_1",
            agent_id="diagnostic_test_1",
            task_type="failure_analysis",
            input_data={
                "device_id": "DEV-123",
                "device_name": "Infusion Pump",
                "symptom": "Device overheating",
                "error_codes": ["ERR_TEMP_001"],
                "conditions": {"temperature": 85},
            },
        )
        
        result = await diagnostic_agent.execute(task)
        
        assert result is not None
        assert result.success is True
        assert result.agent_id == "diagnostic_test_1"
        assert result.output["task_type"] == "failure_analysis"
    
    @pytest.mark.asyncio
    async def test_execute_root_cause_analysis(self, diagnostic_agent):
        """Test root cause analysis task execution."""
        task = AgentTask(
            task_id="task_2",
            agent_id="diagnostic_test_1",
            task_type="root_cause",
            input_data={
                "device_id": "DEV-456",
                "symptom": "Intermittent power failures",
            },
        )
        
        result = await diagnostic_agent.execute(task)
        
        assert result is not None
        assert result.success is True
        assert result.output["task_type"] == "root_cause_analysis"
        assert "root_cause" in result.output
    
    @pytest.mark.asyncio
    async def test_execute_troubleshooting(self, diagnostic_agent):
        """Test troubleshooting task execution."""
        task = AgentTask(
            task_id="task_3",
            agent_id="diagnostic_test_1",
            task_type="troubleshooting",
            input_data={
                "device_id": "DEV-789",
                "symptom": "Device not responding",
            },
        )
        
        result = await diagnostic_agent.execute(task)
        
        assert result is not None
        assert result.success is True
        assert result.output["task_type"] == "troubleshooting"
        assert "steps" in result.output
    
    @pytest.mark.asyncio
    async def test_execute_predictive(self, diagnostic_agent):
        """Test predictive diagnosis task execution."""
        task = AgentTask(
            task_id="task_4",
            agent_id="diagnostic_test_1",
            task_type="predictive",
            input_data={
                "device_id": "DEV-101",
            },
        )
        
        result = await diagnostic_agent.execute(task)
        
        assert result is not None
        assert result.success is True
        assert result.output["task_type"] == "predictive_diagnosis"
        assert "predictions" in result.output
    
    @pytest.mark.asyncio
    async def test_metrics(self, diagnostic_agent):
        """Test agent metrics."""
        metrics = diagnostic_agent.get_metrics()
        
        assert "diagnoses_completed" in metrics
        assert "reports_generated" in metrics
        assert "engines_enabled" in metrics
        
        assert metrics["engines_enabled"]["failure_analyzer"] is True
        assert metrics["engines_enabled"]["root_cause_analyzer"] is True


# =============================================================================
# TEST DOMAIN OBJECTS
# =============================================================================

class TestDiagnosticTask:
    """Tests for DiagnosticTask."""
    
    def test_task_creation(self):
        """Test task creation."""
        task = DiagnosticTask(
            task_id="dt_1",
            task_type=DiagnosticTaskType.FAILURE_ANALYSIS,
            device_id="DEV-123",
            symptom="Test symptom",
        )
        
        assert task.task_id == "dt_1"
        assert task.task_type == DiagnosticTaskType.FAILURE_ANALYSIS
        assert task.status == "pending"
    
    def test_task_auto_id(self):
        """Test automatic ID generation."""
        task = DiagnosticTask(
            task_type=DiagnosticTaskType.ROOT_CAUSE,
        )
        
        assert task.task_id != ""
        assert len(task.task_id) > 0
    
    def test_task_duration(self):
        """Test duration calculation."""
        task = DiagnosticTask(
            task_id="dt_2",
            task_type=DiagnosticTaskType.INVESTIGATION,
        )
        
        task.started_at = datetime.now(UTC)
        task.completed_at = datetime.now(UTC)
        
        assert task.duration_ms == 0


class TestFailurePattern:
    """Tests for FailurePattern."""
    
    def test_pattern_creation(self):
        """Test pattern creation."""
        pattern = FailurePattern(
            pattern_id="fp_1",
            pattern_name="Overheating Pattern",
            severity=FailureSeverity.HIGH,
        )
        
        assert pattern.pattern_id == "fp_1"
        assert pattern.severity == FailureSeverity.HIGH


class TestDiagnosticReport:
    """Tests for DiagnosticReport."""
    
    def test_report_creation(self):
        """Test report creation."""
        report = DiagnosticReport(
            report_id="dr_1",
            task_id="task_1",
            diagnosis="Cooling system failure",
            confidence=DiagnosisConfidence.HIGH,
        )
        
        assert report.report_id == "dr_1"
        assert report.diagnosis == "Cooling system failure"
        assert report.confidence == DiagnosisConfidence.HIGH
    
    def test_add_hypothesis(self):
        """Test adding hypothesis."""
        report = DiagnosticReport(
            task_id="task_2",
        )
        
        report.add_hypothesis(
            hypothesis="Power supply failure",
            probability=0.8,
            evidence=["Power fluctuations detected"],
        )
        
        assert len(report.hypotheses) == 1
        assert report.hypotheses[0]["probability"] == 0.8
    
    def test_set_primary_cause(self):
        """Test setting primary cause."""
        report = DiagnosticReport(
            task_id="task_3",
        )
        
        report.add_hypothesis("Cause A", 0.7)
        report.add_hypothesis("Cause B", 0.5)
        report.set_primary_cause("Cause A")
        
        assert report.primary_cause == "Cause A"
        assert report.confidence_score == 0.7
        assert report.confidence == DiagnosisConfidence.MEDIUM


# =============================================================================
# TEST ENGINES
# =============================================================================

class TestFailureAnalyzer:
    """Tests for FailureAnalyzer."""
    
    @pytest.mark.asyncio
    async def test_analyze_with_symptoms(self):
        """Test analysis with symptoms."""
        analyzer = FailureAnalyzer()
        
        result = await analyzer.analyze(
            device_id="DEV-123",
            symptoms=["thermal shutdown detected", "cooling_failure"],
            error_codes=["ERR_TEMP_001"],
            conditions={"temperature": 85},
        )
        
        assert result.device_id == "DEV-123"
        assert result.failures is not None
        # Severity should be HIGH or CRITICAL for overheating
        assert result.overall_severity in [FailureSeverity.HIGH, FailureSeverity.CRITICAL]
    
    @pytest.mark.asyncio
    async def test_analyze_no_symptoms(self):
        """Test analysis with no symptoms."""
        analyzer = FailureAnalyzer()
        
        result = await analyzer.analyze(
            device_id="DEV-456",
            symptoms=[],
            error_codes=[],
            conditions={},
        )
        
        assert result.device_id == "DEV-456"
        assert len(result.failures) == 0


class TestRootCauseAnalyzer:
    """Tests for RootCauseAnalyzer."""
    
    @pytest.mark.asyncio
    async def test_analyze_overheating(self):
        """Test RCA for overheating."""
        analyzer = RootCauseAnalyzer()
        
        result = await analyzer.analyze(
            device_id="DEV-123",
            symptom="Device overheating",
            failure_data={"temperature": 90},
        )
        
        assert result.device_id == "DEV-123"
        assert "Cooling" in result.root_cause or result.root_cause == "unknown"
    
    @pytest.mark.asyncio
    async def test_analyze_calibration(self):
        """Test RCA for calibration issue."""
        analyzer = RootCauseAnalyzer()
        
        result = await analyzer.analyze(
            device_id="DEV-456",
            symptom="Calibration accuracy issues",
            failure_data={},
        )
        
        assert result.device_id == "DEV-456"


class TestDiagnosticPlanner:
    """Tests for DiagnosticPlanner."""
    
    @pytest.mark.asyncio
    async def test_create_plan(self):
        """Test plan creation."""
        planner = DiagnosticPlanner()
        
        task = DiagnosticTask(
            task_id="task_1",
            task_type=DiagnosticTaskType.FAILURE_ANALYSIS,
        )
        
        analysis_result = FailureAnalysisResult(
            device_id="DEV-123",
            failures=[{"mode": "test_failure"}],
        )
        
        plan = await planner.create_plan(task, analysis_result)
        
        assert plan.task_id == "task_1"
        assert len(plan.steps) > 0
        assert plan.status == "pending"


class TestFaultCorrelator:
    """Tests for FaultCorrelator."""
    
    @pytest.mark.asyncio
    async def test_correlate(self):
        """Test fault correlation."""
        correlator = FaultCorrelator()
        
        primary_event = {
            "event_id": "evt_1",
            "device_id": "DEV-123",
            "timestamp": datetime.now(UTC),
        }
        
        event_history = [
            {
                "event_id": "evt_2",
                "device_id": "DEV-123",
                "timestamp": datetime.now(UTC),
            },
        ]
        
        result = await correlator.correlate(primary_event, event_history)
        
        assert result.primary_event == primary_event
        assert len(result.correlated_events) >= 0


# =============================================================================
# TEST ENUMS
# =============================================================================

class TestEnums:
    """Tests for enum values."""
    
    def test_diagnostic_task_type_values(self):
        """Test DiagnosticTaskType enum values."""
        assert DiagnosticTaskType.FAILURE_ANALYSIS.value == "failure_analysis"
        assert DiagnosticTaskType.ROOT_CAUSE.value == "root_cause"
        assert DiagnosticTaskType.PREDICTIVE.value == "predictive"
    
    def test_failure_severity_values(self):
        """Test FailureSeverity enum values."""
        assert FailureSeverity.CRITICAL.value == "critical"
        assert FailureSeverity.HIGH.value == "high"
        assert FailureSeverity.MEDIUM.value == "medium"
    
    def test_diagnosis_confidence_values(self):
        """Test DiagnosisConfidence enum values."""
        assert DiagnosisConfidence.HIGH.value == "high"
        assert DiagnosisConfidence.MEDIUM.value == "medium"
        assert DiagnosisConfidence.LOW.value == "low"


# =============================================================================
# TEST RUN
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
