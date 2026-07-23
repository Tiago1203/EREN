"""
Tests for EPIC 2: Biomedical Agent

Test suite for the Biomedical Agent.
"""

import pytest
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

# =============================================================================
# IMPORTS FROM PHASE 5
# =============================================================================

from core.PHASE_5.foundation import (
    AgentType,
    AgentState,
    AgentTask,
    AgentResult,
)

from core.PHASE_5.epic2_biomedical_agent import (
    BiomedicalAgent,
    BiomedicalAgentConfig,
)

from core.PHASE_5.epic2_biomedical_agent.domain import (
    BiomedicalTask,
    BiomedicalTaskType,
    DeviceAssessment,
    AssessmentSeverity,
    AssessmentStatus,
    MaintenanceRecommendation,
    MaintenancePriority,
    MaintenanceType,
)

from core.PHASE_5.epic2_biomedical_agent.experts import (
    EquipmentExpert,
    EquipmentAnalysis,
    MaintenanceExpert,
    MaintenanceAdvice,
    ManufacturerExpert,
    ManufacturerInfo,
    StandardsExpert,
    StandardReference,
    CalibrationExpert,
    CalibrationRecord,
)


# =============================================================================
# TEST FIXTURES
# =============================================================================

@pytest.fixture
def agent_config():
    """Create agent config."""
    return BiomedicalAgentConfig(
        enable_equipment_expert=True,
        enable_maintenance_expert=True,
        enable_manufacturer_expert=True,
        enable_standards_expert=True,
        enable_calibration_expert=True,
    )


@pytest.fixture
def biomedical_agent(agent_config):
    """Create biomedical agent."""
    return BiomedicalAgent(
        agent_id="biomedical_test_1",
        config=agent_config,
    )


# =============================================================================
# TEST BIOMEDICAL AGENT
# =============================================================================

class TestBiomedicalAgent:
    """Tests for BiomedicalAgent."""
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self, biomedical_agent, agent_config):
        """Test agent initializes correctly."""
        assert biomedical_agent.agent_id == "biomedical_test_1"
        assert biomedical_agent.agent_type == AgentType.BIOMEDICAL
        assert biomedical_agent.config == agent_config
        
        # Experts should be initialized
        assert biomedical_agent._equipment_expert is not None
        assert biomedical_agent._maintenance_expert is not None
        assert biomedical_agent._standards_expert is not None
        assert biomedical_agent._calibration_expert is not None
        assert biomedical_agent._manufacturer_expert is not None
    
    @pytest.mark.asyncio
    async def test_agent_initialize(self, biomedical_agent):
        """Test agent initialization method."""
        await biomedical_agent.initialize()
        assert biomedical_agent.state == AgentState.IDLE
    
    @pytest.mark.asyncio
    async def test_execute_device_analysis(self, biomedical_agent):
        """Test device analysis task execution."""
        task = AgentTask(
            task_id="task_1",
            agent_id="biomedical_test_1",
            task_type="device_analysis",
            input_data={
                "device_id": "DEV-123",
                "device_name": "Infusion Pump",
                "device_type": "therapeutic_equipment",
                "manufacturer": "Medtronic",
                "model": "Symbia T",
                "age_years": 3,
                "usage_hours": 5000,
            },
        )
        
        result = await biomedical_agent.execute(task)
        
        assert result is not None
        assert result.success is True
        assert result.agent_id == "biomedical_test_1"
        assert "equipment_analysis" in result.output
    
    @pytest.mark.asyncio
    async def test_execute_maintenance_planning(self, biomedical_agent):
        """Test maintenance planning task execution."""
        task = AgentTask(
            task_id="task_2",
            agent_id="biomedical_test_1",
            task_type="maintenance_planning",
            input_data={
                "device_id": "DEV-456",
                "device_type": "monitoring_equipment",
                "age_years": 5,
                "usage_hours": 15000,
            },
        )
        
        result = await biomedical_agent.execute(task)
        
        assert result is not None
        assert result.success is True
        assert result.output["task_type"] == "maintenance_planning"
        assert "recommendations" in result.output
    
    @pytest.mark.asyncio
    async def test_execute_calibration_check(self, biomedical_agent):
        """Test calibration check task execution."""
        task = AgentTask(
            task_id="task_3",
            agent_id="biomedical_test_1",
            task_type="calibration_check",
            input_data={
                "device_id": "DEV-789",
            },
        )
        
        result = await biomedical_agent.execute(task)
        
        assert result is not None
        assert result.success is True
        assert result.output["task_type"] == "calibration_check"
        assert "calibration_status" in result.output
    
    @pytest.mark.asyncio
    async def test_execute_compliance_audit(self, biomedical_agent):
        """Test compliance audit task execution."""
        task = AgentTask(
            task_id="task_4",
            agent_id="biomedical_test_1",
            task_type="compliance_audit",
            input_data={
                "device_id": "DEV-101",
                "device_type": "diagnostic_equipment",
                "device_class": "Class II",
            },
        )
        
        result = await biomedical_agent.execute(task)
        
        assert result is not None
        assert result.success is True
        assert result.output["task_type"] == "compliance_audit"
        assert "standards" in result.output
    
    @pytest.mark.asyncio
    async def test_execute_risk_assessment(self, biomedical_agent):
        """Test risk assessment task execution."""
        task = AgentTask(
            task_id="task_5",
            agent_id="biomedical_test_1",
            task_type="risk_assessment",
            input_data={
                "device_id": "DEV-202",
                "usage_hours": 20000,
                "age_years": 7,
            },
        )
        
        result = await biomedical_agent.execute(task)
        
        assert result is not None
        assert result.success is True
        assert result.output["task_type"] == "risk_assessment"
        assert "risk_level" in result.output
        assert "risk_factors" in result.output
    
    @pytest.mark.asyncio
    async def test_metrics(self, biomedical_agent):
        """Test agent metrics."""
        metrics = biomedical_agent.get_metrics()
        
        assert "assessments_completed" in metrics
        assert "recommendations_generated" in metrics
        assert "experts_enabled" in metrics
        
        assert metrics["experts_enabled"]["equipment"] is True
        assert metrics["experts_enabled"]["maintenance"] is True


