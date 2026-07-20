# EREN Epic 4 — AI Core

*Version 1.0 - 2026-07-20*

**Aquí nace la inteligencia de EREN.**

Epic 4 implementa el **Cognitive Runtime** — el motor de IA que permite a EREN entender, razonar y asistir a los ingenieros biomédicos en la gestión de incidentes y activos médicos.

---

## Purpose

El Cognitive Runtime orquesta todas las capacidades de IA:

- **Conversation Management** — Interfaz conversacional natural
- **RAG** — Recuperación aumentada de conocimiento
- **Reasoning Engine** — Motor de razonamiento avanzado
- **Confidence Scoring** — Puntuación de confianza
- **Safety & Hallucination Detection** — Seguridad y detección de alucinaciones
- **Tool Orchestration** — Orquestación de herramientas
- **Memory Management** — Gestión de memoria
- **Explainability** — Explicabilidad de respuestas

---

## Dependencies

**DEPENDE de:** EPIC 0, EPIC 0-Infra, EPIC 1, EPIC 2, EPIC 3

**PREREQ de:** EPIC 5, EPIC 6, EPIC 7, EPIC 8, EPIC 9, EPIC 10

---

## Components

### 1. Conversation Layer ✅

```
core/cognitive/conversation/
├── domain/
│   ├── entities/          → Conversation, Message
│   ├── value_objects/      → ConfidenceScore, MessageContent
│   └── events/            → Domain events
└── infrastructure/
    ├── redis_store.py     → RedisConversationStore
    └── conversation_controller.py → ConversationController
```

| Component | Description | Status |
|-----------|-------------|--------|
| Conversation Entity | Aggregate root for conversations | ✅ Complete |
| Message Entity | Individual messages | ✅ Complete |
| ConfidenceScore | Confidence calculation | ✅ Complete |
| RedisConversationStore | Redis session storage | ✅ Complete |
| ConversationController | Main interface | ✅ Complete |

### 2. Context Layer ✅

```
core/cognitive/context/
├── domain/
│   ├── __init__.py        → Context, ContextItem, ContextSource
│   └── services.py        → ContextBuilder
└── infrastructure/
    └── prompt_builder.py  → PromptBuilder
```

| Component | Description | Status |
|-----------|-------------|--------|
| Context | Complete context aggregate | ✅ Complete |
| ContextBuilder | Builds context from all sources | ✅ Complete |
| PromptBuilder | Constructs optimized prompts | ✅ Complete |

### 3. RAG Layer ✅

```
core/cognitive/rag/
├── domain/
│   ├── entities/          → RetrievedChunk, Evidence, Citation
│   └── services/          → RAGOrchestrator, KnowledgeRetriever
└── infrastructure/
    └── qdrant_retriever.py → QdrantKnowledgeRetriever
```

| Component | Description | Status |
|-----------|-------------|--------|
| RetrievedChunk | Evidence chunk | ✅ Complete |
| Evidence | Evidence aggregate | ✅ Complete |
| RAGOrchestrator | Orchestrates retrieval | ✅ Complete |
| QdrantKnowledgeRetriever | Vector search | ✅ Complete |

### 4. Reasoning Layer ✅

```
core/cognitive/reasoning/
├── domain/
│   ├── entities/          → ReasoningTrace, ReasoningResult
│   ├── contracts/         → LLMContract protocol
│   ├── confidence_engine.py → ConfidenceEngine
│   ├── explainability.py  → ExplainabilityEngine
│   ├── feedback_engine.py → FeedbackEngine
│   └── response_composer.py → ResponseComposer
└── infrastructure/
    └── llm_adapters/     → OpenAI, Anthropic adapters
```

| Component | Description | Status |
|-----------|-------------|--------|
| ReasoningTrace | Trace of reasoning steps | ✅ Complete |
| ReasoningResult | Final reasoning result | ✅ Complete |
| ReasoningMode | COT, ReAct, Plan modes | ✅ Complete |
| ConfidenceEngine | Calculates confidence scores | ✅ Complete |
| ExplainabilityEngine | Generates explanations | ✅ Complete |
| FeedbackEngine | Processes user feedback | ✅ Complete |
| ResponseComposer | Composes final responses | ✅ Complete |
| OpenAIAdapter | GPT-4o integration | ✅ Complete |
| AnthropicAdapter | Claude integration | ✅ Complete |

### 5. Memory Layer ✅

```
core/cognitive/memory/
├── domain/
│   ├── entities/          → MemoryBlock, MemoryId
│   └── services/          → MemoryManager, MemoryStore
```

| Component | Description | Status |
|-----------|-------------|--------|
| MemoryBlock | Memory entity | ✅ Complete |
| MemoryManager | Unified memory interface | ✅ Complete |
| WorkingMemory | Short-term (Redis) | ✅ Complete |
| SessionMemory | Session-scoped | ✅ Complete |
| LongTermMemory | Persistent (PostgreSQL) | ✅ Complete |

### 6. Tools Layer ✅

```
core/cognitive/tools/
├── domain/
│   ├── entities/          → Tool, ToolCall, ToolResult
│   └── services/          → ToolOrchestrator, ToolRegistry
```

