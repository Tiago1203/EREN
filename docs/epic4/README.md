# EREN Epic 4 — AI Core
*Version 1.0 - 2026-07-20*

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-07-20 | Architecture Board | Initial - AI Core foundation |

---

## Overview

**Epic 4 es donde nace la inteligencia de EREN.**

Epic 4 implementa el **Cognitive Runtime** — el motor que permite a EREN pensar, razonar, aprender y explicar. Sin Epic 4, EREN es solo una base de datos con API. Con Epic 4, EREN se convierte en un asistente clínico inteligente.

Epic 4 se construye sobre:
- **Epic 0** — Filosofía de AI, Modelo Cognitivo, Principios de Confianza
- **Epic 1** — Infraestructura (FastAPI, Redis, observabilidad)
- **Epic 2** — Dominios Core (Device, Incident, Recommendation, Knowledge)
- **Epic 3** — Dominios Hospital (Capacity, Staffing, Organization, etc.)

Epic 4 es prerrequisito para:
- **Epic 5** — Clinical Intelligence (usa AI Core para CDSS)
- **Epic 6** — Integrations (enriquece datos con AI)
- **Epic 7** — User Experience (chat interface consume AI Core)
- **Epic 9** — Machine Learning (feedback loop requiere AI Core)

---

## EPIC Dependencies

```
Epic 0 ────────────────────────────────────────────────────────────→ Epic 4
  │                                                                         │
  ├── Cognitive Model ───────────────────→ Frozen, basis for AI Core        │
  ├── Philosophy (AI principles) ────────→ Trust, Evidence, Explainability │
  ├── Guardrails (G5, G6, G7) ───────────→ AI output requirements          │
  └── Capability Map ────────────────────→ Cognitive capabilities          │

Epic 1 ────────────────────────────────────────────────────────────→ Epic 4
  │                                                                         │
  ├── FastAPI ────────────────────────────→ API framework                   │
  ├── Redis ─────────────────────────────→ Cache for session/memory        │
  ├── RabbitMQ ────────────────────────────→ Event-driven communication     │
  └── OpenTelemetry ─────────────────────→ Tracing for AI operations       │

Epic 2 ────────────────────────────────────────────────────────────→ Epic 4
  │                                                                         │
  ├── Device Context ─────────────────────→ Device data for reasoning       │
  ├── Incident Context ───────────────────→ Incident context for AI recs    │
  ├── Recommendation Context ─────────────→ AI recommendations output      │
  └── Knowledge Context ──────────────────→ Evidence source for RAG       │

Epic 3 ────────────────────────────────────────────────────────────→ Epic 4
  │                                                                         │
  ├── Capacity Context ───────────────────→ Bed/room status for planning   │
  ├── Staffing Context ───────────────────→ Staff availability             │
  ├── Organization Context ───────────────→ Hospital structure             │
  └── Asset Context ──────────────────────→ Equipment data                 │

Epic 4 ────────────────────────────────────────────────────────────→ Epic 5
  │                                                                         │
  ├── Cognitive Runtime ──────────────────→ Reasoning engine               │
  ├── RAG System ─────────────────────────→ Evidence retrieval             │
  └── Confidence Engine ──────────────────→ Uncertainty quantification    │

Epic 4 ────────────────────────────────────────────────────────────→ Epic 7
  │                                                                         │
  └── Conversation Controller ────────────→ Chat interface backend        │

Epic 4 ────────────────────────────────────────────────────────────→ Epic 9
  │                                                                         │
  └── Feedback Engine ────────────────────→ ML feedback loop source       │
```

---

## Components Architecture

