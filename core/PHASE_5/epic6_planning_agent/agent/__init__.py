"""
PHASE 5 - EPIC 6: Planning Agent

Agente dedicado a generar planes de acción.
Convierte decisiones clínicas en planes ejecutables.
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
# IMPORTS FROM EPIC 6 DOMAIN
# =============================================================================

from core.PHASE_5.epic6_planning_agent.domain import (
    ActionPlan,
    ActionPriority,
    ClinicalPlan,
    ClinicalPhase,
    ExecutionTask,
)

# =============================================================================
# IMPORTS FROM EPIC 6 ENGINES
# =============================================================================

from core.PHASE_5.epic6_planning_agent.engines import (
    ActionPlanner,
    ScheduleGenerator,
    TaskGenerator,
    RiskPlanner,
)


# =============================================================================
# PLANNING AGENT CONFIG
# =============================================================================

@dataclass
class PlanningAgentConfig:
    """Configuración del Planning Agent."""
    # Engines
    enable_action_planner: bool = True
    enable_schedule_generator: bool = True
    enable_task_generator: bool = True
    enable_risk_planner: bool = True
    
    # Comportamiento
    default_priority: str = "medium"
    max_actions_per_plan: int = 50
    
    # Integración
    integrate_with_orchestrator: bool = True


# =============================================================================
# PLANNING AGENT
# =============================================================================

class PlanningAgent(BaseAgent):
    """
    Agente dedicado a generar planes de acción.
    
    Responsabilidades:
    - Convertir decisiones clínicas en planes ejecutables
    - Generar horarios de ejecución
    - Descomponer acciones en tareas
    - Evaluar y mitigar riesgos
    - Crear planes clínicos estructurados
    
    Hereda de BaseAgent y utiliza los motores especializados.
    """
    
    def __init__(
        self,
        agent_id: str,
        config: PlanningAgentConfig | None = None,
    ):
        super().__init__(
            agent_id=agent_id,
            agent_type=AgentType.PLANNING,
            name="Planning Agent",
            description="Agente dedicado a generar planes de acción",
        )
        
        self.config = config or PlanningAgentConfig()
        
        # Inicializar motores
        self._action_planner = ActionPlanner() if self.config.enable_action_planner else None
        self._schedule_generator = ScheduleGenerator() if self.config.enable_schedule_generator else None
        self._task_generator = TaskGenerator() if self.config.enable_task_generator else None
        self._risk_planner = RiskPlanner() if self.config.enable_risk_planner else None
        
        # Métricas
        self._plans_created = 0
        self._tasks_generated = 0
    
    # =============================================================================
    # LIFECYCLE METHODS
    # =============================================================================
    
    async def initialize(self) -> None:
        """Inicializa el agente."""
        await super().initialize()
        logger.info(f"PlanningAgent {self.agent_id} initialized")
        logger.info(f"  - Action Planner: {self._action_planner is not None}")
        logger.info(f"  - Schedule Generator: {self._schedule_generator is not None}")
        logger.info(f"  - Task Generator: {self._task_generator is not None}")
        logger.info(f"  - Risk Planner: {self._risk_planner is not None}")
    
    async def shutdown(self) -> None:
        """Detiene el agente."""
        await super().shutdown()
        logger.info(f"PlanningAgent {self.agent_id} shutdown")
    
    # =============================================================================
    # CORE METHODS
    # =============================================================================
    
    async def execute(self, task: AgentTask) -> AgentResult:
        """Ejecuta una tarea de planificación."""
        from datetime import UTC, datetime
        
        start_time = datetime.now(UTC)
        
        try:
            # Obtener parámetros de entrada
            input_data = task.input_data
            plan_type = input_data.get("plan_type", "action")
            
            # Procesar según tipo
            if plan_type == "action":
                result = await self._create_action_plan(input_data)
            elif plan_type == "clinical":
                result = await self._create_clinical_plan(input_data)
            elif plan_type == "schedule":
                result = await self._create_schedule(input_data)
            elif plan_type == "risk":
                result = await self._assess_risks(input_data)
            else:
                result = await self._create_generic_plan(input_data)
            
            self._plans_created += 1
            
            end_time = datetime.now(UTC)
            execution_time_ms = int((end_time - start_time).total_seconds() * 1000)
            
            return AgentResult(
                task_id=task.task_id,
                agent_id=self.agent_id,
                success=True,
                output=result,
                execution_time_ms=execution_time_ms,
                confidence=0.90,
            )
            
        except Exception as e:
            logger.error(f"PlanningAgent execution failed: {e}")
            return AgentResult(
                task_id=task.task_id,
                agent_id=self.agent_id,
                success=False,
                error=str(e),
                confidence=0.0,
            )
    
    # =============================================================================
    # PLANNING METHODS
    # =============================================================================
    
    async def _create_action_plan(self, input_data: dict) -> dict:
        """Crea un plan de acción."""
        result = {
            "plan_type": "action",
            "context_id": input_data.get("context_id", ""),
            "plan": {},
            "schedule": {},
            "risks": {},
        }
        
        # Extraer objetivos
        objectives = input_data.get("objectives", [])
        context_id = input_data.get("context_id", "")
        constraints = input_data.get("constraints", {})
        
        # Crear plan
        if self._action_planner:
            plan_result = await self._action_planner.create_plan(
                context_id=context_id,
                objectives=objectives,
                constraints=constraints,
            )
            
            result["plan"] = {
                "plan_id": plan_result.plan.plan_id if plan_result.plan else "",
                "actions_count": plan_result.actions_count,
                "critical_count": plan_result.critical_count,
                "estimated_duration_minutes": plan_result.estimated_duration_minutes,
                "progress_percentage": plan_result.plan.get_progress_percentage() if plan_result.plan else 0,
            }
            
            # Generar schedule
            if self._schedule_generator and plan_result.plan:
                schedule_result = await self._schedule_generator.generate_schedule(
                    plan_result.plan,
                )
                result["schedule"] = {
                    "tasks_count": schedule_result.total_tasks,
                    "total_duration_minutes": schedule_result.total_duration_minutes,
                }
            
            # Evaluar riesgos
            if self._risk_planner and plan_result.plan:
                risk_result = await self._risk_planner.assess_risks(plan_result.plan)
                result["risks"] = {
                    "risk_level": risk_result.risk_level,
                    "risk_score": risk_result.overall_risk_score,
                    "risks_count": len(risk_result.risks),
                    "mitigations": risk_result.mitigations,
                }
        
        return result
    
    async def _create_clinical_plan(self, input_data: dict) -> dict:
        """Crea un plan clínico."""
        result = {
            "plan_type": "clinical",
            "patient_id": input_data.get("patient_id", ""),
            "plan": {},
        }
        
        # Extraer datos
        phases_data = input_data.get("phases", [])
        
        # Crear plan
        clinical_plan = ClinicalPlan(
            patient_id=input_data.get("patient_id", ""),
            title=input_data.get("title", "Clinical Plan"),
        )
        
        # Agregar fases
        for phase_data in phases_data:
            from core.PHASE_5.epic6_planning_agent.domain import ClinicalPhaseItem
            phase = ClinicalPhaseItem(
                phase=ClinicalPhase(phase_data.get("phase", "assessment")),
                objectives=phase_data.get("objectives", []),
                activities=phase_data.get("activities", []),
                estimated_duration_minutes=phase_data.get("duration", 60),
                order=phase_data.get("order", 0),
            )
            clinical_plan.add_phase(phase)
        
        result["plan"] = {
            "plan_id": clinical_plan.plan_id,
            "phases_count": len(clinical_plan.phases),
            "progress_percentage": clinical_plan.progress_percentage,
            "estimated_duration_minutes": sum(p.estimated_duration_minutes for p in clinical_plan.phases),
        }
        
        return result
    
    async def _create_schedule(self, input_data: dict) -> dict:
        """Crea un horario de ejecución."""
        result = {
            "plan_type": "schedule",
            "schedule": {},
        }
        
        # Placeholder para schedule
        result["schedule"] = {
            "tasks_count": 5,
            "total_duration_minutes": 240,
        }
        
        return result
    
    async def _assess_risks(self, input_data: dict) -> dict:
        """Evalúa riesgos de un plan."""
        result = {
            "plan_type": "risk",
            "risks": {},
        }
        
        # Placeholder
        result["risks"] = {
            "risk_level": "medium",
            "risk_score": 0.45,
            "mitigations": ["Monitor closely", "Have backup plan"],
        }
        
        return result
    
    async def _create_generic_plan(self, input_data: dict) -> dict:
        """Crea un plan genérico."""
        return {
            "plan_type": "generic",
            "objectives": input_data.get("objectives", []),
        }
    
    # =============================================================================
    # HELPER METHODS
    # =============================================================================
    
    def get_plan_summary(self, plan: ActionPlan) -> dict:
        """Obtiene resumen del plan."""
        return {
            "plan_id": plan.plan_id,
            "total_actions": plan.total_actions,
            "completed_actions": plan.completed_actions,
            "critical_actions": plan.critical_actions,
            "progress_percentage": plan.get_progress_percentage(),
            "estimated_completion": plan.estimated_completion.isoformat() if plan.estimated_completion else None,
        }
    
    # =============================================================================
    # METRICS
    # =============================================================================
    
    def get_metrics(self) -> dict:
        """Obtiene métricas del agente."""
        return {
            "plans_created": self._plans_created,
            "tasks_generated": self._tasks_generated,
            "engines_enabled": {
                "action_planner": self._action_planner is not None,
                "schedule_generator": self._schedule_generator is not None,
                "task_generator": self._task_generator is not None,
                "risk_planner": self._risk_planner is not None,
            },
        }


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "PlanningAgent",
    "PlanningAgentConfig",
]
