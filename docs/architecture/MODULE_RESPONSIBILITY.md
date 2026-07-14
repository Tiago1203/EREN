# EREN OS Module Responsibility Report

**Fecha:** 2026-07-14  
**Auditor:** Architecture Review Board

---

## 1. RESUMEN DE MÓDULOS

| Módulo | Responsabilidad | Contratos | Impl | Tipo |
|--------|----------------|------------|------|------|
| agents | Runtime de agentes cognitivos | 3 | 12 | Platform |
| boot | Boot sequence | 2 | 8 | Manager |
| capabilities | Registro de capacidades | 3 | 8 | Registry |
| collaboration | Multi-agente collaboration | 4 | 13 | Platform |
| composition | Composition root | 2 | 12 | Infrastructure |
| container | Dependency injection | 4 | 15 | Container |
| context | Context management | 2 | 9 | Manager |
| contracts | System contracts | 9 | 9 | Interface |
| decision | Decision engine | 3 | 13 | Engine |
| diagnostic | Diagnostics contracts | 2 | 6 | Stub |
| diagnostics | Full diagnostics | 8 | 17 | Platform |
| embeddings | Embedding services | 3 | 11 | Platform |
| events | Event system | 2 | 6 | Bus |
| execution | Execution engine | 3 | 10 | Engine |
| ingestion | Data ingestion | 2 | 6 | Pipeline |
| intent | Intent detection | 1 | 6 | Engine |
| knowledge | Knowledge system | 4 | 17 | Platform |
| knowledge_assets | Asset registry | 3 | 8 | Registry |
| learning | Learning platform | 2 | 8 | Platform |
| lifecycle | Lifecycle management | 3 | 10 | Manager |
| memory | Memory system | 4 | 15 | Platform |
| models | Model definitions | 2 | 7 | Models |
| orchestration | Orchestration contracts | 5 | 10 | Contracts |
| orchestrator | Orchestrator engine | 3 | 12 | Engine |
| pipeline | Pipeline system | 4 | 14 | Pipeline |
| planner | Planner contracts | 2 | 9 | Contracts |
| planning | Planning engine | 3 | 9 | Engine |
| plugins | Plugin framework | 3 | 12 | Framework |
| providers | Multi-provider layer | 2 | 7 | Layer |
| rag | RAG pipeline | 3 | 10 | Pipeline |
| reasoning | Reasoning platform | 6 | 24 | Platform |
| registry | Registry base | 2 | 6 | Base |
| retrieval | Retrieval engine | 4 | 13 | Engine |
| router | Router system | 3 | 13 | System |
| runtime | Runtime engine | 5 | 14 | Engine |
| scheduler | Scheduler | 3 | 10 | Manager |
| sdk | SDK layer | 2 | 7 | SDK |
| session | Session management | 1 | 10 | Manager |
| tools | Tool system | 3 | 10 | Platform |
| workflow | Workflow stubs | 2 | 5 | Stub |
| workflows | Workflow platform | 5 | 14 | Platform |

---

## 2. MATRIZ DE DEPENDENCIAS

| Depende de \ | agents | boot | container | orchestrator | memory | reasoning |
|---------------|--------|------|-----------|--------------|--------|-----------|
| **agents** | - | ❌ | ✅ | ✅ | ✅ | ✅ |
| **boot** | ❌ | - | ✅ | ✅ | ❌ | ❌ |
| **container** | ❌ | ❌ | - | ✅ | ❌ | ❌ |
| **orchestrator** | ✅ | ✅ | ✅ | - | ✅ | ✅ |
| **memory** | ✅ | ❌ | ❌ | ✅ | - | ✅ |
| **reasoning** | ✅ | ❌ | ❌ | ✅ | ✅ | - |

---

## 3. RESPONSABILIDADES DUPLICADAS

| Responsabilidad | Módulos | Resolución |
|-----------------|---------|------------|
| Planning | planner/, planning/ | Mantener - contratos vs impl |
| Orchestration | orchestration/, orchestrator/ | Mantener - contratos vs impl |
| Workflows | workflow/, workflows/ | **Merge** → workflows/ |
| Diagnostics | diagnostic/, diagnostics/ | **Deprecate** → diagnostics/ |

---

## 4. CONTRATOS DEL SISTEMA

### 4.1 Contratos Principales

| Contrato | Ubicación | Implementadores |
|----------|-----------|----------------|
| CognitiveEngine | contracts/ | Reasoning, Memory, Planning |
| EventPublisher | events/ | Todos los módulos |
| CapabilityRegistry | capabilities/ | Agents, Plugins |
| ServiceContainer | container/ | Composition |
| OrchestratorPort | orchestrator/ | Orchestrator |
| MemoryContract | memory/ | MemoryEngine |
| ToolContract | tools/ | ToolEngine |

---

## 5. ESTRUCTURA DE CAPAS

```
┌─────────────────────────────────────────────────────────────┐
│                     APLICACIONES                            │
│              (apps/api, apps/web, apps/desktop)             │
├─────────────────────────────────────────────────────────────┤
│                        SDK                                  │
│                   (core/sdk)                                │
├─────────────────────────────────────────────────────────────┤
│                   ORCHESTRATOR                              │
│              (orchestrator, orchestration)                  │
├─────────────────────────────────────────────────────────────┤
│                    PLATFORMS                               │
│  agents│reasoning│learning│memory│knowledge│workflows     │
├─────────────────────────────────────────────────────────────┤
│                    ENGINES                                 │
│   retrieval│planning│decision│execution│tool│router       │
├─────────────────────────────────────────────────────────────┤
│                   INFRASTRUCTURE                          │
│       container│boot│events│composition│runtime           │
├─────────────────────────────────────────────────────────────┤
│                     CONTRACTS                              │
│                   (core/contracts)                         │
└─────────────────────────────────────────────────────────────┘
```

---

*Architecture Review Board*
