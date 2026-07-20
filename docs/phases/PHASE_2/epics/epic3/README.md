# EREN Epic 3 — Prompt

*Version 1.0 - 2026-07-20*

**Ingeniería de prompts.**

Epic 3 implementa el sistema de construcción y optimización de prompts.

---

## Objetivo

Construir prompts efectivos para generación de respuestas.

---

## Dependencias

- **EPIC 0** (AI Foundation) - Requerido
- **EPIC 1** (Conversation) - Requerido
- **EPIC 2** (Context) - Requerido

---

## Componentes

### Prompt Builder
Construcción de prompts desde templates.

### Prompt Optimizer
Optimización de prompts basada en feedback.

### Prompt Templates
Biblioteca de templates de prompts.

### Prompt Validator
Validación de prompts construidos.

---

## ADR Index

| ADR | Título | Estado |
|-----|--------|--------|
| ADR-2300 | Prompt Architecture | Proposed |
| ADR-2301 | Template System | Proposed |
| ADR-2302 | Prompt Optimization | Proposed |

---

## Flujo

```
EPIC 2 (Context)
        │
        ▼
EPIC 3 (Prompt) ← ACTUAL
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

**Epic 3 Status:** PENDING

---

## EPIC Roadmap Status

**FASE 2 (AI Core):**

| EPIC | Status |
|------|--------|
| EPIC 0 (AI Foundation) | 🚧 IN PROGRESS |
| EPIC 1 (Conversation) | PENDING |
| EPIC 2 (Context) | PENDING |
| **EPIC 3 (Prompt)** | 🚧 NEXT |
| EPIC 4 (Memory) | PENDING |
| EPIC 5 (Tools) | PENDING |
| EPIC 6 (Response) | PENDING |
| EPIC 7 (Providers) | PENDING |
| EPIC 8 (Sessions) | PENDING |
| EPIC 9 (AI Integration) | PENDING |

---

*EREN Epic 3 v1.0 - Prompt*
*Architecture Board - 2026-07-20*