# =============================================================================
# TEST DOMAIN OBJECTS
# =============================================================================

class TestBiomedicalTask:
    """Tests for BiomedicalTask."""
    
    def test_task_creation(self):
        """Test task creation."""
        task = BiomedicalTask(
            task_id="bt_1",
            task_type=BiomedicalTaskType.DEVICE_ANALYSIS,
            device_id="DEV-123",
            device_name="Test Device",
            device_type="diagnostic",
        )
        
        assert task.task_id == "bt_1"
        assert task.task_type == BiomedicalTaskType.DEVICE_ANALYSIS
        assert task.device_id == "DEV-123"
        assert task.status == AssessmentStatus.PENDING
    
    def test_task_auto_id(self):
        """Test automatic ID generation."""
        task = BiomedicalTask(
            task_type=BiomedicalTaskType.MAINTENANCE_PLANNING,
        )
        
        assert task.task_id != ""
        assert len(task.task_id) > 0
    
    def test_task_duration(self):
        """Test duration calculation."""
        task = BiomedicalTask(
            task_id="bt_2",
            task_type=BiomedicalTaskType.CALIBRATION_CHECK,
        )
        
        task.started_at = datetime.now(UTC)
        task.completed_at = datetime.now(UTC)
        
        assert task.duration_ms == 0


class TestDeviceAssessment:
    """Tests for DeviceAssessment."""
    
    def test_assessment_creation(self):
        """Test assessment creation."""
        assessment = DeviceAssessment(
            assessment_id="da_1",
            device_id="DEV-123",
        )
        
        assert assessment.assessment_id == "da_1"
        assert assessment.device_id == "DEV-123"
        assert assessment.severity == AssessmentSeverity.INFO
        assert len(assessment.findings) == 0
    
    def test_add_finding(self):
        """Test adding findings."""
        assessment = DeviceAssessment(
            assessment_id="da_2",
            device_id="DEV-456",
        )
        
        assessment.add_finding(
            title="Test Finding",
            description="Test description",
            severity=AssessmentSeverity.HIGH,
            recommendation="Fix immediately",
        )
        
        assert len(assessment.findings) == 1
        assert assessment.findings[0]["severity"] == AssessmentSeverity.HIGH.value
    
    def test_calculate_risk(self):
        """Test risk calculation."""
        assessment = DeviceAssessment(
            assessment_id="da_3",
            device_id="DEV-789",
        )
        
        assessment.add_finding("F1", "D1", AssessmentSeverity.CRITICAL)
        assessment.add_finding("F2", "D2", AssessmentSeverity.LOW)
        
        risk = assessment.calculate_risk()
        assert risk > 0.4  # Between LOW and CRITICAL weighted average


class TestMaintenanceRecommendation:
    """Tests for MaintenanceRecommendation."""
    
    def test_recommendation_creation(self):
        """Test recommendation creation."""
        rec = MaintenanceRecommendation(
            recommendation_id="mr_1",
            device_id="DEV-123",
            maintenance_type=MaintenanceType.PREVENTIVE,
            priority=MaintenancePriority.MEDIUM,
            title="Test Maintenance",
        )
        
        assert rec.recommendation_id == "mr_1"
        assert rec.maintenance_type == MaintenanceType.PREVENTIVE
        assert rec.total_cost == 0.0
    
    def test_total_cost(self):
        """Test total cost calculation."""
        rec = MaintenanceRecommendation(
            recommendation_id="mr_2",
            device_id="DEV-456",
            maintenance_type=MaintenanceType.CORRECTIVE,
            parts_cost=100.0,
            labor_cost=200.0,
        )
        
        assert rec.total_cost == 300.0
    
    def test_is_overdue(self):
        """Test overdue check."""
        rec = MaintenanceRecommendation(
            recommendation_id="mr_3",
            device_id="DEV-789",
            scheduled_date=datetime(2020, 1, 1, tzinfo=UTC),
        )
        
        assert rec.is_overdue is True


