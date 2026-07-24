"""
ClinicalContextAggregator: Agregador de contexto clínico
"""

from datetime import datetime

from core.PHASE_5.epic12_clinical_context.domain import (
    ClinicalContext,
    PatientContext,
    DeviceContext,
    HospitalContext,
    ClinicalTimeline,
    RiskFactor,
    RiskLevel,
    ContextMetadata,
)


class ClinicalContextAggregator:
    """Agregador de contexto clínico."""
    
    async def aggregate(
        self,
        patient_context: PatientContext,
        device_context: DeviceContext,
        hospital_context: HospitalContext,
    ) -> ClinicalContext:
        """
        Agrega contextos en contexto clínico.
        
        Args:
            patient_context: Contexto de paciente
            device_context: Contexto de dispositivo
            hospital_context: Contexto hospitalario
        
        Returns:
            ClinicalContext unificado
        """
        context_id = f"ctx_{patient_context.patient_id}_{device_context.device_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        metadata = ContextMetadata(
            created_at=datetime.now(),
            updated_at=datetime.now(),
            created_by="system",
            session_id=f"session_{datetime.now().strftime('%Y%m%d')}",
            version=1,
        )
        
        clinical_context = ClinicalContext(
            context_id=context_id,
            patient_context=patient_context,
            device_context=device_context,
            hospital_context=hospital_context,
            timeline=ClinicalTimeline(events=[]),
            risk_factors=[],
            metadata=metadata,
        )
        
        # Identificar factores de riesgo
        risk_factors = await self.identify_risk_factors(clinical_context)
        clinical_context.risk_factors = risk_factors
        
        return clinical_context
    
    async def enrich_with_timeline(
        self,
        context: ClinicalContext,
    ) -> ClinicalContext:
        """Enriquece con línea de tiempo."""
        timeline = ClinicalTimeline()
        
        # Agregar eventos de paciente
        if context.patient_context.medical_history:
            timeline.add_event({
                "type": "medical_history",
                "patient_id": context.patient_context.patient_id,
                "timestamp": datetime.now(),
            })
        
        # Agregar eventos de dispositivo
        for incident in context.device_context.incident_history:
            timeline.add_event({
                "type": "incident",
                "device_id": context.device_context.device_id,
                "incident_id": incident.incident_id,
                "timestamp": incident.date,
            })
        
        context.timeline = timeline
        return context
    
    async def identify_risk_factors(
        self,
        context: ClinicalContext,
    ) -> list[RiskFactor]:
        """Identifica factores de riesgo."""
        risk_factors = []
        
        # Verificar condiciones críticas del paciente
        critical_conditions = context.patient_context.get_critical_conditions()
        for condition in critical_conditions:
            risk_factors.append(RiskFactor(
                factor_id=f"rf_patient_{condition}",
                description=f"Patient has critical condition: {condition}",
                level=RiskLevel.HIGH,
                source="patient_context",
            ))
        
        # Verificar estado de calibración del dispositivo
        if context.device_context.calibration_status.value == "expired":
            risk_factors.append(RiskFactor(
                factor_id="rf_device_calibration",
                description="Device calibration expired",
                level=RiskLevel.CRITICAL,
                source="device_context",
            ))
        
        # Verificar disponibilidad de recursos
        constraints = context.hospital_context.get_resource_constraints()
        for constraint in constraints:
            risk_factors.append(RiskFactor(
                factor_id=f"rf_hospital_{len(risk_factors)}",
                description=constraint,
                level=RiskLevel.MEDIUM,
                source="hospital_context",
            ))
        
        return risk_factors
