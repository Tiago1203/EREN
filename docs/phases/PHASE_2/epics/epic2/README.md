# EREN Epic 2 — Context Builder

*Version 1.0 - 2026-07-20*

**Construcción de contexto para el LLM.**

Epic 2 implementa el sistema de construcción de contexto.

---

## Objetivo

Construir el contexto que recibirá el LLM desde múltiples fuentes.

---

## Dependencias

- **EPIC 0** (AI Foundation) - ✅ COMPLETO
- **EPIC 1** (Conversation) - ✅ COMPLETO

---

## Fuentes de Contexto

El Context Builder integra información de:
- **Conversation** (EPIC 1) - Mensajes y sesiones
- **Memory** (EPIC 4) - Memoria a largo plazo
- **Incidents** (FASE 1) - Incidentes activos
- **Devices** (FASE 1) - Estado de dispositivos
- **Knowledge** (FASE 1) - Artículos de conocimiento
- **User** - Perfil y preferencias
- **Hospital** - Información organizacional
- **Session** - Datos de la sesión actual

---

## Componentes Implementados ✅

### ContextBuilder ✅
Constructor principal que orquesta la construcción.

### ContextWindow ✅
- Límite de tokens configurable
- Mínimo de tokens críticos
- Items priorizados

### ContextCompressor ✅
- RemoveDuplicatesStrategy
- TrimWhitespaceStrategy
- RemoveRedundantInfoStrategy
- SummarizeStrategy
- IntelligentCompressor

### ContextPrioritizer ✅
- Scoring basado en relevancia, recencia, prioridad
- Priorización configurable
- Fill window inteligente

### ContextAssembler ✅
- Formatos: default, minimal, detailed
- Ensamblaje como mensajes API

---

## Ubicación de Implementación

```
core/ai/context_builder/
├── __init__.py           # Exports
├── models.py             # ContextItem, ContextWindow, ContextQuery
├── prioritizer.py        # ContextPrioritizer, RelevanceCalculator
├── compressor.py         # ContextCompressor, estrategias
└── builder.py           # ContextBuilder, ContextAssembler
```

---

## ADR Index

| ADR | Título | Estado |
|-----|--------|--------|
| ADR-2200 | Context Architecture | ✅ Accepted |
| ADR-2201 | Context Window | ✅ Accepted |
| ADR-2202 | Compression & Prioritization | ✅ Accepted |

---

## Uso

```python
from core.ai.context_builder import (
    ContextBuilder,
    ContextAssembler,
    ContextConfig,
    ContextQuery,
    ContextSource,
)

# Configurar
config = ContextConfig(
    default_max_tokens=8192,
    compression_enabled=True,
)

# Crear builder
builder = ContextBuilder(config=config)

# Registrar fuentes
builder.register_source(
    ContextSource.CONVERSATION,
    get_conversation_context,
)

# Construir contexto
query = ContextQuery(
    conversation_id="conv-123",
    user_id="user-456",
    max_tokens=8192,
)

result = await builder.build(query)

# Ensamblar
assembler = ContextAssembler(config)
context_text = assembler.assemble(result)
```

---

## Status

**Epic 2 Status:** ✅ COMPLETE

---

## Auditoría de Implementación

### ✅ Checklist de Verificación

| Componente | Módulo | Clase Principal | Líneas | Estado |
|------------|--------|-----------------|--------|--------|
| Models | `models.py` | ContextItem, ContextWindow, ContextQuery | 221 | ✅ |
| Prioritizer | `prioritizer.py` | ContextPrioritizer, RelevanceCalculator | 210 | ✅ |
| Compressor | `compressor.py` | ContextCompressor, estrategias | 242 | ✅ |
| Builder | `builder.py` | ContextBuilder, ContextAssembler | 315 | ✅ |

**Total: ~988 líneas de código**

### ✅ ADRs Verificados

| ADR | Título | Archivo |
|-----|--------|---------|
| ADR-2200 | Context Architecture | epic2/ADR-2200.md |
| ADR-2201 | Context Window | epic2/ADR-2201.md |
| ADR-2202 | Compression & Prioritization | epic2/ADR-2202.md |

**Total: 3 ADRs - Todos ✅ Accepted**

---

## EPIC Roadmap Status

**FASE 2 (AI Core):**

| EPIC | Status | Descripción |
|------|--------|-------------|
| EPIC 0 (AI Foundation) | ✅ COMPLETE | Kernel, Contracts, Interfaces |
| EPIC 1 (Conversation) | ✅ COMPLETE | Conversation management |
| **EPIC 2 (Context)** | ✅ COMPLETE | Context building |
| EPIC 3 (Prompt) | 🚧 NEXT | Prompt engineering |
| EPIC 4 (Memory) | PENDING | Memory system |
| EPIC 5 (Tools) | PENDING | Tool registry |
| EPIC 6 (Response) | PENDING | Response building |
| EPIC 7 (Providers) | PENDING | LLM providers |
| EPIC 8 (Sessions) | PENDING | Session management |
| EPIC 9 (AI Integration) | PENDING | Full integration |

---

*EREN Epic 2 v1.0 - Context Builder*
*Architecture Board - 2026-07-20*
