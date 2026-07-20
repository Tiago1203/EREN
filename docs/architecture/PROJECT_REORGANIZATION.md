# EREN - Propuesta de Reorganización

**Fecha:** 2026-07-20  
**Estado:** Propuesta  
**Versión:** 1.0

---

## 1. DIAGNÓSTICO ACTUAL

### 1.1 Problemas Identificados

| # | Problema | Impacto |
|---|----------|---------|
| 1 | `core/` y `apps/api/app/` tienen código duplicado/separado | Confusión |
| 2 | `core/` no está integrado con la API | No funciona |
| 3 | 57 carpetas en `core/` sin uso claro | Complejidad |
| 4 | Documentación dispersa en root y docs/ | Dificultad |
| 5 | AI Layer en ambos lugares (`core/` y `apps/api/app/ai/`) | Duplicación |

### 1.2 Estado Actual de Código

```
EREN/
├── core/                          ← ⚠️ 57 carpetas, NO integrado
│   ├── cognitive/                 ← AI real (~2000 líneas)
│   ├── clinical/                 ← Clinical real (~1000 líneas)
│   ├── integrations/             ← FHIR/HL7/etc real
│   ├── memory/                   ← Memory real (~4000 líneas)
│   ├── reasoning/                ← Reasoning real (~3000 líneas)
│   ├── device/                   ← Domain (duplicado)
│   ├── incident/                 ← Domain (duplicado)
│   └── ...
│
├── apps/api/app/                 ← ✅ Integrado
│   ├── ai/                       ← ❌ Stubs (no se usa)
│   ├── clinical/                 ← ❌ Stubs (no se usa)
│   ├── integrations/             ← ❌ Stubs (no se usa)
│   ├── domain/                   ← ✅ Domain (SÍ se usa)
│   ├── infrastructure/           ← ✅ Repos, Outbox, UoW
│   └── routers/                  ← ✅ Endpoints
│
├── docs/                          ← Documentación dispersa
│   ├── *.md (10 archivos root)   ← ❌ deberían estar en docs/
│   ├── epic0/...epic10/         ← ✅ Bien organizados
│   ├── adr/                     ← ✅ Bien organizado
│   └── core/                     ← ⚠️ Documentación de código legacy
│
└── [root *.md]                    ← ❌ Confuso
```

---

## 2. ESTRUCTURA PROPUESTA

### 2.1 Estructura Final por Fases

