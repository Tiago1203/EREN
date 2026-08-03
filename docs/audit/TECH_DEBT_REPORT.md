# TECH DEBT REPORT — Deuda Técnica Cuantificada

**Fecha:** 2026-08-03

---

## DEUDA DE CÓDIGO

### 1. Código Muerto (Dead Code)

| Categoría | Elemento | Archivos | Líneas | Prioridad remediación |
|---|---|---|---|---|
| core/PHASE_1 | DI Container | 19 | ~2,500 | 🔴 CRÍTICA |
| core/PHASE_1 | Boot Manager | ~8 | ~1,000 | 🔴 CRÍTICA |
| core/PHASE_1 | Lifecycle Manager | ~6 | ~600 | 🔴 CRÍTICA |
| core/PHASE_1 | Diagnostics | 19 | ~2,000 | 🔴 CRÍTICA |
| core/PHASE_1 | Diagnostic vacío | 2 | ~50 | 🟡 BAJA |
| core/PHASE_2 | Runtime | ~15 | ~3,000 | 🔴 CRÍTICA |
| core/PHASE_2 | ai/di vacío | 1 | ~5 | 🟡 BAJA |
| core/LEGACY | Collaboration + Tools | ~20 | ~2,000 | 🔴 CRÍTICA |
| apps/api | UnitOfWork | 1 | ~123 | 🟡 BAJA |
| apps/api | CircuitBreaker | 1 | ~150 | 🟡 BAJA |
| apps/api | 4× RepositoryImpl | 4 | ~400 | 🟡 BAJA |
| apps/api | Events duplicados | 2 | ~150 | 🟡 BAJA |
| apps/api | 4 integration stubs | 4 | ~400 | 🟡 BAJA |
| apps/api | Vault stub | 1 | ~50 | 🟡 BAJA |
| apps/api | 3 enterprise stubs | 3 | ~150 | 🟡 BAJA |
| apps/api | diagnosis + patient models | 2 | ~100 | 🟡 BAJA |
| tests | Tests para LEGACY | 2 | ~100 | 🟡 BAJA |
| tests | Tests para runtime | 2 | ~100 | 🟡 BAJA |
| tests | Tests para infrastructure dead | ~40 | ~4,000 | 🟡 BAJA |
| packages | 4 stubs npm | 4 | ~50 | 🟡 BAJA |
| **TOTAL** | | **~117** | **~17,000** | |

### 2. Código Duplicado

| Elemento | Ubicaciones | Líneas duplicadas | Prioridad |
|---|---|---|---|
| ai/rag + cognitive/rag | core/PHASE_2/ | ~2,000 | 🟡 MEDIA |
| ai/memory + cognitive/memory | core/PHASE_2/ | ~1,500 | 🟡 MEDIA |
| reasoning/ + cognitive/reasoning/ | core/PHASE_2/ | ~1,000 | 🟡 MEDIA |
| orchestrator/ + orchestration/ | core/PHASE_2/ | ~500 | 🟡 MEDIA |
| ai/providers/ + providers/providers/ | core/PHASE_2/ | ~300 | 🟡 MEDIA |
| EventBus en 3 ubicaciones | core + apps/api | ~300 | 🟡 MEDIA |
| apps/api/events + apps/api/infra/events | apps/api/ | ~150 | 🟡 MEDIA |
| Provider en 2 ubicaciones | core/PHASE_1 + apps/api | ~100 | 🟡 BAJA |

### 3. Architecture Violations

| Violación | Ubicación | Severidad |
|---|---|---|
| Dependency Rule: infrastructure en core/ | core/PHASE_1/infrastructure/ | 🔴 CRÍTICA |
| PHASE_4 → PHASE_2 infra | core/PHASE_4/foundation/__init__.py:793 | 🔴 CRÍTICA |
| PHASE_2 → PHASE_1 infra | core/PHASE_2/runtime/runtime.py | 🟡 MEDIA (dead) |
| Dual port system incompatible | core/ vs apps/api/ | 🔴 CRÍTICA |

