# EREN FASE 2 — AI Core

*Version 1.0 - 2026-07-20*

**El motor cognitivo.**

FASE 2 implementa el Cognitive Operating System core — foundation, conversation, context, prompts, memory, tools, response, providers, sessions e integración.

---

## Overview

FASE 2 transforma EREN de una plataforma de gestión a un **Cognitive Operating System** que:

- **Foundation**: Kernel, contratos, interfaces base
- **Conversation**: Gestión de conversaciones
- **Context**: Construcción de contexto cognitivo
- **Prompt**: Ingeniería de prompts
- **Memory**: Sistema de memoria institucional
- **Tools**: Registro de herramientas ejecutables
- **Response**: Construcción de respuestas
- **Providers**: Abstracción de proveedores LLM
- **Sessions**: Gestión de sesiones de usuario
- **Integration**: Integración completa del sistema

---

## Flujo de Dependencias

```
FASE 1 (Platform) ✅
        │
        ▼
EPIC 0 (AI Foundation)
        │
        ▼
EPIC 1 (Conversation)
        │
        ▼
EPIC 2 (Context)
        │
        ▼
EPIC 3 (Prompt)
        │
        ▼
EPIC 4 (Memory)
        │
        ▼
EPIC 5 (Tools)
        │
        ▼
EPIC 6 (Response)
        │
        ├──────────────┐
        ▼                                    ▼
EPIC 7 (Providers)                  EPIC 8 (Sessions)
        │                                     │
        └──────┬───────┘
                          ▼
        EPIC 9 (AI Integration)
               │
               ▼
    EPIC 10 (Domain Integration Layer)
               │
               ▼
        ┌──────┴──────┐
        ▼             ▼
    EPIC 11-1    EPIC 11-2
    (Runtime Fix)  (Runtime Int.)
        │             │
        └──────┬──────┘
               ▼
        ┌─────────────┐
        │  FASE 3    │
        │Clinical Int.│
        └─────────────┘
```

---

## Épicas

| Épica | Nombre | Descripción | Estado |
|-------|--------|-------------|--------|
| **EPIC 0** | AI Foundation | Kernel, Contracts, Interfaces | ✅ COMPLETE |
| **EPIC 1** | Conversation | Gestión de conversaciones | ✅ COMPLETE |
| **EPIC 2** | Context | Construcción de contexto | ✅ COMPLETE |
| **EPIC 3** | Prompt | Ingeniería de prompts | ✅ COMPLETE |
| **EPIC 4** | Memory | Sistema de memoria | ✅ COMPLETE |
| **EPIC 5** | Tools | Registro de herramientas | ✅ COMPLETE |
| **EPIC 6** | Response | Construcción de respuestas | ✅ COMPLETE |
| **EPIC 7** | Providers | Abstracción LLM | ✅ COMPLETE |
| **EPIC 8** | Sessions | Gestión de sesiones | ✅ COMPLETE |
| **EPIC 9** | AI Integration | Integración completa | ✅ COMPLETE |
| **EPIC 10** | Domain Integration Layer | Conectar AI Core con Dominio | ✅ COMPLETE |
| **EPIC 11-1** | Runtime Fix Phase 2 | Bug fixes y estabilización | ✅ COMPLETE |
| **EPIC 11-2** | Runtime Integration | AI Core ↔ Business Domain | ✅ COMPLETE |

---

## Arquitectura General

```
┌─────────────────────────────────────────────────────────────┐
│                    AI CORE                                         │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              AI FOUNDATION (EPIC 0)                     │ │
│  │         Kernel, Contracts, Interfaces, DTOs              │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                               │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────┐ │
│  │ CONVERSATION│ │   CONTEXT    │ │       PROMPT         │ │
│  │   (EPIC 1)  │ │   (EPIC 2)  │ │      (EPIC 3)        │ │
│  └──────────────┘ └──────────────┘ └──────────────────────┘ │
│                                                               │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────┐ │
│  │    MEMORY    │ │    TOOLS    │ │      RESPONSE        │ │
│  │   (EPIC 4)   │ │   (EPIC 5)  │ │      (EPIC 6)        │ │
│  └──────────────┘ └──────────────┘ └──────────────────────┘ │
│                                                               │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────┐ │
│  │  PROVIDERS   │ │  SESSIONS   │ │    INTEGRATION       │ │
│  │   (EPIC 7)   │ │  (EPIC 8)   │ │      (EPIC 9)        │ │
│  └──────────────┘ └──────────────┘ └──────────────────────┘ │
└───────────────────────────────────────────────────────────────┘
```

