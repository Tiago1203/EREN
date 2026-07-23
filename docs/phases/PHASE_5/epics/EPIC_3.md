# EPIC 3: Diagnostic Agent

*Versión: 1.0.0*
*Fecha: 2026-07-23*

---

## Objetivo

**Crear un agente especializado en diagnóstico técnico.**

EPIC 3 es responsable de:
- Analizar fallas de equipos médicos
- Generar hipótesis diagnósticas
- Identificar causa raíz
- Construir planes de diagnóstico
- Correlacionar eventos de falla

---

## Dependencias

### Fases
- **FASE 3**: Clinical Intelligence (Reasoning, Evidence, Decision)

### EPICs
- **EPIC 1**: Agent Orchestrator (lo invoca)
- **EPIC 2**: Biomedical Agent (provee contexto)

---

## Arquitectura

```
┌─────────────────────────────────────────────────────────────────────────┐
│                   EPIC 3: Diagnostic Agent                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    DIAGNOSTIC AGENT                                 │   │
│  │  ├── FailureAnalyzer ──────────── Análisis de fallas             │   │
│  │  ├── RootCauseAnalyzer ─────────── Análisis de causa raíz        │   │
│  │  ├── DiagnosticPlanner ─────────── Planificación de diagnóstico  │   │
│  │  └── FaultCorrelator ───────────── Correlación de fallas        │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                       TASK PROCESSORS                              │   │
│  │  ├── Failure Analysis ───────────── Análisis de falla            │   │
│  │  ├── Root Cause Analysis ─────────── Análisis RCA               │   │
│  │  ├── Predictive Diagnosis ─────────── Diagnóstico predictivo     │   │
│  │  ├── Fault Correlation ───────────── Correlación de eventos      │   │
│  │  └── Troubleshooting ─────────────── Resolución de problemas     │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                       DOMAIN OBJECTS                               │   │
│  │  ├── DiagnosticTask ────────────── Tarea de diagnóstico        │   │
│  │  ├── FailurePattern ────────────── Patrón de falla              │   │
│  │  └── DiagnosticReport ───────────── Reporte de diagnóstico       │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Estructura de Archivos

```
core/PHASE_5/epic3_diagnostic_agent/
├── __init__.py                    # Módulo principal
├── domain/
│   └── __init__.py              # DiagnosticTask, FailurePattern, DiagnosticReport
├── engines/
│   └── __init__.py              # FailureAnalyzer, RootCauseAnalyzer, etc.
└── agent/
    └── __init__.py              # DiagnosticAgent
```

---

## Componentes

### 1. DiagnosticAgent

Agente principal especializado en diagnóstico técnico.

```python
class DiagnosticAgent(BaseAgent):
    """Agente especializado en diagnóstico técnico."""
    
    async def execute(self, task: AgentTask) -> AgentResult:
        """Ejecuta tarea de diagnóstico."""
```

**Tipos de tarea:**
- `FAILURE_ANALYSIS`: Análisis de falla
- `ROOT_CAUSE`: Análisis de causa raíz
- `PREDICTIVE`: Diagnóstico predictivo
- `CORRELATION`: Correlación de fallas
- `TROUBLESHOOTING`: Resolución de problemas
- `INVESTIGATION`: Investigación

### 2. FailureAnalyzer

Analiza fallas y detecta patrones.

```python
class FailureAnalyzer:
    """Motor de análisis de fallas."""
    
    async def analyze(
        self,
        device_id: str,
        symptoms: list[str],
        error_codes: list[str],
        conditions: dict,
    ) -> FailureAnalysisResult:
        """Analiza fallas basadas en síntomas."""
```

**Modos de falla detectados:**
- `sudden_failure`: Falla total
- `degradation`: Degradación
- `intermittent`: Intermitente
- `overheating`: Sobrecalentamiento
- `calibration_drift`: Deriva de calibración

### 3. RootCauseAnalyzer

Realiza análisis de causa raíz (RCA).

```python
class RootCauseAnalyzer:
    """Motor de análisis de causa raíz."""
    
    async def analyze(
        self,
        device_id: str,
        symptom: str,
        failure_data: dict,
        historical_data: list[dict] | None = None,
    ) -> RootCauseAnalysisResult:
        """Realiza análisis de causa raíz."""
