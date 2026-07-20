# EREN Epic 2 — Context

*Version 1.0 - 2026-07-20*

**Construcción de contexto cognitivo.**

Epic 2 implementa el sistema de construcción de contexto.

---

## Objetivo

Construir y mantener el contexto cognitivo para cada request.

---

## Dependencias

- **EPIC 0** (AI Foundation) - Requerido
- **EPIC 1** (Conversation) - Requerido

---

## Componentes

### Context Builder
Construcción de contexto desde múltiples fuentes.

### Context Aggregator
Agregación de información contextual.

### Context Cache
Caché de contexto para optimización.

### Context Validator
Validación de contexto construido.

---

## ADR Index

| ADR | Título | Estado |
|-----|--------|--------|
| ADR-2200 | Context Architecture | Proposed |
| ADR-2201 | Context Sources | Proposed |
| ADR-2202 | Context Aggregation | Proposed |

---

## Flujo

```
EPIC 1 (Conversation)
        │
        ▼
EPIC 2 (Context) ← ACTUAL
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

## Status

**Epic 2 Status:** PENDING

---

## EPIC Roadmap Status

**FASE 2 (AI Core):**

| EPIC | Status |
|------|--------|
| EPIC 0 (AI Foundation) | 🚧 IN PROGRESS |
| EPIC 1 (Conversation) | PENDING |
| **EPIC 2 (Context)** | 🚧 NEXT |
| EPIC 3 (Prompt) | PENDING |
| EPIC 4 (Memory) | PENDING |
| EPIC 5 (Tools) | PENDING |
| EPIC 6 (Response) | PENDING |
| EPIC 7 (Providers) | PENDING |
| EPIC 8 (Sessions) | PENDING |
| EPIC 9 (AI Integration) | PENDING |

---

*EREN Epic 2 v1.0 - Context*
*Architecture Board - 2026-07-20*
