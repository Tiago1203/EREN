# EREN OS Module Map

**Fecha:** 2026-07-14  
**Versión:** 1.0

---

## 1. RESUMEN

| Total Módulos | 41 |
|--------------|-----|
| Plataformas | 9 |
| Motores | 6 |
| Infraestructura | 7 |
| Contratos | 1 |
| Capas | 3 |
| Stubs | 2 |

---

## 2. MAPA COMPLETO

### 2.1 Layer: CONTRACTS

| Módulo | Responsabilidad | Contratos | Capa |
|--------|----------------|-----------|------|
| contracts | Interfaces del sistema | 9 contratos | Abstraction |

### 2.2 Layer: INFRASTRUCTURE

| Módulo | Responsabilidad | Dependencias | Capa |
|--------|----------------|-------------|------|
| container | Dependency Injection | contracts | Infrastructure |
| events | Event Bus | ninguna | Infrastructure |
| composition | Composition Root | container, events | Infrastructure |
| boot | Boot Manager | container, events | Infrastructure |
| runtime | Runtime Engine | todas | Infrastructure |
| lifecycle | Lifecycle Manager | events, container | Infrastructure |
| session | Session Manager | events | Infrastructure |

### 2.3 Layer: PLATFORMS

| Módulo | Responsabilidad | Contrato | Capa |
|--------|----------------|----------|------|
| memory | Memory System | Memory | Platform |
| reasoning | Reasoning Platform | Reasoning | Platform |
| planning | Planning Engine | Planner | Platform |
| workflows | Workflow Platform | Workflow | Platform |
| knowledge | Knowledge System | Knowledge | Platform |
| diagnostics | Diagnostics | Diagnostic | Platform |
| agents | Agent Runtime | AgentContract | Platform |
| collaboration | Multi-Agent | AgentContract | Platform |
| tools | Tool System | Tool | Platform |

### 2.4 Layer: ENGINES

| Módulo | Responsabilidad | Contrato | Capa |
|--------|----------------|----------|------|
| retrieval | Retrieval Engine | CognitiveEngine | Engine |
| decision | Decision Engine | CognitiveEngine | Engine |
| execution | Execution Engine | CognitiveEngine | Engine |
| embeddings | Embedding Service | - | Engine |
| router | Request Router | - | Engine |
| intent | Intent Detection | - | Engine |

### 2.5 Layer: LAYERS

| Módulo | Responsabilidad | Contrato | Capa |
|--------|----------------|----------|------|
| providers | LLM Providers | ProviderContract | Layer |
| pipeline | Processing Pipeline | - | Layer |
| plugins | Plugin Framework | CapabilityRegistry | Layer |

### 2.6 Layer: UTILITIES

| Módulo | Responsabilidad | Capa |
|--------|----------------|------|
| models | Model Definitions | Utilities |
| registry | Registry Base | Utilities |
| capabilities | Capability Registry | Utilities |
| scheduler | Task Scheduler | Utilities |

### 2.7 Layer: STUBS (Para deprecación)

| Módulo | Status | Destino |
|--------|--------|---------|
| diagnostic | DEPRECATE | diagnostics |
| workflow | MERGE | workflows |

---

## 3. DIAGRAMA DE CAPAS

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              APLICACIONES                                   │
│                    apps/api  │  apps/web  │  apps/desktop                  │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                                 SDK                                         │
│                           core/sdk                                          │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              ORCHESTRATOR                                    │
│               orchestrator/  │  orchestration/                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
        ┌─────────────────────────────┼─────────────────────────────┐
        │                             │                             │
        ▼                             ▼                             ▼
┌───────────────────┐     ┌───────────────────┐     ┌───────────────────┐
│    PLATFORMS     │     │    PLATFORMS     │     │    PLATFORMS     │
│    reasoning     │     │    memory        │     │    planning       │
│    knowledge     │     │    diagnostics   │     │    workflows      │
│    agents        │     │    collaboration │     │    tools         │
└───────────────────┘     └───────────────────┘     └───────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                               ENGINES                                        │
│     retrieval  │  decision  │  execution  │  embeddings  │  router       │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            INFRASTRUCTURE                                    │
│   container  │  events  │  composition  │  boot  │  runtime  │  lifecycle   │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CONTRACTS                                        │
│                            core/contracts                                    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. CONTRATOS DEL SISTEMA

| Contrato | Descripción | Implementadores |
|----------|-------------|----------------|
| CognitiveEngine | Base para todos los motores | 7 |
| SupportsLifecycle | Start/stop lifecycle | 5 |
| Memory | Sistema de memoria | memory |
| Planner | Motor de planificación | planning |
| Reasoning | Motor de razonamiento | reasoning |
| Tool | Sistema de herramientas | tools |
| Workflow | Motor de workflows | workflows |
| Knowledge | Sistema de conocimiento | knowledge |
| Diagnostic | Motor de diagnóstico | diagnostics |

---

## 5. ESTADO DE MÓDULOS

| Estado | Módulos |
|--------|---------|
| ✅ ACTIVE | 39 |
| ⚠️ DEPRECATE | 1 (diagnostic) |
| 🔄 MERGE | 1 (workflow) |

---

*Generado por Architecture Review Board*
