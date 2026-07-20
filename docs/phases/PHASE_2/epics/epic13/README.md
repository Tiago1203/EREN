# EREN Epic 13 — Orchestrator

*Version 1.0 - 2026-07-20*

**El corazón de EREN.**

Epic 13 implementa el Orchestrator Engine — el sistema nervioso central que coordina todos los motores cognitivos.

---

## Purpose

El Orchestrator es responsable de:

- **Recibir** contextos cognitivos
- **Planificar** ejecuciones
- **Invocar** motores cognitivos
- **Fusionar** respuestas
- **Retornar** resultados explicables

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    ORCHESTRATOR ENGINE                               │
│                                                               │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │              COGNITIVE CONTEXT                           │ │
│  │  (Request + Tenant + Correlation + Metadata)            │ │
│  └──────────────────────────────────────────────────────────┘ │
│                          │                                   │
│                          ▼                                   │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │                  PLAN EXECUTION                          │ │
│  │  (Ordenar y ejecutar pasos del plan)                     │ │
│  └──────────────────────────────────────────────────────────┘ │
│                          │                                   │
│                          ▼                                   │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │                ENGINE INVOCATION                         │ │
│  │  (Delegar a reasoning, rag, memory, tools)               │ │
│  └──────────────────────────────────────────────────────────┘ │
│                          │                                   │
│                          ▼                                   │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │               RESPONSE MERGING                          │ │
│  │  (Fusionar respuestas de motores)                        │ │
│  └──────────────────────────────────────────────────────────┘ │
│                          │                                   │
│                          ▼                                   │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │               ORCHESTRATION RESULT                      │ │
│  │  (Output + Explicabilidad + Métricas)                  │ │
│  └──────────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────────┘
```

---

## Components

### 1. Context Receiver
Recibe y valida contextos cognitivos.

### 2. Plan Executor
Ejecuta planes generados por el Planner.

### 3. Engine Invoker
Invoca motores cognitivos específicos:
- Reasoning Engine
- RAG Pipeline
- Memory System
- Tools Registry
- Agent Runtime

### 4. Response Merger
Fusiona respuestas parciales en respuesta coherente.

### 5. Result Assembler
Ensambla el resultado final con explicabilidad.

---

## ADR Index

| ADR | Title | Status |
|-----|-------|--------|
| ADR-1300 | Orchestrator Architecture | Proposed |
| ADR-1301 | Plan Execution Model | Proposed |
| ADR-1302 | Engine Composition | Proposed |
| ADR-1303 | Response Fusion | Proposed |
| ADR-1304 | Error Handling | Proposed |
| ADR-1305 | Tracing & Observability | Proposed |

---

## Implementation Location

- `core/orchestrator/` - Main orchestrator
- `core/planner/` - Planning components
- `core/execution/` - Execution components

---

## Status

**Epic 13 Status:** PENDING

---

## EPIC Roadmap Status

**FASE 2 (AI Core):**

| EPIC | Status |
|------|--------|
| EPIC 11 (Reasoning Engine) | IN PROGRESS |
| EPIC 12 (RAG Pipeline) | PENDING |
| **EPIC 13 (Orchestrator)** | 🚧 NEXT |
| EPIC 14 (Agent Runtime) | PENDING |
| EPIC 15 (Memory & Learning) | PENDING |

---

*EREN Epic 13 v1.0 - Orchestrator*
*Architecture Board - 2026-07-20*