```

**Categorías de causa raíz:**
- `design_flaw`: Defecto de diseño
- `manufacturing_defect`: Defecto de manufactura
- `wear_and_tear`: Desgaste
- `environmental_stress`: Estrés ambiental
- `operational_error`: Error operacional
- `maintenance_deficiency`: Deficiencia de mantenimiento
- `software_issue`: Problema de software
- `external_factor`: Factor externo

### 4. DiagnosticPlanner

Crea planes de diagnóstico sistemático.

```python
class DiagnosticPlanner:
    """Motor de planificación de diagnóstico."""
    
    async def create_plan(
        self,
        task: DiagnosticTask,
        analysis_result: FailureAnalysisResult,
    ) -> DiagnosticPlan:
        """Crea un plan de diagnóstico."""
```

### 5. FaultCorrelator

Correla eventos de falla.

```python
class FaultCorrelator:
    """Motor de correlación de fallas."""
    
    async def correlate(
        self,
        primary_event: dict,
        event_history: list[dict],
    ) -> CorrelationResult:
        """Correla fallas con eventos históricos."""
```

---

## Domain Objects

### DiagnosticTask

```python
@dataclass
class DiagnosticTask:
    """Tarea de diagnóstico técnico."""
    task_id: str
    task_type: DiagnosticTaskType
    device_id: str
    symptom: str
    error_codes: list[str]
    conditions: dict
```

### FailurePattern

```python
@dataclass
class FailurePattern:
    """Patrón de falla identificado."""
    pattern_id: str
    pattern_name: str
    severity: FailureSeverity
    known_causes: list[str]
    recommended_solutions: list[str]
```

### DiagnosticReport

```python
@dataclass
class DiagnosticReport:
    """Reporte de diagnóstico."""
    report_id: str
    diagnosis: str
    confidence: DiagnosisConfidence
    hypotheses: list[dict]
    primary_cause: str
    supporting_evidence: list[str]
```

---

## Uso

### Análisis de falla

```python
from core.PHASE_5.epic3_diagnostic_agent import (
    DiagnosticAgent,
    DiagnosticAgentConfig,
)

# Crear agente
agent = DiagnosticAgent(
    agent_id="diagnostic_1",
    config=DiagnosticAgentConfig(),
)

# Analizar falla
result = await agent.execute(AgentTask(
    task_id="task_1",
    agent_id="diagnostic_1",
    task_type="failure_analysis",
    input_data={
        "device_id": "DEV-123",
        "symptom": "Device overheating",
        "error_codes": ["ERR_TEMP_001", "ERR_SHUTDOWN"],
        "conditions": {"temperature": 85, "humidity": 60},
    },
))
```

### Análisis de causa raíz

```python
result = await agent.execute(AgentTask(
    task_id="task_2",
    agent_id="diagnostic_1",
    task_type="root_cause",
    input_data={
        "device_id": "DEV-456",
        "symptom": "Intermittent power failures",
    },
))
```

### Troubleshooting

```python
result = await agent.execute(AgentTask(
    task_id="task_3",
    agent_id="diagnostic_1",
    task_type="troubleshooting",
    input_data={
        "device_id": "DEV-789",
        "symptom": "Device not responding",
    },
))

for step in result.output["steps"]:
    print(f"Step {step['step']}: {step['description']}")
```

---

## Eventos

| Evento | Descripción |
|--------|-------------|
| `FAILURE_ANALYZED` | Falla analizada |
| `ROOT_CAUSE_IDENTIFIED` | Causa raíz identificada |
| `DIAGNOSTIC_PLAN_CREATED` | Plan de diagnóstico creado |
| `FAULTS_CORRELATED` | Fallas correlacionadas |

---

## Excepciones

| Excepción | Descripción |
|-----------|-------------|
| `AnalysisTimeoutError` | Timeout en análisis |
| `InsufficientDataError` | Datos insuficientes |
| `MultipleCausesError` | Múltiples causas posibles |

---

## Concatenación

```
EPIC 2 (Biomedical) ──► EPIC 3 (Diagnostic)
FASE 3 ──► EPIC 3 (consume Reasoning, Evidence)
EPIC 1 ──► EPIC 3 (orquesta)
EPIC 3 ──► EPIC 4 (Knowledge Agent)
```

---

## Estado

**🚧 EN PROGRESO**

Implementación en desarrollo.

---

## Próximos Pasos

- EPIC 4: Knowledge Agent
- EPIC 5: Research Agent

---

*EREN PHASE 5 - EPIC 3*
*Architecture Board - 2026-07-23*
