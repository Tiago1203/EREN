# EPIC 4: Knowledge Agent

*Versión: 1.0.0*
*Fecha: 2026-07-23*

---

## Objetivo

**Especializar un agente exclusivamente en conocimiento biomédico.**

EPIC 4 es responsable de:
- Consultar toda la plataforma de conocimiento construida en FASE 4
- Búsqueda de literatura científica
- Búsqueda de normas y estándares
- Generación de citas y referencias
- Construcción de paquetes de conocimiento

---

## Dependencias

### Fases
- **FASE 4**: Knowledge Platform (RAG, Embeddings, Qdrant, Citations)

### EPICs
- **EPIC 1**: Agent Orchestrator (lo invoca)
- **EPIC 2**: Biomedical Agent (provee contexto)
- **EPIC 3**: Diagnostic Agent (provee contexto)

---

## Arquitectura

```
┌─────────────────────────────────────────────────────────────────────────┐
│                   EPIC 4: Knowledge Agent                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    KNOWLEDGE AGENT                                 │   │
│  │  ├── KnowledgeRetriever ─────────── Retrieval de conocimiento  │   │
│  │  ├── CitationCollector ──────────── Colección de citas         │   │
│  │  ├── LiteratureSearchEngine ─────── Búsqueda de literatura    │   │
│  │  └── StandardsSearchEngine ──────── Búsqueda de normas        │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                       QUERY HANDLERS                               │   │
│  │  ├── Factual Query ───────────────── Consulta factual           │   │
│  │  ├── Regulatory Query ─────────────── Consulta regulatoria      │   │
│  │  ├── Literature Query ─────────────── Búsqueda de literatura   │   │
│  │  └── Standards Query ──────────────── Búsqueda de normas        │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                       DOMAIN OBJECTS                               │   │
│  │  ├── KnowledgeQuery ──────────────── Consulta de conocimiento   │   │
│  │  ├── KnowledgePackage ───────────── Paquete de conocimiento     │   │
│  │  └── CitationBundle ─────────────── Bundle de citas             │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Estructura de Archivos

```
core/PHASE_5/epic4_knowledge_agent/
├── __init__.py                    # Módulo principal
├── domain/
│   └── __init__.py              # KnowledgeQuery, KnowledgePackage, CitationBundle
├── engines/
│   └── __init__.py              # KnowledgeRetriever, CitationCollector, etc.
└── agent/
    └── __init__.py              # KnowledgeAgent
```

---

## Componentes

### 1. KnowledgeAgent

Agente principal especializado en conocimiento.

```python
class KnowledgeAgent(BaseAgent):
    """Agente especializado en búsqueda de conocimiento."""
    
    async def execute(self, task: AgentTask) -> AgentResult:
        """Ejecuta tarea de conocimiento."""
```

**Tipos de query:**
- `FACTUAL`: Consulta factual
- `PROCEDURAL`: Procedimientos
- `REGULATORY`: Normativa/regulación
- `TECHNICAL`: Técnica
- `CLINICAL`: Clínica
- `EQUIPMENT`: Equipos
- `SAFETY`: Seguridad
- `COMPLIANCE`: Cumplimiento

### 2. KnowledgeRetriever

Retrieval de conocimiento desde FASE 4.

```python
class KnowledgeRetriever:
    """Motor de retrieval de conocimiento."""
    
    async def retrieve(
        self,
        query: KnowledgeQuery,
    ) -> RetrievalResult:
        """Retrieves knowledge based on query."""
```

**Fuentes soportadas:**
- Manuales de equipos
- Normas (IEC, ISO, AAMI)
- Guías clínicas
- Literatura científica
- Regulaciones
- Mejores prácticas

### 3. CitationCollector

Colección de citas de fuentes.

```python
class CitationCollector:
    """Motor de colección de citas."""
    
    async def collect(
        self,
        query: KnowledgeQuery,
        items: list[KnowledgeItem],
    ) -> CitationResult:
        """Collect citations from items."""
    
    def create_bundle(
        self,
        citations: list[Citation],
        topic: str,
    ) -> CitationBundle:
        """Crea un bundle de citas."""
