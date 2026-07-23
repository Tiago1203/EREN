# EPIC 5: Research Agent

*Versión: 1.0.0*
*Fecha: 2026-07-23*

---

## Objetivo

**Construir un agente dedicado a investigación biomédica.**

EPIC 5 es responsable de:
- Buscar evidencia científica
- Comparar artículos y estudios
- Generar resúmenes técnicos
- Producir revisiones de literatura

---

## Dependencias

### Fases
- **FASE 4**: Knowledge Platform (provee conocimiento base)
- **EPIC 4**: Knowledge Agent (provee búsqueda de literatura)

### EPICs
- **EPIC 1**: Agent Orchestrator (lo invoca)
- **EPIC 4**: Knowledge Agent (provee contexto de conocimiento)

---

## Arquitectura

```
┌─────────────────────────────────────────────────────────────────────────┐
│                   EPIC 5: Research Agent                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                     RESEARCH AGENT                                 │   │
│  │  ├── ResearchPlanner ─────────────── Planificación sistemática    │   │
│  │  ├── EvidenceComparator ─────────── Comparación de evidencia    │   │
│  │  ├── PaperAnalyzer ───────────────── Análisis de artículos        │   │
│  │  └── LiteratureReviewer ─────────── Generación de revisiones    │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    RESEARCH METHODS                               │   │
│  │  ├── Systematic Review ─────────────── Revisión sistemática      │   │
│  │  ├── Meta-Analysis ─────────────────── Meta-análisis            │   │
│  │  ├── Technical Review ──────────────── Revisión técnica          │   │
│  │  └── General Research ───────────────── Investigación general      │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                       DOMAIN OBJECTS                             │   │
│  │  ├── ResearchRequest ─────────────── Solicitud de investigación │   │
│  │  ├── ResearchResult ──────────────── Resultado de investigación │   │
│  │  └── LiteratureReview ────────────── Revisión de literatura     │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Estructura de Archivos

```
core/PHASE_5/epic5_research_agent/
├── __init__.py                    # Módulo principal
├── domain/
│   └── __init__.py              # ResearchRequest, ResearchResult, LiteratureReview
├── engines/
│   └── __init__.py              # ResearchPlanner, EvidenceComparator, etc.
└── agent/
    └── __init__.py              # ResearchAgent
```

---

## Componentes

### 1. ResearchAgent

Agente principal dedicado a investigación biomédica.

```python
class ResearchAgent(BaseAgent):
    """Agente dedicado a investigación biomédica."""
    
    async def execute(self, task: AgentTask) -> AgentResult:
        """Ejecuta tarea de investigación."""
```

**Tipos de investigación:**
- `SYSTEMATIC_REVIEW`: Revisión sistemática
- `META_ANALYSIS`: Meta-análisis
- `CLINICAL_TRIAL`: Ensayo clínico
- `CASE_STUDY`: Caso clínico
- `TECHNICAL_REVIEW`: Revisión técnica
- `COMPARATIVE_STUDY`: Estudio comparativo
- `COHORT_STUDY`: Estudio de cohorte
- `EXPERIMENTAL`: Experimental

### 2. ResearchPlanner

Planificación de investigaciones sistemáticas.

```python
class ResearchPlanner:
    """Motor de planificación de investigación."""
    
    async def create_plan(
        self,
        request: ResearchRequest,
    ) -> ResearchPlan:
        """Crea un plan de investigación."""
```

**Pasos del plan:**
1. Definir estrategia de búsqueda
2. Búsqueda en bases de datos
3. Screening inicial
4. Evaluación de calidad
5. Extracción de datos
6. Síntesis
7. Generación de reporte

### 3. EvidenceComparator

Comparación de evidencia entre estudios.

```python
class EvidenceComparator:
    """Motor de comparación de evidencia."""
    
    async def compare(
        self,
        paper_1_id: str,
        paper_2_id: str,
        comparison_type: ComparisonType,
    ) -> ComparisonResult:
        """Compara dos artículos."""
```

**Tipos de comparación:**
- `METHODOLOGY`: Metodología
- `RESULTS`: Resultados
- `POPULATION`: Población
- `OUTCOMES`: Resultados
- `QUALITY`: Calidad

### 4. PaperAnalyzer

Análisis de artículos científicos.

```python
class PaperAnalyzer:
    """Motor de análisis de artículos."""
    
    async def analyze(
        self,
        paper_id: str,
        content: str,
    ) -> AnalysisResult:
        """Analiza un artículo."""