---

## Ubicación de Implementación

```
core/
├── ai/                          # AI Core
│   ├── foundation/              # EPIC 0: AI Foundation
│   ├── conversation/           # EPIC 1: Conversation
│   ├── context/                # EPIC 2: Context
│   ├── prompt/                 # EPIC 3: Prompt
│   ├── memory/                 # EPIC 4: Memory
│   ├── tools/                  # EPIC 5: Tools
│   ├── response/               # EPIC 6: Response
│   ├── providers/              # EPIC 7: Providers
│   ├── sessions/               # EPIC 8: Sessions
│   └── integration/            # EPIC 9: Integration
```

---

## ADR Index

Ver `adr/README.md` para 36 ADRs de arquitectura.

---

## ✅ EPIC 10: Domain Integration Bridge - IMPLEMENTADO

> **IMPLEMENTADO**: EPIC 10 conecta el AI Core con el Business Domain de FASE 1.

### Componentes Implementados

| Componente | Descripción |
|-----------|-------------|
| `AIUnitOfWorkFactory` | Factory para UnitOfWork desde AI Core |
| `DomainGatewayAdapter` | Crea gateways conectados al dominio real |
| `DeviceGatewayImpl` | Gateway de dispositivos con datos reales |
| `IncidentGatewayImpl` | Gateway de incidentes con datos reales |
| `KnowledgeGatewayImpl` | Gateway de conocimiento con datos reales |
| `RecommendationGatewayImpl` | Gateway de recomendaciones |
| `HospitalGatewayImpl` | Gateway de hospital/capacidad |
| `WorkOrderGatewayImpl` | Gateway de órdenes de trabajo |
| `MemoryBridge` | Almacena referencias a entidades del dominio |
| `EventBridge` | Conecta eventos de AI con Event Bus |

### Arquitectura de Integración

```
AI CORE (FASE 2)
Conversation → Memory → Context → Prompt → Tools → Response
                            │
                    DomainGateways
                            │
                     UnitOfWork
                                    │
                                    ▼
BUSINESS DOMAIN (FASE 1)
Device │ Incident │ Knowledge │ Recommendation │ Hospital
Repository Interfaces + Entities + Domain Events
```

### Ubicación de Implementación

```
core/ai/integration/
├── __init__.py          # Exports + setup_integration()
├── uow_factory.py       # AIUnitOfWorkFactory
├── domain_adapter.py     # DomainGatewayAdapter + Impls
├── memory_bridge.py      # MemoryBridge
└── event_bridge.py      # EventBridge
```

### Documentación

- [EPIC 10 README](epics/epic10-domain-bridge/README.md) - Descripción completa
- [EPIC 10 ADRs](adr/epic10-domain-bridge/) - 5 ADRs de diseño

---

## ✅ EPIC 11: Runtime Integration - IMPLEMENTADO

> **IMPLEMENTADO**: EPIC 11 conecta el AI Core con el Business Domain.

### Componentes Implementados

| Componente | Descripción |
|-----------|-------------|
| Domain Gateway Adapter | Factory de gateways conectados al dominio |
| Device Gateway | Gateway de dispositivos |
| Incident Gateway | Gateway de incidentes |
| Knowledge Gateway | Gateway de conocimiento |
| Memory Bridge | Almacena referencias a entidades del dominio |
| Event Bridge | Conecta eventos de AI con Event Bus |

### Documentación

- [EPIC 11 README](epics/epic11-runtime-integration/README.md) - Descripción completa

---

## ✅ EPIC 11-2: Runtime Fix Phase 2 - IMPLEMENTADO

> **IMPLEMENTADO**: EPIC 11-2 corrige bugs críticos y completa módulos faltantes.