```

### 4. Search Engines

| Engine | Responsabilidad |
|--------|-----------------|
| `KnowledgeSearchEngine` | Búsqueda general |
| `LiteratureSearchEngine` | Literatura científica (PubMed) |
| `StandardsSearchEngine` | Normas y estándares |

---

## Domain Objects

### KnowledgeQuery

```python
@dataclass
class KnowledgeQuery:
    """Consulta de conocimiento."""
    query_id: str
    query_type: QueryType
    question: str
    sources: list[KnowledgeSource]
    max_results: int
    min_relevance: float
```

### KnowledgePackage

```python
@dataclass
class KnowledgePackage:
    """Paquete de conocimiento retrieval."""
    package_id: str
    items: list[KnowledgeItem]
    total_items: int
    avg_relevance: float
    citations: list[dict]
```

### CitationBundle

```python
@dataclass
class CitationBundle:
    """Bundle de citas."""
    bundle_id: str
    citations: list[Citation]
    topic: str
    
    def format_references(self, style: str = "apa") -> str:
        """Formatea todas las referencias."""
```

---

## Uso

### Consulta factual

```python
from core.PHASE_5.epic4_knowledge_agent import (
    KnowledgeAgent,
    KnowledgeAgentConfig,
)

# Crear agente
agent = KnowledgeAgent(
    agent_id="knowledge_1",
    config=KnowledgeAgentConfig(),
)

# Consultar conocimiento
result = await agent.execute(AgentTask(
    task_id="task_1",
    agent_id="knowledge_1",
    input_data={
        "query_type": "factual",
        "question": "How to perform preventive maintenance on infusion pumps?",
        "max_results": 10,
        "min_relevance": 0.8,
    },
))
```

### Búsqueda de literatura

```python
result = await agent.execute(AgentTask(
    task_id="task_2",
    agent_id="knowledge_1",
    input_data={
        "query_type": "clinical",
        "question": "Clinical evidence on biomedical device safety",
        "sources": ["literature"],
    },
))

# Acceder a citas en formato APA
print(result.output["citations"]["references_apa"])
```

### Búsqueda de normas

```python
result = await agent.execute(AgentTask(
    task_id="task_3",
    agent_id="knowledge_1",
    input_data={
        "query_type": "regulatory",
        "question": "Electrical safety standards for medical devices",
        "sources": ["standards"],
    },
))
```

---

## Integración con FASE 4

El KnowledgeAgent está diseñado para integrarse con FASE 4:

```
FASE 4                           EPIC 4
   │                               │
   ├── embeddings/                │
   │   └── Medical Embeddings ────┼──► KnowledgeRetriever
   │                               │
   ├── qdrant/                    │
   │   └── Vector Store ──────────┼──► KnowledgeRetriever
   │                               │
   ├── knowledge/                 │
   │   └── Knowledge Retriever ───┼──► KnowledgeAgent
   │                               │
   ├── rag/                       │
   │   └── Clinical RAG ───────────┼──► KnowledgeAgent
   │                               │
   └── citations/                 │
       └── Citation Engine ───────┼──► CitationCollector
```

---

## Eventos

| Evento | Descripción |
|--------|-------------|
| `KNOWLEDGE_RETRIEVED` | Conocimiento retrieval |
| `CITATIONS_COLLECTED` | Citas coleccionadas |
| `BUNDLE_CREATED` | Bundle de citas creado |

---

## Excepciones

| Excepción | Descripción |
|-----------|-------------|
| `NoResultsError` | Sin resultados |
| `LowRelevanceError` | Resultados con baja relevancia |
| `CitationError` | Error en colección de citas |

---

## Concatenación

```
EPIC 2 (Biomedical) ──┬──► EPIC 4 (Knowledge Agent)
EPIC 3 (Diagnostic) ──┘
FASE 4 ──► EPIC 4 (consume RAG, Knowledge, Citations)
EPIC 1 ──► EPIC 4 (orquesta)
EPIC 4 ──► EPIC 5 (Research Agent)
```

---

## Estado

**🚧 EN PROGRESO**

Implementación en desarrollo.

---

## Próximos Pasos

- EPIC 5: Research Agent
- EPIC 6: Planning Agent

---

*EREN PHASE 5 - EPIC 4*
*Architecture Board - 2026-07-23*