```
EREN/
├── apps/
│   ├── api/
│   │   ├── app/
│   │   │   ├── __init__.py
│   │   │   ├── main.py                    # FastAPI entry point
│   │   │   │
│   │   │   ├── core/                      # FASE 1: Infraestructura base
│   │   │   │   ├── __init__.py
│   │   │   │   ├── database.py            # SQLAlchemy setup
│   │   │   │   ├── exceptions.py          # Custom exceptions
│   │   │   │   └── logging.py             # Logging config
│   │   │   │
│   │   │   ├── config/                    # FASE 1: Configuración
│   │   │   │   ├── __init__.py
│   │   │   │   └── settings.py            # Pydantic settings
│   │   │   │
│   │   │   ├── domain/                   # FASE 1: Bounded Contexts (DDD)
│   │   │   │   ├── __init__.py
│   │   │   │   ├── shared/                # Shared Kernel (Patient)
│   │   │   │   │   ├── models.py
│   │   │   │   │   ├── schemas.py
│   │   │   │   │   └── repositories.py
│   │   │   │   ├── device/                # Device Context
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── entities.py
│   │   │   │   │   ├── value_objects.py
│   │   │   │   │   ├── services.py
│   │   │   │   │   ├── repositories.py
│   │   │   │   │   ├── events.py
│   │   │   │   │   └── routers.py
│   │   │   │   ├── incident/              # Incident Context
│   │   │   │   ├── recommendation/        # Recommendation Context
│   │   │   │   ├── knowledge/             # Knowledge Context
│   │   │   │   ├── work_order/           # Work Order Context
│   │   │   │   ├── capacity/             # Hospital Capacity
│   │   │   │   ├── staffing/             # Staffing
│   │   │   │   ├── organization/         # Organization
│   │   │   │   ├── department/           # Department
│   │   │   │   ├── inventory/           # Inventory
│   │   │   │   └── asset/               # Asset
│   │   │   │
│   │   │   ├── schemas/                 # FASE 1: Pydantic DTOs
│   │   │   │   ├── __init__.py
│   │   │   │   ├── device.py
│   │   │   │   ├── incident.py
│   │   │   │   ├── patient.py
│   │   │   │   └── ...
│   │   │   │
│   │   │   ├── models/                   # FASE 1: SQLAlchemy ORM
│   │   │   │   ├── __init__.py
│   │   │   │   ├── base.py
│   │   │   │   ├── device.py
│   │   │   │   ├── patient.py
│   │   │   │   └── ...
│   │   │   │
│   │   │   ├── routers/                  # FASE 1: API Endpoints
│   │   │   │   ├── __init__.py
│   │   │   │   ├── devices.py
│   │   │   │   ├── incidents.py
│   │   │   │   ├── patients.py
│   │   │   │   └── ...
│   │   │   │
│   │   │   ├── infrastructure/           # FASE 1: Cross-cutting
│   │   │   │   ├── __init__.py
│   │   │   │   ├── repositories/         # Repository implementations
│   │   │   │   │   ├── device.py
│   │   │   │   │   ├── incident.py
│   │   │   │   │   └── ...
│   │   │   │   ├── events/              # Outbox pattern
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── outbox.py
│   │   │   │   │   └── publisher.py
│   │   │   │   ├── messaging/           # RabbitMQ
│   │   │   │   ├── observability/       # OpenTelemetry
│   │   │   │   ├── unit_of_work.py
│   │   │   │   └── vault/              # Secrets
│   │   │   │
│   │   │   ├── middleware/              # FASE 1: Auth, CORS, etc
│   │   │   │   ├── __init__.py
│   │   │   │   ├── auth.py
│   │   │   │   ├── audit.py
│   │   │   │   └── request_context.py
│   │   │   │
│   │   │   ├── ai/                     # FASE 2: AI Core Layer
│   │   │   │   ├── __init__.py
│   │   │   │   ├── conversation/       # EPIC 10: Conversation Controller
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── controller.py
│   │   │   │   │   ├── handlers.py
│   │   │   │   │   └── schemas.py
│   │   │   │   ├── context/            # EPIC 11: Context Builder
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── builder.py
│   │   │   │   │   └── memory_integration.py
│   │   │   │   ├── prompts/            # EPIC 12: Prompt Builder
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── builder.py
│   │   │   │   │   ├── templates.py
│   │   │   │   │   └── optimizer.py
│   │   │   │   ├── memory/            # EPIC 13: Memory Manager
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── short_term.py
│   │   │   │   │   ├── long_term.py
│   │   │   │   │   ├── working.py
│   │   │   │   │   └── coordinator.py
│   │   │   │   ├── tools/              # EPIC 14: Tool Orchestrator
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── registry.py
│   │   │   │   │   ├── executor.py
│   │   │   │   │   └── definitions/
│   │   │   │   ├── response/           # EPIC 15: Response Composer
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── composer.py
│   │   │   │   │   ├── formatter.py
│   │   │   │   │   └── validator.py
│   │   │   │   ├── reasoning/          # FASE 3: Reasoning Engine
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── engine.py
│   │   │   │   │   ├── confidence.py
│   │   │   │   │   ├── explainability.py
│   │   │   │   │   └── evidence.py
│   │   │   │   ├── safety/             # FASE 3: Safety Engine
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── guard.py
│   │   │   │   │   └── validators/
│   │   │   │   └── runtime.py          # Cognitive Runtime
│   │   │   │
│   │   │   ├── clinical/               # FASE 3: Clinical Intelligence
│   │   │   │   ├── __init__.py
│   │   │   │   ├── cdss/               # Clinical Decision Support
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── engine.py
│   │   │   │   │   ├── rules/
│   │   │   │   │   └── validators/
│   │   │   │   ├── diagnosis/           # Differential Diagnosis
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── differentiator.py
│   │   │   │   │   └── root_cause.py
│   │   │   │   ├── troubleshooting/     # Troubleshooting Engine
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── engine.py
│   │   │   │   │   └── advisors/
│   │   │   │   └── predictive/         # Failure Prediction
│   │   │   │       ├── __init__.py
│   │   │   │       ├── model.py
│   │   │   │       └── risk.py
│   │   │   │
│   │   │   ├── knowledge/              # FASE 4: RAG & Knowledge
│   │   │   │   ├── __init__.py
│   │   │   │   ├── embeddings/         # Embeddings generation
│   │   │   │   ├── retrieval/          # Vector retrieval
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── qdrant.py
│   │   │   │   │   └── hybrid.py
│   │   │   │   ├── pipeline/          # RAG Pipeline
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── orchestrator.py
│   │   │   │   │   └── citation.py
│   │   │   │   └── indexer/          # Knowledge indexing
│   │   │   │
│   │   │   ├── agents/                 # FASE 5: Multi-Agent System
│   │   │   │   ├── __init__.py
│   │   │   │   ├── orchestrator.py     # Main orchestrator
│   │   │   │   ├── biomedical.py       # Biomedical agent
│   │   │   │   ├── diagnostic.py       # Diagnostic agent
│   │   │   │   ├── knowledge.py       # Knowledge agent
│   │   │   │   ├── research.py        # Research agent
│   │   │   │   └── planning.py        # Planning agent
│   │   │   │
│   │   │   ├── integrations/           # FASE 6: Hospital Integrations
│   │   │   │   ├── __init__.py
│   │   │   │   ├── fhir/              # FHIR client
│   │   │   │   ├── hl7/              # HL7 listener
│   │   │   │   ├── mqtt/             # MQTT client
│   │   │   │   ├── dicom/            # DICOM client
│   │   │   │   └── hospital/         # HIS/PACS integration
│   │   │   │
│   │   │   ├── ml/                    # FASE 4-5: ML Layer
│   │   │   │   ├── __init__.py
│   │   │   │   ├── feedback_learning.py
│   │   │   │   ├── model_evaluation.py
│   │   │   │   ├── fine_tuning.py
│   │   │   │   └── analytics.py
│   │   │   │
│   │   │   ├── enterprise/             # FASE 7: Enterprise Features
│   │   │   │   ├── __init__.py
│   │   │   │   ├── licensing.py
│   │   │   │   ├── versioning.py
│   │   │   │   └── support.py
│   │   │   │
│   │   │   ├── events/                # Domain events
│   │   │   ├── services/               # Application services
│   │   │   ├── providers/              # External API providers
│   │   │   └── tasks/                  # Background tasks
│   │   │
│   │   ├── tests/                     # Tests
│   │   ├── migrations/                # Alembic migrations
│   │   ├── Dockerfile
│   │   └── ...
│   │
│   ├── web/                          # FASE 6: Frontend
│   ├── mobile/                       # FASE 6: Mobile
│   └── desktop/                      # FASE 6: Desktop
│
├── infra/                            # Infraestructura
│   ├── k8s/                         # Kubernetes manifests
│   ├── helm/                        # Helm charts
│   ├── scripts/                     # Deployment scripts
│   └── production/                  # Production configs
│
├── docs/                             # Documentación
│   ├── index.md                     # Índice principal
│   ├── README.md
│   ├── architecture/                 # Visión, Diseño, Overview
│   │   ├── VISION.md
│   │   ├── SYSTEM_DESIGN.md
│   │   ├── ARCHITECTURE_OVERVIEW.md
│   │   ├── TECH_BIBLE.md
│   │   └── PROJECT_STATUS.md
│   ├── guides/                      # Guías técnicas
│   │   ├── QUICK_START.md
│   │   ├── DEVELOPMENT.md
│   │   ├── DEPLOYMENT.md
│   │   └── API_REFERENCE.md
│   ├── adr/                         # Architecture Decision Records
│   │   ├── README.md
│   │   ├── epic0/
│   │   ├── epic1/
│   │   │   └── ...
│   │   └── epic10/
│   ├── phases/                      # Fases reorganizadas
│   │   ├── PHASE_1_FOUNDATION.md
│   │   ├── PHASE_2_AI_CORE.md
│   │   ├── PHASE_3_CLINICAL.md
│   │   ├── PHASE_4_KNOWLEDGE.md
│   │   ├── PHASE_5_AGENTS.md
│   │   ├── PHASE_6_PLATFORM.md
│   │   └── PHASE_7_ENTERPRISE.md
│   ├── domain/                      # Documentación de dominio
│   ├── epic0/...epic10/             # Histórico de épicas
│   └── ...
│
├── tests/                           # Tests E2E
│   ├── e2e/
│   ├── contract/
│   └── performance/
│
├── packages/                        # Librerías compartidas (si aplica)
│   └── shared/
│
├── docker-compose.yml
├── pyproject.toml
├── package.json
├── .github/
│   └── workflows/
│
└── [root config files]
```

