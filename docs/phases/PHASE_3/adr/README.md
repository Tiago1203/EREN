# FASE 3 ADR Index

*Architecture Decision Records para FASE 3 - Clinical Intelligence*

---

## 📁 Estructura de ADRs por EPIC

```
docs/phases/PHASE_3/adr/
├── README.md
├── epic0/                           # ✅ COMPLETO (7 ADRs)
├── epic1/                           # ✅ COMPLETO (5 ADRs)
├── epic2/                           # ✅ COMPLETO (3 ADRs)
├── epic3/                           # ✅ COMPLETO (2 ADRs)
├── epic4/                           # ✅ COMPLETO (2 ADRs)
├── epic5/                           # ✅ COMPLETO (2 ADRs)
├── epic6/                           # ✅ COMPLETO (2 ADRs)
├── epic7/                           # ✅ COMPLETO (2 ADRs)
├── epic8/                           # ✅ COMPLETO (2 ADRs)
├── epic9/                           # ✅ COMPLETO (2 ADRs)
├── epic10/                          # ✅ COMPLETO (2 ADRs)
├── epic11/                          # ✅ COMPLETO (3 ADRs)
└── epic11-1/                        # ✅ COMPLETO (1 ADR)
```

---

## 📊 Tabla de ADRs por EPIC

| Épica | ADRs | Estado |
|-------|------|--------|
| **EPIC 0** | 7 | ✅ COMPLETO |
| **EPIC 1** | 5 | ✅ COMPLETO |
| **EPIC 2** | 3 | ✅ COMPLETO |
| **EPIC 3** | 2 | ✅ COMPLETO |
| **EPIC 4** | 2 | ✅ COMPLETO |
| **EPIC 5** | 2 | ✅ COMPLETO |
| **EPIC 6** | 2 | ✅ COMPLETO |
| **EPIC 7** | 2 | ✅ COMPLETO |
| **EPIC 8** | 2 | ✅ COMPLETO |
| **EPIC 9** | 2 | ✅ COMPLETO |
| **EPIC 10** | 2 | ✅ COMPLETO |
| **EPIC 11** | 3 | ✅ COMPLETO |
| **EPIC 11.1** | 1 | ✅ COMPLETO |

---

## 📋 EPIC 0 - ADRs (COMPLETO)

| ADR | Título | Estado |
|-----|--------|--------|
| ADR-3000 | Clinical Intelligence Architecture | ✅ Accepted |
| ADR-3001 | Clinical DTO Design | ✅ Accepted |
| ADR-3002 | Evidence Model Design | ✅ Accepted |
| ADR-3003 | Safety Model Design | ✅ Accepted |
| ADR-3004 | Confidence Interface Design | ✅ Accepted |
| ADR-3005 | Validation Model Design | ✅ Accepted |
| ADR-3006 | Knowledge Interface Design | ✅ Accepted |

**Ubicación:** `docs/phases/PHASE_3/adr/epic0/`

---

## 📋 EPIC 1 - ADRs (COMPLETO)

| ADR | Título | Estado |
|-----|--------|--------|
| ADR-3010 | Knowledge Graph Architecture | ✅ Accepted |
| ADR-3011 | Medical Ontology Design | ✅ Accepted |
| ADR-3012 | Equipment Taxonomy Design | ✅ Accepted |
| ADR-3013 | Standards Repository Design | ✅ Accepted |
| ADR-3014 | Evidence Store Architecture | ✅ Accepted |

**Ubicación:** `docs/phases/PHASE_3/adr/epic1/`

---

## Formato ADR

```markdown
# ADR-XXXX: Título

## Estado
Proposed | Accepted | Deprecated | Superseded

## Contexto
Descripción del problema o decisión a tomar.

## Decisión
Descripción de la decisión tomada.

## Consecuencias
- Positivas
- Negativas

## Metadatos ADR
| Campo | Valor |
|-------|-------|
| ID | ADR-XXXX |
```

---

## Conexión con FASE 1 y FASE 2

```
FASE 1 (Business Domain) ✅
        │
        ▼
FASE 2 (AI Core) ✅
        │
        ▼
FASE 3 (Clinical Intelligence) ✅
        │
        ├── EPIC 0: Foundation ✅
        ├── EPIC 1: Biomedical Knowledge Engine ✅
        ├── EPIC 2: Reasoning Engine ✅
        ├── EPIC 3: Evidence Engine ✅
        ├── EPIC 4: Confidence Engine ✅
        ├── EPIC 5: Explainability Engine ✅
        ├── EPIC 6: Rules Engine ✅
        ├── EPIC 7: Safety Engine ✅
        ├── EPIC 8: Validation Engine ✅
        ├── EPIC 9: Decision Engine ✅
        ├── EPIC 10: Learning Engine ✅
        ├── EPIC 11: Continuous Improvement ✅
        └── EPIC 11.1: Architecture Consolidation ✅
```

---

## Notas de Auditoría (2026-07-22)

Esta versión del ADR Index refleja los cambios realizados durante la auditoría arquitectónica:

### Cambios Realizados

1. **Consolidación de Enums** - 9 enums duplicados fueron centralizados en `core.intelligence.foundation.enums`
2. **Tests Unitarios** - Se agregaron 84 tests para módulos de FASE 3
3. **Documentación** - README y ADR Index actualizados

### Known Bugs Documentados

| Bug | Módulo | Descripción |
|-----|--------|-------------|
| Frozen Dataclass | explainability | EvidenceTreeBuilder intenta modificar frozen dataclass |
| Attribute Error | evidence | EvidenceBundle requiere relevance_score en evidencia items |

---

*EREN FASE 3 ADR Index v1.2*
*Architecture Board - 2026-07-22*
