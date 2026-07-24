# EPIC 13: Evidence Lifecycle Model

*Versión: 1.0.0*
*Fecha: 2026-07-24*

---

## Objetivo

**Construir el modelo completo de ciclo de vida de evidencia para decisiones clínicas.**

EPIC 13 es responsable de:
- Retrieval de evidencia científica
- Evaluación de calidad de evidencia
- Síntesis de evidencia
- Versionamiento de evidencia
- Trazabilidad de evidencia

---

## Dependencias

### Fases
- **FASE 3**: Clinical Intelligence (Evidence Retrieval, Reasoning)
- **FASE 4**: Knowledge Platform (RAG, Citations, Quality)

### EPICs
- **EPIC 12**: Clinical Context Builder (provee contexto)
- **EPIC 1**: Agent Orchestrator (lo invoca)

---

## Arquitectura

```
┌─────────────────────────────────────────────────────────────────────────┐
│                   EPIC 13: Evidence Lifecycle Model                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                  EVIDENCE LIFECYCLE MODULES                         │   │
│  │  ├── EvidenceRetriever ─────────────────── Recupera evidencia     │   │
│  │  ├── EvidenceEvaluator ─────────────────── Evalúa calidad         │   │
│  │  ├── EvidenceSynthesizer ───────────────── Sintetiza evidencia    │   │
│  │  ├── EvidenceVersioner ─────────────────── Versiona evidencia    │   │
│  │  └── EvidenceTracer ─────────────────────── Traza evidencia       │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    DOMAIN OBJECTS                                   │   │
│  │  ├── Evidence ──────────────────────────── Evidencia base         │   │
│  │  ├── EvidenceBundle ─────────────────────── Bundle de evidencia    │   │
│  │  ├── EvidenceQuality ────────────────────── Calidad de evidencia  │   │
│  │  ├── EvidenceSource ─────────────────────── Fuente de evidencia   │   │
│  │  └── EvidenceCitation ───────────────────── Citación de evidencia │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    EVIDENCE TYPES                                  │   │
│  │  ├── ClinicalTrial ─────────────────────── Ensayo clínico        │   │
│  │  ├── MetaAnalysis ──────────────────────── Meta-análisis         │   │
│  │  ├── ClinicalGuideline ─────────────────── Guía clínica          │   │
│  │  ├── CaseReport ────────────────────────── Reporte de caso      │   │
│  │  └── ExpertOpinion ──────────────────────── Opinión de experto    │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Estructura de Archivos

```
core/PHASE_5/epic13_evidence_model/
├── __init__.py                    # Módulo principal
├── domain/
│   └── __init__.py              # Evidence, EvidenceBundle, etc.
├── retrieval/
│   ├── __init__.py              # EvidenceRetriever
│   ├── literature_retriever.py  # Literature retrieval
│   └── guideline_retriever.py    # Guideline retrieval
├── evaluation/
│   ├── __init__.py              # EvidenceEvaluator
│   ├── quality_scorer.py       # Quality scoring
│   └── relevance_scorer.py     # Relevance scoring
├── synthesis/
│   ├── __init__.py              # EvidenceSynthesizer
│   ├── evidence_aggregator.py  # Evidence aggregation
│   └── summary_generator.py     # Summary generation
├── versioning/
│   ├── __init__.py              # EvidenceVersioner
│   └── version_manager.py       # Version management
├── tracing/
│   ├── __init__.py              # EvidenceTracer
│   └── citation_tracker.py      # Citation tracking
└── agent/
    └── __init__.py              # EvidenceLifecycleAgent
```

---

## Componentes

### 1. EvidenceLifecycleAgent

Agente principal de ciclo de vida de evidencia.

```python
class EvidenceLifecycleAgent(BaseAgent):
    """Agente de ciclo de vida de evidencia."""
    
    async def execute(self, task: AgentTask) -> AgentResult:
        """Ejecuta operaciones de evidencia."""
