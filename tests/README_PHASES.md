# Tests by Phase

Este directorio contiene los tests organizados por fase, siguiendo la misma estructura que `core/`.

## Estructura

```
tests/
├── README_PHASES.md            # Este archivo
├── README.md                    # Documentación general
├── conftest.py                # Configuración de pytest
│
├── unit/
│   ├── PHASE_1/               # Tests de Business Domain
│   │   ├── domain/           # Tests de entidades
│   │   ├── infrastructure/   # Tests de infraestructura
│   │   ├── clinical/        # Tests clínicos
│   │   ├── application/     # Tests de aplicación
│   │   └── workflows/       # Tests de workflows
│   │
│   ├── PHASE_2/             # Tests de AI Core
│   │   ├── ai/             # Tests del kernel de IA
│   │   ├── agents/         # Tests de agentes
│   │   ├── context/        # Tests de context
│   │   ├── embeddings/     # Tests de embeddings
│   │   ├── execution/      # Tests de ejecución
│   │   ├── ingestion/      # Tests de ingesta
│   │   ├── memory/         # Tests de memoria
│   │   ├── orchestration/  # Tests de orquestación
│   │   ├── pipeline/      # Tests de pipeline
│   │   ├── planner/       # Tests de planner
│   │   ├── providers/     # Tests de providers
│   │   ├── rag/           # Tests de RAG
│   │   ├── registry/       # Tests de registry
│   │   ├── retrieval/      # Tests de retrieval
│   │   ├── session/       # Tests de sesión
│   │   └── [otros módulos]
│   │
│   ├── PHASE_3/             # Tests de Clinical Intelligence
│   │   ├── intelligence/    # Tests de motores de inteligencia
│   │   │   ├── foundation/    # Tests de foundation
│   │   │   ├── confidence/    # Tests de confidence
│   │   │   ├── decision/      # Tests de decision
│   │   │   ├── evidence/      # Tests de evidence
│   │   │   ├── explainability/ # Tests de explainability
│   │   │   ├── improvement/   # Tests de improvement
│   │   │   ├── knowledge/     # Tests de knowledge
│   │   │   ├── learning/      # Tests de learning
│   │   │   ├── reasoning/     # Tests de reasoning
│   │   │   ├── rules/         # Tests de rules
│   │   │   ├── safety/        # Tests de safety
│   │   │   └── validation/    # Tests de validation
│   │   ├── integrations/    # Tests de integraciones
│   │   ├── embeddings/      # Tests de embeddings
│   │   ├── clinical/        # Tests clínicos
│   │   ├── recommendation/ # Tests de recomendación
│   │   └── knowledge_assets/ # Tests de knowledge assets
│   │
│   ├── SHARED/              # Tests compartidos
│   │
│   └── LEGACY/              # Tests de módulos huérfanos
│       ├── collaboration/
│       └── tools/
│
├── integration/
│   ├── PHASE_1/             # Tests de integración FASE 1
│   ├── PHASE_2/             # Tests de integración FASE 2
│   └── PHASE_3/             # Tests de integración FASE 3
│
├── ai_core/                  # Tests de AI Core
├── runtime/                  # Tests de runtime
└── plugins/                 # Tests de plugins
```

## Mapeo de Tests a Código

| Carpeta Tests | Carpeta Código | Fase |
|--------------|----------------|------|
| `unit/PHASE_1/` | `core/PHASE_1/` | PHASE 1 |
| `unit/PHASE_2/` | `core/PHASE_2/` | PHASE 2 |
| `unit/PHASE_3/` | `core/PHASE_3/` | PHASE 3 |
| `unit/LEGACY/` | `core/LEGACY/` | LEGACY |
| `unit/SHARED/` | `core/shared/` | SHARED |

## Ejecución de Tests

### Todos los tests
```bash
pytest tests/
```

### Tests por fase
```bash
# PHASE 1
pytest tests/unit/PHASE_1/

# PHASE 2
pytest tests/unit/PHASE_2/

# PHASE 3
pytest tests/unit/PHASE_3/

# LEGACY
pytest tests/unit/LEGACY/
```

### Tests de integración
```bash
pytest tests/integration/
```

## Documentación Relacionada

- [core/PHASE_1/](../core/PHASE_1/) - Código de FASE 1
- [core/PHASE_2/](../core/PHASE_2/) - Código de FASE 2
- [core/PHASE_3/](../core/PHASE_3/) - Código de FASE 3
- [core/LEGACY/](../core/LEGACY/) - Código LEGACY
- [docs/phases/](../docs/phases/) - Documentación por fases

---

*Última actualización: 2026-07-22*