---

## 3. PLAN DE MIGRACIÓN (Paso a Paso)

### FASE A: Limpieza Previa (Antes de todo)

```bash
# 1. Mover archivos de documentación del root a docs/
mv ARCHITECTURE_OVERVIEW.md docs/architecture/
mv CORE_SPECIFICATION.md docs/guides/
mv EREN_MANIFESTO.md docs/
mv MASTER_ROADMAP.md docs/architecture/
mv PROJECT_BOOTSTRAP.md docs/guides/
mv SYSTEM_DESIGN.md docs/architecture/
mv TECH_BIBLE.md docs/guides/
mv VISION.md docs/

# 2. Eliminar carpetas vacías/redundantes
rm -rf infrastructure/           # Contenido ya en apps/api/app/infrastructure/
rm -rf packages/prompts/        # Mover a apps/api/app/ai/prompts/
rm -rf packages/schemas/       # Ya existe apps/api/app/schemas/

# 3. Decidir qué hacer con packages/
# Si no se usa, eliminar o mover a docs/reference/
```

### FASE B: Integrar core/ → apps/api/app/

```bash
# Esta es la migración más crítica

# 1. AI Layer: core/cognitive/ → apps/api/app/ai/
cp -r core/cognitive/context apps/api/app/ai/context
cp -r core/cognitive/conversation apps/api/app/ai/conversation
cp -r core/cognitive/memory apps/api/app/ai/memory
cp -r core/cognitive/rag apps/api/app/ai/rag
cp -r core/cognitive/reasoning apps/api/app/ai/reasoning
cp -r core/cognitive/safety apps/api/app/ai/safety
cp -r core/cognitive/tools apps/api/app/ai/tools
cp core/cognitive/runtime.py apps/api/app/ai/runtime.py

# 2. Clinical Layer: core/clinical/ → apps/api/app/clinical/
cp -r core/clinical/* apps/api/app/clinical/

# 3. Integrations: core/integrations/ → apps/api/app/integrations/
cp -r core/integrations/* apps/api/app/integrations/

# 4. Memory standalone: core/memory/ → apps/api/app/ai/memory/
cp -r core/memory/* apps/api/app/ai/memory/

# 5. Reasoning standalone: core/reasoning/ → apps/api/app/ai/reasoning/
cp -r core/reasoning/* apps/api/app/ai/reasoning/
```