```

**Acciones:**
- `retrieve`: Recuperar evidencia
- `evaluate`: Evaluar calidad
- `synthesize`: Sintetizar evidencia
- `version`: Versionar evidencia
- `trace`: Trazar evidencia
- `bundle`: Crear bundle

### 2. EvidenceRetriever

Recupera evidencia de múltiples fuentes.

```python
class EvidenceRetriever:
    """Recuperador de evidencia."""
    
    async def retrieve(
        self,
        query: EvidenceQuery,
        sources: list[EvidenceSource] | None = None,
    ) -> list[Evidence]:
        """Recupera evidencia."""
    
    async def retrieve_literature(
        self,
        query: str,
        filters: LiteratureFilters | None = None,
    ) -> list[ClinicalLiterature]:
        """Recupera literatura clínica."""
    
    async def retrieve_guidelines(
        self,
        condition: str,
        specialty: str | None = None,
    ) -> list[ClinicalGuideline]:
        """Recupera guías clínicas."""
```

### 3. EvidenceEvaluator

Evalúa calidad de evidencia.

```python
class EvidenceEvaluator:
    """Evaluador de evidencia."""
    
    async def evaluate(
        self,
        evidence: Evidence,
    ) -> EvidenceQuality:
        """Evalúa calidad de evidencia."""
    
    async def score_quality(
        self,
        evidence: Evidence,
    ) -> QualityScore:
        """Calcula score de calidad."""
    
    async def score_relevance(
        self,
        evidence: Evidence,
        query: EvidenceQuery,
    ) -> RelevanceScore:
        """Calcula score de relevancia."""
    
    async def detect_conflicts(
        self,
        evidence_list: list[Evidence],
    ) -> list[EvidenceConflict]:
        """Detecta conflictos entre evidencias."""
```

### 4. EvidenceSynthesizer

Sintetiza múltiples evidencias.

```python
class EvidenceSynthesizer:
    """Sintetizador de evidencia."""
    
    async def synthesize(
        self,
        evidence_bundle: EvidenceBundle,
        synthesis_type: SynthesisType,
    ) -> EvidenceSynthesis:
        """Sintetiza evidencia."""
    
    async def aggregate_findings(
        self,
        evidence_list: list[Evidence],
    ) -> AggregatedFinding:
        """Agrega hallazgos."""
    
    async def generate_summary(
        self,
        synthesis: EvidenceSynthesis,
        format: SummaryFormat,
    ) -> str:
        """Genera resumen."""
```

### 5. EvidenceVersioner

Versiona evidencia para trazabilidad.

```python
class EvidenceVersioner:
    """Versionador de evidencia."""
    
    async def version_evidence(
        self,
        evidence: Evidence,
    ) -> EvidenceVersion:
        """Crea versión de evidencia."""
    
    async def get_latest_version(
        self,
        evidence_id: str,
    ) -> EvidenceVersion:
        """Obtiene última versión."""
    
    async def compare_versions(
        self,
        evidence_id: str,
        version_a: int,
        version_b: int,
    ) -> VersionDiff:
        """Compara versiones."""
```

### 6. EvidenceTracer

Trazabilidad de evidencia.

```python
class EvidenceTracer:
    """Trazador de evidencia."""
    
    async def trace(
        self,
        decision_id: str,
    ) -> EvidenceTrace:
        """Traza evidencia de una decisión."""
    
    async def get_citations(
        self,
        evidence_id: str,
    ) -> list[EvidenceCitation]:
        """Obtiene citaciones."""
    
    async def track_usage(
        self,
        evidence_id: str,
        decision_id: str,
    ) -> None:
        """Registra uso de evidencia."""
```

---

## Domain Objects

### Evidence

```python
@dataclass
class Evidence:
    """Evidencia base."""
    evidence_id: str
    evidence_type: EvidenceType
    source: EvidenceSource
    content: EvidenceContent
    quality: EvidenceQuality
    relevance: RelevanceScore
    applicability: ApplicabilityScore
    citation: EvidenceCitation
    
    def get_confidence_level(self) -> ConfidenceLevel:
        """Obtiene nivel de confianza."""
    
    def is_strong(self) -> bool:
        """Verifica si es evidencia fuerte."""
