"""
PHASE 5 - EPIC 6: Planning Engines

Motores especializados para planificación:
- ActionPlanner
- ScheduleGenerator
- TaskGenerator
- RiskPlanner
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Any, Optional
import logging

logger = logging.getLogger(__name__)

# =============================================================================
# IMPORTS FROM EPIC 6 DOMAIN
# =============================================================================

from core.PHASE_5.epic6_planning_agent.domain import (
    ActionPlan,
    ActionItem,
    ActionPriority,
    ActionStatus,
    ClinicalPlan,
    ClinicalPhase,
    ClinicalPhaseItem,
    ExecutionTask,
    TaskType,
    TaskStatus,
)


# =============================================================================
# PLAN RESULT
# =============================================================================

@dataclass
class PlanResult:
    """Resultado de planificación."""
    context_id: str
    
    # Plan generado
    plan: ActionPlan | None = None
    
    # Stats
    actions_count: int = 0
    critical_count: int = 0
    estimated_duration_minutes: int = 0
    
    # Metadatos
    planned_at: datetime = field(default_factory=lambda: datetime.now(UTC))


# =============================================================================
# SCHEDULE RESULT
# =============================================================================

@dataclass
class ScheduleResult:
    """Resultado de programación."""
    plan_id: str
    
    # Tareas programadas
    tasks: list[ExecutionTask] = field(default_factory=list)
    
    # Stats
    total_tasks: int = 0
    total_duration_minutes: int = 0
    
    # Metadatos
    scheduled_at: datetime = field(default_factory=lambda: datetime.now(UTC))


# =============================================================================
# TASK RESULT
# =============================================================================

@dataclass
class TaskResult:
    """Resultado de generación de tareas."""
    plan_id: str
    
    # Tareas generadas
    tasks: list[ExecutionTask] = field(default_factory=list)
    
    # Stats
    tasks_by_type: dict = field(default_factory=dict)
    
    # Metadatos
    generated_at: datetime = field(default_factory=lambda: datetime.now(UTC))


# =============================================================================
# RISK ASSESSMENT
# =============================================================================

@dataclass
class RiskAssessment:
    """Evaluación de riesgo."""
    plan_id: str
    
    # Riesgos identificados
    risks: list[dict] = field(default_factory=list)
    
    # Score
    overall_risk_score: float = 0.0
    risk_level: str = "low"  # low, medium, high, critical
    
    # Mitigaciones
    mitigations: list[str] = field(default_factory=list)
    
    # Metadatos
    assessed_at: datetime = field(default_factory=lambda: datetime.now(UTC))


# =============================================================================
# ACTION PLANNER
# =============================================================================

class ActionPlanner:
    """
    Motor de planificación de acciones.
    
    Responsabilidades:
    - Generar planes de acción a partir de decisiones
    - Identificar dependencias entre acciones
    - Priorizar acciones
    - Estimar duración y recursos
    """
    
    async def create_plan(
        self,
        context_id: str,
        objectives: list[str],
        constraints: dict | None = None,
    ) -> PlanResult:
        """
        Crea un plan de acción.
        
        Args:
            context_id: ID del contexto (incident, diagnosis, etc.)
            objectives: Lista de objetivos
            constraints: Restricciones opcionales
        
        Returns:
            PlanResult con el plan generado
        """
        logger.info(f"Creating action plan for: {context_id}")
        
        plan = ActionPlan(
            context_id=context_id,
            title=f"Action Plan for {context_id}",
            description=f"Plan to achieve: {', '.join(objectives)}",
        )
        
        # Generar acciones basadas en objetivos
        for i, objective in enumerate(objectives):
            action = ActionItem(
                title=f"Action for: {objective}",
                description=f"Execute: {objective}",
                priority=self._determine_priority(i, len(objectives)),
                estimated_duration_minutes=30 + (i * 15),
            )
            plan.add_action(action)
        
        return PlanResult(
            context_id=context_id,
            plan=plan,
            actions_count=plan.total_actions,
            critical_count=plan.critical_actions,
            estimated_duration_minutes=sum(a.estimated_duration_minutes for a in plan.actions),
        )
    
    def _determine_priority(self, index: int, total: int) -> ActionPriority:
        """Determina la prioridad basada en el índice."""
        if index == 0:
            return ActionPriority.CRITICAL
        elif index < total * 0.3:
            return ActionPriority.HIGH
        elif index < total * 0.7:
            return ActionPriority.MEDIUM
        else:
            return ActionPriority.LOW


# =============================================================================
# SCHEDULE GENERATOR
# =============================================================================

class ScheduleGenerator:
    """
    Motor de generación de horarios.
    
    Responsabilidades:
    - Programar tareas en el tiempo
    - Respetar dependencias
    - Optimizar uso de recursos
    - Considerar disponibilidad
    """
    
    async def generate_schedule(
        self,
        plan: ActionPlan,
        start_time: datetime | None = None,
        available_slots: list[dict] | None = None,
    ) -> ScheduleResult:
        """
        Genera un horario para el plan.
        
        Args:
            plan: ActionPlan a programar
            start_time: Tiempo de inicio
            available_slots: Slots disponibles
        
        Returns:
            ScheduleResult con las tareas programadas
        """
        logger.info(f"Generating schedule for plan: {plan.plan_id}")
        
        if start_time is None:
            start_time = datetime.now(UTC)
        
        tasks = []
        current_time = start_time
        
        # Ordenar acciones por prioridad
        sorted_actions = sorted(
            plan.actions,
            key=lambda x: (x.priority.value, x.estimated_duration_minutes),
        )
        
        # Crear tareas
        for action in sorted_actions:
            task = ExecutionTask(
                plan_id=plan.plan_id,
                title=action.title,
                description=action.description,
                task_type=self._map_priority_to_task_type(action.priority),
                scheduled_start=current_time,
                scheduled_end=current_time + timedelta(minutes=action.estimated_duration_minutes),
                estimated_duration_minutes=action.estimated_duration_minutes,
                assigned_to=action.assigned_to,
            )
            tasks.append(task)
            current_time += timedelta(minutes=action.estimated_duration_minutes + 5)  # 5 min buffer
        
        return ScheduleResult(
            plan_id=plan.plan_id,
            tasks=tasks,
            total_tasks=len(tasks),
            total_duration_minutes=sum(t.estimated_duration_minutes for t in tasks),
        )
    
    def _map_priority_to_task_type(self, priority: ActionPriority) -> TaskType:
        """Mapea prioridad a tipo de tarea."""
        mapping = {
            ActionPriority.CRITICAL: TaskType.COORDINATION,
            ActionPriority.HIGH: TaskType.MAINTENANCE,
            ActionPriority.MEDIUM: TaskType.TECHNICAL,
            ActionPriority.LOW: TaskType.DOCUMENTATION,
            ActionPriority.ROUTINE: TaskType.DOCUMENTATION,
        }
        return mapping.get(priority, TaskType.TECHNICAL)


# =============================================================================
# TASK GENERATOR
# =============================================================================

class TaskGenerator:
    """
    Motor de generación de tareas.
    
    Responsabilidades:
    - Descomponer acciones en tareas ejecutables
    - Asignar recursos
    - Definir dependencias
    """
    
    async def generate_tasks(
        self,
        plan: ActionPlan,
    ) -> TaskResult:
        """
        Genera tareas ejecutables desde el plan.
        
        Args:
            plan: ActionPlan a descomponer
        
        Returns:
            TaskResult con las tareas generadas
        """
        logger.info(f"Generating tasks for plan: {plan.plan_id}")
        
        tasks = []
        tasks_by_type: dict[str, int] = {}
        
        # Descomponer cada acción en tareas
        for action in plan.actions:
            # Tarea principal
            main_task = ExecutionTask(
                plan_id=plan.plan_id,
                title=f"[MAIN] {action.title}",
                description=action.description,
                task_type=TaskType.MAINTENANCE,
                priority=5 if action.priority == ActionPriority.CRITICAL else 3,
                estimated_duration_minutes=action.estimated_duration_minutes,
                assigned_to=action.assigned_to,
            )
            tasks.append(main_task)
            tasks_by_type[main_task.task_type.value] = tasks_by_type.get(main_task.task_type.value, 0) + 1
            
            # Tarea de documentación
            doc_task = ExecutionTask(
                plan_id=plan.plan_id,
                title=f"[DOC] Document {action.title}",
                description=f"Document results of: {action.title}",
                task_type=TaskType.DOCUMENTATION,
                priority=2,
                estimated_duration_minutes=10,
            )
            tasks.append(doc_task)
            tasks_by_type[doc_task.task_type.value] = tasks_by_type.get(doc_task.task_type.value, 0) + 1
        
        return TaskResult(
            plan_id=plan.plan_id,
            tasks=tasks,
            tasks_by_type=tasks_by_type,
        )


# =============================================================================
# RISK PLANNER
# =============================================================================

class RiskPlanner:
    """
    Motor de planificación de riesgos.
    
    Responsabilidades:
    - Identificar riesgos
    - Evaluar probabilidad e impacto
    - Proponer mitigaciones
    """
    
    async def assess_risks(
        self,
        plan: ActionPlan,
        tasks: list[ExecutionTask] | None = None,
    ) -> RiskAssessment:
        """
        Evalúa los riesgos del plan.
        
        Args:
            plan: ActionPlan a evaluar
            tasks: Tareas opcionales
        
        Returns:
            RiskAssessment con la evaluación
        """
        logger.info(f"Assessing risks for plan: {plan.plan_id}")
        
        risks = []
        mitigations = []
        
        # Evaluar riesgos por prioridad
        critical_actions = [a for a in plan.actions if a.priority == ActionPriority.CRITICAL]
        if len(critical_actions) > 3:
            risks.append({
                "type": "too_many_critical",
                "description": f"{len(critical_actions)} critical actions may overload resources",
                "probability": 0.7,
                "impact": 0.8,
            })
            mitigations.append("Consider delegating critical actions")
        
        # Evaluar dependencias
        actions_with_deps = [a for a in plan.actions if a.dependencies]
        if actions_with_deps:
            risks.append({
                "type": "complex_dependencies",
                "description": f"{len(actions_with_deps)} actions have dependencies",
                "probability": 0.5,
                "impact": 0.6,
            })
            mitigations.append("Monitor dependency chain closely")
        
        # Evaluar duración total
        total_duration = sum(a.estimated_duration_minutes for a in plan.actions)
        if total_duration > 480:  # > 8 hours
            risks.append({
                "type": "long_duration",
                "description": f"Plan duration ({total_duration} min) exceeds single shift",
                "probability": 0.6,
                "impact": 0.5,
            })
            mitigations.append("Split into multiple shifts or days")
        
        # Calcular score
        if risks:
            overall_score = sum(r["probability"] * r["impact"] for r in risks) / len(risks)
        else:
            overall_score = 0.0
        
        # Determinar nivel
        if overall_score > 0.7:
            risk_level = "critical"
        elif overall_score > 0.5:
            risk_level = "high"
        elif overall_score > 0.3:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        return RiskAssessment(
            plan_id=plan.plan_id,
            risks=risks,
            overall_risk_score=overall_score,
            risk_level=risk_level,
            mitigations=mitigations,
        )


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Result classes
    "PlanResult",
    "ScheduleResult",
    "TaskResult",
    "RiskAssessment",
    # Engines
    "ActionPlanner",
    "ScheduleGenerator",
    "TaskGenerator",
    "RiskPlanner",
]
