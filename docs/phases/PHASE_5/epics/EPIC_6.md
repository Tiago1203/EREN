# EPIC 6: Planning Agent

*Versión: 1.0.0*
*Fecha: 2026-07-23*

---

## Objetivo

**Generar planes de acción.**

EPIC 6 es responsable de:
- Convertir decisiones clínicas en planes ejecutables
- Generar horarios de ejecución
- Descomponer acciones en tareas
- Evaluar y mitigar riesgos
- Crear planes clínicos estructurados

---

## Dependencias

### Fases
- **FASE 3**: Clinical Intelligence (Decision Engine - provee decisiones)

### EPICs
- **EPIC 1**: Agent Orchestrator (lo invoca)
- **EPIC 5**: Research Agent (provee contexto)

---

## Arquitectura

```
┌─────────────────────────────────────────────────────────────────────────┐
│                   EPIC 6: Planning Agent                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                     PLANNING AGENT                                 │   │
│  │  ├── ActionPlanner ─────────────────── Planificación de acciones   │   │
│  │  ├── ScheduleGenerator ─────────────── Generación de horarios    │   │
│  │  ├── TaskGenerator ─────────────────── Generación de tareas      │   │
│  │  └── RiskPlanner ───────────────────── Evaluación de riesgos      │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    PLAN TYPES                                     │   │
│  │  ├── Action Plan ─────────────────── Plan de acciones            │   │
│  │  ├── Clinical Plan ────────────────── Plan clínico estructurado   │   │
│  │  └── Schedule ─────────────────────── Horario de ejecución        │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                       DOMAIN OBJECTS                               │   │
│  │  ├── ActionPlan ───────────────────── Plan de acción            │   │
│  │  ├── ClinicalPlan ─────────────────── Plan clínico              │   │
│  │  └── ExecutionTask ─────────────────── Tarea de ejecución         │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Estructura de Archivos

```
core/PHASE_5/epic6_planning_agent/
├── __init__.py                    # Módulo principal
├── domain/
│   └── __init__.py              # ActionPlan, ClinicalPlan, ExecutionTask
├── engines/
│   └── __init__.py              # ActionPlanner, ScheduleGenerator, etc.
└── agent/
    └── __init__.py              # PlanningAgent
```

---

## Componentes

### 1. PlanningAgent

Agente principal dedicado a generación de planes.

```python
class PlanningAgent(BaseAgent):
    """Agente dedicado a generar planes de acción."""
    
    async def execute(self, task: AgentTask) -> AgentResult:
        """Ejecuta tarea de planificación."""
```

**Tipos de plan:**
- `action`: Plan de acción
- `clinical`: Plan clínico
- `schedule`: Horario de ejecución
- `risk`: Evaluación de riesgos

### 2. ActionPlanner

Planificación de acciones.

```python
class ActionPlanner:
    """Motor de planificación de acciones."""
    
    async def create_plan(
        self,
        context_id: str,
        objectives: list[str],
        constraints: dict | None,
    ) -> PlanResult:
        """Crea un plan de acción."""
```

**Prioridades:**
- `CRITICAL`: Crítica - acción inmediata
- `HIGH`: Alta - ASAP
- `MEDIUM`: Media - esta semana
- `LOW`: Baja - planificar
- `ROUTINE`: Rutina - cuando sea posible

### 3. ScheduleGenerator

Generación de horarios.

```python
class ScheduleGenerator:
    """Motor de generación de horarios."""
    
    async def generate_schedule(
        self,
        plan: ActionPlan,
        start_time: datetime | None,
    ) -> ScheduleResult:
        """Genera un horario para el plan."""
```

### 4. TaskGenerator

Descomposición de acciones en tareas.

```python
class TaskGenerator:
    """Motor de generación de tareas."""
    
    async def generate_tasks(
        self,
        plan: ActionPlan,
    ) -> TaskResult:
        """Genera tareas ejecutables."""
```

### 5. RiskPlanner

Evaluación de riesgos.

```python
class RiskPlanner:
    """Motor de planificación de riesgos."""
    
    async def assess_risks(
        self,
        plan: ActionPlan,
    ) -> RiskAssessment:
        """Evalúa los riesgos del plan."""
