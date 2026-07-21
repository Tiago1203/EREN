# EPIC 0: Clinical Intelligence Foundation

**Estado:** 🚧 IN PROGRESS
**Fecha de inicio:** 2026-07-21
**Epic Owner:** Architecture Team

---

## Objetivo

Establecer la foundation de Clinical Intelligence para EREN, definiendo los contratos, DTOs, interfaces y modelos base que todo el resto del sistema de Clinical Intelligence dependerá.

Este EPIC es el **cimiento** sobre el cual se construirán:
- Biomedical Knowledge Engine (EPIC 1)
- Reasoning Engine (EPIC 2)
- Evidence Retrieval (EPIC 3)
- Confidence Engine (EPIC 4)
- Explainability Engine (EPIC 5)
- Biomedical Rules Engine (EPIC 6)
- Safety Engine (EPIC 7)
- Clinical Validation (EPIC 8)
- Decision Engine (EPIC 9)
- Learning Engine (EPIC 10)
- Continuous Improvement (EPIC 11)

---

## Arquitectura General

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CLINICAL INTELLIGENCE LAYER (FASE 3)                      │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    EPIC 0: FOUNDATION                               │    │
│  │                                                                       │    │
│  │   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │    │
│  │   │  Clinical    │  │  Reasoning   │  │   Evidence   │           │    │
│  │   │    DTOs      │  │  Contracts   │  │   Models     │           │    │
│  │   └──────────────┘  └──────────────┘  └──────────────┘           │    │
│  │                                                                       │    │
│  │   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │    │
│  │   │  Validation  │  │   Safety     │  │  Knowledge   │           │    │
│  │   │   Models     │  │   Models     │  │  Interfaces  │           │    │
│  │   └──────────────┘  └──────────────┘  └──────────────┘           │    │
│  │                                                                       │    │
│  │   ┌──────────────┐  ┌──────────────┐                              │    │
│  │   │ Confidence   │  │   Policy     │                              │    │
│  │   │  Interfaces  │  │   Engine     │                              │    │
│  │   └──────────────┘  └──────────────┘                              │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│   MÓDULOS: foundation/                                                      │
│   DEPENDENCIAS: FASE 1 + FASE 2                                            │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Componentes a Construir

### 1. Clinical DTOs

| DTO | Descripción |
|-----|-------------|
| `ClinicalFinding` | Hallazgo clínico con evidencia |
| `DiagnosisCandidate` | Candidato a diagnóstico |
| `TreatmentRecommendation` | Recomendación de tratamiento |
| `ClinicalAlert` | Alerta clínica |
| `PatientSummary` | Resumen del paciente |

### 2. Reasoning Contracts

| Contract | Descripción |
|----------|-------------|
| `IClinicalReasoner` | Interface para razonamiento clínico |
| `IEvidenceEvaluator` | Interface para evaluación de evidencia |
| `IClinicalValidator` | Interface para validación |

### 3. Evidence Models

| Model | Descripción |
|-------|-------------|
| `EvidenceLevel` | Nivel de evidencia (A, B, C, D) |
| `EvidenceSource` | Fuente de evidencia |
| `EvidenceWeight` | Peso de la evidencia |
| `EvidenceChain` | Cadena de evidencia |

### 4. Validation Models

| Model | Descripción |
|-------|-------------|
| `ValidationResult` | Resultado de validación |
| `ValidationRule` | Regla de validación |
| `ValidationSeverity` | Severidad de validación |

### 5. Safety Models

| Model | Descripción |
|-------|-------------|
| `SafetyLevel` | Nivel de seguridad |
| `SafetyCheck` | Verificación de seguridad |
| `ClinicalWarning` | Advertencia clínica |

### 6. Knowledge Interfaces

| Interface | Descripción |
|-----------|-------------|
| `IKnowledgeBase` | Interface para base de conocimiento |
| `IMedicalOntology` | Interface para ontología médica |
| `IGuidelineRepository` | Interface para repositorio de guías |

### 7. Confidence Interfaces

| Interface | Descripción |
|-----------|-------------|
| `IConfidenceCalculator` | Interface para cálculo de confianza |
| `IUncertaintyQuantifier` | Interface para cuantificación de incertidumbre |

---

## Estructura de Archivos

