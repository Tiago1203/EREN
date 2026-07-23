"""
PHASE 5 - EPIC 1: Orchestrator Domain Objects

Domain objects para el sistema de orquestación:
- Workflow
- AgentExecution
- OrchestrationPlan
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any, Optional
import uuid


# =============================================================================
# ENUMS
# =============================================================================

class OrchestrationStrategy(str, Enum):
    """Estrategia de orquestación."""
    SEQUENTIAL = "sequential"     # Ejecuta agentes en orden
    PARALLEL = "parallel"         # Ejecuta agentes en paralelo
    FAN_OUT = "fan_out"           # Un agente envía a múltiples
    PIPELINE = "pipeline"         # Salida de uno es entrada de otro
    HYBRID = "hybrid"             # Combinación de estrategias


class ExecutionMode(str, Enum):
    """Modo de ejecución."""
    SYNC = "sync"                 # Síncrono - espera resultado
    ASYNC = "async"               # Asíncrono - no espera
    STREAM = "stream"             # Streaming de resultados


class AggregationMethod(str, Enum):
    """Método de agregación de resultados."""
    FIRST = "first"               # Primer resultado válido
    BEST = "best"                 # Mejor resultado según score
    ALL = "all"                   # Todos los resultados
    MERGE = "merge"               # Fusiona todos
    VOTE = "vote"                 # Votación entre resultados
    WEIGHTED = "weighted"         # Promedio ponderado


class WorkflowStatus(str, Enum):
    """Estado del workflow."""
    PENDING = "pending"           # Esperando inicio
    RUNNING = "running"           # En ejecución
    COMPLETED = "completed"        # Completado exitosamente
    FAILED = "failed"            # Falló
    CANCELLED = "cancelled"       # Cancelado
    PARTIAL = "partial"           # Parcialmente completado


class ExecutionStatus(str, Enum):
    """Estado de ejecución."""
    PENDING = "pending"           # Esperando ejecución
    RUNNING = "running"           # Ejecutando
    COMPLETED = "completed"        # Completada
    FAILED = "failed"             # Falló
    TIMEOUT = "timeout"           # Timeout
    SKIPPED = "skipped"           # Saltado


class PlanStatus(str, Enum):
    """Estado del plan de orquestación."""
    CREATED = "created"           # Creado
    VALIDATED = "validated"       # Validado
    APPROVED = "approved"          # Aprobado
    EXECUTING = "executing"        # En ejecución
    COMPLETED = "completed"        # Completado
    FAILED = "failed"             # Falló


# =============================================================================
# WORKFLOW - Flujo de orquestación
# =============================================================================

@dataclass
class WorkflowStep:
    """Paso individual en un workflow."""
    step_id: str
    agent_type: str
    agent_id: str | None = None
    
    # Configuración
    input_mapping: dict = field(default_factory=dict)  # De qué fuentes obtiene input
    output_mapping: dict = field(default_factory=dict)  # A dónde va el output
    depends_on: list[str] = field(default_factory=list)  # step_ids de los que depende
    
    # Constraints
    timeout_seconds: int = 300
    retry_count: int = 0
    required_capabilities: list[str] = field(default_factory=list)
    
    # State
    status: ExecutionStatus = ExecutionStatus.PENDING
    started_at: datetime | None = None
    completed_at: datetime | None = None
    error: str | None = None
    
    def __post_init__(self):
        if not self.step_id:
            self.step_id = str(uuid.uuid4())
    
    @property
    def duration_ms(self) -> int | None:
        """Duración en milisegundos."""
        if self.started_at and self.completed_at:
            return int((self.completed_at - self.started_at).total_seconds() * 1000)
        return None
    
    @property
    def is_completed(self) -> bool:
        return self.status == ExecutionStatus.COMPLETED
    
    @property
    def is_failed(self) -> bool:
        return self.status in [ExecutionStatus.FAILED, ExecutionStatus.TIMEOUT]


@dataclass
class Workflow:
    """Workflow de orquestación."""
    workflow_id: str
    name: str
    description: str = ""
    
    # Configuración
    strategy: OrchestrationStrategy = OrchestrationStrategy.SEQUENTIAL
    execution_mode: ExecutionMode = ExecutionMode.SYNC
    aggregation_method: AggregationMethod = AggregationMethod.BEST
    
    # Pasos
    steps: list[WorkflowStep] = field(default_factory=list)
    
    # State
    status: WorkflowStatus = WorkflowStatus.PENDING
    current_step_index: int = 0
    
    # Contexto
    input_context: dict = field(default_factory=dict)
    output_context: dict = field(default_factory=dict)
    shared_context: dict = field(default_factory=dict)
    
    # Resultados
    step_results: dict[str, dict] = field(default_factory=dict)  # step_id -> result
    
    # Metadatos
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    started_at: datetime | None = None
    completed_at: datetime | None = None
    timeout_seconds: int = 3600
    
    def __post_init__(self):
        if not self.workflow_id:
            self.workflow_id = str(uuid.uuid4())
    
    def add_step(self, step: WorkflowStep) -> None:
        """Agrega un paso al workflow."""
        self.steps.append(step)
    
    def get_step(self, step_id: str) -> Optional[WorkflowStep]:
        """Obtiene un paso por ID."""
        for step in self.steps:
            if step.step_id == step_id:
                return step
        return None
    
    def get_ready_steps(self) -> list[WorkflowStep]:
        """Obtiene pasos listos para ejecutar (dependencias cumplidas)."""
        ready = []
        completed_ids = {s.step_id for s in self.steps if s.is_completed}
        
        for step in self.steps:
            if step.status != ExecutionStatus.PENDING:
                continue
            deps_satisfied = all(dep_id in completed_ids for dep_id in step.depends_on)
            if deps_satisfied:
                ready.append(step)
        
        return ready
    
    @property
    def is_complete(self) -> bool:
        return self.status == WorkflowStatus.COMPLETED
    
    @property
    def is_failed(self) -> bool:
        return self.status == WorkflowStatus.FAILED
    
    @property
    def progress(self) -> float:
        """Progreso del workflow (0.0 - 1.0)."""
        if not self.steps:
            return 0.0
        completed = sum(1 for s in self.steps if s.is_completed)
        return completed / len(self.steps)


# =============================================================================
# AGENT EXECUTION - Ejecución de un agente
# =============================================================================

@dataclass
class ExecutionResult:
    """Resultado de ejecución de un agente."""
    execution_id: str
    
    # Resultado
    success: bool
    output: dict = field(default_factory=dict)
    error: str | None = None
    
    # Métricas
    execution_time_ms: int = 0
    tokens_used: int = 0
    
    # Confianza
    confidence: float = 0.0
    citations: list[str] = field(default_factory=list)
    
    # Timestamps
    started_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    completed_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    
    def __post_init__(self):
        if not self.execution_id:
            self.execution_id = str(uuid.uuid4())
    
    @property
    def is_success(self) -> bool:
        return self.success


@dataclass
class AgentExecution:
    """Ejecución de un agente en el contexto de orquestación."""
    execution_id: str
    workflow_id: str
    step_id: str
    agent_id: str
    agent_type: str
    
    # Task
    task_type: str
    task_input: dict = field(default_factory=dict)
    
    # Configuración
    timeout_seconds: int = 300
    retry_count: int = 0
    max_retries: int = 3
    
    # State
    status: ExecutionStatus = ExecutionStatus.PENDING
    result: ExecutionResult | None = None
    
    # Context
    input_context: dict = field(default_factory=dict)
    output_context: dict = field(default_factory=dict)
    
    # Timestamps
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    started_at: datetime | None = None
    completed_at: datetime | None = None
    
    def __post_init__(self):
        if not self.execution_id:
            self.execution_id = str(uuid.uuid4())
    
    @property
    def is_completed(self) -> bool:
        return self.status == ExecutionStatus.COMPLETED
    
    @property
    def is_failed(self) -> bool:
        return self.status in [ExecutionStatus.FAILED, ExecutionStatus.TIMEOUT]
    
    @property
    def can_retry(self) -> bool:
        return self.retry_count < self.max_retries
    
    @property
    def duration_ms(self) -> int | None:
        if self.started_at and self.completed_at:
            return int((self.completed_at - self.started_at).total_seconds() * 1000)
        return None


# =============================================================================
# ORCHESTRATION PLAN - Plan de orquestación
# =============================================================================

@dataclass
class PlanStep:
    """Paso en el plan de orquestación."""
    step_id: str
    order: int
    
    # Agente
    agent_type: str
    required_capabilities: list[str] = field(default_factory=list)
    
    # Input/Output
    input_sources: list[str] = field(default_factory=list)  # IDs de pasos o "input"
    output_target: str = ""  # "output" o ID de paso
    
    # Constraints
    timeout_seconds: int = 300
    priority: int = 0  # Mayor = más prioridad
    
    # State
    status: ExecutionStatus = ExecutionStatus.PENDING
    assigned_agent_id: str | None = None
    
    def __post_init__(self):
        if not self.step_id:
            self.step_id = str(uuid.uuid4())


@dataclass
class OrchestrationPlan:
    """Plan de orquestación para una solicitud."""
    plan_id: str
    request_id: str
    
    # Solicitud original
    original_query: str
    intent: str = ""
    
    # Estrategia
    strategy: OrchestrationStrategy = OrchestrationStrategy.SEQUENTIAL
    execution_mode: ExecutionMode = ExecutionMode.SYNC
    
    # Pasos planificados
    steps: list[PlanStep] = field(default_factory=list)
    
    # Agentes seleccionados
    selected_agents: dict[str, str] = field(default_factory=dict)  # agent_type -> agent_id
    
    # State
    status: PlanStatus = PlanStatus.CREATED
    
    # Validación
    validation_errors: list[str] = field(default_factory=list)
    is_validated: bool = False
    
    # Metadatos
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    validated_at: datetime | None = None
    executed_at: datetime | None = None
    
    def __post_init__(self):
        if not self.plan_id:
            self.plan_id = str(uuid.uuid4())
    
    def add_step(self, step: PlanStep) -> None:
        """Agrega un paso al plan."""
        self.steps.append(step)
        self.steps.sort(key=lambda s: s.order)
    
    def get_step(self, step_id: str) -> Optional[PlanStep]:
        """Obtiene un paso por ID."""
        for step in self.steps:
            if step.step_id == step_id:
                return step
        return None
    
    def get_next_step(self) -> Optional[PlanStep]:
        """Obtiene el siguiente paso a ejecutar."""
        for step in self.steps:
            if step.status == ExecutionStatus.PENDING:
                return step
        return None
    
    @property
    def is_complete(self) -> bool:
        return self.status == PlanStatus.COMPLETED
    
    @property
    def progress(self) -> float:
        """Progreso del plan (0.0 - 1.0)."""
        if not self.steps:
            return 0.0
        completed = sum(1 for s in self.steps if s.status == ExecutionStatus.COMPLETED)
        return completed / len(self.steps)
    
    def to_dict(self) -> dict:
        """Convierte a diccionario."""
        return {
            "plan_id": self.plan_id,
            "request_id": self.request_id,
            "original_query": self.original_query,
            "intent": self.intent,
            "strategy": self.strategy.value,
            "steps": [
                {
                    "step_id": s.step_id,
                    "order": s.order,
                    "agent_type": s.agent_type,
                    "status": s.status.value,
                }
                for s in self.steps
            ],
            "progress": self.progress,
            "status": self.status.value,
        }


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Enums
    "OrchestrationStrategy",
    "ExecutionMode",
    "AggregationMethod",
    "WorkflowStatus",
    "ExecutionStatus",
    "PlanStatus",
    # Workflow
    "WorkflowStep",
    "Workflow",
    # AgentExecution
    "ExecutionResult",
    "AgentExecution",
    # OrchestrationPlan
    "PlanStep",
    "OrchestrationPlan",
]
