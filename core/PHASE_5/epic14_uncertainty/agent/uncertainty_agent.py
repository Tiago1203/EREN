"""
UncertaintyAgent: Agente principal de cuantificación de incertidumbre
"""

from typing import Optional

from core.PHASE_5.foundation import BaseAgent, AgentType, AgentCapability, AgentTask
from core.PHASE_5.epic14_uncertainty.domain import (
    Uncertainty,
    ConfidenceLevel,
    UncertaintySource,
    UncertaintyStatement,
    UncertaintyType,
    ProbabilityDistribution,
    UncertaintyConfig,
    AudienceType,
)


class UncertaintyAgent(BaseAgent):
    """Agente de cuantificación de incertidumbre."""
    
    def __init__(
        self,
        agent_id: str,
        config: Optional[UncertaintyConfig] = None,
    ):
        """Inicializa el agente."""
        super().__init__(
            agent_id=agent_id,
            agent_type=AgentType.DIAGNOSTIC,
            capabilities=[
                AgentCapability.DIAGNOSE,
                AgentCapability.VALIDATE,
            ],
        )
        self.config = config or UncertaintyConfig()
    
    async def _execute_impl(self, task: AgentTask) -> dict:
        """Implementa la ejecución del agente."""
        action = task.input.get("action", "quantify")
        
        if action == "quantify":
            return await self._quantify_uncertainty(task.input)
        elif action == "calibrate":
            return await self._calibrate_confidence(task.input)
        elif action == "propagate":
            return await self._propagate_uncertainty(task.input)
        elif action == "communicate":
            return await self._communicate_uncertainty(task.input)
        elif action == "detect_sources":
            return await self._detect_sources(task.input)
        else:
            return {"error": f"Unknown action: {action}"}
    
    async def _quantify_uncertainty(self, input_data: dict) -> dict:
        """Cuantifica incertidumbre."""
        value = input_data.get("value")
        uncertainty_type = input_data.get("uncertainty_type", "epistemic")
        evidence_ids = input_data.get("evidence_ids", [])
        
        if value is None:
            return {"error": "value is required"}
        
        # Crear distribución
        distribution = ProbabilityDistribution(
            distribution_type="normal",
            parameters={},
            mean=value,
            std_dev=value * 0.2,
        )
        
        # Crear incertidumbre
        uncertainty = Uncertainty(
            uncertainty_id=f"unc_{value}_{uncertainty_type}",
            uncertainty_type=UncertaintyType(uncertainty_type),
            value=value,
            distribution=distribution,
            sources=[],
        )
        
        # Agregar fuentes basadas en evidencia
        for evidence_id in evidence_ids[:3]:
            uncertainty.sources.append(UncertaintySource(
                source_id=f"src_{evidence_id}",
                source_type=UncertaintyType(uncertainty_type),
                description=f"Based on evidence: {evidence_id}",
                estimated_impact=0.1,
                mitigatable=True,
            ))
        
        return {
            "uncertainty_id": uncertainty.uncertainty_id,
            "uncertainty_type": uncertainty.uncertainty_type.value,
            "value": uncertainty.value,
            "confidence_interval": uncertainty.get_confidence_interval(),
            "std_deviation": uncertainty.get_std_deviation(),
            "sources_count": len(uncertainty.sources),
        }
    
    async def _calibrate_confidence(self, input_data: dict) -> dict:
        """Calibra confianza."""
        confidence_level = input_data.get("confidence_level", 0.8)
        predictions = input_data.get("predictions", [])
        outcomes = input_data.get("outcomes", [])
        
        if len(predictions) != len(outcomes):
            return {"error": "predictions and outcomes must have same length"}
        
        # Calcular calibration error
        correct = sum(1 for p, o in zip(predictions, outcomes) if (p > 0.5) == o)
        calibration_error = 1 - (correct / len(outcomes)) if outcomes else 0.0
        
        confidence = ConfidenceLevel(
            level=confidence_level,
            is_calibrated=True,
            calibration_error=calibration_error,
            based_on=[f"prediction_{i}" for i in range(len(predictions))],
        )
        
        return {
            "confidence_level": confidence.level,
            "is_calibrated": confidence.is_calibrated,
            "calibration_error": confidence.calibration_error,
            "is_high_confidence": confidence.is_high_confidence(),
            "requires_qualification": confidence.requires_qualification(),
        }
    
    async def _propagate_uncertainty(self, input_data: dict) -> dict:
        """Propaga incertidumbre."""
        uncertainties = input_data.get("uncertainties", [])
        
        if not uncertainties:
            return {"error": "uncertainties is required"}
        
        # Calcular propagated uncertainty (simplified)
        total_value = sum(u.get("value", 0) for u in uncertainties) / len(uncertainties)
        
        return {
            "propagated_uncertainty": total_value,
            "input_count": len(uncertainties),
            "method": "average",
        }
    
    async def _communicate_uncertainty(self, input_data: dict) -> dict:
        """Comunica incertidumbre."""
        uncertainty_id = input_data.get("uncertainty_id")
        probability = input_data.get("probability")
        confidence_interval = input_data.get("confidence_interval")
        audience = input_data.get("audience", "clinical")
        
        statement = UncertaintyStatement(
            statement=f"Uncertainty for {uncertainty_id}",
            probability=probability,
            confidence_interval=tuple(confidence_interval) if confidence_interval else None,
            caveats=["Based on available evidence", "Further validation needed"],
            audience=AudienceType(audience),
        )
        
        return {
            "statement": statement.format_for_clinical(),
            "audience": statement.audience.value,
            "probability": statement.probability,
            "confidence_interval": statement.confidence_interval,
        }
    
    async def _detect_sources(self, input_data: dict) -> dict:
        """Detecta fuentes de incertidumbre."""
        decision_type = input_data.get("decision_type", "diagnostic")
        
        # Detectar fuentes basadas en tipo de decisión
        sources = []
        
        if decision_type == "diagnostic":
            sources.append({
                "type": "epistemic",
                "description": "Limited diagnostic evidence",
                "impact": 0.3,
            })
            sources.append({
                "type": "aleatory",
                "description": "Patient variability",
                "impact": 0.2,
            })
        elif decision_type == "treatment":
            sources.append({
                "type": "epistemic",
                "description": "Treatment response uncertainty",
                "impact": 0.4,
            })
        
        return {
            "sources": sources,
            "total_sources": len(sources),
        }
