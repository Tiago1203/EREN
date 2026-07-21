# EPIC 2: Reasoning Engine

**Estado:** ✅ COMPLETO
**Fecha de inicio:** 2026-07-21
**Epic Owner:** Architecture Team
**Depende de:** EPIC 0 (Foundation), EPIC 1 (Biomedical Knowledge Engine)

---

## Objetivo

Construir el "cerebro" de EREN: el motor de razonamiento que transforma información en conocimiento accionable. Este EPIC implementa la capacidad de EREN para **razonar** sobre problemas de ingeniería clínica.

El Reasoning Engine no responde directamente. **Razona** para generar hipótesis, cadenas de razonamiento, alternativas e inferencias.

---

## Arquitectura General

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         REASONING ENGINE (EPIC 2)                            │
│                                                                              │
│  INPUT                                                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ Context Builder                                                         │    │
│  │ ├── Memory (historial)                                                │    │
│  │ ├── Knowledge (epic1)                                                 │    │
│  │ ├── Domain (equipos médicos)                                          │    │
│  │ └── Conversation (contexto actual)                                    │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                         │
│                                    ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    REASONING PIPELINE                                  │    │
│  │                                                                       │    │
│  │   Equipment Type → Failure History → Maintenance History               │    │
│  │         │                  │                    │                       │    │
│  │         ▼                  ▼                    ▼                       │    │
│  │   Biomedical Rules ──────► Knowledge ──────► Evidence                │    │
│  │         │                  │                    │                       │    │
│  │         └──────────────────┴────────────────────┘                       │    │
│  │                              │                                         │    │
│  │                              ▼                                         │    │
│  │                     Possible Causes                                    │    │
│  │                              │                                         │    │
│  │                              ▼                                         │    │
│  │                         Probability                                    │    │
│  │                              │                                         │    │
│  │                              ▼                                         │    │
│  │                        Recommendations                                 │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                         │
│                                    ▼                                         │
│  OUTPUT                                                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ • Hypotheses (hipótesis generadas)                                    │    │
│  │ • Reasoning Chains (cadenas de razonamiento)                          │    │
│  │ • Alternatives (alternativas evaluadas)                                │    │
│  │ • Inferences (inferencias deducidas)                                  │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Componentes del Reasoning Engine

### 1. Hypothesis Engine

```
HypothesisEngine
├── HypothesisGenerator
│   ├── Equipment-based generation
│   ├── Pattern-based generation
│   └── Evidence-based generation
├── HypothesisEvaluator
│   ├── Probability calculation
│   ├── Evidence assessment
│   └── Confidence scoring
└── HypothesisPrioritizer
    ├── Severity-based prioritization
    └── Likelihood-based prioritization
```

**Responsabilidades:**
- Generar hipótesis a partir de síntomas
- Evaluar probabilidad de cada hipótesis
- Priorizar hipótesis por severidad

### 2. Inference Engine

```
InferenceEngine
├── ForwardChaining
│   ├── Rule-based inference
│   └── Data-driven inference
├── BackwardChaining
│   ├── Goal-based reasoning
│   └── Hypothesis testing
├── AbductiveReasoning
│   ├── Best explanation inference
│   └── Causal abduction
└── BayesianInference
    ├── Probability networks
    └── Conditional reasoning
```

**Responsabilidades:**
- Encadenamiento hacia adelante y atrás
- Razonamiento abductivo
- Inferencia bayesiana

### 3. Diagnostic Engine

```
DiagnosticEngine
├── SymptomAnalyzer
│   ├── Pattern matching
│   └── Anomaly detection
├── DifferentialDiagnosis
│   ├── Candidate generation
│   ├── Elimination process
│   └── Likelihood ranking
├── RootCauseAnalysis
│   ├── 5 Whys analysis
│   ├── Fishbone diagrams
│   └── Fault tree analysis
└── DiagnosticConfidence
    ├── Evidence weight
    └── Uncertainty quantification
```

**Responsabilidades:**
- Análisis de síntomas
- Diagnóstico diferencial
- Análisis de causa raíz

