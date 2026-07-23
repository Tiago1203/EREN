# EPIC 10: Agent Learning & Optimization

*Versión: 1.0.0*
*Fecha: 2026-07-23*

---

## Objetivo

**Optimizar continuamente el comportamiento de los agentes.**

EPIC 10 es responsable de:
- Analizar rendimiento de agentes
- Detectar mejoras
- Optimizar estrategias
- Mejorar colaboración

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
│                   EPIC 10: Agent Learning & Optimization                     │
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
│  │                    DOMAIN OBJECTS                                   │   │
│  │  ├── AgentMetric ─────────────────────── Métrica de agente       │   │
│  │  ├── LearningSession ─────────────────── Sesión de aprendizaje   │   │
│  │  └── OptimizationReport ────────────────── Reporte de optimización│   │
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
│   └── __init__.py              # PerformanceAnalyzer, StrategyOptimizer, etc.
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
```

---

## Estado

**🚧 EN PROGRESO**

Implementación en desarrollo.

---

## Próximos Pasos

- EPIC 11: Multi-Agent Governance

---

*EREN PHASE 5 - EPIC 10*
*Architecture Board - 2026-07-23*
