"""
PHASE 5 - EPIC 1: Task Scheduler

Componente que programa y ordena la ejecución de tareas.
Gestiona dependencias, prioridades y timing.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any, Optional
import heapq
import logging

logger = logging.getLogger(__name__)

# =============================================================================
# IMPORTS FROM DOMAIN
# =============================================================================

from core.PHASE_5.epic1_orchestrator.domain import (
    WorkflowStep,
    Workflow,
    OrchestrationStrategy,
)


# =============================================================================
# SCHEDULE STRATEGY
# =============================================================================

class ScheduleStrategy(str, Enum):
    """Estrategia de scheduling."""
    FIFO = "fifo"                     # First in, first out
    PRIORITY = "priority"             # Por prioridad
    DEPENDENCY = "dependency"         # Por dependencias
    LOAD_BALANCE = "load_balance"      # Balancear carga
    DYNAMIC = "dynamic"                # Dinámico


# =============================================================================
# SCHEDULED TASK
# =============================================================================

@dataclass
class ScheduledTask:
    """Tarea programada."""
    step_id: str
    priority: int
    scheduled_at: datetime
    estimated_duration_ms: int = 0
    
    # Para heap comparison
    def __lt__(self, other: "ScheduledTask") -> bool:
        return self.scheduled_at < other.scheduled_at


# =============================================================================
# TASK SCHEDULER
# =============================================================================

class TaskScheduler:
    """
    Scheduler de tareas.
    
    Responsabilidades:
    1. Ordenar tareas según estrategia
    2. Gestionar dependencias entre tareas
    3. Calcular timing óptimo
    4. Manejar slots de ejecución
    """
    
    def __init__(
        self,
        config: Any | None = None,
        max_concurrent: int = 10,
    ):
        self.config = config
        self.max_concurrent = max_concurrent
        
        # Estado
        self._task_queue: list[ScheduledTask] = []
        self._running_tasks: dict[str, WorkflowStep] = {}
        self._completed_tasks: set[str] = set()
        self._failed_tasks: set[str] = set()
        
        # Timing
        self._slot_duration_ms = 1000  # 1 segundo por slot
    
    def schedule_workflow(
        self,
        workflow: Workflow,
        strategy: ScheduleStrategy = ScheduleStrategy.DEPENDENCY,
    ) -> list[WorkflowStep]:
        """
        Programa los pasos de un workflow.
        
        Args:
            workflow: Workflow a programar
            strategy: Estrategia de scheduling
        
        Returns:
            Lista ordenada de pasos para ejecución
        """
        
        if strategy == ScheduleStrategy.FIFO:
            return self._schedule_fifo(workflow)
        elif strategy == ScheduleStrategy.PRIORITY:
            return self._schedule_priority(workflow)
        elif strategy == ScheduleStrategy.DEPENDENCY:
            return self._schedule_dependency(workflow)
        elif strategy == ScheduleStrategy.DYNAMIC:
            return self._schedule_dynamic(workflow)
        else:
            return self._schedule_dependency(workflow)
    
    def _schedule_fifo(self, workflow: Workflow) -> list[WorkflowStep]:
        """Schedule FIFO - orden original."""
        return list(workflow.steps)
    
    def _schedule_priority(self, workflow: Workflow) -> list[WorkflowStep]:
        """Schedule por prioridad."""
        sorted_steps = sorted(
            workflow.steps,
            key=lambda s: getattr(s, 'priority', 0),
            reverse=True,
        )
        return sorted_steps
    
    def _schedule_dependency(self, workflow: Workflow) -> list[WorkflowStep]:
        """
        Schedule por dependencias.
        
        Algoritmo de Kahn para topological sort.
        """
        # Calcular in-degree de cada paso
        in_degree: dict[str, int] = {s.step_id: 0 for s in workflow.steps}
        
        for step in workflow.steps:
            for dep_id in step.depends_on:
                if dep_id in in_degree:
                    in_degree[step.step_id] += 1
        
        # Cola con nodos sin dependencias
        queue = [
            s for s in workflow.steps
            if in_degree[s.step_id] == 0
        ]
        
        result = []
        
        while queue:
            # Tomar siguiente
            current = queue.pop(0)
            result.append(current)
            
            # Reducir in-degree de dependientes
            for step in workflow.steps:
                if current.step_id in step.depends_on:
                    in_degree[step.step_id] -= 1
                    if in_degree[step.step_id] == 0:
                        queue.append(step)
        
        # Verificar ciclos
        if len(result) != len(workflow.steps):
            logger.warning("Cycle detected in workflow dependencies")
            # Devolver los que se pudieron ordenar
            return result
        
        return result
    
    def _schedule_dynamic(self, workflow: Workflow) -> list[WorkflowStep]:
        """
        Schedule dinámico.
        
        Combina dependencias + prioridad + balanceo de carga.
        """
        # Primero resolver dependencias
        ordered = self._schedule_dependency(workflow)
        
        # Luego reordenar por prioridad dentro de cada nivel
        levels: dict[int, list[WorkflowStep]] = {}
        
        for step in ordered:
            level = len(step.depends_on)
            if level not in levels:
                levels[level] = []
            levels[level].append(step)
        
        # Ordenar cada nivel por prioridad
        for level in levels:
            levels[level].sort(
                key=lambda s: getattr(s, 'priority', 0),
                reverse=True,
            )
        
        # Concatenar niveles
        result = []
        for level in sorted(levels.keys()):
            result.extend(levels[level])
        
        return result
    
    def get_ready_steps(
        self,
        workflow: Workflow,
    ) -> list[WorkflowStep]:
        """
        Obtiene pasos listos para ejecutar.
        
        Un paso está listo si:
        1. Su estado es PENDING
        2. Todas sus dependencias están COMPLETED
        """
        ready = []
        
        for step in workflow.steps:
            if step.status.value != "pending":
                continue
            
            # Verificar dependencias
            deps_completed = all(
                self._is_completed(dep_id)
                for dep_id in step.depends_on
            )
            
            if deps_completed:
                ready.append(step)
        
        return ready
    
    def _is_completed(self, step_id: str) -> bool:
        """Verifica si un paso está completado."""
        return step_id in self._completed_tasks
    
    def can_execute_more(self) -> bool:
        """Verifica si se pueden ejecutar más tareas."""
        return len(self._running_tasks) < self.max_concurrent
    
    def mark_running(self, step: WorkflowStep) -> None:
        """Marca un paso como en ejecución."""
        self._running_tasks[step.step_id] = step
    
    def mark_completed(self, step: WorkflowStep) -> None:
        """Marca un paso como completado."""
        self._completed_tasks.add(step.step_id)
        if step.step_id in self._running_tasks:
            del self._running_tasks[step.step_id]
    
    def mark_failed(self, step: WorkflowStep) -> None:
        """Marca un paso como fallido."""
        self._failed_tasks.add(step.step_id)
        if step.step_id in self._running_tasks:
            del self._running_tasks[step.step_id]
    
    def get_estimated_time(
        self,
        workflow: Workflow,
    ) -> int:
        """
        Estima el tiempo total de ejecución del workflow.
        
        Considera paralelismo según estrategia.
        """
        if workflow.strategy == OrchestrationStrategy.PARALLEL:
            # Tiempo del paso más largo en paralelo
            return max(
                (s.timeout_seconds * 1000 for s in workflow.steps),
                default=0,
            )
        else:
            # Suma de todos los tiempos (secuencial)
            return sum(
                s.timeout_seconds * 1000
                for s in workflow.steps
            )
    
    def get_stats(self) -> dict:
        """Obtiene estadísticas del scheduler."""
        
        return {
            "queued_tasks": len(self._task_queue),
            "running_tasks": len(self._running_tasks),
            "completed_tasks": len(self._completed_tasks),
            "failed_tasks": len(self._failed_tasks),
            "max_concurrent": self.max_concurrent,
        }


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "TaskScheduler",
    "ScheduleStrategy",
    "ScheduledTask",
]
