# core/

The **cognitive core** of EREN — the domain and cognition layer that makes
EREN a Cognitive Operating System rather than an application.

## Structure by Phase

```
core/
├── PHASE_1/                 # Business Domain
│   ├── domain/             # Entidades de negocio (Asset, Device, Incident, etc.)
│   ├── infrastructure/     # Infraestructura (Events, Shared, etc.)
│   ├── clinical/           # Clínica
│   ├── application/         # Servicios de aplicación
│   └── workflows/          # Flujos de trabajo
│
├── PHASE_2/                 # AI Core
│   ├── ai/                # Kernel de IA
│   ├── agents/            # Sistema de agentes
│   ├── context/           # Context Builder
│   ├── embeddings/        # Embeddings
│   ├── execution/         # Motor de ejecución
│   ├── ingestion/         # Ingesta de datos
│   ├── memory/            # Sistema de memoria
│   ├── orchestration/    # Orquestación
│   ├── pipeline/         # Pipeline de datos
│   ├── planner/          # Planificador
│   ├── providers/        # Proveedores LLM
│   ├── rag/              # RAG Pipeline
│   ├── registry/         # Registro de servicios
│   ├── retrieval/        # Motor de recuperación
│   ├── session/          # Gestión de sesiones
│   └── [otros módulos]
│
├── PHASE_3/                 # Clinical Intelligence
│   ├── intelligence/       # Motores de inteligencia clínica
│   │   ├── foundation/    # EPIC 0: Foundation
│   │   ├── confidence/   # EPIC 4: Confidence Engine
│   │   ├── decision/     # EPIC 9: Decision Engine
│   │   ├── evidence/     # EPIC 3: Evidence Retrieval
│   │   ├── explainability/ # EPIC 5: Explainability
│   │   ├── improvement/ # EPIC 11: Improvement
│   │   ├── knowledge/    # EPIC 1: Knowledge Engine
│   │   ├── learning/     # EPIC 10: Learning Engine
│   │   ├── reasoning/    # EPIC 2: Reasoning Engine
│   │   ├── rules/        # EPIC 6: Rules Engine
│   │   ├── safety/       # EPIC 7: Safety Engine
│   │   └── validation/   # EPIC 8: Validation
│   ├── integrations/     # Integraciones
│   └── embeddings/       # Embeddings clínicos
│
├── PHASE_4/                 # Knowledge Infrastructure
│   ├── embeddings/          # Clinical Embeddings
│   ├── qdrant/             # Vector DB Integration
│   ├── knowledge/           # Knowledge Retrieval
│   ├── rag/                # Clinical RAG Pipeline
│   └── citations/          # Citation Engine

└── LEGACY/                  # Módulos sin clasificar
    ├── collaboration/
    └── tools/
```

## Fases

| Fase | Descripción | Ubicación |
|------|-------------|-----------|
| PHASE_1 | Business Domain | Entidades de negocio, Infraestructura | [Ver README](./PHASE_1/README.md) |
| PHASE_2 | AI Core | Kernel de IA, Memoria, Agentes, RAG | [Ver README](./PHASE_2/README.md) |
| PHASE_3 | Clinical Intelligence | Motores de inteligencia clínica | [Ver README](./PHASE_3/README.md) |
| PHASE_4 | Knowledge Infrastructure | Embeddings, Qdrant, Retrieval, RAG, Citations | [Ver README](./PHASE_4/README.md) |
| LEGACY | Sin clasificar | Módulos huérfanos | [Ver README](./LEGACY/README.md) |

## Engines (FASE 1-2)

| Engine | Phase | Responsibility |
| --- | --- | --- |
| [`orchestrator/`](./PHASE_2/orchestrator) | PHASE_2 | Coordinates engines and manages the cognitive request lifecycle. |
| [`planner/`](./PHASE_2/planner) | PHASE_2 | Decomposes goals into executable, ordered steps. |
| [`reasoning/`](./PHASE_2/reasoning) | PHASE_2 | Explainable reasoning strategies over evidence. |
| [`memory/`](./PHASE_2/memory) | PHASE_2 | Short- and long-term institutional memory. |
| [`diagnostic/`](./PHASE_1/infrastructure/diagnostic) | PHASE_1 | Clinical-engineering fault analysis and troubleshooting. |
| [`workflow/`](./PHASE_1/workflows/workflow) | PHASE_1 | Long-running multi-step operational processes. |
| [`knowledge/`](./PHASE_1/domain/knowledge) | PHASE_1 | Structures and serves institutional knowledge. |
| [`tools/`](./LEGACY/tools) | LEGACY | Registry/adapters for controlled capabilities and integrations. |

## Clinical Intelligence Engines (FASE 3)

| Engine | EPIC | Responsibility |
| --- | --- | --- |
| [`foundation/`](./PHASE_3/intelligence/foundation) | EPIC 0 | DTOs, Contracts, Models, Interfaces |
| [`knowledge/`](./PHASE_3/intelligence/knowledge) | EPIC 1 | Biomedical Knowledge Graph |
| [`reasoning/`](./PHASE_3/intelligence/reasoning) | EPIC 2 | Clinical Reasoning |
| [`evidence/`](./PHASE_3/intelligence/evidence) | EPIC 3 | Evidence Retrieval |
| [`confidence/`](./PHASE_3/intelligence/confidence) | EPIC 4 | Confidence Scoring |
| [`explainability/`](./PHASE_3/intelligence/explainability) | EPIC 5 | Explainability |
| [`rules/`](./PHASE_3/intelligence/rules) | EPIC 6 | Clinical Rules |
| [`safety/`](./PHASE_3/intelligence/safety) | EPIC 7 | Safety Engine |
| [`validation/`](./PHASE_3/intelligence/validation) | EPIC 8 | Clinical Validation |
| [`decision/`](./PHASE_3/intelligence/decision) | EPIC 9 | Decision Engine |
| [`learning/`](./PHASE_3/intelligence/learning) | EPIC 10 | Learning Engine |
| [`improvement/`](./PHASE_3/intelligence/improvement) | EPIC 11 | Continuous Improvement |

## Dependency rules

- `core/*` may depend on `packages/*` (shared contracts/utilities).
- `core/*` must **not** depend on `apps/*`.
- Cross-engine calls go **through** the orchestrator where possible.

## Documentación

Ver [docs/phases/](../../docs/phases/) para documentación detallada por fase.

---

*Última actualización: 2026-07-23*