### FASE C: Limpiar core/

```bash
# Una vez integrados, archivar core/
mv core packages/legacy_core
```

---

## 4. MAPEO: Épicas → Carpetas → Fases

### Fase 1: Foundation (COMPLETA)

| Épica | Carpeta | Estado |
|-------|---------|--------|
| EPIC 0 | docs/adr/, docs/epic0/ | ✅ |
| EPIC 1 | infra/, apps/api/app/core/ | ✅ |
| EPIC 2 | apps/api/app/domain/shared/ | ✅ |
| EPIC 3 | apps/api/app/domain/device/ | ✅ |
| EPIC 4 (partial) | docs/epic4/, core/cognitive/ | ✅ |
| EPIC 5 (partial) | docs/epic5/, core/clinical/ | ✅ |
| EPIC 6 (partial) | docs/epic6/, core/integrations/ | ✅ |
| EPIC 7 | apps/web/ | ✅ |
| EPIC 8 | infra/production/ | ✅ |
| EPIC 9 | apps/api/app/ml/ | ✅ |
| EPIC 10 | apps/api/app/enterprise/ | ✅ |

### Fase 2: AI Core (Integración Pendiente)

| Componente | Carpeta Destino | Épica |
|------------|----------------|-------|
| Conversation Controller | apps/api/app/ai/conversation/ | EPIC 10 |
| Context Builder | apps/api/app/ai/context/ | EPIC 11 |
| Prompt Builder | apps/api/app/ai/prompts/ | EPIC 12 |
| Memory Manager | apps/api/app/ai/memory/ | EPIC 13 |
| Tool Orchestrator | apps/api/app/ai/tools/ | EPIC 14 |
| Response Composer | apps/api/app/ai/response/ | EPIC 15 |

