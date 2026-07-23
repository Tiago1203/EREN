"""
PHASE 5 - EPIC 2: Biomedical Agent

Agente especializado en Ingeniería Clínica.
Integra Equipment, Maintenance, Manufacturer, Standards y Calibration Experts.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Optional
import logging

logger = logging.getLogger(__name__)

# =============================================================================
# IMPORTS FROM PHASE 5 FOUNDATION
# =============================================================================

from core.PHASE_5.foundation import (
    BaseAgent,
    AgentType,
    AgentCapability,
    AgentCapabilityVO,
    AgentState,
)
from core.PHASE_5.foundation.domain import AgentTask, AgentResult

# =============================================================================
# IMPORTS FROM EPIC 2 DOMAIN
# =============================================================================

from core.PHASE_5.epic2_biomedical_agent.domain import (
    BiomedicalTask,
    BiomedicalTaskType,
    DeviceAssessment,
    AssessmentSeverity,
    AssessmentStatus,
    MaintenanceRecommendation,
    MaintenancePriority,
)

# =============================================================================
# IMPORTS FROM EPIC 2 EXPERTS
# =============================================================================

from core.PHASE_5.epic2_biomedical_agent.experts import (
    EquipmentExpert,
    MaintenanceExpert,
    ManufacturerExpert,
    StandardsExpert,
    CalibrationExpert,
)


# =============================================================================
# BIOMEDICAL AGENT CONFIG
# =============================================================================

@dataclass
class BiomedicalAgentConfig:
    """Configuración del Biomedical Agent."""
    # Experts
    enable_equipment_expert: bool = True
    enable_maintenance_expert: bool = True
    enable_manufacturer_expert: bool = True
    enable_standards_expert: bool = True
    enable_calibration_expert: bool = True
    
    # Comportamiento
    default_timeout_seconds: int = 300
    max_findings_per_assessment: int = 10
    
    # Calidad
    min_confidence_threshold: float = 0.7
    require_evidence: bool = True


# =============================================================================
# BIOMEDICAL AGENT
# =============================================================================

class BiomedicalAgent(BaseAgent):
    """
    Agente especializado en Ingeniería Clínica.
    
    Responsabilidades:
    - Analizar equipos médicos
    - Generar recomendaciones de mantenimiento
    - Verificar cumplimiento de normas (IEC, ISO)
    - Proporcionar información de fabricantes
    - Gestionar calibraciones
    
    Hereda de BaseAgent y utiliza los expertos especializados.
    """
    
    def __init__(
        self,
        agent_id: str,
        config: BiomedicalAgentConfig | None = None,
    ):
        super().__init__(
            agent_id=agent_id,
            agent_type=AgentType.BIOMEDICAL,
            name="Biomedical Agent",
            description="Agente especializado en Ingeniería Clínica",
        )
        
        self.config = config or BiomedicalAgentConfig()
        
        # Inicializar expertos
        self._equipment_expert = EquipmentExpert() if self.config.enable_equipment_expert else None
        self._maintenance_expert = MaintenanceExpert() if self.config.enable_maintenance_expert else None
        self._manufacturer_expert = ManufacturerExpert() if self.config.enable_manufacturer_expert else None
        self._standards_expert = StandardsExpert() if self.config.enable_standards_expert else None
        self._calibration_expert = CalibrationExpert() if self.config.enable_calibration_expert else None
        
        # Métricas
        self._assessments_completed = 0
        self._recommendations_generated = 0
    
    # =============================================================================
    # LIFECYCLE METHODS
    # =============================================================================
    
    async def initialize(self) -> None:
        """Inicializa el agente."""
        await super().initialize()
        logger.info(f"BiomedicalAgent {self.agent_id} initialized")
        logger.info(f"  - Equipment Expert: {self._equipment_expert is not None}")
        logger.info(f"  - Maintenance Expert: {self._maintenance_expert is not None}")
        logger.info(f"  - Manufacturer Expert: {self._manufacturer_expert is not None}")
        logger.info(f"  - Standards Expert: {self._standards_expert is not None}")
        logger.info(f"  - Calibration Expert: {self._calibration_expert is not None}")
    
    async def shutdown(self) -> None:
        """Detiene el agente."""
        await super().shutdown()
        logger.info(f"BiomedicalAgent {self.agent_id} shutdown")
    
    # =============================================================================
    # CORE METHODS
    # =============================================================================
    
    async def execute(self, task: AgentTask) -> AgentResult:
        """Ejecuta una tarea biomédica."""
        from datetime import UTC, datetime
        
        start_time = datetime.now(UTC)
        
        try:
            # Crear tarea biomédica
            biomedical_task = self._create_biomedical_task(task)
            
            # Procesar según tipo
            if biomedical_task.task_type == BiomedicalTaskType.DEVICE_ANALYSIS:
                result = await self._analyze_device(biomedical_task)
            elif biomedical_task.task_type == BiomedicalTaskType.MAINTENANCE_PLANNING:
                result = await self._plan_maintenance(biomedical_task)
            elif biomedical_task.task_type == BiomedicalTaskType.CALIBRATION_CHECK:
                result = await self._check_calibration(biomedical_task)
            elif biomedical_task.task_type == BiomedicalTaskType.COMPLIANCE_AUDIT:
                result = await self._audit_compliance(biomedical_task)
            elif biomedical_task.task_type == BiomedicalTaskType.RISK_ASSESSMENT:
                result = await self._assess_risk(biomedical_task)
            else:
                result = await self._general_analysis(biomedical_task)
            
            end_time = datetime.now(UTC)
            execution_time_ms = int((end_time - start_time).total_seconds() * 1000)
            
            self._assessments_completed += 1
            
            return AgentResult(
                task_id=task.task_id,
                agent_id=self.agent_id,
                success=True,
                output=result,
                execution_time_ms=execution_time_ms,
                confidence=0.85,
            )
            
        except Exception as e:
            logger.error(f"BiomedicalAgent execution failed: {e}")
            return AgentResult(
                task_id=task.task_id,
                agent_id=self.agent_id,
                success=False,
                error=str(e),
                confidence=0.0,
            )
    
    # =============================================================================
    # TASK PROCESSING METHODS
    # =============================================================================
    
    async def _analyze_device(self, task: BiomedicalTask) -> dict:
        """Analiza un dispositivo médico."""
        result = {
            "task_type": "device_analysis",
            "device_id": task.device_id,
            "assessments": [],
            "recommendations": [],
        }
        
        # 1. Análisis de equipo
        if self._equipment_expert:
            analysis = await self._equipment_expert.analyze_device(
                task.device_id,
                task.context,
            )
            result["equipment_analysis"] = {
                "specifications": analysis.specifications,
                "condition": analysis.condition_assessment,
                "expected_lifetime": analysis.expected_lifetime_years,
                "confidence": analysis.confidence,
            }
            
            # Agregar como assessment
            assessment = DeviceAssessment(
                assessment_id="",
                device_id=task.device_id,
                assessment_type="equipment_analysis",
                description=f"Analysis of {task.device_name}",
                severity=AssessmentSeverity.INFO,
            )
            result["assessments"].append({
                "type": "equipment",
                "findings": analysis.specifications,
            })
        
        # 2. Análisis de mantenimiento
        if self._maintenance_expert:
            recommendations = await self._maintenance_expert.generate_recommendations(
                task.device_id,
                task.device_type,
                age_years=task.context.get("age_years", 0),
                usage_hours=task.context.get("usage_hours", 0),
            )
            
            for rec in recommendations:
                result["recommendations"].append({
                    "type": rec.maintenance_type.value,
                    "priority": rec.priority.value,
                    "title": rec.title,
                    "description": rec.description,
                })
                self._recommendations_generated += 1
        
        # 3. Análisis de calibración
        if self._calibration_expert:
            calibration_status = await self._calibration_expert.get_calibration_status(
                task.device_id
            )
            result["calibration_status"] = calibration_status
            
            if calibration_status.get("is_overdue"):
                result["assessments"].append({
                    "type": "calibration",
                    "severity": AssessmentSeverity.HIGH.value,
                    "description": "Calibration overdue",
                })
        
        return result
    
    async def _plan_maintenance(self, task: BiomedicalTask) -> dict:
        """Planifica mantenimiento para un dispositivo."""
        result = {
            "task_type": "maintenance_planning",
            "device_id": task.device_id,
            "recommendations": [],
            "schedule": [],
        }
        
        if self._maintenance_expert:
            recommendations = await self._maintenance_expert.generate_recommendations(
                task.device_id,
                task.device_type,
                age_years=task.context.get("age_years", 0),
                usage_hours=task.context.get("usage_hours", 0),
            )
            
            for rec in recommendations:
                result["recommendations"].append({
                    "id": rec.recommendation_id,
                    "type": rec.maintenance_type.value,
                    "priority": rec.priority.value,
                    "title": rec.title,
                    "description": rec.description,
                    "estimated_duration_minutes": rec.estimated_duration_minutes,
                    "frequency_days": rec.frequency_days,
                    "estimated_cost": rec.total_cost,
                    "standards": rec.standards,
                })
                self._recommendations_generated += 1
        
        return result
    
    async def _check_calibration(self, task: BiomedicalTask) -> dict:
        """Verifica calibración de un dispositivo."""
        result = {
            "task_type": "calibration_check",
            "device_id": task.device_id,
            "calibration_status": {},
            "recommendations": [],
        }
        
        if self._calibration_expert:
            status = await self._calibration_expert.get_calibration_status(
                task.device_id
            )
            result["calibration_status"] = status
            
            if status.get("is_overdue"):
                result["recommendations"].append({
                    "type": "calibration",
                    "priority": MaintenancePriority.URGENT.value,
                    "description": "Schedule calibration immediately",
                })
        
        return result
    
    async def _audit_compliance(self, task: BiomedicalTask) -> dict:
        """Audita cumplimiento de normas."""
        result = {
            "task_type": "compliance_audit",
            "device_id": task.device_id,
            "standards": [],
            "compliance_status": {},
            "violations": [],
        }
        
        if self._standards_expert:
            standards = await self._standards_expert.find_applicable_standards(
                task.device_type,
                task.context.get("device_class", "Class II"),
            )
            
            for std in standards:
                compliance = await self._standards_expert.check_compliance(
                    std.standard_id,
                    task.context,
                )
                
                result["standards"].append({
                    "id": std.standard_id,
                    "title": std.title,
                    "version": std.version,
                    "is_mandatory": std.is_mandatory,
                    "compliant": compliance.get("compliant", False),
                })
                
                if not compliance.get("compliant"):
                    result["violations"].extend(compliance.get("issues", []))
        
        return result
    
    async def _assess_risk(self, task: BiomedicalTask) -> dict:
        """Evalúa riesgo de un dispositivo."""
        result = {
            "task_type": "risk_assessment",
            "device_id": task.device_id,
            "risk_level": 0.0,
            "risk_factors": [],
            "recommendations": [],
        }
        
        # Análisis de equipo
        if self._equipment_expert:
            failures = await self._equipment_expert.predict_failures(
                task.device_id,
                usage_hours=task.context.get("usage_hours", 0),
                age_years=task.context.get("age_years", 0),
            )
            
            for failure in failures:
                result["risk_factors"].append({
                    "type": failure["type"],
                    "probability": failure["probability"],
                    "recommended_action": failure["recommended_action"],
                })
            
            # Calcular nivel de riesgo
            if failures:
                result["risk_level"] = max(f["probability"] for f in failures)
        
        # Estado de calibración
        if self._calibration_expert:
            status = await self._calibration_expert.get_calibration_status(task.device_id)
            if status.get("is_overdue"):
                result["risk_factors"].append({
                    "type": "calibration_overdue",
                    "probability": 0.8,
                    "recommended_action": "Immediate calibration required",
                })
                result["risk_level"] = max(result["risk_level"], 0.8)
        
        return result
    
    async def _general_analysis(self, task: BiomedicalTask) -> dict:
        """Análisis general combinando todos los expertos."""
        result = {
            "task_type": "general_analysis",
            "device_id": task.device_id,
            "device_type": task.device_type,
            "summary": {},
            "assessments": [],
            "recommendations": [],
        }
        
        # Ejecutar análisis de dispositivo
        device_result = await self._analyze_device(task)
        result["assessments"] = device_result.get("assessments", [])
        result["recommendations"] = device_result.get("recommendations", [])
        
        # Generar resumen
        result["summary"] = {
            "assessments_count": len(result["assessments"]),
            "recommendations_count": len(result["recommendations"]),
            "high_priority_count": sum(
                1 for r in result["recommendations"]
                if r.get("priority") in ["HIGH", "URGENT"]
            ),
        }
        
        return result
    
    # =============================================================================
    # HELPER METHODS
    # =============================================================================
    
    def _create_biomedical_task(self, task: AgentTask) -> BiomedicalTask:
        """Convierte AgentTask a BiomedicalTask."""
        input_data = task.input_data
        
        # Determinar tipo de tarea (prioridad: task.task_type > input_data.task_type)
        task_type_str = task.task_type  # Puede ser "device_analysis", etc.
        if not task_type_str:
            task_type_str = input_data.get("task_type", "general_analysis")
        
        try:
            task_type = BiomedicalTaskType(task_type_str)
        except ValueError:
            task_type = BiomedicalTaskType.MANUAL_REVIEW
        
        return BiomedicalTask(
            task_id=task.task_id,
            task_type=task_type,
            device_id=input_data.get("device_id"),
            device_name=input_data.get("device_name", ""),
            device_type=input_data.get("device_type", ""),
            manufacturer=input_data.get("manufacturer", ""),
            model=input_data.get("model", ""),
            serial_number=input_data.get("serial_number", ""),
            description=input_data.get("description", task.description),
            user_query=input_data.get("query", ""),
            context=input_data.get("context", {}),
            priority=self._parse_priority(input_data.get("priority")),
            timeout_seconds=task.timeout_seconds,
        )
    
    def _parse_priority(self, value: Any) -> MaintenancePriority:
        """Parse priority from string or return default."""
        if value is None:
            return MaintenancePriority.MEDIUM
        if isinstance(value, MaintenancePriority):
            return value
        try:
            # Try direct conversion
            return MaintenancePriority(value)
        except ValueError:
            # Try lowercase conversion
            try:
                return MaintenancePriority(value.lower())
            except (ValueError, AttributeError):
                return MaintenancePriority.MEDIUM
    
    # =============================================================================
    # METRICS
    # =============================================================================
    
    def get_metrics(self) -> dict:
        """Obtiene métricas del agente."""
        return {
            "assessments_completed": self._assessments_completed,
            "recommendations_generated": self._recommendations_generated,
            "experts_enabled": {
                "equipment": self._equipment_expert is not None,
                "maintenance": self._maintenance_expert is not None,
                "manufacturer": self._manufacturer_expert is not None,
                "standards": self._standards_expert is not None,
                "calibration": self._calibration_expert is not None,
            },
        }


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "BiomedicalAgent",
    "BiomedicalAgentConfig",
]
