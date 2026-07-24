"""
PatientContextBuilder: Constructor de contexto de paciente
"""

from datetime import datetime
from typing import Optional

from core.PHASE_5.epic12_clinical_context.domain import (
    PatientContext,
    MedicalHistory,
    PatientDemographics,
)


class PatientContextBuilder:
    """Constructor de contexto de paciente."""
    
    async def build(
        self,
        patient_id: str,
        include_history: bool = True,
        include_conditions: bool = True,
    ) -> PatientContext:
        """
        Construye contexto de paciente.
        
        Args:
            patient_id: ID del paciente
            include_history: Incluir historial médico
            include_conditions: Incluir condiciones activas
        
        Returns:
            PatientContext construido
        """
        # En implementación real, esto consultaría FASE 1/Knowledge
        medical_history = MedicalHistory(
            history_id=f"history_{patient_id}",
            conditions=[],
            allergies=[],
            medications=[],
            procedures=[],
        ) if include_history else None
        
        patient_context = PatientContext(
            patient_id=patient_id,
            medical_history=medical_history,
            active_conditions=[] if include_conditions else None,
            allergies=[],
            medications=[],
            demographics=None,
        )
        
        return patient_context
    
    async def get_medical_history(
        self,
        patient_id: str,
    ) -> MedicalHistory:
        """Obtiene historial médico."""
        return MedicalHistory(
            history_id=f"history_{patient_id}",
            conditions=["hypertension", "hyperlipidemia"],
            allergies=["penicillin"],
            medications=["lisinopril 10mg", "atorvastatin 20mg"],
            procedures=["coronary angiography 2023"],
        )
    
    async def get_active_conditions(
        self,
        patient_id: str,
    ) -> list[str]:
        """Obtiene condiciones activas."""
        return ["hypertension", "hyperlipidemia"]
