# EREN Epic 1 — Conversation

*Version 1.0 - 2026-07-20*

**Gestión de conversaciones cognitivas.**

Epic 1 implementa el sistema de conversación del AI Core.

---

## Objetivo

Gestionar conversaciones entre usuarios y el sistema cognitivo.

---

## Dependencias

- **EPIC 0** (AI Foundation) - Requerido

---

## Componentes

### Conversation Manager
Gestión de conversaciones activas.

### Conversation State
Estado de cada conversación.

### Message Handler
Manejo de mensajes entrantes/salientes.

### Turn Tracker
Seguimiento de turnos de conversación.

---

## ADR Index

| ADR | Título | Estado |
|-----|--------|--------|
| ADR-2100 | Conversation Architecture | Proposed |
| ADR-2101 | Conversation State | Proposed |
| ADR-2102 | Message Format | Proposed |

---

## Flujo

```
EPIC 0 (AI Foundation)
        │
        ▼
EPIC 1 (Conversation) ← ACTUAL
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

## Status

**Epic 1 Status:** PENDING

---

## EPIC Roadmap Status

**FASE 2 (AI Core):**

| EPIC | Status |
|------|--------|
| EPIC 0 (AI Foundation) | 🚧 IN PROGRESS |
| **EPIC 1 (Conversation)** | 🚧 NEXT |
| EPIC 2 (Context) | PENDING |
| EPIC 3 (Prompt) | PENDING |
| EPIC 4 (Memory) | PENDING |
| EPIC 5 (Tools) | PENDING |
| EPIC 6 (Response) | PENDING |
| EPIC 7 (Providers) | PENDING |
| EPIC 8 (Sessions) | PENDING |
| EPIC 9 (AI Integration) | PENDING |

---

*EREN Epic 1 v1.0 - Conversation*
*Architecture Board - 2026-07-20*
