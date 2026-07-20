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

## Status

**FASE 2 Status:** IN PROGRESS 🚧

**Próximo:** EPIC 0 (AI Foundation)

---

## Quick Start

```python
from core.ai.foundation import AIKernel

# Initialize AI Core
kernel = AIKernel()

# Start orchestration
result = await kernel.process(request)
```

---

*EREN FASE 2 v1.0 - AI Core*
*Architecture Board - 2026-07-20*
