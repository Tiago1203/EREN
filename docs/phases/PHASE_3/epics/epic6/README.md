# EPIC 6: Biomedical Rules Engine

**Estado:** ✅ COMPLETO
**Fecha de inicio:** 2026-07-21
**Epic Owner:** Architecture Team
**Depende de:** EPIC 1 (Knowledge), EPIC 2 (Reasoning), EPIC 3 (Evidence), EPIC 5 (Explainability)

---

## Objetivo

Construir el motor de reglas biomédicas que valida recomendaciones contra estándares regulatorios (IEC, ISO, AAMI) y reglas clínicas/ingeniería. Este módulo **NO usa IA** - es determinístico.

---

## Arquitectura General

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                  BIOMEDICAL RULES ENGINE (EPIC 6)                           │
│                                                                              │
│  INPUT                                                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ From Knowledge + Reasoning + Explainability                            │    │
│  │ ├── Equipment Context                                                   │    │
│  │ ├── Recommendation                                                      │    │
│  │ └── Evidence Bundle                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                         │
│                                    ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    RULES ENGINE CORE                                    │    │
│  │                                                                       │    │
│  │   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                │    │
│  │   │   IEC      │  │   ISO      │  │   AAMI     │                │    │
│  │   │ Validation │  │ Validation │  │ Validation │                │    │
│  │   └─────────────┘  └─────────────┘  └─────────────┘                │    │
│  │          │               │               │                            │    │
│  │          └───────────────┼───────────────┘                            │    │
│  │                          ▼                                            │    │
│  │   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │    │
│  │   │  Clinical  │  │Engineering │  │  Hospital   │              │    │
│  │   │   Rules    │  │   Rules    │  │  Policies   │              │    │
│  │   └─────────────┘  └─────────────┘  └─────────────┘              │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                         │
│                                    ▼                                         │
│  OUTPUT                                                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ ValidationResult                                                       │    │
│  │ ├── is_compliant: bool                                                 │    │
│  │ ├── violations: list[Violation]                                         │    │
│  │ ├── recommendations: list[str]                                          │    │
│  │ └── risk_level: RiskLevel                                               │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Ejemplo: Ventilador

```
INPUT:
├── Equipment: Ventilator
├── Recommendation: Schedule PM
└── Last PM: 200 days ago

RULES ENGINE:

IF Equipment = "Ventilator" AND Last_PM > 180 days
THEN Risk = HIGH
     Action = "Immediate PM Required"
     Compliance = IEC 60601-1

IF Leakage_Current > 0.5mA
THEN Risk = CRITICAL
     Action = "IMMEDIATE REMOVAL"
     Compliance = IEC 60601-1 Clause 8.7

OUTPUT:
├── is_compliant: false
├── violations: ["PM overdue by 20 days"]
├── risk_level: HIGH
└── recommendations: ["Schedule PM within 7 days"]
```

---

## Arquitectura de Archivos

```
core/
└── intelligence/
    └── rules/                                 # EPIC 6: Biomedical Rules Engine
        ├── __init__.py                      # Main module (extends EPIC 3)
        │
        ├── validation/                      # IEC/ISO/AAMI Validation
        │   ├── __init__.py
        │   ├── iec_validator.py            # IEC 60601 validation
        │   ├── iso_validator.py             # ISO validation
        │   └── aami_validator.py           # AAMI validation
        │
        ├── clinical/                       # Clinical Rules
        │   ├── __init__.py
        │   ├── alarm_rules.py
        │   ├── dosing_rules.py
        │   └── safety_rules.py
        │
        └── engineering/                    # Engineering Rules
            ├── __init__.py
            ├── maintenance_rules.py
            ├── calibration_rules.py
            └── electrical_rules.py
```

---

## Dependencias

| Dependencia | Tipo | Descripción |
|-------------|------|-------------|
| EPIC 1 | Requerida | Knowledge Graph |
| EPIC 2 | Requerida | Reasoning Engine |
| EPIC 3 | Requerida | Evidence Retrieval (base rules) |
| EPIC 5 | Requerida | Explainability (for rule explanations) |

---

## Estado del Proyecto

| EPIC | Estado |
|------|--------|
| EPIC 0 | ✅ COMPLETO |
| EPIC 1 | ✅ COMPLETO |
| EPIC 2 | ✅ COMPLETO |
| EPIC 3 | ✅ COMPLETO |
| EPIC 4 | ✅ COMPLETO |
| EPIC 5 | ✅ COMPLETO |
| EPIC 6 | ✅ COMPLETO |

---

## Referencias

- [ADR-3060: Biomedical Rules Architecture](./adr/ADR-3060.md)
- [ADR-3061: IEC Validation Design](./adr/ADR-3061.md)
- [ADR-3062: Clinical Rules Design](./adr/ADR-3062.md)
- [ADR-3063: Engineering Rules Design](./adr/ADR-3063.md)

---

*Document created: 2026-07-21*
*Last updated: 2026-07-21*