Epic 4 se organiza en **6 capas cognitivas**:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         CONVERSATION LAYER                               │
│  ┌─────────────────┐  ┌──────────────────┐  ┌─────────────────────────┐  │
│  │ Conversation    │  │ Response         │  │ Explainability          │  │
│  │ Controller      │  │ Composer         │  │ Engine                  │  │
│  └─────────────────┘  └──────────────────┘  └─────────────────────────┘  │
├─────────────────────────────────────────────────────────────────────────┤
│                           RAG LAYER                                      │
│  ┌─────────────────┐  ┌──────────────────┐                              │
│  │ Knowledge       │  │ RAG              │                              │
│  │ Retriever       │  │ Orchestrator     │                              │
│  └─────────────────┘  └──────────────────┘                              │
├─────────────────────────────────────────────────────────────────────────┤
│                         REASONING LAYER                                  │
│  ┌─────────────────┐  ┌──────────────────┐  ┌─────────────────────────┐  │
│  │ Reasoning       │  │ Confidence       │  │ Feedback               │  │
│  │ Engine          │  │ Engine           │  │ Engine                 │  │
│  └─────────────────┘  └──────────────────┘  └─────────────────────────┘  │
├─────────────────────────────────────────────────────────────────────────┤
│                         CONTEXT LAYER                                    │
│  ┌─────────────────┐  ┌──────────────────┐                              │
│  │ Context         │  │ Prompt           │                              │
│  │ Builder         │  │ Builder          │                              │
│  └─────────────────┘  └──────────────────┘                              │
├─────────────────────────────────────────────────────────────────────────┤
│                          MEMORY LAYER                                    │
│  ┌─────────────────┐                                                    │
│  │ Memory          │                                                    │
│  │ Manager         │                                                    │
│  └─────────────────┘                                                    │
├─────────────────────────────────────────────────────────────────────────┤
│                          TOOLS LAYER                                     │
│  ┌─────────────────┐                                                    │
│  │ Tool            │                                                    │
│  │ Orchestrator    │                                                    │
│  └─────────────────┘                                                    │
├─────────────────────────────────────────────────────────────────────────┤
│                         SAFETY LAYER                                     │
│  ┌─────────────────┐                                                    │
│  │ Safety          │                                                    │
│  │ Engine          │                                                    │
│  └─────────────────┘                                                    │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Component Inventory

### 1. Conversation Layer

#### Conversation Controller
**Purpose:** Gestiona el ciclo de vida de una conversación con el usuario.

**Responsabilidades:**
- Crear/iniciar conversaciones (nuevo o continuar existente)
- Gestionar sesiones de chat
- Recibir mensajes del usuario
- Enrutar al Cognitive Runtime
- Retornar respuestas estructuradas

**Ubicación:** `core/cognitive/conversation/`

**Contratos:**
```python
class ConversationController(Protocol):
    async def create_conversation(self, user_id: UserId, context: ConversationContext) -> Conversation
    async def send_message(self, conversation_id: ConversationId, message: Message) -> Response
    async def get_conversation_history(self, conversation_id: ConversationId) -> list[Message]
    async def end_conversation(self, conversation_id: ConversationId) -> None
```

---

#### Response Composer
**Purpose:** Compone respuestas finales para el usuario.

**Responsabilidades:**
- Formatear respuestas según el tipo (text, structured, error)
- Aplicar templates de respuesta
- Incluir citations y fuentes
- Generar explicaciones cuando sea necesario
- Manejar streaming de respuestas

**Ubicación:** `core/cognitive/conversation/response_composer.py`

---

#### Explainability Engine
**Purpose:** Genera explicaciones claras de las decisiones/respuestas de EREN.

**Responsabilidades:**
- Generar explanations basadas en reasoning trace
- Identificar fuentes de evidencia usadas
- Cuantificar confianza
- Proporcionar tracebacks de decisión
- Traducir术语 técnicas a lenguaje entendible

**Ubicación:** `core/cognitive/explainability/`

---

### 2. RAG Layer

#### Knowledge Retriever
**Purpose:** Recupera conocimiento relevante de la base de conocimientos.

**Responsabilidades:**
- Semantic search en Knowledge Articles (vía Qdrant)
- Hybrid search (vector + keyword)
- Filtrado por dominio, categoría, fecha
- Reranking de resultados
- Freshness scoring

