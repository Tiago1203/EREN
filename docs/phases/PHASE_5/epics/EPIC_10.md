# EPIC 10: Agent Learning & Optimization

*Versión: 2.0.0*
*Fecha: 2026-07-24*

---

## Objetivo

**Optimizar continuamente el comportamiento de los agentes con aprendizaje validado.**

EPIC 10 es responsable de:
- Analizar rendimiento de agentes
- Detectar mejoras
- Optimizar estrategias
- Mejorar colaboración
- **Aprendizaje basado en resultados clínicos** *(NUEVO v2.0)*
- **Validación de predicciones** *(NUEVO v2.0)*
- **Feedback loop cerrado** *(NUEVO v2.0)*

---

## Dependencias

### Fases
- **FASE 3**: Clinical Intelligence (Learning, Improvement)

### EPICs
- **EPIC 9**: Agent Memory Engine (provee datos)
- **EPIC 1**: Agent Orchestrator (lo invoca)

---

## Arquitectura

```
┌─────────────────────────────────────────────────────────────────────────┐
│           EPIC 10: Agent Learning & Optimization (v2.0)                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                  AGENT LEARNING ENGINE                               │   │
│  │  ├── PerformanceAnalyzer ─────────────── Análisis de rendimiento   │   │
│  │  ├── StrategyOptimizer ────────────────── Optimización de estrategia│   │
│  │  ├── AgentEvaluator ───────────────────── Evaluación de agentes    │   │
│  │  └── CollaborationOptimizer ────────────── Optimización de collab │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │              VALIDATED LEARNING MODULE (NUEVO v2.0)                │   │
│  │  ├── OutcomeTracker ───────────────────── Rastreo de resultados   │   │
│  │  ├── PredictionValidator ───────────────── Validador de predicciones│   │
│  │  ├── ClinicalFeedbackLoop ──────────────── Feedback loop clínico │   │
│  │  ├── LearningFromOutcome ──────────────── Aprendizaje de resultados│   │
│  │  └── ModelUpdater ─────────────────────── Actualizador de modelos  │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    DOMAIN OBJECTS                                   │   │
│  │  ├── AgentMetric ─────────────────────── Métrica de agente       │   │
│  │  ├── LearningSession ─────────────────── Sesión de aprendizaje   │   │
│  │  ├── OptimizationReport ────────────────── Reporte de optimización│   │
│  │  ├── ClinicalOutcome ──────────────────── Resultado clínico     │   │
│  │  └── PredictionValidation ──────────────── Validación de predicción│   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Estructura de Archivos

```
core/PHASE_5/epic10_learning/
├── __init__.py                    # Módulo principal
├── domain/
│   └── __init__.py              # AgentMetric, LearningSession, etc.
├── engines/
│   ├── __init__.py              # PerformanceAnalyzer, StrategyOptimizer, etc.
│   └── validated/                # Validated Learning (NUEVO v2.0)
│       ├── __init__.py          # OutcomeTracker, PredictionValidator, etc.
│       ├── outcome_tracker.py     # Outcome tracking
│       ├── prediction_validator.py # Prediction validation
│       ├── feedback_loop.py       # Clinical feedback loop
│       └── model_updater.py      # Model updating
└── agent/
    └── __init__.py              # AgentLearningEngine
```

---

## Componentes

### 1. AgentLearningEngine

Motor principal de aprendizaje.

```python
class AgentLearningEngine(BaseAgent):
    """Motor de aprendizaje y optimización."""
    
    async def execute(self, task: AgentTask) -> AgentResult:
        """Ejecuta tarea de aprendizaje."""
```

**Acciones:**
- `analyze`: Analizar rendimiento
- `optimize`: Optimizar estrategia
- `evaluate`: Evaluar agente
- `collab_optimize`: Optimizar colaboración
- `session`: Gestionar sesiones

### 2. PerformanceAnalyzer

Análisis de rendimiento.

```python
class PerformanceAnalyzer:
    """Analizador de rendimiento."""
    
    async def analyze(
        self,
        agent_id: str,
        metrics: list[AgentMetric],
    ) -> AnalysisResult:
        """Analiza el rendimiento."""
    
    async def detect_anomalies(
        self,
        metrics: list[AgentMetric],
    ) -> list[AgentMetric]:
        """Detecta anomalías."""
```

### 3. StrategyOptimizer

Optimización de estrategias.

```python
class StrategyOptimizer:
    """Optimizador de estrategias."""
    
    async def optimize(
        self,
        agent_id: str,
        current_strategy: dict,
        performance_data: dict,
    ) -> OptimizationResult:
        """Optimiza la estrategia."""
```

### 4. AgentEvaluator

Evaluación de agentes.

```python
class AgentEvaluator:
    """Evaluador de agentes."""
    
    async def evaluate(
        self,
        agent_id: str,
        metrics: list[AgentMetric],
    ) -> EvaluationResult:
        """Evalúa un agente."""
```

### 5. CollaborationOptimizer

Optimización de colaboración.

```python
class CollaborationOptimizer:
    """Optimizador de colaboración."""
    
    async def optimize(
        self,
        agent_ids: list[str],
        collaboration_data: dict,
    ) -> CollabOptimizationResult:
        """Optimiza la colaboración."""
```

### 6. OutcomeTracker (NUEVO v2.0)

Rastreo de resultados clínicos.

```python
class OutcomeTracker:
    """Rastreador de resultados."""
    
    async def track(
        self,
        decision_id: str,
        prediction: ClinicalPrediction,
    ) -> TrackedOutcome:
        """Registra resultado de predicción."""
    
    async def get_outcome(
        self,
        decision_id: str,
    ) -> ClinicalOutcome | None:
        """Obtiene resultado final."""