```

---

## Domain Objects

### ActionPlan

```python
@dataclass
class ActionPlan:
    """Plan de acción completo."""
    plan_id: str
    actions: list[ActionItem]
    total_actions: int
    completed_actions: int
    
    def add_action(self, action: ActionItem) -> None:
        """Agrega una acción."""
    
    def get_critical_path(self) -> list[ActionItem]:
        """Obtiene el camino crítico."""
    
    def get_progress_percentage(self) -> float:
        """Obtiene el porcentaje de progreso."""
```

### ClinicalPlan

```python
@dataclass
class ClinicalPlan:
    """Plan clínico estructurado."""
    plan_id: str
    phases: list[ClinicalPhaseItem]
    
    def advance_phase(self) -> bool:
        """Avanza a la siguiente fase."""
    
    def to_timeline(self) -> list[dict]:
        """Convierte a formato de línea de tiempo."""
```

### ExecutionTask

```python
@dataclass
class ExecutionTask:
    """Tarea ejecutable."""
    task_id: str
    task_type: TaskType
    status: TaskStatus
    
    def is_overdue(self) -> bool:
        """Verifica si la tarea está vencida."""
    
    def complete(self, output: str) -> None:
        """Marca la tarea como completada."""
```

---

## Uso

### Crear plan de acción

```python
from core.PHASE_5.epic6_planning_agent import (
    PlanningAgent,
    PlanningAgentConfig,
)

# Crear agente
agent = PlanningAgent(
    agent_id="planning_1",
    config=PlanningAgentConfig(),
)

# Crear plan de acción
result = await agent.execute(AgentTask(
    task_id="task_1",
    agent_id="planning_1",
    task_type="planning",
    input_data={
        "plan_type": "action",
        "context_id": "incident_123",
        "objectives": [
            "Repair critical device",
            "Verify functionality",
            "Document repair",
        ],
    },
))

# Acceder al plan
print(result.output["plan"])
```

### Crear plan clínico

```python
result = await agent.execute(AgentTask(
    task_id="task_2",
    agent_id="planning_1",
    task_type="planning",
    input_data={
        "plan_type": "clinical",
        "patient_id": "patient_123",
        "title": "Calibration Protocol",
        "phases": [
            {"phase": "assessment", "order": 1, "duration": 30},
            {"phase": "preparation", "order": 2, "duration": 15},
            {"phase": "implementation", "order": 3, "duration": 60},
            {"phase": "evaluation", "order": 4, "duration": 15},
        ],
    },
))
```

---

## Integración con FASE 3

El PlanningAgent usa el Decision Engine de FASE 3:

```
FASE 3 (Decision Engine) ──► EPIC 6 (Planning Agent)
                                       │
                                       ├── ActionPlanner
                                       ├── ScheduleGenerator
                                       ├── TaskGenerator
                                       └── RiskPlanner
```

---

## Eventos

| Evento | Descripción |
|--------|-------------|
| `PLAN_CREATED` | Plan creado |
| `TASKS_GENERATED` | Tareas generadas |
| `SCHEDULE_GENERATED` | Horario generado |
| `RISKS_ASSESSED` | Riesgos evaluados |

---

## Excepciones

| Excepción | Descripción |
|-----------|-------------|
| `NoObjectivesError` | Sin objetivos definidos |
| `InvalidPlanError` | Plan inválido |
| `ResourceConflictError` | Conflicto de recursos |

---

## Concatenación

```
EPIC 5 (Research) ──► EPIC 6 (Planning Agent)
EPIC 1 (Orchestrator) ──► EPIC 6 (orquesta)
EPIC 6 ──► EPIC 7 (Collaboration Engine)
```

---

## Estado

**🚧 EN PROGRESO**

Implementación en desarrollo.

---

## Próximos Pasos

- EPIC 7: Collaboration Engine
- EPIC 8: Consensus Engine

---

*EREN PHASE 5 - EPIC 6*
*Architecture Board - 2026-07-23*