**Ubicación:** `core/cognitive/rag/knowledge_retriever.py`

**Contratos:**
```python
class KnowledgeRetriever(Protocol):
    async def retrieve(
        self, 
        query: str, 
        filters: RetrievalFilters,
        top_k: int = 10
    ) -> list[RetrievedChunk]
```

---

#### RAG Orchestrator
**Purpose:** Orquestra el proceso completo de RAG.

**Responsabilidades:**
- Coordinating retrieval from multiple sources
- Fusionar resultados de diferentes retrievers
- Context window management
- Chunk selection y ordering
- Citation management

**Ubicación:** `core/cognitive/rag/orchestrator.py`

---

### 3. Reasoning Layer

#### Reasoning Engine
**Purpose:** Motor de razonamiento clínico de EREN.

**Responsabilidades:**
- Chain-of-thought reasoning
- Razonamiento multi-paso
- Integración con LLMs (OpenAI, Anthropic, local)
- Planning de tareas complejas
- Tool use planning

**Ubicación:** `core/cognitive/reasoning/`

**Modos de razonamiento:**
1. **Direct** — Respuesta directa simple
2. **Chain-of-Thought** — Razonamiento paso a paso
3. **Tree-of-Thought** — Exploración de múltiples paths
4. **ReAct** — Reason + Act (con tools)

---

#### Confidence Engine
**Purpose:** Cuantifica la incertidumbre de las respuestas.

**Responsabilidades:**
- Calcular scores de confianza (0.0 - 1.0)
- Identificar gaps de información
- Detectar conflicto de fuentes
- Generar calibrated uncertainties
- Aplicar debiasing

**Ubicación:** `core/cognitive/reasoning/confidence_engine.py`

**Niveles de confianza:**
| Score | Nivel | Acción |
|-------|-------|--------|
| 0.9-1.0 | Alta confianza | Respuesta directa |
| 0.7-0.9 | Confianza media | Respuesta + caveats |
| 0.5-0.7 | Baja confianza | Respuesta + disclaimer + escalate |
| <0.5 | Muy baja | Escalar a profesional |

---

#### Feedback Engine
**Purpose:** Recoge y procesa feedback del usuario.

**Responsabilidades:**
- Recibir feedback explícito (thumbs up/down, ratings)
- Recibir feedback implícito (correcciones, seguimientos)
- Almacenar feedback para ML pipeline
- Detectar drift en quality

**Ubicación:** `core/cognitive/feedback/`

---

### 4. Context Layer

#### Context Builder
**Purpose:** Construye el contexto de conversación para el LLM.

**Responsabilidades:**
- Agregar información del usuario (tenant, role, preferences)
- Incluir relevant device/incident data
- Añadir knowledge snippets del RAG
- Incluir conversation history
- Aplicar safety context

**Ubicación:** `core/cognitive/context/builder.py`

---

#### Prompt Builder
**Purpose:** Construye prompts optimizados para el LLM.

**Responsabilidades:**
- Template management
- Variable substitution
- Few-shot example selection
- System prompt engineering
- Prompt versioning y A/B testing

**Ubicación:** `core/cognitive/context/prompt_builder.py`

---

### 5. Memory Layer

#### Memory Manager
**Purpose:** Gestiona la memoria de sesión y persistent memory.

**Tipos de memoria:**
1. **Working Memory** — Contexto actual de la conversación (Redis)
2. **Session Memory** — Historial de la sesión actual (Redis)
3. **Long-term Memory** — Conocimiento persistente aprendido (PostgreSQL)

**Responsabilidades:**
- Store/retrieve session context
- Consolidate memories
- Forget irrelevant information
- Persist important learnings
- Privacy-aware memory management

**Ubicación:** `core/cognitive/memory/`

---

### 6. Tools Layer

#### Tool Orchestrator
**Purpose:** Orquesta las tools disponibles para el reasoning engine.

**Herramientas disponibles:**
- **Query Tools:** Device search, Incident lookup, Knowledge search
- **Action Tools:** Create incident, Update device, Schedule maintenance
- **External Tools:** FHIR queries, Weather, Calendar