```

### 7. PredictionValidator (NUEVO v2.0)

Validación de predicciones contra resultados.

```python
class PredictionValidator:
    """Validador de predicciones."""
    
    async def validate(
        self,
        prediction: ClinicalPrediction,
        outcome: ClinicalOutcome,
    ) -> PredictionValidation:
        """Valida predicción contra resultado."""
    
    async def calculate_accuracy(
        self,
        agent_id: str,
        time_window: TimeWindow,
    ) -> AccuracyMetrics:
        """Calcula métricas de accuracy."""
```

### 8. ClinicalFeedbackLoop (NUEVO v2.0)

Loop de feedback clínico cerrado.

```python
class ClinicalFeedbackLoop:
    """Loop de feedback clínico."""
    
    async def process_feedback(
        self,
        outcome: ClinicalOutcome,
        decision_id: str,
    ) -> FeedbackResult:
        """Procesa feedback de resultado."""
    
    async def update_knowledge(
        self,
        feedback: FeedbackResult,
    ) -> KnowledgeUpdate:
        """Actualiza base de conocimiento."""
    
    async def close_loop(
        self,
        decision_id: str,
    ) -> ClosedLoopResult:
        """Cierra el loop de feedback."""
```

### 9. LearningFromOutcome (NUEVO v2.0)

Aprendizaje de resultados clínicos.

```python
class LearningFromOutcome:
    """Aprendizaje de resultados."""
    
    async def learn(
        self,
        validated_outcome: PredictionValidation,
    ) -> LearningResult:
        """Aprende de resultado validado."""
    
    async def extract_lessons(
        self,
        outcomes: list[PredictionValidation],
    ) -> list[ClinicalLesson]:
        """Extrae lecciones de múltiples resultados."""
```

---

## Domain Objects

### AgentMetric

```python
@dataclass
class AgentMetric:
    """Métrica de agente."""
    metric_id: str
    agent_id: str
    metric_type: MetricType
    current_value: float
    
    def calculate_trend(self) -> str:
        """Calcula la tendencia."""
    
    def get_change_percentage(self) -> float:
        """Obtiene el porcentaje de cambio."""
```

### LearningSession

```python
@dataclass
class LearningSession:
    """Sesión de aprendizaje."""
    session_id: str
    metrics: list[AgentMetric]
    status: SessionStatus
    
    def start(self) -> None:
        """Inicia la sesión."""
    
    def complete(self) -> None:
        """Completa la sesión."""
```

### OptimizationReport

```python
@dataclass
class OptimizationReport:
    """Reporte de optimización."""
    recommendations: list[Recommendation]
    
    def get_top_recommendations(self, count: int) -> list[Recommendation]:
        """Obtiene las mejores recomendaciones."""
```

---

## Tipos de Métrica

| Tipo | Descripción |
|------|-------------|
| `PERFORMANCE` | Rendimiento general |
| `ACCURACY` | Precisión |
| `RESPONSE_TIME` | Tiempo de respuesta |
| `COLLABORATION` | Colaboración |
| `LEARNING` | Aprendizaje |

---

## Uso

### Analizar rendimiento

```python
from core.PHASE_5.epic10_learning import (
    AgentLearningEngine,
    AgentLearningConfig,
)

engine = AgentLearningEngine(
    agent_id="learning_1",
    config=AgentLearningConfig(),
)

result = await engine.execute(AgentTask(
    task_id="task_1",
    agent_id="learning_1",
    task_type="learning",
    input_data={
        "action": "analyze",
        "agent_id": "agent_1",
        "metrics": [
            {"type": "performance", "current_value": 0.85},
            {"type": "accuracy", "current_value": 0.92},
        ],
    },
))
```

### Evaluar agente

```python
result = await engine.execute(AgentTask(
    task_id="task_2",
    agent_id="learning_1",
    task_type="learning",
    input_data={
        "action": "evaluate",
        "agent_id": "agent_1",
        "metrics": [
            {"type": "performance", "current_value": 0.85},
            {"type": "collaboration", "current_value": 0.78},
        ],
    },
))
```

---

## Integración con FASE 3

```
FASE 3 (Learning/Improvement) ──► EPIC 10 (Agent Learning)
                                    │
                                    ├── PerformanceAnalyzer
                                    ├── StrategyOptimizer
                                    └── AgentEvaluator
```

---

## Concatenación

```
EPIC 9 (Agent Memory) ──► EPIC 10 (Agent Learning & Optimization)
EPIC 1 (Orchestrator) ──► EPIC 10 (orquesta)
EPIC 10 ──► EPIC 11 (Multi-Agent Governance)
EPIC 12 (Clinical Context) ──► EPIC 10 (provee contexto)
EPIC 13 (Evidence) ──► EPIC 10 (valida predicciones)
```

---

## Estado

**✅ ACTUALIZADO v2.0**

- Agent Learning base: ✅ COMPLETO
- Validated Learning Module: ✅ AÑADIDO v2.0
  - OutcomeTracker
  - PredictionValidator
  - ClinicalFeedbackLoop
  - LearningFromOutcome

Este EPIC cierra parcialmente el gap de Validated Learning (30/100 → 80/100).

---

## Próximos Pasos

- EPIC 11: Multi-Agent Governance
- PHASE 5 Cognitive Evolution completa
- PHASE 6: Hospital Digital

---

*EREN PHASE 5 - EPIC 10 v2.0*
*Architecture Board - 2026-07-24*