### 4. Reasoning Chains

```
ReasoningChains
├── ChainBuilder
│   ├── Premise extraction
│   ├── Logical connections
│   └── Conclusion derivation
├── ChainValidator
│   ├── Logical consistency
│   ├── Evidence coverage
│   └── Confidence assessment
├── ChainExporter
│   ├── Natural language output
│   ├── JSON structured output
│   └── Visual graph output
└── ChainMemory
    ├── Previous chains storage
    ├── Pattern recognition
    └── Learning from history
```

**Responsabilidades:**
- Construir cadenas lógicas
- Validar consistencia
- Exportar en múltiples formatos

### 5. Causal Graph

```
CausalGraph
├── CausalRelations
│   ├── Direct causation
│   ├── Contributing factors
│   └── Temporal relationships
├── CausalInference
│   ├── Do-calculus
│   ├── Counterfactuals
│   └── Mediation analysis
├── EvidenceLinking
│   ├── Evidence-to-cause mapping
│   └── Confidence propagation
└── CausalDiscovery
    ├── From data learning
    └── From knowledge integration
```

**Responsabilidades:**
- Representar relaciones causales
- Inferencia causal
- Descubrimiento de causalidades

---

## Flujo de Datos

### Ejemplo: SpO2 Monitor con lectura incorrecta

```
INPUT:
"Monitor gives wrong SpO2 reading"

│
▼ Context Building
├── Memory: Previous incidents with SpO2 monitors
├── Knowledge: Equipment taxonomy, failure modes
├── Domain: Pulse oximetry equipment
└── Conversation: Current session context

│
▼ Hypothesis Generation
├── H1: Sensor malfunction (p=0.35)
├── H2: Patient physiology interference (p=0.25)
├── H3: Calibration drift (p=0.20)
├── H4: Software error (p=0.12)
└── H5: Environmental interference (p=0.08)

│
▼ Evidence Evaluation
├── Supporting evidence for H1:
│   ├── 73% of similar cases were sensor issues
│   ├── Sensor age > 2000 hours
│   └── Recent drop in reading quality
└── Contradicting evidence:
    └── Last calibration was 30 days ago

│
▼ Probability Update (Bayesian)
├── P(H1|E) = 0.42 (increased)
├── P(H2|E) = 0.23 (decreased)
└── P(H3|E) = 0.18 (unchanged)

│
▼ Recommendations Generation
├── R1: Replace sensor probe (confidence: 0.85)
├── R2: Verify patient positioning (confidence: 0.72)
├── R3: Run calibration procedure (confidence: 0.68)
└── R4: Check for environmental interference (confidence: 0.45)

OUTPUT:
├── Top Hypothesis: Sensor malfunction (42%)
├── Reasoning Chain: [symptom] → [evidence] → [hypothesis]
├── Confidence: 0.78
└── Recommended Action: Replace sensor probe
```

---

## Arquitectura de Archivos

```
core/
└── intelligence/
    └── reasoning/                    # EPIC 2: Reasoning Engine
        ├── __init__.py
        │
        ├── hypothesis/              # Hypothesis Engine
        │   ├── __init__.py
        │   ├── hypothesis_engine.py
        │   ├── hypothesis.py
        │   ├── hypothesis_generator.py
        │   ├── hypothesis_evaluator.py
        │   └── hypothesis_prioritizer.py
        │
        ├── inference/               # Inference Engine
        │   ├── __init__.py
        │   ├── inference_engine.py
        │   ├── forward_chaining.py
        │   ├── backward_chaining.py
        │   ├── abductive_reasoning.py
        │   └── bayesian_inference.py
        │
        ├── diagnostic/              # Diagnostic Engine
        │   ├── __init__.py
        │   ├── diagnostic_engine.py
        │   ├── symptom_analyzer.py
        │   ├── differential_diagnosis.py
        │   ├── root_cause_analysis.py
        │   └── diagnostic_confidence.py
        │
        ├── chains/                  # Reasoning Chains
        │   ├── __init__.py
        │   ├── reasoning_chain.py
        │   ├── chain_builder.py
        │   ├── chain_validator.py
        │   └── chain_exporter.py
        │
        ├── causal/                  # Causal Graph
        │   ├── __init__.py
        │   ├── causal_graph.py
        │   ├── causal_relations.py
        │   ├── causal_inference.py
        │   └── causal_discovery.py
        │
        ├── context/                 # Context Builder
        │   ├── __init__.py
        │   ├── context_builder.py
        │   ├── memory_context.py
        │   ├── knowledge_context.py
        │   └── conversation_context.py
        │
        ├── pipeline/                # Reasoning Pipeline
        │   ├── __init__.py
        │   ├── reasoning_pipeline.py
        │   ├── pipeline_stages.py
        │   └── pipeline_config.py
        │
        └── exceptions/              # Reasoning Exceptions
            ├── __init__.py
            └── reasoning_errors.py
```