### Fase 3: Clinical Intelligence

| Componente | Carpeta Destino |
|------------|----------------|
| Reasoning Engine | apps/api/app/ai/reasoning/ |
| Explainability | apps/api/app/ai/reasoning/explainability.py |
| Confidence | apps/api/app/ai/reasoning/confidence.py |
| Safety Engine | apps/api/app/ai/safety/ |
| Biomedical Rules | apps/api/app/clinical/ |
| Clinical Validation | apps/api/app/clinical/cdss/ |

### Fase 4: Knowledge & RAG

| Componente | Carpeta Destino |
|------------|----------------|
| Embeddings | apps/api/app/knowledge/embeddings/ |
| Qdrant | apps/api/app/knowledge/retrieval/ |
| Knowledge Retriever | apps/api/app/knowledge/retrieval/ |
| RAG Orchestrator | apps/api/app/knowledge/pipeline/ |
| Citation Engine | apps/api/app/knowledge/pipeline/citation.py |

### Fase 5: Multi-Agent System

| Componente | Carpeta Destino |
|------------|----------------|
| Orchestrator | apps/api/app/agents/orchestrator.py |
| Biomedical Agent | apps/api/app/agents/biomedical.py |
| Diagnostic Agent | apps/api/app/agents/diagnostic.py |
| Knowledge Agent | apps/api/app/agents/knowledge.py |
| Research Agent | apps/api/app/agents/research.py |
| Planning Agent | apps/api/app/agents/planning.py |

### Fase 6: Hospital Platform

| Componente | Carpeta Destino |
|------------|----------------|
| Dashboard | apps/web/ |
| Chat | apps/web/ |
| Reportes | apps/web/ |
| Analytics | apps/web/ |
| HIS/PACS/FHIR | apps/api/app/integrations/ |

### Fase 7: Enterprise & Production

