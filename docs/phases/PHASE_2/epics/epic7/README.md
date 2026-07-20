# EREN Epic 7 — Providers

*Version 1.0 - 2026-07-20*

**Abstracción de proveedores LLM.**

Epic 7 implementa la capa de proveedores de IA.

---

## Objetivo

Abstraer la comunicación con múltiples proveedores LLM.

---

## Dependencias

- **EPIC 0** (AI Foundation) - Requerido
- **EPIC 6** (Response) - Requerido

---

## Componentes

### Provider Base
Clase base para providers.

### OpenAI Provider
Implementación para OpenAI.

### Anthropic Provider
Implementación para Anthropic.

### Azure Provider
Implementación para Azure OpenAI.

### Provider Router
Enrutador de requests a providers.

### Rate Limiter
Limitador de tasa de requests.

---

## ADR Index

| ADR | Título | Estado |
|-----|--------|--------|
| ADR-2700 | Provider Architecture | Proposed |
| ADR-2701 | Provider Interface | Proposed |
| ADR-2702 | Rate Limiting | Proposed |

---

## Flujo

```
EPIC 6 (Response)
        │
        ▼
EPIC 7 (Providers) ← ACTUAL
        │
        └──────┐
               │
               ▼
        (se une con EPIC 8)
               │
               ▼
        EPIC 9 (AI Integration)
```

---

## Status

**Epic 7 Status:** PENDING

---

## EPIC Roadmap Status

**FASE 2 (AI Core):**

| EPIC | Status |
|------|--------|
| EPIC 0 (AI Foundation) | 🚧 IN PROGRESS |
| EPIC 1 (Conversation) | PENDING |
| EPIC 2 (Context) | PENDING |
| EPIC 3 (Prompt) | PENDING |
| EPIC 4 (Memory) | PENDING |
| EPIC 5 (Tools) | PENDING |
| EPIC 6 (Response) | PENDING |
| **EPIC 7 (Providers)** | 🚧 NEXT |
| EPIC 8 (Sessions) | PENDING |
| EPIC 9 (AI Integration) | PENDING |

---

*EREN Epic 7 v1.0 - Providers*
*Architecture Board - 2026-07-20*