```

### EvidenceBundle

```python
@dataclass
class EvidenceBundle:
    """Bundle de evidencia."""
    bundle_id: str
    query: EvidenceQuery
    evidence_list: list[Evidence]
    synthesis: EvidenceSynthesis | None
    created_at: datetime
    
    def get_average_quality(self) -> float:
        """Obtiene calidad promedio."""
    
    def get_strongest_evidence(self) -> Evidence:
        """Obtiene evidencia más fuerte."""
```

### EvidenceQuality

```python
@dataclass
class EvidenceQuality:
    """Calidad de evidencia."""
    quality_level: QualityLevel
    score: float
    methodology_score: float
    sample_size_score: float
    consistency_score: float
    publication_bias_score: float
    
    def is_high_quality(self) -> bool:
        """Verifica si es alta calidad."""
    
    def get_limitations(self) -> list[str]:
        """Obtiene limitaciones."""
```

### EvidenceSource

```python
@dataclass
class EvidenceSource:
    """Fuente de evidencia."""
    source_type: SourceType
    name: str
    url: str | None
    doi: str | None
    published_date: datetime
    authors: list[str]
    journal: str | None
    
    def is_peer_reviewed(self) -> bool:
        """Verifica si es peer-reviewed."""
```

### EvidenceCitation

```python
@dataclass
class EvidenceCitation:
    """Citación de evidencia."""
    citation_text: str
    bibtex: str | None
    apa: str | None
    links: list[str]
    
    def format(self, style: CitationStyle) -> str:
        """Formatea citación."""
```

---

## Niveles de Calidad (GRADE)

| Nivel | Descripción | Score |
|-------|-------------|-------|
| `HIGH` | Alta confianza en estimación | 4 |
| `MODERATE` | Confianza moderada | 3 |
| `LOW` | Baja confianza | 2 |
| `VERY_LOW` | Muy baja confianza | 1 |

---

## Uso

### Recuperar y evaluar evidencia

```python
from core.PHASE_5.epic13_evidence_model import (
    EvidenceLifecycleAgent,
    EvidenceLifecycleConfig,
)

agent = EvidenceLifecycleAgent(
    agent_id="evidence_1",
    config=EvidenceLifecycleConfig(),
)

result = await agent.execute(AgentTask(
    task_id="task_1",
    agent_id="evidence_1",
    task_type="evidence",
    input_data={
        "action": "retrieve",
        "query": "ventilator maintenance protocols",
        "include_guidelines": True,
        "include_trials": True,
    },
))
```

### Sintetizar evidencia

```python
result = await agent.execute(AgentTask(
    task_id="task_2",
    agent_id="evidence_1",
    task_type="evidence",
    input_data={
        "action": "synthesize",
        "evidence_ids": ["ev_1", "ev_2", "ev_3"],
        "synthesis_type": "comprehensive",
    },
))
```

### Trazar evidencia de decisión

```python
result = await agent.execute(AgentTask(
    task_id="task_3",
    agent_id="evidence_1",
    task_type="evidence",
    input_data={
        "action": "trace",
        "decision_id": "decision_123",
    },
))
```

---

## Integración con FASE 3 y FASE 4

```
FASE 3 (Evidence Retrieval) ───────────────────────┐
                                                    │
FASE 4 (Knowledge/Citations) ───────────────────────┼──► EvidenceLifecycleAgent
                                                    │              │
PHASE 5 EPIC 12 (Clinical Context) ────────────────┴──► EvidenceRetriever
                                                              │
                                                              ▼
                                                      EvidenceBundle
```

---

## Concatenación

```
EPIC 12 (Clinical Context) ──► EPIC 13 (Evidence Lifecycle)
EPIC 1 (Orchestrator) ──► EPIC 13 (recupera evidencia)
EPIC 13 ──► EPIC 2-6 (provee evidencia a agentes)
EPIC 13 ──► EPIC 14 (evidencia → incertidumbre)
```

---

## Estado

**✅ IMPLEMENTADO**

Este EPIC cierra el gap de Evidence Model (20/100 → 85/100).

---

## Próximos Pasos

- EPIC 14: Uncertainty Quantification
- EPIC 2-6: Usarán evidencia de EPIC 13

---

*EREN PHASE 5 - EPIC 13*
*Architecture Board - 2026-07-24*
