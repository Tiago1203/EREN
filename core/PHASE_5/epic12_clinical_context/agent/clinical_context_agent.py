"""
ClinicalContextAgent: Agente principal de construcción de contexto clínico
"""

from typing import Optional

from core.PHASE_5.foundation import BaseAgent, AgentType, AgentCapability, AgentTask, AgentResult
from core.PHASE_5.epic12_clinical_context.domain import (
    ClinicalContext,
    PatientContext,
    DeviceContext,
    HospitalContext,
    ClinicalContextConfig,
)
from core.PHASE_5.epic12_clinical_context.lifecycle import ContextLifecycleManager


class ClinicalContextAgent(BaseAgent):
    """Agente de construcción de contexto clínico."""
    
    def __init__(
        self,
        agent_id: str,
        config: Optional[ClinicalContextConfig] = None,
    ):
        """Inicializa el agente."""
        super().__init__(
            agent_id=agent_id,
            agent_type=AgentType.KNOWLEDGE,
            capabilities=[
                AgentCapability.DIAGNOSE,
                AgentCapability.RESEARCH,
            ],
        )
        self.config = config or ClinicalContextConfig()
        self.lifecycle_manager = ContextLifecycleManager(self.config)
    
    async def _execute_impl(self, task: AgentTask) -> dict:
        """Implementa la ejecución del agente."""
        action = task.input.get("action", "build")
        
        if action == "build":
            return await self._build_context(task.input)
        elif action == "patient":
            return await self._build_patient_context(task.input)
        elif action == "device":
            return await self._build_device_context(task.input)
        elif action == "hospital":
            return await self._build_hospital_context(task.input)
        elif action == "aggregate":
            return await self._aggregate_contexts(task.input)
        elif action == "snapshot":
            return await self._snapshot_context(task.input)
        else:
            return {"error": f"Unknown action: {action}"}
    
    async def _build_context(self, input_data: dict) -> dict:
        """Construye contexto clínico completo."""
        patient_id = input_data.get("patient_id")
        device_id = input_data.get("device_id")
        hospital_id = input_data.get("hospital_id", "default_hospital")
        session_id = input_data.get("session_id", "default_session")
        
        if not patient_id or not device_id:
            return {"error": "patient_id and device_id are required"}
        
        context = await self.lifecycle_manager.create_context(
            session_id=session_id,
            patient_id=patient_id,
            device_id=device_id,
        )
        
        return {
            "context_id": context.context_id,
            "patient_id": context.patient_context.patient_id,
            "device_id": context.device_context.device_id,
            "risk_level": context.get_risk_level().value,
            "risk_factors": [
                {
                    "id": rf.factor_id,
                    "description": rf.description,
                    "level": rf.level.value,
                }
                for rf in context.risk_factors
            ],
        }
    
    async def _build_patient_context(self, input_data: dict) -> dict:
        """Construye solo contexto de paciente."""
        from core.PHASE_5.epic12_clinical_context.builders import PatientContextBuilder
        
        patient_id = input_data.get("patient_id")
        if not patient_id:
            return {"error": "patient_id is required"}
        
        builder = PatientContextBuilder()
        context = await builder.build(
            patient_id=patient_id,
            include_history=input_data.get("include_history", True),
            include_conditions=input_data.get("include_conditions", True),
        )
        
        return {
            "patient_id": context.patient_id,
            "active_conditions": context.active_conditions,
            "allergies": context.allergies,
            "medications": context.medications,
        }
    
    async def _build_device_context(self, input_data: dict) -> dict:
        """Construye solo contexto de dispositivo."""
        from core.PHASE_5.epic12_clinical_context.builders import DeviceContextBuilder
        
        device_id = input_data.get("device_id")
        if not device_id:
            return {"error": "device_id is required"}
        
        builder = DeviceContextBuilder()
        context = await builder.build(
            device_id=device_id,
            include_maintenance=input_data.get("include_maintenance", True),
            include_incidents=input_data.get("include_incidents", True),
        )
        
        return {
            "device_id": context.device_id,
            "device_type": context.device_type,
            "manufacturer": context.manufacturer,
            "model": context.model,
            "calibration_status": context.calibration_status.value,
            "needs_maintenance": context.needs_maintenance(),
        }
    
    async def _build_hospital_context(self, input_data: dict) -> dict:
        """Construye solo contexto hospitalario."""
        from core.PHASE_5.epic12_clinical_context.builders import HospitalContextBuilder
        
        hospital_id = input_data.get("hospital_id", "default_hospital")
        
        builder = HospitalContextBuilder()
        context = await builder.build(
            hospital_id=hospital_id,
            include_departments=input_data.get("include_departments", True),
            include_capacity=input_data.get("include_capacity", True),
        )
        
        return {
            "hospital_id": context.hospital_id,
            "department": context.department.name if context.department else None,
            "resource_constraints": context.get_resource_constraints(),
        }
    
    async def _aggregate_contexts(self, input_data: dict) -> dict:
        """Agrega múltiples contextos."""
        from core.PHASE_5.epic12_clinical_context.builders import (
            PatientContextBuilder,
            DeviceContextBuilder,
            HospitalContextBuilder,
            ClinicalContextAggregator,
        )
        
        patient_id = input_data.get("patient_id")
        device_id = input_data.get("device_id")
        
        if not patient_id or not device_id:
            return {"error": "patient_id and device_id are required"}
        
        # Construir contextos
        patient_builder = PatientContextBuilder()
        patient_context = await patient_builder.build(patient_id)
        
        device_builder = DeviceContextBuilder()
        device_context = await device_builder.build(device_id)
        
        hospital_builder = HospitalContextBuilder()
        hospital_context = await hospital_builder.build("default_hospital")
        
        # Agregar
        aggregator = ClinicalContextAggregator()
        context = await aggregator.aggregate(
            patient_context=patient_context,
            device_context=device_context,
            hospital_context=hospital_context,
        )
        
        return {
            "context_id": context.context_id,
            "risk_level": context.get_risk_level().value,
        }
    
    async def _snapshot_context(self, input_data: dict) -> dict:
        """Guarda snapshot de contexto."""
        context_id = input_data.get("context_id")
        if not context_id:
            return {"error": "context_id is required"}
        
        snapshot = await self.lifecycle_manager.snapshot(context_id)
        
        return {
            "snapshot_id": snapshot.context_id,
            "message": "Snapshot created successfully",
        }