```

**Aspectos analizados:**
- Metodología
- Calidad
- Relevancia
- Hallazgos clave
- Limitaciones

### 5. LiteratureReviewer

Generación de revisiones de literatura.

```python
class LiteratureReviewer:
    """Motor de generación de revisiones."""
    
    async def create_review(
        self,
        request: ResearchRequest,
        analyses: list[AnalysisResult],
        findings: list[ResearchFinding],
    ) -> LiteratureReview:
        """Crea una revisión de literatura."""
```

---

## Domain Objects

### ResearchRequest

```python
@dataclass
class ResearchRequest:
    """Solicitud de investigación."""
    request_id: str
    research_type: ResearchType
    research_question: str
    scope: ResearchScope
    keywords: list[str]
    max_articles: int
    inclusion_criteria: list[str]
    exclusion_criteria: list[str]
```

### ResearchResult

```python
@dataclass
class ResearchResult:
    """Resultado de investigación."""
    result_id: str
    findings: list[ResearchFinding]
    articles_reviewed: int
    articles_included: int
    conclusion: str
    recommendations: list[str]
```

### LiteratureReview

```python
@dataclass
class LiteratureReview:
    """Revisión de literatura estructurada."""
    review_id: str
    title: str
    sections: list[SummarySection]
    comparisons: list[PaperComparison]
    references_count: int
    
    def to_markdown(self) -> str:
        """Convierte a formato markdown."""
```

---

## Uso

### Revisión sistemática

```python
from core.PHASE_5.epic5_research_agent import (
    ResearchAgent,
    ResearchAgentConfig,
)

# Crear agente
agent = ResearchAgent(
    agent_id="research_1",
    config=ResearchAgentConfig(),
)

# Realizar revisión sistemática
result = await agent.execute(AgentTask(
    task_id="task_1",
    agent_id="research_1",
    task_type="research",
    input_data={
        "research_type": "systematic_review",
        "research_question": "Effectiveness of preventive maintenance protocols?",
        "scope": "comprehensive",
        "max_articles": 50,
        "keywords": ["preventive maintenance", "medical devices", "efficacy"],
    },
))

# Acceder a la revisión
print(result.output["literature_review"]["title"])
```

### Meta-análisis

```python
result = await agent.execute(AgentTask(
    task_id="task_2",
    agent_id="research_1",
    task_type="research",
    input_data={
        "research_type": "meta_analysis",
        "research_question": "Impact of training on device reliability",
    },
))

# Acceder a resultados del meta-análisis
print(result.output["pooled_estimate"])
```

---

## Integración con EPIC 4

El ResearchAgent usa KnowledgeAgent para obtener literatura:

```
EPIC 4 (Knowledge) ──► EPIC 5 (Research)
                              │
                              ├── KnowledgeSearchEngine
                              ├── LiteratureSearchEngine
                              └── StandardsSearchEngine
```

---

## Eventos

| Evento | Descripción |
|--------|-------------|
| `RESEARCH_PLAN_CREATED` | Plan de investigación creado |
| `PAPERS_ANALYZED` | Artículos analizados |
| `EVIDENCE_COMPARED` | Evidencia comparada |
| `REVIEW_GENERATED` | Revisión generada |

---

## Excepciones

| Excepción | Descripción |
|-----------|-------------|
| `NoPapersFoundError` | Sin artículos encontrados |
| `LowQualityEvidenceError` | Evidencia de baja calidad |
| `InsufficientDataError` | Datos insuficientes |

---

## Concatenación

```
EPIC 4 (Knowledge) ──► EPIC 5 (Research Agent)
EPIC 1 (Orchestrator) ──► EPIC 5 (orquesta)
EPIC 5 ──► EPIC 6 (Planning Agent)
```

---

## Estado

**🚧 EN PROGRESO**

Implementación en desarrollo.

---

## Próximos Pasos

- EPIC 6: Planning Agent
- EPIC 7: Collaboration Engine

---

*EREN PHASE 5 - EPIC 5*
*Architecture Board - 2026-07-23*