**Responsabilidades:**
- Tool discovery y registration
- Tool execution orchestration
- Result parsing y formatting
- Error handling y retry
- Rate limiting

**Ubicación:** `core/cognitive/tools/`

---

### 7. Safety Layer

#### Safety Engine
**Purpose:** Garantiza que las respuestas de EREN sean seguras y éticas.

**Responsabilidades:**
- Content filtering (PHI, harmful content)
- Hallucination detection
- Medical safety checks
- Compliance validation (GDPR, HIPAA)
- Audit logging de decisiones

**Ubicación:** `core/cognitive/safety/`

---

## Document Index

| Document | Purpose | Status |
|---------|---------|--------|
| [README.md](./README.md) | This index | READY |
| [EREN_AI_CORE_ARCHITECTURE.md](./EREN_AI_CORE_ARCHITECTURE.md) | Complete AI Core architecture | TODO |
| [EREN_COGNITIVE_RUNTIME.md](./EREN_COGNITIVE_RUNTIME.md) | Runtime architecture | TODO |
| [EREN_CONVERSATION_MODEL.md](./EREN_CONVERSATION_MODEL.md) | Conversation handling | TODO |
| [EREN_RAG_ARCHITECTURE.md](./EREN_RAG_ARCHITECTURE.md) | RAG system design | TODO |
| [EREN_REASONING_ENGINE.md](./EREN_REASONING_ENGINE.md) | Reasoning engine design | TODO |
| [EREN_MEMORY_MODEL.md](./EREN_MEMORY_MODEL.md) | Memory architecture | TODO |
| [EREN_SAFETY_FRAMEWORK.md](./EREN_SAFETY_FRAMEWORK.md) | Safety requirements | TODO |
| [EREN_TOOL_SYSTEM.md](./EREN_TOOL_SYSTEM.md) | Tool orchestration | TODO |
| [EREN_CONFIDENCE_MODEL.md](./EREN_CONFIDENCE_MODEL.md) | Confidence scoring | TODO |

---

## ADR Index

| File | Title | Status |
|------|-------|--------|
| `docs/adr/epic4/ADR-0400.md` | AI Core Architecture | PROPOSED |
| `docs/adr/epic4/ADR-0401.md` | LLM Provider Abstraction | PROPOSED |
| `docs/adr/epic4/ADR-0402.md` | Cognitive Runtime Design | PROPOSED |
| `docs/adr/epic4/ADR-0403.md` | RAG Architecture | PROPOSED |
| `docs/adr/epic4/ADR-0404.md` | Conversation Model | PROPOSED |
| `docs/adr/epic4/ADR-0405.md` | Reasoning Engine Strategy | PROPOSED |
| `docs/adr/epic4/ADR-0406.md` | Confidence Scoring Model | PROPOSED |
| `docs/adr/epic4/ADR-0407.md` | Safety & Hallucination Detection | PROPOSED |
| `docs/adr/epic4/ADR-0408.md` | Tool Orchestration | PROPOSED |
| `docs/adr/epic4/ADR-0409.md` | Memory Architecture | PROPOSED |
| `docs/adr/epic4/ADR-0410.md` | Explainability Requirements | PROPOSED |

---

## Hexagonal Architecture

Epic 4 sigue **Hexagonal Architecture**:

```
core/cognitive/
├── conversation/
│   ├── domain/
│   │   ├── entities/          # Conversation, Message, Response
│   │   ├── value_objects/     # MessageContent, Confidence
│   │   └── events/            # ConversationStarted, MessageReceived
│   ├── application/
│   │   └── services/          # ConversationService
│   └── infrastructure/
│       └── adapters/          # RedisSessionStore
│
├── reasoning/
│   ├── domain/
│   │   ├── entities/          # ReasoningTrace, Confidence
│   │   ├── services/          # ReasoningService
│   │   └── contracts/         # LLMContract
│   └── infrastructure/
│       └── llm_adapters/       # OpenAIAdapter, AnthropicAdapter
│
├── rag/
│   ├── domain/
│   │   ├── entities/          # RetrievedChunk, Citation
│   │   └── services/          # RetrievalService
│   └── infrastructure/
│       └── qdrant_adapter/     # QdrantRetriever
│
├── memory/
│   ├── domain/
│   │   ├── entities/          # Memory, MemoryBlock
│   │   └── services/          # MemoryService
│   └── infrastructure/
│       └── postgres_adapter/    # MemoryRepository
│
├── tools/
│   ├── domain/
│   │   ├── entities/          # Tool, ToolResult
│   │   └── services/          # ToolOrchestrator
│   └── infrastructure/
│       └── tool_adapters/      # DeviceTool, IncidentTool
│
└── safety/
    ├── domain/
    │   └── services/          # SafetyValidator
    └── infrastructure/
        └── content_filter/    # ContentFilterAdapter
```

---

## Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| LLM | OpenAI GPT-4o / Anthropic Claude | Reasoning |
| Vector DB | Qdrant | Semantic search (RAG) |
| Cache | Redis | Session memory, rate limiting |
| Database | PostgreSQL | Long-term memory |
| Tracing | OpenTelemetry | Observability |
| Config | pydantic-settings | Configuration |

---

## Implementation Phases

### Phase 1: Foundation (Week 1-2)
- Cognitive Runtime skeleton
- LLM Provider abstraction
- Basic Conversation Controller
- Safety Engine skeleton

### Phase 2: Reasoning (Week 3-4)
- Reasoning Engine implementation
- Chain-of-Thought support
- Tool Orchestrator
- Context Builder

### Phase 3: RAG (Week 5-6)
- Knowledge Retriever
- RAG Orchestrator
- Integration with Knowledge Context (EPIC 2)
- Citation management

### Phase 4: Memory (Week 7-8)
- Memory Manager
- Redis session store
- Long-term memory (PostgreSQL)
- Memory consolidation

### Phase 5: Quality (Week 9-10)
- Confidence Engine
- Explainability Engine
- Feedback Engine
- Response Composer

### Phase 6: Integration (Week 11-12)
- Integration with EPIC 2 domains (Device, Incident, Recommendation)
- Integration with EPIC 3 domains (Capacity, Staffing, Organization)
- End-to-end testing
- Performance optimization

---

## Status: IN PROGRESS 🚧

**Epic 4 Status:** IN PROGRESS 🚧 v1.0

**EPIC Roadmap Status:**
- EPIC 0 (Architecture) — COMPLETE ✅
- EPIC 0-Infra (Infrastructure Design) — COMPLETE ✅
- EPIC 1 (Infrastructure Platform) — COMPLETE ✅ (merged)
- EPIC 2 (Core Business Domain) — COMPLETE ✅ (merged)
- EPIC 3 (Hospital Management) — COMPLETE ✅ (merged PR #131)
- **EPIC 4 (AI Core) — IN PROGRESS 🚧**
- EPIC 5 (Clinical Intelligence) — Pending
- EPIC 6 (Integrations) — Pending
- EPIC 7 (User Experience) — Pending
- EPIC 8 (Production Readiness) — Pending
- EPIC 9 (Machine Learning) — Pending
- EPIC 10 (Enterprise Release) — Pending

**Next:** Epic 5 - Clinical Intelligence

---

## Reference Documents

| Document | Path |
|----------|------|
| Cognitive Model | `../epic0/EREN_COGNITIVE_MODEL.md` |
| Capability Map | `../epic0/EREN_CAPABILITY_MAP.md` |
| Architecture Blueprint | `../epic0/EREN_ARCHITECTURE_BLUEPRINT.md` |
| Guardrails | `../epic0/EREN_ARCHITECTURAL_GUARDRAILS.md` |
| ADR Index | `../adr/README.md` |

---

*EREN Epic 4 v1.0 - AI Core*
*Architecture Board - 2026-07-20*
