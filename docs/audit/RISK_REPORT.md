# RISK REPORT — Matriz de Riesgos

**Fecha:** 2026-08-03

---

## MATRIZ DE PROBABILIDAD × IMPACTO

| Probabilidad → | Muy baja | Baja | Media | Alta | Muy alta |
|---|---|---|---|---|---|
| **Catastrófico** | | | | | |
| **Mayor** | | | | | |
| **Moderado** | | | R6, R7 | R1, R2 | R5 |
| **Menor** | R9 | R4, R8 | R3, R10 | | |
| **Insignificante** | | | | | |

---

## RIESGOS CRÍTICOS

### R5 — Tests no se ejecutan en CI
| Campo | Detalle |
|---|---|
| **Probabilidad** | Muy alta — confirmado |
| **Impacto** | Catastrófico — regresiones en producción |
| **Estado** | ⚠️ RIESGO ACTIVO |
| **Evidencia** | `.github/workflows/ci.yml` no tiene job de tests |
| **Mitigación inmediata** | Agregar `test-api` job a ci.yml (1 día) |
| **Owner** | DevOps / Backend |

### R1 — PHASE_5 no integrado — funcionalidad clave no disponible
| Campo | Detalle |
|---|---|
| **Probabilidad** | Alta — confirmado |
| **Impacto** | Mayor — producto incompleto |
| **Estado** | ⚠️ RIESGO ACTIVO |
| **Evidencia** | 5 imports comentados con marcadores "En producción" |
| **Mitigación inmediata** | Diseñar Gateway Pattern antes de implementar |
| **Owner** | Backend / AI |

### R2 — Dual port system — incompatibilidad silenciosa
| Campo | Detalle |
|---|---|
| **Probabilidad** | Alta — confirmado |
| **Impacto** | Mayor — cambios en un sistema no se reflejan en el otro |
| **Estado** | ⚠️ RIESGO ACTIVO |
| **Evidencia** | ABC usa `Result[Device, str]`, Protocol usa `DeviceModel \| None` |
| **Mitigación inmediata** | Contract tests + decisión de contrato canónico |
| **Owner** | Backend |

---

## RIESGOS ALTOS

### R3 — PHASE_4 → PHASE_2 importando infraestructura
| Campo | Detalle |
|---|---|
| **Probabilidad** | Media — confirmado |
| **Impacto** | Mayor — PHASE_4 puede romper si PHASE_2 cambia |
| **Estado** | ⚠️ RIESGO ACTIVO |
| **Evidencia** | `from core.PHASE_2.embeddings.manager import EmbeddingManager` |
| **Owner** | Backend |

### R6 — Frontend con acceso directo a Supabase
| Campo | Detalle |
|---|---|
| **Probabilidad** | Alta — confirmado |
| **Impacto** | Moderado — cambios de schema rompen frontend |
| **Estado** | ⚠️ RIESGO ACTIVO |
| **Evidencia** | 20 accesses directos en 9 archivos |
| **Owner** | Frontend |

### R7 — PHASE_2 macro-módulo sin límites claros
| Campo | Detalle |
|---|---|
| **Probabilidad** | Media — confirmado (duplicación de carpetas) |
| **Impacto** | Moderado — complejidad innecesaria |
| **Estado** | ⚠️ RIESGO ACTIVO |
| **Evidencia** | `ai/rag` vs `cognitive/rag`, `ai/memory` vs `cognitive/memory` |
| **Owner** | Backend / AI |

### R10 — PHASE_2 Runtime dead code
| Campo | Detalle |
|---|---|
| **Probabilidad** | Alta — confirmado dead |
| **Impacto** | Menor — código no utilizado |
| **Estado** | ⚠️ RIESGO ACTIVO |
| **Evidencia** | `grep -rn "from core.PHASE_2.runtime" . \| grep -v "runtime/"` → vacío |
| **Mitigación** | Eliminar (30 min) |
| **Owner** | Backend |

---

## RIESGOS MEDIOS

### R4 — PHASE_1 infrastructure/ en core/
| Campo | Detalle |
|---|---|
| **Probabilidad** | Alta — confirmado (container, boot, lifecycle dead) |
| **Impacto** | Menor — viola Dependency Rule |
| **Estado** | ⚠️ RIESGO ACTIVO |
| **Mitigación** | Eliminar dead code + mover lo activo a apps/api/ |
| **Owner** | Backend |

### R8 — CI permite errores de lint silenciosamente
| Campo | Detalle |
|---|---|
| **Probabilidad** | Alta — confirmado (`|| true`) |
| **Impacto** | Menor — lint pasa con errores |
| **Estado** | ⚠️ RIESGO ACTIVO |
| **Mitigación** | Eliminar `\|\| true` (10 min) |
| **Owner** | DevOps |

### R9 — MyPy sin strict mode
| Campo | Detalle |
|---|---|
| **Probabilidad** | Media — confirmado |
| **Impacto** | Menor — errores de tipo no detectados |
| **Estado** | ⚠️ RIESGO ACTIVO |
| **Mitigación** | Habilitar strict progresivamente |
| **Owner** | Backend |

---

## RIESGOS RESIDUALES (aceptados)

| Riesgo | Probabilidad | Impacto | Razón para aceptar |
|---|---|---|---|
| PHASE_7 no conectado | Baja | Moderado | Planeado para fase posterior |
| apps/desktop mobile stubs | Baja | Insignificante | Dependencias futuras |
| packages/ stubs vacíos | Media | Menor | Dependientes de M3 |
| Qdrant no instalado | Media | Menor | Dependiente de PHASE_4 implementation |

---

*Reporte generado: 2026-08-03*
