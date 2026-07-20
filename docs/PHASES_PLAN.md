# EREN - Plan de Fases y Estructura

**Última actualización:** 2026-07-20

---

## 📁 ESTRUCTURA DE CARPETAS

```
EREN/
├── apps/                          # Código fuente
│   ├── api/                       # API FastAPI
│   ├── web/                       # Frontend Next.js
│   └── mobile/                    # Mobile (futuro)
│
├── core/                          # Dominios y lógica de negocio
│   ├── device/                    # Device Context
│   ├── incident/                  # Incident Context
│   ├── knowledge/                 # Knowledge Context
│   ├── recommendation/            # Recommendation Context
│   ├── capacity/                  # Hospital Capacity
│   ├── staffing/                  # Staffing
│   ├── organization/              # Organization
│   ├── department/               # Department
│   ├── inventory/                # Inventory
│   ├── asset/                    # Asset
│   └── [futuro: cognitive/, clinical/, etc.]
│
├── infra/                         # Infraestructura
│   ├── k8s/                      # Kubernetes
│   ├── helm/                     # Helm charts
│   ├── scripts/                  # Scripts deployment
│   └── production/               # Config producción
│
├── docs/                          # Documentación
│   ├── README.md                  # Índice principal
│   ├── VISION.md                  # Visión del proyecto
│   │
│   ├── phases/                    # 📋 PLAN POR FASES
│   │   ├── README.md              # Índice de fases
│   │   ├── PHASE_1_FOUNDATION.md  # EPIC 0-3 ✅ COMPLETO
│   │   ├── PHASE_2_AI_CORE.md    # EPIC 4-6 🔜 PRÓXIMO
│   │   ├── PHASE_3_CLINICAL.md    # EPIC 7
│   │   └── PHASE_4_PLATFORM.md    # EPIC 8-10
│   │
│   ├── adr/                      # Architecture Decision Records
│   │   ├── README.md
│   │   ├── epic0/
│   │   ├── epic1/
│   │   ├── epic2/
│   │   ├── epic3/
│   │   └── ...epic10/
│   │
│   ├── epic0/                    # EPIC 0: Foundation
│   ├── epic1/                    # EPIC 1: Infrastructure
│   ├── epic2/                    # EPIC 2: Shared Kernel
│   ├── epic3/                    # EPIC 3: Device Context
│   ├── epic4/                    # EPIC 4: AI Core (pendiente)
│   ├── epic5-10/                 # EPIC 5-10 (pendiente)
│   │
│   ├── architecture/             # Documentos arquitectura
│   │   ├── SYSTEM_DESIGN.md
│   │   ├── ARCHITECTURE_OVERVIEW.md
│   │   ├── MASTER_ROADMAP.md
│   │   └── PROJECT_REORGANIZATION.md
│   │
│   └── guides/                   # Guías técnicas
│       ├── TECH_BIBLE.md
│       ├── CORE_SPECIFICATION.md
│       ├── PROJECT_BOOTSTRAP.md
│       └── API_REFERENCE.md      # (futuro)
│
├── tests/                         # Tests
│   ├── test_epic3_*.py           # Tests EPIC 3
│   └── [otros]
│
├── docker-compose.yml
├── pyproject.toml
└── .github/workflows/
```

---

## 📋 FASES DEL PROYECTO

### ✅ FASE 1: FOUNDATION (COMPLETADA)

**Contenido:** EPIC 0, EPIC 1, EPIC 2, EPIC 3

| Componente | Ubicación | Estado |
|------------|-----------|--------|
| Arquitectura base | `docs/epic0/` | ✅ |
| Infrastructure as Code | `infra/` | ✅ |
| Shared Kernel | `core/shared/` | ✅ |
| Device Context | `core/device/` | ✅ |
| Incident Context | `core/incident/` | ✅ |
| Knowledge Context | `core/knowledge/` | ✅ |
| Recommendation Context | `core/recommendation/` | ✅ |
| APIs Device | `apps/api/app/routers/` | ✅ |
| APIs Incident | `apps/api/app/routers/` | ✅ |
| APIs Knowledge | `apps/api/app/routers/` | ✅ |

### 🔜 FASE 2: AI CORE (PRÓXIMO - EPIC 4, 5, 6)

**Carpeta de trabajo:** `docs/phases/PHASE_2_AI_CORE.md`

| Componente | Descripción | Carpeta destino |
|------------|-------------|-----------------|
| Conversation Controller | Chat con AI | `apps/api/app/ai/conversation/` |
| Context Builder | Construye contexto | `apps/api/app/ai/context/` |
| Prompt Builder | Construye prompts | `apps/api/app/ai/prompts/` |
| Memory Manager | Gestiona memoria | `apps/api/app/ai/memory/` |
| Tool Orchestrator | Orchestrates tools | `apps/api/app/ai/tools/` |
| Response Composer | Compone respuestas | `apps/api/app/ai/response/` |

### ⏳ FASE 3: CLINICAL (EPIC 7)

**Carpeta de trabajo:** `docs/phases/PHASE_3_CLINICAL.md`

| Componente | Descripción | Carpeta destino |
|------------|-------------|-----------------|
| Reasoning Engine | Motor de razonamiento | `apps/api/app/ai/reasoning/` |
| Safety Engine | Motor de seguridad | `apps/api/app/ai/safety/` |
| Explainability | Explicabilidad | `apps/api/app/ai/reasoning/explainability/` |
| Clinical Rules | Reglas clínicas | `apps/api/app/clinical/` |

### ⏳ FASE 4: PLATFORM (EPIC 8, 9, 10)

**Carpeta de trabajo:** `docs/phases/PHASE_4_PLATFORM.md`

| Componente | Descripción | Carpeta destino |
|------------|-------------|-----------------|
| Dashboard | UI principal | `apps/web/` |
| Chat Interface | Interfaz chat | `apps/web/` |
| FHIR Integration | Integración FHIR | `apps/api/app/integrations/fhir/` |
| HL7 Integration | Integración HL7 | `apps/api/app/integrations/hl7/` |
| ML Feedback | Feedback learning | `apps/api/app/ml/` |
| Enterprise | Licensing, versioning | `apps/api/app/enterprise/` |

---

## 🔴 DIRECTORIOS A ELIMINAR

Estos directorios contienen documentos mezclados o legacy y deben eliminarse:

```bash
docs/agents/          # 1 archivo (legacy)
docs/ai/              # 1 archivo (legacy)
docs/plugins/          # 1 archivo (legacy)
docs/specifications/   # 12 archivos (legacy, duplicados)
docs/knowledge/        # 1 archivo (legacy)
docs/architecture-review/  # (revisar si sirve)
docs/audits/           # (legacy)
docs/roadmap/          # (duplicado)
docs/verification/     # (legacy)
docs/data/             # (revisar)
```

---

## 📝 REGLA DE ORO

**Antes de crear un archivo, pregúntate:**

1. ¿A qué FASE pertenece?
2. ¿Va en `docs/epicX/` o `docs/phases/`?
3. ¿Es un ADR? → `docs/adr/epicX/`
4. ¿Es guía técnica? → `docs/guides/`
5. ¿Es documento de arquitectura? → `docs/architecture/`

**NUNCA crear archivos sueltos en `docs/` sin carpeta.**

---

## 🚀 PRÓXIMOS PASOS

1. [ ] Eliminar directorios legacy en `docs/`
2. [ ] Crear `docs/phases/` con índices
3. [ ] Consolidar ADRs en `docs/adr/epicX/`
4. [ ] Empezar FASE 2 (AI Core)
