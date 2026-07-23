# EPIC 1: Agent Orchestrator

*Versión: 1.0.0*
*Fecha: 2026-07-23*

---

## Objetivo

Crear el cerebro que coordina todos los agentes especializados.

---

## Responsabilidad

**Orquestar la ejecución de agentes.**

EPIC 1 es responsable de:

- Recibir solicitudes clínicas
- Decidir qué agentes participan
- Determinar el orden de ejecución
- Distribuir información a cada agente
- Combinar y sintetizar los resultados
- Devolver una respuesta unificada

---

## Dependencias

### Fases
- **FASE 3**: Clinical Intelligence (Reasoning, Evidence, Decision, Learning)
- **FASE 4**: Knowledge Platform (RAG, Embeddings, Citations)

### EPICs
- **EPIC 0**: Usa Foundation (AgentRegistry, MessageBroker, EventBus, BaseAgent)

---

## Arquitectura

```
┌─────────────────────────────────────────────────────────────────────────┐
│                   EPIC 1: Agent Orchestrator                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    REQUEST HANDLER                                │   │
│  │  ├── Intent Analyzer ─────────── Detecta tipo de request        │   │
│  │  ├── Context Extractor ───────── Extrae contexto relevante      │   │
│  │  └── Request Validator ────────── Valida request               │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                              │                                             │
│                              ▼                                             │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    PLAN BUILDER                                   │   │
│  │  ├── Intent Classification ───────── Clasifica según intent      │   │
│  │  ├── Agent Selector ─────────────── Selecciona agentes           │   │
│  │  └── Step Planner ───────────────── Planifica pasos             │   │
│  │                                                              │   │
│  │              OrchestrationPlan (output)                              │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                              │                                             │
│                              ▼                                             │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    WORKFLOW ENGINE                                │   │
│  │  ├── Task Dispatcher ────────────── Envía tareas a agentes       │   │
│  │  ├── Task Scheduler ─────────────── Programa ejecución           │   │
│  │  ├── Dependency Manager ─────────── Gestiona dependencias        │   │
│  │  └── Execution Monitor ───────────── Monitorea progreso          │   │
│  │                                                              │   │
│  │              Workflow (output)                                       │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                              │                                             │
│                              ▼                                             │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    RESPONSE AGGREGATOR                            │   │
│  │  ├── Result Collector ───────────── Recolecta resultados         │   │
│  │  ├── Conflict Resolver ───────────── Resuelve conflictos          │   │
│  │  ├── Confidence Calculator ───────── Calcula confianza total      │   │
│  │  └── Response Synthesizer ────────── Sintetiza respuesta final   │   │
│  │                                                              │   │
│  │              AggregatedResponse (output)                            │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Estructura de Archivos

```
core/PHASE_5/epic1_orchestrator/
├── __init__.py                    # Módulo principal
├── domain/
│   └── __init__.py               # Domain objects (Workflow, OrchestrationPlan, etc.)
├── engine/
│   └── __init__.py               # OrchestratorEngine
├── dispatcher/
│   └── __init__.py               # TaskDispatcher
├── scheduler/
│   └── __init__.py               # TaskScheduler
└── aggregator/
    └── __init__.py               # ResponseAggregator
```

---

## Componentes

### 1. OrchestratorEngine

Motor principal de orquestación.

```python
class OrchestratorEngine:
    """Motor de orquestación de agentes."""
    
    async def process_request(
        self,
        query: str,
        context: dict | None = None,
        strategy: OrchestrationStrategy | None = None,
    ) -> dict:
        """Procesa una solicitud clínica."""
```

**Flujo:**
1. Crear plan de orquestación
2. Seleccionar agentes
3. Crear workflow
4. Ejecutar workflow
5. Agregar resultados
6. Devolver respuesta

### 2. TaskDispatcher

Dispatcha tareas a agentes.

```python
class TaskDispatcher:
    """Dispatcher de tareas a agentes."""
    
    async def dispatch(
        self,
        execution: AgentExecution,
        agent: BaseAgent,
        strategy: DispatchStrategy = DispatchStrategy.DIRECT,
    ) -> ExecutionResult | None:
        """Dispatcha una ejecución a un agente."""
```

**Estrategias:**
- `DIRECT`: Ejecuta inmediatamente
- `QUEUE`: Cola el mensaje
- `BALANCED`: Balancea carga

### 3. TaskScheduler

Programa la ejecución de tareas.

```python
class TaskScheduler:
    """Scheduler de tareas."""
    
    def schedule_workflow(
        self,
        workflow: Workflow,
        strategy: ScheduleStrategy = ScheduleStrategy.DEPENDENCY,
    ) -> list[WorkflowStep]:
        """Programa los pasos de un workflow."""
```

**Estrategias:**
- `FIFO`: Orden original
- `PRIORITY`: Por prioridad
- `DEPENDENCY`: Topological sort
- `DYNAMIC`: Combina todas

### 4. ResponseAggregator

Agrega resultados de múltiples agentes.

```python
class ResponseAggregator:
    """Agregador de respuestas."""
    
    async def aggregate(
        self,
        results: dict[str, dict],
        shared_context: dict,
        method: AggregationMethod | None = None,
    ) -> dict:
        """Agrega resultados de múltiples pasos."""
