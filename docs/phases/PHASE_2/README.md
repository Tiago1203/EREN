# EREN FASE 2 — AI Core

*Version 1.0 - 2026-07-20*

**El motor cognitivo.**

FASE 2 implementa el Cognitive Operating System core — reasoning, orchestration, agents, y RAG.

---

## Overview

FASE 2 transforma EREN de una plataforma de gestión a un **Cognitive Operating System** que:

- **Razona** sobre evidencia para generar conclusiones explicables
- **Orquesta** múltiples motores cognitivos de forma coordinada
- **Ejecuta** agentes especializados que colaboran
- **Recupera** conocimiento relevante para cada contexto
- **Memorializa** interacciones para aprendizaje continuo

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    COGNITIVE OPERATING SYSTEM                        │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                   ORCHESTRATOR ENGINE                   │ │
│  │              (Coordina todos los motores)               │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                               │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────┐ │
│  │   REASONING  │ │     RAG      │ │     AGENTS           │ │
│  │    ENGINE    │ │   PIPELINE   │ │     RUNTIME          │ │
│  └──────────────┘ └──────────────┘ └──────────────────────┘ │
│                                                               │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────┐ │
│  │    MEMORY    │ │     LLM      │ │     TOOLS            │ │
│  │    SYSTEM    │ │   PROVIDER   │ │     REGISTRY         │ │
│  └──────────────┘ └──────────────┘ └──────────────────────┘ │
└───────────────────────────────────────────────────────────────┘
```

---

## Épicas

| Épica | Nombre | Descripción |
|-------|--------|-------------|
| **EPIC 11** | Reasoning Engine | Motor de razonamiento explicable |
| **EPIC 12** | RAG Pipeline | Pipeline de retrieval augmentation |
| **EPIC 13** | Orchestrator | Motor de orquestación cognitiva |
| **EPIC 14** | Agent Runtime | Runtime de agentes cognitivos |
| **EPIC 15** | Memory & Learning | Sistema de memoria y aprendizaje |

---

## Components

### EPIC 11 - Reasoning Engine
- Evidence-based reasoning
- Chain-of-thought reasoning
- Confidence scoring
- Explainability layer

### EPIC 12 - RAG Pipeline
- Hybrid retrieval (dense + sparse)
- Semantic chunking
- Reranking
- Citation building

### EPIC 13 - Orchestrator
- Plan execution
- Engine composition
- Response merging
- Error handling

### EPIC 14 - Agent Runtime
- Agent registry
- Task scheduling
- Inter-agent communication
- Health monitoring

### EPIC 15 - Memory & Learning
- Short-term memory
- Long-term memory
- Episodic memory
- Feedback learning

---

## Dependencies

**DEPENDE de:** FASE 1 (Completa)

**PREREQ de:** FASE 3 (Production AI)

---

## Status

**FASE 2 Status:** IN PROGRESS 🚧

---

## Quick Start

```python
from core.orchestrator import OrchestratorEngine
from core.agents import get_agent_runtime

# Create orchestrator
orchestrator = OrchestratorEngine()

# Get agent runtime
runtime = get_agent_runtime()

# Start orchestration
result = await orchestrator.orchestrate(context)
```

---

## ADR Index

Ver `adr/README.md` para arquitectura de decisiones.

---

*EREN FASE 2 v1.0 - AI Core*
*Architecture Board - 2026-07-20*
