"""
Tests para EPIC 12: Clinical Context Builder
"""

import pytest
from datetime import datetime

from core.PHASE_5.epic12_clinical_context.domain import (
    ClinicalContext,
    PatientContext,
    DeviceContext,
    HospitalContext,
    RiskLevel,
    CalibrationStatus,
    MedicalHistory,
)
from core.PHASE_5.epic12_clinical_context.builders import (
    PatientContextBuilder,
    DeviceContextBuilder,
    HospitalContextBuilder,
    ClinicalContextAggregator,
)
from core.PHASE_5.epic12_clinical_context.lifecycle import ContextLifecycleManager
from core.PHASE_5.epic12_clinical_context.agent import ClinicalContextAgent


class TestPatientContextBuilder:
    """Tests para PatientContextBuilder."""
    
    @pytest.mark.asyncio
    async def test_build_patient_context(self):
        """Test construir contexto de paciente."""
        builder = PatientContextBuilder()
        context = await builder.build(
            patient_id="patient_123",
            include_history=True,
            include_conditions=True,
        )
        
        assert context.patient_id == "patient_123"
        assert context.medical_history is not None
    
    @pytest.mark.asyncio
    async def test_get_medical_history(self):
        """Test obtener historial médico."""
        builder = PatientContextBuilder()
        history = await builder.get_medical_history("patient_123")
        
        assert history.history_id == "history_patient_123"
        assert isinstance(history.conditions, list)


class TestDeviceContextBuilder:
    """Tests para DeviceContextBuilder."""
    
    @pytest.mark.asyncio
    async def test_build_device_context(self):
        """Test construir contexto de dispositivo."""
        builder = DeviceContextBuilder()
        context = await builder.build(
            device_id="device_456",
            include_maintenance=True,
            include_incidents=True,
        )
        
        assert context.device_id == "device_456"
        assert context.device_type == "infusion_pump"
    
    @pytest.mark.asyncio
    async def test_needs_maintenance(self):
        """Test verificar si necesita mantenimiento."""
        builder = DeviceContextBuilder()
        context = await builder.build(device_id="device_456")
        
        # Initially should not need maintenance
        assert context.calibration_status == CalibrationStatus.VALID


class TestHospitalContextBuilder:
    """Tests para HospitalContextBuilder."""
    
    @pytest.mark.asyncio
    async def test_build_hospital_context(self):
        """Test construir contexto hospitalario."""
        builder = HospitalContextBuilder()
        context = await builder.build(
            hospital_id="hospital_789",
            include_departments=True,
            include_capacity=True,
        )
        
        assert context.hospital_id == "hospital_789"
        assert context.department is not None


class TestClinicalContextAggregator:
    """Tests para ClinicalContextAggregator."""
    
    @pytest.mark.asyncio
    async def test_aggregate_contexts(self):
        """Test agregar contextos."""
        patient_builder = PatientContextBuilder()
        device_builder = DeviceContextBuilder()
        hospital_builder = HospitalContextBuilder()
        aggregator = ClinicalContextAggregator()
        
        patient_ctx = await patient_builder.build("patient_123")
        device_ctx = await device_builder.build("device_456")
        hospital_ctx = await hospital_builder.build("hospital_789")
        
        clinical_ctx = await aggregator.aggregate(
            patient_context=patient_ctx,
            device_context=device_ctx,
            hospital_context=hospital_ctx,
        )
        
        assert clinical_ctx.context_id is not None
        assert clinical_ctx.patient_context.patient_id == "patient_123"
        assert clinical_ctx.device_context.device_id == "device_456"
        assert clinical_ctx.hospital_context.hospital_id == "hospital_789"
    
    @pytest.mark.asyncio
    async def test_identify_risk_factors(self):
        """Test identificar factores de riesgo."""
        patient_ctx = PatientContext(
            patient_id="patient_123",
            medical_history=MedicalHistory(history_id="h1"),
            active_conditions=["hypertension"],  # Critical condition
            allergies=[],
            medications=[],
        )
        device_ctx = DeviceContext(
            device_id="device_456",
            device_type="infusion_pump",
            manufacturer="Baxter",
            model="Sigma",
            calibration_status=CalibrationStatus.EXPIRED,
        )
        hospital_ctx = HospitalContext(
            hospital_id="hospital_789",
            department=None,
        )
        
        aggregator = ClinicalContextAggregator()
        clinical_ctx = await aggregator.aggregate(patient_ctx, device_ctx, hospital_ctx)
        risk_factors = await aggregator.identify_risk_factors(clinical_ctx)
        
        assert len(risk_factors) > 0


class TestContextLifecycleManager:
    """Tests para ContextLifecycleManager."""
    
    @pytest.mark.asyncio
    async def test_create_context(self):
        """Test crear contexto."""
        manager = ContextLifecycleManager()
        context = await manager.create_context(
            session_id="session_1",
            patient_id="patient_123",
            device_id="device_456",
        )
        
        assert context.context_id is not None
        assert context.patient_context.patient_id == "patient_123"
    
    @pytest.mark.asyncio
    async def test_snapshot_context(self):
        """Test snapshot de contexto."""
        manager = ContextLifecycleManager()
        context = await manager.create_context(
            session_id="session_1",
            patient_id="patient_123",
            device_id="device_456",
        )
        
        snapshot = await manager.snapshot(context.context_id)
        assert snapshot.context_id == context.context_id


class TestClinicalContextAgent:
    """Tests para ClinicalContextAgent."""
    
    @pytest.mark.asyncio
    async def test_build_context_action(self):
        """Test acción build_context."""
        from core.PHASE_5.foundation import AgentTask
        
        agent = ClinicalContextAgent(agent_id="test_agent")
        
        task = AgentTask(
            task_id="task_1",
            agent_id="test_agent",
            task_type="clinical_context",
            input={
                "action": "build",
                "patient_id": "patient_123",
                "device_id": "device_456",
            },
        )
        
        result = await agent.execute(task)
        
        assert "context_id" in result
        assert result["patient_id"] == "patient_123"