### Bugs Corregidos

| Bug | Descripción | Severidad |
|-----|-------------|-----------|
| SessionEvent Naming Conflict | Dataclass sobrescribía Enum | 🔴 Crítica |
| PromptConfig API | Parámetros incorrectos en tests | 🟡 Media |
| BaseContextProvider Tests | Métodos abstractos sin implementar | 🟡 Media |
| IncidentGateway Mock | Sintaxis incorrecta `list(a, b)` | 🟡 Media |
| GetDeviceHistoryTool Test | Referencia incorrecta `_gateway` | 🟢 Baja |

### Módulos Completados

| Módulo | Descripción |
|--------|-------------|
| `core/ingestion/metadata.py` | MetadataBuilder, MedicalMetadataBuilder |
| `core/session/__init__.py` | Exports de SessionPolicies, SessionMetricsCollector |

### Resultados

| Métrica | Antes | Después |
|---------|-------|---------|
| Tests Fallando | 12 | 0 |
| Tests Pasando | 65 | 77+ |
| AI Core Tests | ❌ | ✅ |

### Documentación

- [EPIC 11-2 README](epics/epic11-2-runtime-fix-phase2/README.md) - Descripción completa
- [ADR-2113](adr/epic11-2-runtime-fix-phase2/ADR-2113.md) - SessionEvent Naming Conflict

---

## Status

**FASE 2 Status:** COMPLETE ✅

**FASE 2 está listo para producción con integración completa al dominio.**

---

## Código Fuente

El código de FASE 2 se encuentra en:

```
core/PHASE_2/
├── ai/                    # Kernel de IA
├── agents/               # Sistema de agentes
├── context/              # Context Builder
├── embeddings/           # Sistema de embeddings
├── execution/            # Motor de ejecución
├── ingestion/            # Ingesta de datos
├── memory/               # Sistema de memoria
├── orchestration/       # Orquestación
│   ├── orchestrator/    # Orquestador principal
│   └── orchestration/   # Componentes de orquestación
├── pipeline/             # Pipeline de datos
├── planner/              # Planificador
│   ├── planner/         # Planificador principal
│   └── planning/         # Componentes de planificación
├── providers/            # Proveedores LLM
├── rag/                  # RAG Pipeline
├── registry/             # Registro de servicios
├── retrieval/            # Motor de recuperación
├── session/              # Gestión de sesiones
├── runtime/              # Runtime
├── router/               # Enrutador
├── intent/               # Detección de intención
├── capabilities/         # Sistema de capacidades
├── cognitive/            # Motor cognitivo
├── plugins/              # Sistema de plugins
├── scheduler/            # Planificador
├── sdk/                  # SDK
├── decision/              # Motor de decisión
├── learning/              # Motor de aprendizaje
└── reasoning/            # Motor de razonamiento
```

Los tests correspondientes se encuentran en:

```
tests/unit/PHASE_2/
├── ai/               # Tests del kernel de IA
├── agents/           # Tests de agentes
├── context/          # Tests de context
├── embeddings/       # Tests de embeddings
├── execution/        # Tests de ejecución
├── ingestion/        # Tests de ingesta
├── memory/           # Tests de memoria
├── orchestration/    # Tests de orquestación
├── pipeline/        # Tests de pipeline
├── planner/         # Tests de planner
├── providers/       # Tests de providers
├── rag/             # Tests de RAG
├── registry/        # Tests de registry
├── retrieval/       # Tests de retrieval
└── session/        # Tests de sesión
```

---

## Quick Start

```python
from core.PHASE_2.ai.foundation import AIKernel

# Initialize AI Core
kernel = AIKernel()

# Start orchestration
result = await kernel.process(request)
```

---

---

## Actualización

*Última actualización: 2026-07-22*
- Corregidas rutas anticuadas en documentación (`core.ai.*` → `core.PHASE_2.ai.*`)
- Eliminados EPICs 11-15 inválidos (eran obsoletos, los válidos son 11-1, 11-2, 11-runtime)

---

*EREN FASE 2 v1.1 - AI Core*
*Architecture Board - 2026-07-22*