| Componente | Carpeta Destino |
|------------|----------------|
| HIPAA Compliance | apps/api/app/middleware/audit.py |
| FDA/ISO/IEC | apps/api/app/clinical/validation/ |
| Multi-tenant | apps/api/app/domain/*/ |
| Monitoring | infra/production/monitoring.py |

---

## 5. COMANDOS DE MIGRACIÓN (Resumen)

```bash
# ============================================================================
# PASO 1: Limpiar root
# ============================================================================
mkdir -p docs/architecture docs/guides docs/phases

# Mover documentación
mv ARCHITECTURE_OVERVIEW.md docs/architecture/
mv SYSTEM_DESIGN.md docs/architecture/
mv MASTER_ROADMAP.md docs/architecture/
mv TECH_BIBLE.md docs/guides/
mv CORE_SPECIFICATION.md docs/guides/
mv PROJECT_BOOTSTRAP.md docs/guides/
mv EREN_MANIFESTO.md docs/
mv VISION.md docs/

# ============================================================================
# PASO 2: Integrar core/ → apps/api/app/
# ============================================================================

# AI Layer
mkdir -p apps/api/app/ai/conversation
mkdir -p apps/api/app/ai/context
mkdir -p apps/api/app/ai/prompts
mkdir -p apps/api/app/ai/memory
mkdir -p apps/api/app/ai/tools
mkdir -p apps/api/app/ai/response
mkdir -p apps/api/app/ai/reasoning
mkdir -p apps/api/app/ai/safety

# Copiar código real
cp core/cognitive/conversation/infrastructure/*.py apps/api/app/ai/conversation/
cp core/cognitive/context/domain/services.py apps/api/app/ai/context/
cp core/cognitive/context/infrastructure/prompt_builder.py apps/api/app/ai/prompts/
cp core/memory/*.py apps/api/app/ai/memory/
cp core/cognitive/tools/domain/*.py apps/api/app/ai/tools/
cp core/cognitive/reasoning/domain/*.py apps/api/app/ai/reasoning/
cp core/cognitive/safety/domain/*.py apps/api/app/ai/safety/

# Clinical
cp -r core/clinical/* apps/api/app/clinical/

# Integrations
cp -r core/integrations/* apps/api/app/integrations/

# ============================================================================
# PASO 3: Archivar core/
# ============================================================================
mv core packages/legacy_core

# ============================================================================
# PASO 4: Limpiar packages/
# ============================================================================
rm -rf packages/prompts
rm -rf packages/schemas

# ============================================================================
# PASO 5: Actualizar imports
# ============================================================================
# Buscar y reemplazar:
# from core.cognitive import → from app.ai
# from core.clinical import → from app.clinical
# from core.integrations import → from app.integrations

# ============================================================================
# PASO 6: Crear docs/phases/
# ============================================================================
cat > docs/phases/PHASE_1_FOUNDATION.md << 'EOF'
# Fase 1: Foundation & Platform ✅ COMPLETA

[Contenido consolidado de EPIC 0-10]
EOF

cat > docs/phases/PHASE_2_AI_CORE.md << 'EOF'
# Fase 2: AI Core 🟡 PENDIENTE

## Épicas
- EPIC 10: Conversation Controller
- EPIC 11: Context Builder
- EPIC 12: Prompt Builder
- EPIC 13: Memory Manager
- EPIC 14: Tool Orchestrator
- EPIC 15: Response Composer
EOF
# ... crear para todas las fases
```

---

## 6. CHECKLIST DE MIGRACIÓN

### Antes de empezar
- [ ] Backup del repo
- [ ] Revisar que todos los tests pasen
- [ ] Documentar imports actuales

### Durante la migración
- [ ] Mover documentación
- [ ] Copiar código de `core/` a `apps/api/app/`
- [ ] Actualizar imports
- [ ] Verificar que tests pasen
- [ ] Archivar `core/`

### Después de la migración
- [ ] Actualizar PYTHONPATH en docker-compose
- [ ] Actualizar GitHub Actions
- [ ] Actualizar README principal
- [ ] Crear docs/phases/
- [ ] Probar docker-compose up
- [ ] Verificar endpoints

---

## 7. PRs SUGERIDOS

| # | Descripción | Tipo |
|---|-------------|------|
| 1 | Mover docs del root a docs/ | Documentación |
| 2 | Integrar AI Layer (core → app) | Código |
| 3 | Integrar Clinical Layer | Código |
| 4 | Integrar Integrations | Código |
| 5 | Archivar core/ | Limpieza |
| 6 | Crear docs/phases/ | Documentación |

---

## 8. RESULTADO FINAL

```
EREN/
├── apps/
│   ├── api/app/
│   │   ├── core/            # ✅ Database, Config
│   │   ├── domain/          # ✅ Bounded Contexts
│   │   ├── ai/              # ✅ AI Layer (todo integrado)
│   │   ├── clinical/        # ✅ Clinical Intelligence
│   │   ├── knowledge/       # ✅ RAG & Knowledge
│   │   ├── agents/          # ✅ Multi-Agent
│   │   ├── integrations/    # ✅ FHIR/HL7/etc
│   │   └── ...
│   ├── web/
│   ├── mobile/
│   └── desktop/
├── infra/
├── docs/
│   ├── phases/              # ✅ Roadmap por fases
│   ├── adr/
│   └── ...
├── packages/
│   └── legacy_core/         # ✅ Archivado
└── ...
```

---

## 9. SIGUIENTE PASO

Una vez aprobada esta propuesta, ejecutar la migración en el siguiente orden:

1. **PR #1**: Mover documentación (bajo riesgo)
2. **PR #2-4**: Integrar código de AI/Clinical/Integrations (alto impacto)
3. **PR #5**: Limpieza final y docs/phases/

¿Quieres que proceda con alguna de estas propuestas?
