# EPIC 0: Clinical Intelligence Foundation - ADR Index

*Architecture Decision Records para EPIC 0 - Clinical Intelligence Foundation*

---

## Tabla de ADRs

| ADR | Título | Estado | Severidad |
|-----|--------|--------|-----------|
| ADR-3000 | Clinical Intelligence Architecture | ✅ Accepted | Crítica |
| ADR-3001 | Clinical DTO Design | ✅ Accepted | Alta |
| ADR-3002 | Evidence Model Design | ✅ Accepted | Alta |
| ADR-3003 | Safety Model Design | ✅ Accepted | Crítica |
| ADR-3004 | Confidence Interface Design | ✅ Accepted | Alta |
| ADR-3005 | Validation Model Design | ✅ Accepted | Crítica |
| ADR-3006 | Knowledge Interface Design | ✅ Accepted | Alta |

**Total: 7 ADRs (7 Accepted)**
**Estado: ✅ COMPLETE**

---

## Resumen de Decisiones

### ADR-3000: Arquitectura
Define la arquitectura general de Clinical Intelligence con capas claras.

### ADR-3001: DTOs
Diseña los Data Transfer Objects inmutables para hallazgos clínicos.

### ADR-3002: Evidencia
Modelo jerárquico de evidencia (A-D) con cadenas de evidencia.

### ADR-3003: Seguridad
Niveles de seguridad (CRITICAL → LOW) y Safety Checks.

### ADR-3004: Confianza
Interfaces para cálculo de confianza con factores y calibración.

### ADR-3005: Validación
Pipeline de validación multi-etapa con severidades.

### ADR-3006: Conocimiento
Interfaces abstractas para bases de conocimiento médico.

---

## Ubicación de Archivos

```
docs/phases/PHASE_3/adr/epic0/
├── README.md
├── ADR-3000.md  (Clinical Intelligence Architecture)
├── ADR-3001.md  (Clinical DTO Design)
├── ADR-3002.md  (Evidence Model Design)
├── ADR-3003.md  (Safety Model Design)
├── ADR-3004.md  (Confidence Interface Design)
├── ADR-3005.md  (Validation Model Design)
└── ADR-3006.md  (Knowledge Interface Design)
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
FASE 3: CLINICAL INTELLIGENCE 🚧
        │
        └── EPIC 0: Foundation ✅ ← COMPLETO
                ├── DTOs
                ├── Contracts
                ├── Models
                ├── Interfaces
                └── Policies
```

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

## Próximo EPIC

**EPIC 1: Biomedical Knowledge Engine** - Construirá sobre esta foundation para crear el motor de conocimiento biomédico.

---

*EREN PHASE 3 ADR Index - EPIC 0 v1.1*
*Architecture Board - 2026-07-21*