---

## Dependencias

| Dependencia | Tipo | Descripción |
|-------------|------|-------------|
| EPIC 0 | Requerida | Foundation (DTOs, Models) |
| EPIC 1 | Requerida | Knowledge Graph, Ontology |
| FASE 1 | Requerida | Device Context, Incident Context |
| FASE 2 | Requerida | AI Core (Memory, Context) |

---

## Flujo de Dependencias

```
FASE 1 (Business Domain) ✅
        │
        ▼
FASE 2 (AI Core) ✅
        │
        ▼
┌───────────────────────────────────────────────────────────────┐
│               FASE 3: CLINICAL INTELLIGENCE                    │
│                                                               │
│   EPIC 0: Foundation ─────────────────────────────────────┐   │
│   (DTOs, Contracts, Models, Interfaces) ✅ COMPLETO         │   │
│                                                           │   │
│   EPIC 1: Biomedical Knowledge ─────────────────────────┐   │   │
│   (Knowledge Graph, Ontology, Taxonomy) ✅ COMPLETO        │   │
│                                                           │   │   │
│   EPIC 2: Reasoning Engine ─────────────────────────────┐   │   │
│   (Hypothesis, Inference, Diagnostic) ✅ COMPLETO           │   │
│                                                           │   │   │
│   EPIC 3-11: ...                                         │   │
│                                                           │   │
└──────────────────────────────────────────────────────────│───┘   │
                                                            │       │
                                                            └───────┘
```

---

## Métricas de Éxito

| Métrica | Objetivo |
|---------|----------|
| Hypothesis accuracy | > 80% top-3 accuracy |
| Reasoning chain validity | 100% logically consistent |
| Diagnostic confidence | Properly calibrated |
| Response time | < 500ms |
| Evidence coverage | > 70% of relevant evidence |
| Tests coverage | 90%+ |
| Documentation | 100% |

---

## Riesgos

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|------------|--------|------------|
| Reasoning complexity | Alta | Medio | Incremental implementation |
| Confidence calibration | Media | Alto | Bayesian updates with evidence |
| Knowledge gaps | Media | Alto | Integration with EPIC 1 |
| Performance | Baja | Alto | Async pipeline design |

---

## Referencias

- [ADR-3020: Reasoning Engine Architecture](./adr/ADR-3020.md)
- [ADR-3021: Hypothesis Engine Design](./adr/ADR-3021.md)
- [ADR-3022: Inference Engine Design](./adr/ADR-3022.md)
- [ADR-3023: Diagnostic Engine Design](./adr/ADR-3023.md)
- [ADR-3024: Causal Graph Design](./adr/ADR-3024.md)

---

## Próximo EPIC

**EPIC 3: Evidence Retrieval** - Construirá sobre el razonamiento para recuperar y evaluar evidencia.

---

## Status

**EPIC 0 Status:** ✅ COMPLETO
**EPIC 1 Status:** ✅ COMPLETO
**EPIC 2 Status:** ✅ COMPLETO

---

*Document created: 2026-07-21*
*Last updated: 2026-07-21*