```
core/
└── intelligence/
    └── foundation/
        ├── __init__.py
        │
        ├── dto/                          # Clinical DTOs
        │   ├── __init__.py
        │   ├── clinical_finding.py
        │   ├── diagnosis_candidate.py
        │   ├── treatment_recommendation.py
        │   ├── clinical_alert.py
        │   └── patient_summary.py
        │
        ├── contracts/                    # Reasoning Contracts
        │   ├── __init__.py
        │   ├── clinical_reasoner.py
        │   ├── evidence_evaluator.py
        │   └── clinical_validator.py
        │
        ├── models/                       # Domain Models
        │   ├── __init__.py
        │   ├── evidence.py
        │   ├── validation.py
        │   ├── safety.py
        │   ├── confidence.py
        │   └── clinical_concept.py
        │
        ├── interfaces/                   # Interfaces
        │   ├── __init__.py
        │   ├── knowledge_base.py
        │   ├── medical_ontology.py
        │   └── guideline_repository.py
        │
        ├── policies/                    # Clinical Policies
        │   ├── __init__.py
        │   └── clinical_policy.py
        │
        └── exceptions/                  # Exceptions
            ├── __init__.py
            └── clinical_intelligence.py
```

---

## Flujo de Dependencias

```
FASE 1 (Business Domain)
        │
        ▼
FASE 2 (AI Core)
        │
        ▼
┌───────────────────────────────────────────────────────────────┐
│               FASE 3: CLINICAL INTELLIGENCE                    │
│                                                               │
│   EPIC 0: Foundation ─────────────────────────────────────┐   │
│   (Interfaces, DTOs, Contracts, Models)                    │   │
│                                                           │   │
│   EPIC 1: Biomedical Knowledge Engine ─────────────────┐   │   │
│   (Medical KB, Ontologies, Guidelines)                  │   │   │
│                                                       │   │   │
│   EPIC 2: Reasoning Engine ──────────────────────────┐   │   │
│   (Clinical reasoning, Decision trees)                │   │   │
│                                                       │   │   │
│   EPIC 3: Evidence Retrieval ──────────────────────┐   │   │
│   (Evidence chains, Source evaluation)               │   │   │
│                                                       │   │   │
│   EPIC 4: Confidence Engine ──────────────────────┐   │   │
│   (Confidence scores, Uncertainty)                 │   │   │
│                                                       │   │   │
│   EPIC 5: Explainability Engine ────────────────┐   │   │
│   (Explanations, Traceability)                   │   │   │
│                                                       │   │   │
│   EPIC 6: Biomedical Rules Engine ───────────┐   │   │
│   (Clinical rules, Drug interactions)        │   │   │
│                                               │   │   │
│   EPIC 7: Safety Engine ───────────────────┐   │   │
│   (Safety checks, Alerts)                  │   │   │
│                                           │   │   │
│   EPIC 8: Clinical Validation ──────────┐   │   │
│   (Validation pipeline)                   │   │   │
│                                       │   │   │
│   EPIC 9: Decision Engine ────────────┐   │   │
│   (Final decisions, Recommendations)  │   │   │
│                                     │   │   │
│   EPIC 10: Learning Engine ───────┐   │   │
│   (Continuous learning)            │   │   │
│                                 │   │   │
│   EPIC 11: Continuous Improvement│   │   │
│   (Feedback, Optimization)         │   │   │
│                               │   │   │
└───────────────────────────────│───┘───┘   │
                                │           │
                                └───────────┘
```

---

## DTOs Detallados

### ClinicalFinding

```python
@dataclass
class ClinicalFinding:
    """Hallazgo clínico."""
    finding_id: str
    concept_id: str  # Código SNOMED, ICD-10, etc.
    description: str
    evidence_level: EvidenceLevel
    source: EvidenceSource
    confidence: float
    patient_context: dict
    clinical_significance: ClinicalSignificance
    timestamp: datetime
```

### DiagnosisCandidate

```python
@dataclass
class DiagnosisCandidate:
    """Candidato a diagnóstico."""
    diagnosis_id: str
    icd_code: str  # ICD-10/ICD-11
    description: str
    probability: float
    supporting_findings: list[str]
    conflicting_findings: list[str]
    evidence_chain: EvidenceChain
    confidence: ConfidenceScore
    explanation: str
```

### TreatmentRecommendation

```python
@dataclass
class TreatmentRecommendation:
    """Recomendación de tratamiento."""
    recommendation_id: str
    treatment_type: TreatmentType
    description: str
    dosage: str
    contraindications: list[str]
    evidence_level: EvidenceLevel
    confidence: ConfidenceScore
    alternatives: list[str]
    monitoring_required: list[str]
```

---