```

**Métodos:**
- `FIRST`: Primer resultado válido
- `BEST`: Mayor confianza
- `ALL`: Todos los resultados
- `MERGE`: Fusiona todos
- `VOTE`: Votación
- `WEIGHTED`: Promedio ponderado

---

## Domain Objects

### Workflow

```python
@dataclass
class Workflow:
    """Workflow de orquestación."""
    workflow_id: str
    name: str
    strategy: OrchestrationStrategy
    steps: list[WorkflowStep]
    input_context: dict
    shared_context: dict
```

### OrchestrationPlan

```python
@dataclass
class OrchestrationPlan:
    """Plan de orquestación para una solicitud."""
    plan_id: str
    request_id: str
    original_query: str
    intent: str
    steps: list[PlanStep]
    selected_agents: dict[str, str]
```

### WorkflowStep

```python
@dataclass
class WorkflowStep:
    """Paso individual en un workflow."""
    step_id: str
    agent_type: str
    agent_id: str | None
    depends_on: list[str]
    timeout_seconds: int
```

---

## Estrategias de Orquestación

### SEQUENTIAL
```
Agente 1 → Agente 2 → Agente 3
```
Cada agente espera que el anterior termine.

### PARALLEL
```
Agente 1 ─┬─→ Agente 2 ─┬─→ Resultado
Agente 2 ─┘            └─→ Resultado
```
Todos los agentes ejecutan simultáneamente.

### PIPELINE
```
Agente 1 → Agente 2 → Agente 3
              ↑            ↑
           input:         input:
           output 1      output 2
```
Salida de uno es entrada del siguiente.

### FAN_OUT
```
              ┌─→ Agente A
              │
Agente 1 ─────┼─→ Agente B
              │
              └─→ Agente C
```
Un agente envía a múltiples.

### HYBRID
```
(Fase 1: Parallel)  ┌─→ Agente A
                    │
Agente 1 ───────────┼─→ Agente B
                    │
                    └─→ Agente C

(Fase 2: Sequential)────────→ Agente D
```
Combina múltiples estrategias.

---

## Detección de Intent

| Intent | Agentes Involucrados | Estrategia |
|--------|----------------------|------------|
| `diagnostic` | biomedical → diagnostic | sequential |
| `device_analysis` | knowledge → biomedical | sequential |
| `maintenance` | knowledge → planning | sequential |
| `incident` | knowledge → biomedical | parallel |
| `research` | research | single |
| `planning` | planning | single |
| `general` | orchestrator | direct |

---

## Uso

### Procesamiento básico

```python
from core.PHASE_5.epic1_orchestrator import (
    OrchestratorEngine,
    OrchestratorConfig,
)

# Crear engine
config = OrchestratorConfig(
    default_timeout_seconds=300,
    default_strategy=OrchestrationStrategy.SEQUENTIAL,
)
orchestrator = OrchestratorEngine(config=config)

# Procesar request
result = await orchestrator.process_request(
    query="Analyze device XYZ-123 for potential issues",
    context={"device_id": "XYZ-123"},
)

print(f"Success: {result['success']}")
print(f"Output: {result['result']['output']}")
```

### Con estrategias específicas

```python
# Parallel execution
result = await orchestrator.process_request(
    query="Research similar incidents",
    context={"query": "infusion pump failures"},
    strategy=OrchestrationStrategy.PARALLEL,
)

# Pipeline execution
result = await orchestrator.process_request(
    query="Full diagnostic analysis",
    context={"device_id": "XYZ-123"},
    strategy=OrchestrationStrategy.PIPELINE,
)
```

### Acceso a componentes

```python
# Dispatcher
dispatcher = orchestrator.dispatcher

# Scheduler
scheduler = orchestrator.scheduler

# Aggregator
aggregator = orchestrator.aggregator

# Registry
registry = orchestrator.registry
```

---

## Eventos

| Evento | Descripción |
|--------|-------------|
| `PLAN_CREATED` | Plan de orquestación creado |
| `PLAN_VALIDATED` | Plan validado exitosamente |
| `AGENTS_SELECTED` | Agentes seleccionados |
| `WORKFLOW_STARTED` | Workflow iniciado |
| `WORKFLOW_COMPLETED` | Workflow completado |
| `WORKFLOW_FAILED` | Workflow falló |
| `STEP_STARTED` | Paso iniciado |
| `STEP_COMPLETED` | Paso completado |
| `STEP_FAILED` | Paso falló |
| `RESPONSE_AGGREGATED` | Respuesta agregada |

---

## Excepciones

| Excepción | Descripción |
|-----------|-------------|
| `OrchestrationError` | Error general de orquestación |
| `PlanValidationError` | Falló validación del plan |
| `AgentSelectionError` | No se pudieron seleccionar agentes |
| `WorkflowExecutionError` | Error en ejecución del workflow |
| `AggregationError` | Error en agregación de resultados |
| `TimeoutError` | Timeout en ejecución |

---

## Concatenación

```
FASE 3 ──► EPIC 1 (consume Reasoning, Evidence, Decision)
FASE 4 ──► EPIC 1 (consume RAG, Knowledge Retrieval)
EPIC 0 ──► EPIC 1 (usa Foundation: AgentRegistry, MessageBroker)
EPIC 1 ──► EPIC 2-4 (orquesta Biomedical, Diagnostic, Knowledge agents)
```

---

## Estado

**🚧 EN PROGRESO**

Implementación en desarrollo.

---

## Próximos Pasos

- EPIC 2: Biomedical Agent
- EPIC 3: Diagnostic Agent
- EPIC 4: Knowledge Agent

---

*EREN PHASE 5 - EPIC 1*
*Architecture Board - 2026-07-23*