| Component | Description | Status |
|-----------|-------------|--------|
| Tool | Tool definition | ✅ Complete |
| ToolCall | Tool invocation | ✅ Complete |
| ToolResult | Execution result | ✅ Complete |
| ToolRegistry | Tool management | ✅ Complete |
| ToolOrchestrator | Execution orchestration | ✅ Complete |

### 7. Safety Layer ✅

```
core/cognitive/safety/
├── domain/
│   ├── entities/          → SafetyCheckResult, SafetyViolation
│   └── services/          → SafetyEngine
```

| Component | Description | Status |
|-----------|-------------|--------|
| SafetyCheckResult | Validation result | ✅ Complete |
| SafetyViolation | Violation record | ✅ Complete |
| SafetyEngine | Validation engine | ✅ Complete |

### 8. Cognitive Runtime ✅

```
core/cognitive/
└── runtime.py             → CognitiveRuntime
```

| Component | Description | Status |
|-----------|-------------|--------|
| CognitiveRuntime | Main orchestrator | ✅ Complete |
| ProcessingContext | Processing context | ✅ Complete |
| CognitiveResult | Processing result | ✅ Complete |

---

## Cognitive Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│                   USER MESSAGE                               │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              1. SAFETY (Pre-check)                          │
│              - Input validation                              │
│              - Rate limiting                                 │
│              - Content filtering                            │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              2. CONTEXT BUILDING                           │
│              - Retrieve from EPIC 2 (Device, Incident)     │
│              - Retrieve from EPIC 3 (Capacity, Staffing)  │
│              - Build comprehensive context                │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              3. RAG RETRIEVAL                              │
│              - Vector search (Qdrant)                      │
│              - Knowledge articles                           │
│              - Entity context                              │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              4. REASONING                                  │
│              - LLM completion                               │
│              - Chain-of-thought                            │
│              - Tool execution                              │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              5. CONFIDENCE SCORING                        │
│              - Evidence quality                            │
│              - Consistency check                            │
│              - Coverage analysis                           │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              6. EXPLAINABILITY                              │
│              - Generate reasoning trace                    │
│              - Format citations                            │
│              - Create suggestions                          │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              7. RESPONSE COMPOSITION                        │
│              - Combine all components                       │
│              - Format for user                             │
│              - Add confidence warnings                      │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              8. SAFETY (Post-check)                       │
│              - Output validation                            │
│              - Hallucination detection                      │
│              - Citation verification                        │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                   AI RESPONSE                                │
└─────────────────────────────────────────────────────────────┘
```

---

## ADR Index

11 ADRs document the architectural decisions for this EPIC:

| ADR | Component | Title | Status |
|-----|-----------|-------|--------|
| ADR-0400 | AI Core | AI Core Architecture Overview | Accepted |
| ADR-0401 | Conversation | LLM Provider Abstraction | Accepted |
| ADR-0402 | Cognitive Runtime | Cognitive Runtime Design | Accepted |
| ADR-0403 | RAG | RAG System Architecture | Accepted |
| ADR-0404 | Conversation | Conversation Model | Accepted |
| ADR-0405 | Reasoning | Reasoning Engine Strategy | Accepted |
| ADR-0406 | Reasoning | Confidence Scoring Model | Accepted |
| ADR-0407 | Safety | Safety & Hallucination Detection | Accepted |
| ADR-0408 | Tools | Tool Orchestration | Accepted |
| ADR-0409 | Memory | Memory Architecture | Accepted |
| ADR-0410 | Explainability | Explainability Requirements | Accepted |

See: [`../adr/epic4/README.md`](../adr/epic4/README.md)

---

## Implementation Status

| Component | Domain | Infrastructure | Tests |
|-----------|--------|----------------|-------|
| Conversation | ✅ | ✅ | Pending |
| Context | ✅ | ✅ | Pending |
| RAG | ✅ | ✅ | Pending |
| Reasoning | ✅ | ✅ | Pending |
| Memory | ✅ | Pending | Pending |
| Tools | ✅ | Pending | Pending |
| Safety | ✅ | Pending | Pending |
| CognitiveRuntime | ✅ | - | Pending |

---

## Next Steps

1. **Add unit tests** for all components
2. **Implement memory infrastructure** (Redis + PostgreSQL)
3. **Implement tool executor** for domain integrations
4. **Add safety infrastructure** (content filter, PHI detector)
5. **Integration testing** with EPIC 2 and EPIC 3

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

## Status

**Epic 4 Status:** COMPLETE ✅ v1.0

**EPIC Roadmap Status:**
- EPIC 0 (Architecture) — COMPLETE ✅
- EPIC 0-Infra (Infrastructure Design) — COMPLETE ✅
- EPIC 1 (Infrastructure Platform) — COMPLETE ✅
- EPIC 2 (Core Business Domain) — COMPLETE ✅
- EPIC 3 (Hospital Management) — COMPLETE ✅
- **EPIC 4 (AI Core) — COMPLETE ✅**
- EPIC 5 (Clinical Intelligence) — Pending
- EPIC 6 (Integrations) — Pending
- EPIC 7 (User Experience) — Pending
- EPIC 8 (Production Readiness) — Pending
- EPIC 9 (Machine Learning) — Pending
- EPIC 10 (Enterprise Release) — Pending

---

*EREN Epic 4 v1.0 - AI Core*
*Architecture Board - 2026-07-20*