# =============================================================================
# TEST EXPERTS
# =============================================================================

class TestEquipmentExpert:
    """Tests for EquipmentExpert."""
    
    @pytest.mark.asyncio
    async def test_analyze_device(self):
        """Test device analysis."""
        expert = EquipmentExpert()
        
        analysis = await expert.analyze_device(
            device_id="DEV-123",
            context={"manufacturer": "GE", "model": "Optima"},
        )
        
        assert analysis.device_id == "DEV-123"
        assert analysis.specifications["manufacturer"] == "GE"
    
    @pytest.mark.asyncio
    async def test_predict_failures(self):
        """Test failure prediction."""
        expert = EquipmentExpert()
        
        failures = await expert.predict_failures(
            device_id="DEV-456",
            usage_hours=15000,
            age_years=6,
        )
        
        assert len(failures) > 0


class TestMaintenanceExpert:
    """Tests for MaintenanceExpert."""
    
    @pytest.mark.asyncio
    async def test_generate_recommendations(self):
        """Test recommendation generation."""
        expert = MaintenanceExpert()
        
        recommendations = await expert.generate_recommendations(
            device_id="DEV-123",
            device_type="monitoring",
            age_years=3,
            usage_hours=8000,
        )
        
        assert len(recommendations) > 0
        assert any(r.maintenance_type == MaintenanceType.PREVENTIVE for r in recommendations)


class TestStandardsExpert:
    """Tests for StandardsExpert."""
    
    @pytest.mark.asyncio
    async def test_find_applicable_standards(self):
        """Test finding applicable standards."""
        expert = StandardsExpert()
        
        standards = await expert.find_applicable_standards(
            device_type="diagnostic_equipment",
            device_class="Class II",
        )
        
        assert len(standards) > 0
        assert any(s.standard_id == "IEC 60601-1" for s in standards)


class TestCalibrationExpert:
    """Tests for CalibrationExpert."""
    
    @pytest.mark.asyncio
    async def test_get_calibration_status(self):
        """Test calibration status check."""
        expert = CalibrationExpert()
        
        status = await expert.get_calibration_status(device_id="DEV-123")
        
        assert "device_id" in status
        assert "is_calibrated" in status
    
    @pytest.mark.asyncio
    async def test_calculate_interval(self):
        """Test interval calculation."""
        expert = CalibrationExpert()
        
        interval = await expert.calculate_interval(
            device_type="monitoring",
            usage_hours=5000,
            accuracy_required=0.95,
        )
        
        assert interval > 0


class TestManufacturerExpert:
    """Tests for ManufacturerExpert."""
    
    @pytest.mark.asyncio
    async def test_get_manufacturer_info_known(self):
        """Test getting info for known manufacturer."""
        expert = ManufacturerExpert()
        
        info = await expert.get_manufacturer_info("GE Healthcare")
        
        assert info is not None
        assert info.manufacturer_name == "GE Healthcare"
    
    @pytest.mark.asyncio
    async def test_get_manufacturer_info_unknown(self):
        """Test getting info for unknown manufacturer."""
        expert = ManufacturerExpert()
        
        info = await expert.get_manufacturer_info("Unknown Corp")
        
        assert info is None


# =============================================================================
# TEST ENUMS
# =============================================================================

class TestEnums:
    """Tests for enum values."""
    
    def test_biomedical_task_type_values(self):
        """Test BiomedicalTaskType enum values."""
        assert BiomedicalTaskType.DEVICE_ANALYSIS.value == "device_analysis"
        assert BiomedicalTaskType.MAINTENANCE_PLANNING.value == "maintenance_planning"
        assert BiomedicalTaskType.CALIBRATION_CHECK.value == "calibration_check"
    
    def test_assessment_severity_values(self):
        """Test AssessmentSeverity enum values."""
        assert AssessmentSeverity.CRITICAL.value == "critical"
        assert AssessmentSeverity.HIGH.value == "high"
        assert AssessmentSeverity.MEDIUM.value == "medium"
    
    def test_maintenance_type_values(self):
        """Test MaintenanceType enum values."""
        assert MaintenanceType.PREVENTIVE.value == "preventive"
        assert MaintenanceType.CORRECTIVE.value == "corrective"
        assert MaintenanceType.PREDICTIVE.value == "predictive"
    
    def test_maintenance_priority_values(self):
        """Test MaintenancePriority enum values."""
        assert MaintenancePriority.URGENT.value == "urgent"
        assert MaintenancePriority.HIGH.value == "high"
        assert MaintenancePriority.MEDIUM.value == "medium"


# =============================================================================
# TEST RUN
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