---

## DEUDA DE TESTS

| Elemento | Costo estimado | Prioridad |
|---|---|---|
| Contract tests para 4 repositories | 1 semana | 🔴 CRÍTICA |
| E2E tests: Device→Recommendation→Event | 1 semana | 🔴 CRÍTICA |
| Tests para incident domain | 3 días | 🟡 MEDIA |
| Tests para Celery workers | 3 días | 🟡 MEDIA |
| Frontend coverage 20%→60% | 2 semanas | 🟡 MEDIA |
| Tests para PHASE_2 AI kernel | 2 semanas | 🟡 MEDIA |
| Tests para PHASE_5 gateways | 1 semana | 🟡 MEDIA |

---

## DEUDA DE DOCUMENTACIÓN

| Elemento | Costo estimado | Prioridad |
|---|---|---|
| 177 ADRs necesitan revisión de consistencia | 3 días | 🟡 MEDIA |
| 427 epics necesitan marca de estado | 1 día | 🟡 MEDIA |
| 100+ documentos de arquitectura desactualizados | 2 semanas | 🟡 MEDIA |
| TECH_BIBLE, CORE_SPEC, PROJECT_BOOTSTRAP desactualizados | 1 semana | 🟡 MEDIA |

---

## DEUDA DE CI/CD

| Elemento | Costo estimado | Prioridad |
|---|---|---|
| Agregar job de tests a CI | 1 día | 🔴 CRÍTICA |
| Agregar CI para apps/web | 1 día | 🔴 CRÍTICA |
| Eliminar "|| true" de ruff en CI | 1 hora | 🟡 BAJA |
| Habilitar mypy strict mode | 1 semana | 🟡 MEDIA |
| Agregar security scanning | 1 día | 🟡 MEDIA |
| Agregar coverage gate en CI | 1 día | 🟡 MEDIA |

---

## DEUDA DE ARQUITECTURA

| Elemento | Costo estimado | Prioridad |
|---|---|---|
| Composition Root con factory functions | 3-5 días | 🔴 CRÍTICA |
| Unificar sistema de puertos | 1-2 semanas | 🔴 CRÍTICA |
| Anti-Corruption Layer en PHASE_4 | 1-2 semanas | 🟡 MEDIA |
| Gateway Pattern para PHASE_5 | 2-3 semanas | 🟡 MEDIA |
| Renombrar PHASE → Dominio | 4-6 semanas | 🟡 MEDIA |
| Mover Application Services a core/ | 3-4 semanas | 🟡 MEDIA |

---

## DEUDA DE FRONTEND

| Elemento | Costo estimado | Prioridad |
|---|---|---|
| 20 accesses directos a Supabase → SDK | 2-4 semanas | 🟡 MEDIA |
| Feature toggle para coexistencia SDK/Supabase | 1 semana | 🟡 MEDIA |
| Completar tests de frontend (~20%→60% coverage) | 2 semanas | 🟡 MEDIA |
| Packages stubs → packages reales | 4 semanas | 🟡 MEDIA |

---

## RESUMEN ECONOMICO

| Categoría | Deuda (días de trabajo) |
|---|---|
| Código muerto (limpieza) | 5 horas |
| Código duplicado (investigación) | 2 semanas |
| Architecture violations (corrección) | 3-5 semanas |
| Tests (contratos + E2E) | 2 semanas |
| CI/CD (completar pipeline) | 3 días |
| Documentación | 2 semanas |
| Frontend | 4 semanas |
| Arquitectura avanzada | 8-14 semanas |
| **TOTAL MÍNIMO** | **~20 semanas** |
| **TOTAL MÁXIMO** | **~36 semanas** |

**Para un equipo de 2 desarrolladores: 10-18 meses de trabajo dedicado.**

---

*Reporte generado: 2026-08-03*