## Contratos de Razonamiento

### IClinicalReasoner

```python
class IClinicalReasoner(Protocol):
    """Contrato para razonadores clínicos."""
    
    async def reason(
        self,
        patient_context: PatientSummary,
        findings: list[ClinicalFinding],
        clinical_question: str,
    ) -> list[DiagnosisCandidate]:
        """Genera candidatos de diagnóstico."""
        ...
    
    async def explain(
        self,
        diagnosis_id: str,
    ) -> ClinicalExplanation:
        """Genera explicación de un diagnóstico."""
        ...
```

### IEvidenceEvaluator

```python
class IEvidenceEvaluator(Protocol):
    """Contrato para evaluadores de evidencia."""
    
    async def evaluate_evidence(
        self,
        evidence: Evidence,
        context: PatientContext,
    ) -> EvidenceAssessment:
        """Evalúa la calidad de la evidencia."""
        ...
    
    async def build_evidence_chain(
        self,
        findings: list[ClinicalFinding],
    ) -> EvidenceChain:
        """Construye cadena de evidencia."""
        ...
```

---

## Niveles de Evidencia

```
┌─────────────────────────────────────────────────────────────┐
│                    EVIDENCE LEVELS                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   LEVEL A                                                   │
│   ├── Systematic reviews / Meta-analyses                   │
│   ├── Randomized controlled trials (RCTs)                  │
│   └── High-quality individual RCTs                         │
│                                                             │
│   LEVEL B                                                   │
│   ├── Systematic reviews of cohort studies                 │
│   ├── Individual cohort studies                           │
│   └── Low-quality RCTs                                    │
│                                                             │
│   LEVEL C                                                   │
│   ├── Systematic reviews of case-control studies           │
│   ├── Individual case-control studies                      │
│   └── Case series                                          │
│                                                             │
│   LEVEL D                                                   │
│   ├── Expert opinion                                       │
│   ├── Bench research                                      │
│   └── Clinical experience                                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Niveles de Seguridad Clínica

```
┌─────────────────────────────────────────────────────────────┐
│                    SAFETY LEVELS                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   🔴 CRITICAL                                               │
│   └── Life-threatening, requires immediate action          │
│   └── Examples: Allergic reaction, Sepsis                  │
│                                                             │
│   🟠 HIGH                                                   │
│   └── Serious harm potential, requires urgent attention     │
│   └── Examples: Drug interactions, Missed diagnosis        │
│                                                             │
│   🟡 MEDIUM                                                 │
│   └── Moderate harm potential, requires review              │
│   └── Examples: Suboptimal dosing, Incomplete workup        │
│                                                             │
│   🟢 LOW                                                    │
│   └── Minimal harm potential, informational                 │
│   └── Examples: Documentation suggestions                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Métricas de Éxito

| Métrica | Objetivo |
|---------|----------|
| DTOs implementados | 5/5 (100%) |
| Contracts implementados | 3/3 (100%) |
| Models implementados | 5/5 (100%) |
| Interfaces implementadas | 5/5 (100%) |
| Tests unitarios | 90%+ coverage |
| Documentación | 100% |

---

## Dependencias

| Dependencia | Tipo | Descripción |
|-------------|------|-------------|
| FASE 1 | Requerida | Business Domain (Device, Incident, Knowledge) |
| FASE 2 | Requerida | AI Core (Context, Prompt, Memory) |
| core.shared | Requerida | Shared Kernel de EREN |

---

## Riesgos

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|------------|--------|------------|
| Conflictos con FASE 2 | Baja | Alto | Reusar AI Core contracts |
| DTOs incompatibles | Media | Alto | Review de arquitectura temprano |
| Performance issues | Baja | Medio | Diseño asíncrono |

---

## Referencias

- [ADR-3000: Clinical Intelligence Architecture](./adr/ADR-3000.md)
- [ADR-3001: Clinical DTO Design](./adr/ADR-3001.md)
- [ADR-3002: Evidence Model Design](./adr/ADR-3002.md)
- [ADR-3003: Safety Model Design](./adr/ADR-3003.md)
- [ADR-3004: Confidence Interface Design](./adr/ADR-3004.md)
- [ADR-3005: Validation Model Design](./adr/ADR-3005.md)

---

## Siguiente EPIC

**EPIC 1: Biomedical Knowledge Engine** - Construirá sobre esta foundation para crear el motor de conocimiento biomédico.

---

*Document created: 2026-07-21*
*Last updated: 2026-07-21*
