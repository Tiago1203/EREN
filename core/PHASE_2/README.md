# FASE 2: AI Core

## Descripción

FASE 2 implementa el Cognitive Operating System de EREN. Aquí se encuentran todos los componentes de inteligencia artificial, incluyendo el kernel de IA, sistema de agentes, memoria, orquestación, proveedores LLM, y RAG.

## Estructura

```
core/PHASE_2/
├── README.md                    # Este archivo
│
├── ai/                        # Kernel de IA (EPIC 1-3)
│
├── agents/                    # Sistema de agentes (EPIC 4)
│
├── context/                   # Context Builder (EPIC 2)
│
├── embeddings/                # Sistema de embeddings (EPIC 4)
│
├── execution/                 # Motor de ejecución (EPIC 1)
│
├── ingestion/                 # Ingesta de datos (EPIC 1)
│
├── memory/                    # Sistema de memoria (EPIC 4)
│
├── orchestration/             # Orquestación
│   ├── orchestrator/         # Orquestador principal
│   └── orchestration/        # Componentes de orquestación
│
├── pipeline/                  # Pipeline de datos (EPIC 2)
│
├── planner/                   # Planificador
│   ├── planner/              # Planificador principal
│   └── planning/            # Componentes de planificación
│
├── providers/                 # Proveedores LLM (EPIC 4)
│
├── rag/                      # RAG Pipeline (EPIC 4)
│
├── registry/                 # Registro de servicios (EPIC 4)
│
├── retrieval/                # Motor de recuperación (EPIC 4)
│
├── session/                  # Gestión de sesiones (EPIC 1)
│
├── runtime/                  # Runtime
│
├── router/                   # Enrutador (EPIC 4)
│
├── intent/                   # Detección de intención (EPIC 2)
│
├── capabilities/             # Sistema de capacidades
│
├── cognitive/                # Motor cognitivo
│
├── plugins/                  # Sistema de plugins
│
├── scheduler/                # Planificador
│
├── sdk/                      # SDK
│
├── decision/                 # Motor de decisión
│
├── learning/                 # Motor de aprendizaje
│
└── reasoning/                # Motor de razonamiento
```

## EPICs Incluidos

| EPIC | Nombre | Descripción |
|------|--------|-------------|
| EPIC 1 | AI Foundation | Kernel, Contracts, Interfaces |
| EPIC 2 | Conversation | Gestión de conversaciones |
| EPIC 3 | Context | Construcción de contexto |
| EPIC 4 | Prompt | Ingeniería de prompts |
| EPIC 5 | Memory | Sistema de memoria |
| EPIC 6 | Tools | Registro de herramientas |
| EPIC 7 | Response | Construcción de respuestas |
| EPIC 8 | Providers | Abstracción LLM |
| EPIC 9 | Sessions | Gestión de sesiones |
| EPIC 10 | AI Integration | Integración completa |
| EPIC 11 | Domain Integration Bridge | Infraestructura de integración |
| EPIC 11-2 | Runtime Fix Phase 2 | Bug fixes y estabilización |

## Tests

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
├── session/        # Tests de sesión
└── [otros módulos]
```

## Documentación Relacionada

- [docs/phases/PHASE_2/](../../docs/phases/PHASE_2/)
- [docs/phases/PHASE_2/epics/](../../docs/phases/PHASE_2/epics/)
- [docs/phases/PHASE_2/adr/](../../docs/phases/PHASE_2/adr/)

---

*Última actualización: 2026-07-22*
