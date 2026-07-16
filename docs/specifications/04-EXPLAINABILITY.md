# EREN - Especificación Técnica Completa
## Fase 4: Explainability

> **Versión:** 1.0  
> **Fecha:** 2026-07-15  
> **Estado:** Ready for Implementation  
> **Depende de:** Fase 1 (Domain Model - Explanation VO), Fase 3 (AI Layer)

---

## Tabla de Contenidos

1. [Filosofía de Explainability](#1-filosofía-de-explainability)
2. [Reasoning Chain](#2-reasoning-chain)
3. [Evidence Model](#3-evidence-model)
4. [Sources & Citations](#4-sources--citations)
5. [Confidence Calculation](#5-confidence-calculation)
6. [Provenance Tracking](#6-provenance-tracking)
7. [Safety Classification](#7-safety-classification)
8. [Reference Tracking](#8-reference-tracking)
9. [Evidence Ranking](#9-evidence-ranking)
10. [Format Outputs](#10-format-outputs)
11. [Audit Trail](#11-audit-trail)

---

## Supuestos Declarados

1. **Regulatory Context:** EREN opera en entorno regulado (FDA, CE, IEC 62366 para usability, ISO 14971 para risk management)
2. **Explainability Level:** Diferentes niveles para diferentes stakeholders (clínico vs regulatorio vs técnico)
3. **Traceability:** Cada recomendación debe poder trazarse hasta sus fuentes originales
4. **No Black Box:** El modelo usado (GPT-4o) proporciona reasoning output que se estructura en Explanation
5. **Human-in-the-Loop:** El clínico siempre tiene la decisión final, la explicabilidad facilita esa decisión
6. **AI Disclosure:** Cumplimiento con regulaciones de IA médica para transparencia

---

## 1. FILOSOFÍA DE EXPLAINABILITY

### 1.1 Principios Rectores

**Principio 1: Patient Safety First**
- Toda explicabilidad debe facilitar decisiones que prioricen la seguridad del paciente
- La confianza en una recomendación nunca debe superar la evidencia disponible
- La explicabilidad debe hacer visible la incertidumbre

**Principio 2: Traceability**
- Cada elemento de una recomendación debe ser trazable hasta su fuente original
- La cadena de razonamiento debe permitir auditoría completa
- Ningún paso del razonamiento puede ser un "mystery box"

**Principio 3: Actionable Transparency**
- La explicabilidad no es solo para "explicar" sino para "habilitar acción"
- El clínico debe poder entender, verificar, y actuar sobre la recomendación
- Cada paso debe tener suficiente contexto para tomar decisiones informadas

**Principio 4: Appropriate Granularity**
- Diferentes stakeholders necesitan diferentes niveles de detalle
- El médico quiere el resumen ejecutivo
- El ingeniero biomédico quiere el procedimiento
- El regulador quiere la auditoría completa

**Principio 5: Continuous Calibration**
- La explicabilidad es también feedback para el sistema
- La calidad de las explicaciones afecta la confianza del usuario
- La explicabilidad permite calibrar expectativas

### 1.2 Niveles de Explicabilidad

```
Level 1: Summary (for busy clinicians)
  - One-line recommendation
  - Confidence level (e.g., "High confidence")
  - Key warning (if any)
  - Time to action

Level 2: Clinical Brief (for physician review)
  - What: The recommendation
  - Why: 3-bullet reasoning
  - Evidence: Citation count + top source
  - Safety: Safety class + key warnings
  - Confidence: Score + what affects it

Level 3: Full Explanation (for biomedical engineer)
  - Complete reasoning chain
  - All evidence with citations
  - Confidence breakdown
  - Alternative hypotheses considered
  - Safety analysis
  - References

Level 4: Audit Trail (for regulators, quality, compliance)
  - Complete reasoning chain with timestamps
  - All data sources accessed
  - All models used
  - All parameters
  - All confidence calculations
  - Complete provenance
  - Audit timestamp
```

---

## 2. REASONING CHAIN

### 2.1 Concepto

La Reasoning Chain es la secuencia estructurada de pasos lógicos que llevan desde los datos de entrada hasta la recomendación final. Es el núcleo de la explicabilidad en EREN.

### 2.2 Data Model

```python
@dataclass(frozen=True)
class ReasoningChain:
    """Complete reasoning chain for a recommendation."""
    
    chain_id: UUID
    recommendation_id: RecommendationId
    
    # Structure
    steps: tuple[ReasoningStep, ...]
    total_steps: int
    
    # Outcome
    conclusion: str
    confidence_trend: str  # "increasing", "stable", "decreasing"
    
    # Analysis
    alternative_paths_considered: tuple[AlternativePath, ...]
    confidence_factors: tuple[ConfidenceFactor, ...]
    knowledge_gaps: tuple[str, ...]  # Areas where information was insufficient
    
    # Metadata
    generation_method: str  # "chain_of_thought", "react", "tree_of_thought"
    model_used: str
    prompt_version: str
    generated_at: datetime
    
    # Quality
    coherence_score: float  # How logically connected the steps are
    evidence_coverage: float  # How much of the chain is grounded in evidence
    is_complete: bool  # All steps have evidence or are marked as assumption
```

### 2.3 Reasoning Step

```python
@dataclass(frozen=True)
class ReasoningStep:
    """A single step in the reasoning chain."""
    
    step_id: UUID
    step_number: int  # 1-indexed, sequential
    
    # Content
    description: str  # Human-readable description
    logic: str  # The logical reasoning applied
    assumption: str | None  # If this step has an assumption
    
    # Evidence grounding
    evidence_references: tuple[str, ...]  # Evidence IDs used
    prior_step_references: tuple[int, ...]  # Step numbers this builds on
    
    # Impact
    confidence_contribution: float  # [-1.0, 1.0] how this affects confidence
    relevance_score: float  # [0.0, 1.0] how relevant to conclusion
    is_key_step: bool  # Critical to the conclusion
    is_controversial: bool  # May be disputed
    controversial_reason: str | None
    
    # Alternatives
    alternative_explanations: tuple[str, ...]  # Other ways to interpret
    why_this_not_alternatives: str | None  # Why this path was chosen
    
    # Safety
    safety_implications: tuple[str, ...]  # Safety considerations at this step
    reversibility: str | None  # "full", "partial", "none"
    
    # Quality
    has_evidence: bool
    evidence_strength: str  # "strong", "moderate", "weak", "none"
    uncertainty_level: str  # "certain", "probable", "possible", "speculative"
```

### 2.4 Step Relationships

```
Sequential Dependency:
  Step N can only reference:
    - Evidence
    - Steps 1 to N-1 (prior steps)
  
  Cannot reference:
    - Future steps
    - The conclusion

Supported Reference Types:
  - evidence:{evidence_id}
  - step:{step_number}
  - assumption:{assumption_id}
  - external:{external_source_id}
```

### 2.5 Alternative Path Tracking

```python
@dataclass(frozen=True)
class AlternativePath:
    """An alternative reasoning path that was considered."""
    
    path_id: UUID
    path_description: str
    why_rejected: str  # Why this path was not chosen
    confidence_if_true: float  # What the confidence would be
    evidence_for: tuple[str, ...]
    evidence_against: tuple[str, ...]
    key_differentiator: str  # The factor that distinguishes this from chosen path
    pursued: bool  # If this path was investigated further
    investigation_result: str | None
```

### 2.6 Reasoning Chain Example

```
Recommendation: "Replace the RF coil assembly on the MRI scanner"

Reasoning Chain:

Step 1: Problem Identification
  Logic: "White noise in MRI images indicates RF (Radio Frequency) signal degradation"
  Evidence: [E1: Symptom description, E2: MRI physics principle from KB-00123]
  Prior steps: []
  Confidence contribution: +0.05
  Is key: YES
  Uncertainty: probable

Step 2: Component Analysis
  Logic: "RF signal degradation in MRI is most commonly caused by faulty RF coils, 
         cable damage, or preamplifier failure. Given the intermittent nature..."
  Evidence: [E3: Manufacturer service manual, E4: Incident history on similar device]
  Prior steps: [1]
  Confidence contribution: +0.10
  Is key: YES
  Alternative: "Could be preamplifier failure (10% of cases)"

Step 3: Hypothesis Refinement
  Logic: "The intermittent nature and specific pattern of artifacts 
         points to RF coil connector issue rather than complete coil failure"
  Evidence: [E5: Specific symptom pattern from incident, E2: Troubleshooting guide]
  Prior steps: [1, 2]
  Confidence contribution: +0.15
  Is key: YES
  Alternative: "Could be cable damage (would show different artifact pattern)"

Step 4: Action Recommendation
  Logic: "Based on the evidence, the recommended action is to replace the RF coil 
         assembly as the first-line intervention. This addresses the most likely 
         cause while being minimally invasive."
  Evidence: [E6: Maintenance procedure KB-00042]
  Prior steps: [2, 3]
  Confidence contribution: +0.20
  Is key: YES
  Safety implications: ["Device must be taken offline", "Qualified engineer required"]
  Reversibility: full

Step 5: Verification Steps
  Logic: "After replacement, image quality test should be performed to verify resolution"
  Evidence: [E7: Quality control procedure]
  Prior steps: [4]
  Confidence contribution: +0.05
  Is key: NO
  Uncertainty: certain

Alternative Paths Considered:
  - Path: "Replace preamplifier first"
    Why rejected: "Preamplifier failure typically shows different artifact pattern"
    Confidence if true: 0.75
    
  - Path: "Full system diagnostic before repair"
    Why rejected: "Takes 4+ hours; symptom pattern strongly suggests RF coil"
    Confidence if true: 0.65
```

---

## 3. EVIDENCE MODEL

### 3.1 Evidence Types

```python
class EvidenceType(Enum):
    # Primary evidence types
    DEVICE_DATA = "device_data"           # Actual readings from device
    INCIDENT_HISTORY = "incident_history" # Past incidents on same device
    KNOWLEDGE_ARTICLE = "knowledge_article" # KB articles
    CLINICAL_GUIDELINE = "clinical_guideline" # Clinical guidelines
    MANUFACTURER_SPEC = "manufacturer_spec" # Manufacturer documentation
    SENSOR_READING = "sensor_reading"     # Real-time sensor data
    MAINTENANCE_LOG = "maintenance_log"   # Maintenance records
    USER_REPORT = "user_report"           # Direct user description
    TEST_RESULT = "test_result"           # Diagnostic test results
    RECALL_DATA = "recall_data"           # FDA/manufacturer recalls
    REGULATION = "regulation"             # Regulatory documents
    STANDARD = "standard"                 # Industry standards (IEC, ISO)
    AI_MODEL_OUTPUT = "ai_model_output"  # Output from AI models
    EXPERT_OPINION = "expert_opinion"     # Expert consultation
    HISTORICAL_PATTERN = "historical_pattern"  # Pattern from historical data
```

### 3.2 Evidence Structure

```python
@dataclass(frozen=True)
class Evidence:
    """A single piece of evidence supporting a recommendation."""
    
    evidence_id: UUID
    evidence_type: EvidenceType
    
    # Content
    content: str  # The actual evidence content
    content_summary: str  # Short summary (max 200 chars)
    
    # Source
    source: Source
    source_id: str  # ID within the source system
    source_name: str
    
    # Relevance
    relevance_score: float  # [0.0, 1.0] relevance to the recommendation
    relevance_explanation: str | None  # Why this evidence is relevant
    
    # Reliability
    reliability_score: float  # [0.0, 1.0] based on source credibility
    reliability_factors: tuple[str, ...]  # Factors affecting reliability
    verification_status: str  # "verified", "unverified", "disputed"
    
    # Temporal
    temporal_relevance: str  # "current", "recent", "historical"
    data_age_days: int  # How old is this data
    max_age_threshold_days: int  # What is acceptable
    
    # Context
    device_id: DeviceId | None
    incident_id: IncidentId | None
    captured_at: datetime | None  # When this data was captured
    retrieved_at: datetime  # When we retrieved this
    
    # Linkage
    linked_reasoning_steps: tuple[int, ...]  # Which steps use this evidence
    
    # Quality
    has_visual_aid: bool  # Contains images, diagrams
    has_citations: bool  # Has its own citations
    is_direct_observation: bool  # First-hand vs second-hand
    
    # Metadata
    metadata: dict | None
```

### 3.3 Evidence Hierarchy

```
Priority Order (for conflict resolution):

Level 1 - Direct Evidence (weight: 1.0)
  - Device data (actual readings)
  - Sensor readings
  - Test results
  - Direct user observations

Level 2 - Expert Documentation (weight: 0.9)
  - Manufacturer specifications
  - Clinical guidelines (peer-reviewed)
  - Regulatory standards (IEC, ISO, FDA)

Level 3 - Institutional Knowledge (weight: 0.8)
  - Knowledge base articles
  - Maintenance logs
  - Incident history

Level 4 - Community Knowledge (weight: 0.6)
  - Expert opinions
  - Historical patterns
  - Case studies

Level 5 - AI Inference (weight: 0.4)
  - AI model outputs (reasoning)
  - Pattern detection
  - Anomaly detection

Conflict Resolution:
  When evidence conflicts:
  1. Higher-level evidence overrides lower-level
  2. Within same level: newer evidence overrides older
  3. Within same level and age: majority consensus
  4. If still conflict: Flag for human review
```

### 3.4 Evidence Quality Assessment

```python
@dataclass(frozen=True)
class EvidenceQuality:
    """Assessment of evidence quality."""
    
    evidence_id: UUID
    
    # Dimensions
    completeness: float  # [0.0, 1.0] all relevant fields present
    accuracy: float     # [0.0, 1.0] correct data
    currency: float     # [0.0, 1.0] up-to-date
    consistency: float # [0.0, 1.0] consistent with other evidence
    coverage: float    # [0.0, 1.0] covers the relevant aspects
    
    # Derived
    overall_quality_score: float  # Weighted average
    quality_level: str  # "excellent", "good", "fair", "poor"
    
    # Issues
    quality_issues: tuple[str, ...]
    warnings: tuple[str, ...]
    improvement_suggestions: tuple[str, ...]
    
    # Quality gates
    passes_minimum_threshold: bool
    requires_human_review: bool
    is_sufficient_for_high_confidence: bool
```

---

## 4. SOURCES & CITATIONS

### 4.1 Source Model

```python
@dataclass(frozen=True)
class Source:
    """A source of knowledge or evidence."""
    
    source_id: str
    source_type: SourceType
    
    # Identification
    name: str
    title: str | None  # For articles, the title
    authors: tuple[str, ...] | None
    publisher: str | None
    
    # Access
    url: str | None
    doi: str | None  # Digital Object Identifier
    isbn: str | None
    
    # Versioning
    version: str | None
    edition: str | None
    publication_date: datetime | None
    last_updated: datetime | None
    access_date: datetime  # When EREN accessed this source
    
    # Credentials
    credibility: CredibilityLevel
    peer_reviewed: bool
    institutional: bool
    
    # Scope
    jurisdiction: str | None  # Geographic/regulatory jurisdiction
    applicability: str  # "global", "regional", "institutional"
    
    # Access control
    requires_authentication: bool
    access_cost: str  # "free", "subscription", "purchase"
```

### 4.2 Source Types

```python
class SourceType(Enum):
    INTERNAL_DB = "internal_db"           # EREN's own knowledge base
    KNOWLEDGE_BASE = "knowledge_base"      # KB articles
    MANUFACTURER_DOCS = "manufacturer_docs"  # OEM documentation
    CLINICAL_GUIDELINE = "clinical_guideline"  # Clinical practice guidelines
    REGULATORY_DOC = "regulatory_doc"      # FDA, EMA, CE regulations
    INDUSTRY_STANDARD = "industry_standard"  # IEC, ISO, IEEE standards
    TEXTBOOK = "textbook"                 # Medical/biomedical textbooks
    JOURNAL_ARTICLE = "journal_article"    # Peer-reviewed papers
    RECALL_DB = "recall_db"               # FDA recall database
    EXPERT_INPUT = "expert_input"         # Domain expert knowledge
    AI_MODEL = "ai_model"                # Output from another AI model
    DEVICE_SENSOR = "device_sensor"       # Real-time device data
    MAINTENANCE_RECORD = "maintenance_record"  # Maintenance history
    INCIDENT_ARCHIVE = "incident_archive"   # Historical incidents
    COMMUNITY_KNOWLEDGE = "community_knowledge"  # Collective experience
```

### 4.3 Citation Model

```python
@dataclass(frozen=True)
class Citation:
    """A citation to a source within a recommendation."""
    
    citation_id: UUID
    source: Source
    
    # What is cited
    cited_text: str | None  # The specific text being cited
    page_reference: str | None
    section_reference: str | None
    figure_reference: str | None
    
    # Context
    reasoning_step: int  # Which step this citation supports
    claim_supported: str  # The claim this citation supports
    quote_excerpt: str | None  # Direct quote if available
    
    # Quality
    relevance_to_recommendation: float  # [0.0, 1.0]
    reliability_of_source: float  # [0.0, 1.0]
    citation_quality: float  # Combined quality score
    
    # Access
    citation_format: CitationFormat
    access_verified: bool  # Can we actually access this source
    cached_at: datetime | None  # When we cached this
    
    # Methods
    def format_citation(self, style: CitationStyle) -> str:
        """Format citation in requested style."""
        
    def format_hospital_internal(self) -> str:
        """Format in hospital's internal citation style."""
        return f"[{self.source.source_id}] {self.source.name}: {self.cited_text[:100]}..."
        
    def format_apa(self) -> str:
        """Format in APA style."""
        return f"{self.source.authors} ({self.source.publication_date.year}). "
               f"{self.source.title}. {self.source.publisher}."
```

### 4.4 Citation Formats

```
CitationStyle.HOSPITAL_INTERNAL:
  Format: [KB-00123] MRI Display Troubleshooting Guide, Siemens Healthineers, 2024
  Use: Internal reports, clinical notes

CitationStyle.APA:
  Format: Siemens Healthineers. (2024). MAGNETOM Vida Service Manual. Siemens AG.
  Use: Academic publications, formal reports

CitationStyle.Vancouver:
  Format: Siemens Healthineers. MAGNETOM Vida Service Manual. Erlangen: Siemens AG; 2024.
  Use: Medical literature

CitationStyle.IEEE:
  Format: Siemens Healthineers, "MAGNETOM Vida Service Manual," Siemens AG, Erlangen, 2024.
  Use: Technical documentation

CitationStyle.REGULATORY:
  Format: IEC 60601-1:2005+AMD1:2012+AMD2:2020, Medical electrical equipment
  Use: Regulatory submissions
```

---

## 5. CONFIDENCE CALCULATION

### 5.1 Confidence Architecture

```
Confidence Architecture:

┌─────────────────────────────────────────────────────────────┐
│                    OVERALL CONFIDENCE                        │
│                        (0.0 - 1.0)                          │
└─────────────────────────────┬───────────────────────────────┘
                              │
            ┌─────────────────┼─────────────────┐
            │                 │                 │
            ▼                 ▼                 ▼
    ┌───────────────┐ ┌──────────────┐ ┌──────────────┐
    │ Data Quality  │ │  Evidence   │ │    Model    │
    │    Score      │ │ Sufficiency │ │  Confidence  │
    │    (25%)      │ │    (25%)    │ │    (20%)    │
    └───────────────┘ └──────────────┘ └──────────────┘
            │                 │                 │
            ▼                 │                 │
    ┌───────────────┐        │                 │
    │Historical Acc. │        │                 │
    │    (15%)      │        │                 │
    └───────────────┘        │                 │
            │                 │                 │
            └─────────────────┼─────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  Contextual     │
                    │  Relevance (15%) │
                    └──────────────────┘
```

### 5.2 Detailed Calculations

```python
@dataclass(frozen=True)
class ConfidenceBreakdown:
    """Detailed breakdown of confidence calculation."""
    
    overall_score: float  # [0.0, 1.0]
    level: ConfidenceLevel
    
    # Component scores
    data_quality_score: float
    data_quality_factors: tuple[str, ...]
    
    evidence_sufficiency_score: float
    evidence_sufficiency_factors: tuple[str, ...]
    evidence_count: int
    strong_evidence_count: int
    
    model_confidence_score: float
    model_used: str
    model_temperature: float
    
    historical_accuracy_score: float
    historical_acceptance_rate: float
    historical_accuracy_rate: float
    total_rated_recommendations: int
    
    contextual_relevance_score: float
    query_context_match: float
    device_match: float
    
    # Derived
    confidence_band: str  # "low" [0-0.4), "medium" [0.4-0.7), "high" [0.7-1.0]
    
    # Uncertainty indicators
    primary_uncertainty: str
    uncertainty_factors: tuple[str, ...]
    
    # Improvement
    improvement_suggestions: tuple[str, ...]
    missing_information: tuple[str, ...]
    
    # Decision support
    needs_human_review: bool
    review_threshold: float  # Human review if confidence < this
    human_review_reason: str | None
```

### 5.3 Component Calculations

```python
# Data Quality Score
def calculate_data_quality_score(
    device_data: DeviceDTO | None,
    incident_data: IncidentDTO | None,
    evidence: list[Evidence],
) -> float:
    """
    Score: [0.0, 1.0]
    """
    
    # Completeness (40%)
    required_fields = [
        "device_type", "device_manufacturer", "device_model",
        "device_serial_number", "device_status",
        "incident_symptoms", "incident_category",
        "incident_occurred_at"
    ]
    
    available_fields = [f for f in required_fields if is_populated(f)]
    completeness = len(available_fields) / len(required_fields)
    
    # Freshness (30%)
    if device_data and incident_data:
        incident_age = now() - incident_data.occurred_at
        freshness = max(0, 1 - (incident_age.days / 30))  # 30-day window
    else:
        freshness = 0.0
    
    # Accuracy (30%) - based on evidence quality
    accuracy = sum(e.reliability_score for e in evidence) / len(evidence) if evidence else 0
    
    return (completeness * 0.4) + (freshness * 0.3) + (accuracy * 0.3)


# Evidence Sufficiency Score
def calculate_evidence_sufficiency_score(
    evidence: list[Evidence],
    required_evidence_types: set[EvidenceType],
) -> float:
    """
    Score: [0.0, 1.0]
    """
    
    if not evidence:
        return 0.0
    
    # Count by type
    type_coverage = sum(
        1 for t in required_evidence_types
        if any(e.evidence_type == t for e in evidence)
    ) / len(required_evidence_types)
    
    # Quantity factor
    quantity_factor = min(1.0, len(evidence) / 5)  # 5+ evidence is ideal
    
    # Quality factor
    quality_factor = sum(
        e.relevance_score * e.reliability_score
        for e in evidence
    ) / len(evidence)
    
    # Temporal factor
    temporal_factor = sum(
        1.0 if e.temporal_relevance == "current"
        else 0.7 if e.temporal_relevance == "recent"
        else 0.3
        for e in evidence
    ) / len(evidence)
    
    return (
        type_coverage * 0.35 +
        quantity_factor * 0.25 +
        quality_factor * 0.25 +
        temporal_factor * 0.15
    )


# Historical Accuracy Score
def calculate_historical_accuracy_score(
    tenant_id: TenantId,
    category: RecommendationCategory,
    model_version: str,
    lookback_days: int = 90,
) -> tuple[float, int]:
    """
    Returns: (accuracy_score, total_count)
    """
    
    recommendations = RecommendationContext.get_rated(
        tenant_id=tenant_id,
        category=category,
        model_version=model_version,
        lookback_days=lookback_days,
    )
    
    if not recommendations:
        return 0.5, 0  # Neutral if no history
    
    total = len(recommendations)
    accepted = sum(1 for r in recommendations if r.status == ACCEPTED)
    accurate = sum(
        1 for r in recommendations
        if r.status == ACCEPTED and r.feedback and r.feedback.was_accurate
    )
    
    acceptance_rate = accepted / total
    accuracy_rate = accurate / accepted if accepted > 0 else 0.0
    
    # Weighted: 60% acceptance, 40% accuracy
    score = (acceptance_rate * 0.6) + (accuracy_rate * 0.4)
    
    return score, total


# Contextual Relevance Score
def calculate_contextual_relevance_score(
    query: str,
    retrieved_knowledge: list[KnowledgeArticleDTO],
    device_context: DeviceDTO | None,
    incident_context: IncidentDTO | None,
) -> float:
    """
    Score: [0.0, 1.0]
    """
    
    if not retrieved_knowledge:
        return 0.0
    
    # Query-context match
    query_terms = set(query.lower().split())
    context_terms = set()
    
    if device_context:
        context_terms.update(device_context.device_type.lower().split())
        context_terms.update(device_context.device_name.lower().split())
    
    if incident_context:
        context_terms.update(incident_context.category.lower().split())
    
    query_context_overlap = len(query_terms & context_terms) / max(len(query_terms), 1)
    
    # Device match
    device_relevance = 0.0
    if device_context and retrieved_knowledge:
        relevant_articles = [
            a for a in retrieved_knowledge
            if any(t in a.tags for t in device_context.device_type.lower().split())
        ]
        device_relevance = len(relevant_articles) / len(retrieved_knowledge)
    
    # Knowledge diversity
    diversity = len(set(a.category for a in retrieved_knowledge)) / max(len(retrieved_knowledge), 1)
    
    return (
        query_context_overlap * 0.35 +
        device_relevance * 0.35 +
        diversity * 0.30
    )
```

---

## 6. PROVENANCE TRACKING

### 6.1 Concepto

Provenance es el registro completo del origen y transformación de cada elemento de una recomendación. Permite responder: "¿De dónde vino esto?" y "¿Cómo llegó a ser parte de la recomendación?"

### 6.2 Provenance Model

```python
@dataclass(frozen=True)
class Provenance:
    """Complete provenance record for a recommendation."""
    
    provenance_id: UUID
    recommendation_id: RecommendationId
    
    # Origin
    generation_timestamp: datetime
    generation_source: str  # "ai_model", "rule_based", "hybrid"
    model_identifier: str  # e.g., "gpt-4o-2024-05-13"
    prompt_version: str
    inference_parameters: InferenceParameters
    
    # Data lineage
    data_sources: tuple[DataSource, ...]
    total_sources: int
    primary_source_type: str
    
    # Processing steps
    processing_steps: tuple[ProcessingStep, ...]
    
    # Human involvement
    human_review_required: bool
    human_review_completed: bool
    human_reviewer_id: EngineerId | None
    human_review_timestamp: datetime | None
    human_modifications: tuple[str, ...] | None
    
    # Compliance
    regulatory_context: tuple[str, ...]  # Applicable regulations
    audit_ready: bool
    
    # Integrity
    content_hash: str  # SHA-256 of recommendation content
    signature: str | None  # Digital signature if required
```

### 6.3 Data Source Lineage

```python
@dataclass(frozen=True)
class DataSource:
    """A data source in the provenance chain."""
    
    source_id: UUID
    source_type: str  # "internal", "external", "device", "user", "ai"
    
    # Identification
    system: str  # Which system provided this
    dataset: str | None  # Which dataset
    endpoint: str | None  # Which API endpoint
    
    # Content
    record_id: str | None  # ID in source system
    content_hash: str  # Hash of the actual data
    
    # Access
    accessed_at: datetime
    access_method: str  # "api", "database", "file", "user_input"
    query_parameters: dict | None
    
    # Quality
    source_reliability: float  # [0.0, 1.0]
    data_currency: datetime
    
    # Lineage
    parent_sources: tuple[str, ...]  # IDs of sources that fed into this
```

### 6.4 Processing Steps

```python
@dataclass(frozen=True)
class ProcessingStep:
    """A step in the data processing pipeline."""
    
    step_id: UUID
    step_number: int
    step_type: str  # "retrieval", "transformation", "reasoning", "synthesis"
    
    # What happened
    description: str
    input_data: str  # What was input (hashed for privacy)
    output_data: str  # What was output (hashed)
    
    # How
    algorithm: str
    parameters: dict
    model_used: str | None
    
    # Quality
    confidence_impact: float  # How this step affected overall confidence
    was_successful: bool
    error_message: str | None
    
    # Timing
    started_at: datetime
    completed_at: datetime
    duration_ms: int
```

### 6.5 Provenance Example

```
Provenance Record for Recommendation REC-001:

Generation:
  - Timestamp: 2026-07-15T14:30:00Z
  - Source: ai_model
  - Model: gpt-4o-2024-05-13
  - Prompt Version: clinical_rec_v2.3.1
  - Temperature: 0.3

Data Sources:
  1. Incident INC-2024-00891
     - System: IncidentContext
     - Accessed via: GET /incidents/inc-891
     - At: 2026-07-15T14:29:55Z
     - Content: MRI display flickering, intermittent
  
  2. Device DEV-MRI-003
     - System: DeviceContext
     - Accessed via: GET /devices/mri-003
     - At: 2026-07-15T14:29:55Z
     - Content: Siemens MAGNETOM Vida 3T
  
  3. Knowledge Article KB-00042
     - System: KnowledgeContext
     - Accessed via: RAG retrieval
     - At: 2026-07-15T14:29:58Z
     - Content: MRI Troubleshooting Guide
  
  4. Knowledge Article KB-00167
     - System: KnowledgeContext
     - Accessed via: RAG retrieval
     - At: 2026-07-15T14:29:58Z
     - Content: RF Coil Replacement Procedure

Processing Steps:
  1. RAG_RETRIEVAL - Retrieved 10 documents in 850ms
  2. RERANKING - Reranked documents in 120ms
  3. CONTEXT_BUILDING - Built context in 45ms
  4. REASONING - Generated reasoning in 2800ms
  5. CONFIDENCE_CALCULATION - Calculated in 15ms
  6. SAFETY_VALIDATION - Validated in 30ms

Human Review:
  - Required: YES (CLASS_C device)
  - Completed: NO (pending biomedical engineer approval)
```

---

## 7. SAFETY CLASSIFICATION

*(Referenced from Phase 3 - Safety Engine)*

### 7.1 Safety Classification Model

```python
@dataclass(frozen=True)
class SafetyClassification:
    """Complete safety classification for a recommendation."""
    
    safety_class: SafetyClass  # SAFE, CAUTION, WARNING, CRITICAL, UNSAFE
    
    # Risk assessment
    patient_safety_risk: RiskLevel
    staff_safety_risk: RiskLevel
    equipment_safety_risk: RiskLevel
    
    # Risk factors
    risk_factors: tuple[str, ...]  # Specific risk factors identified
    mitigating_factors: tuple[str, ...]  # Factors that reduce risk
    residual_risk: str  # "acceptable", "alara", "unacceptable"
    
    # Warnings
    warnings: tuple[SafetyWarning, ...]
    contraindications: tuple[Contraindication, ...]
    
    # Requirements
    required_verifications: tuple[str, ...]  # What must be verified
    required_certifications: tuple[str, ...]  # Who must perform
    required_approvals: tuple[ApprovalRequirement, ...]
    
    # Monitoring
    monitoring_requirements: tuple[str, ...]  # What to monitor during/after
    monitoring_duration: str  # "immediate", "1_hour", "24_hours", "until_resolved"
    
    # Escalation
    escalation_required: bool
    escalation_path: tuple[str, ...]  # Roles to notify
    escalation_deadline: datetime | None
    
    # Decision support
    can_proceed: bool
    proceed_conditions: tuple[str, ...] | None  # Conditions for proceeding
    alternative_approaches: tuple[str, ...]  # Safer alternatives
```

---

## 8. REFERENCE TRACKING

### 8.1 Reference Types

```python
class ReferenceType(Enum):
    INTERNAL_ARTICLE = "internal_article"    # KB articles within EREN
    EXTERNAL_URL = "external_url"             # External web resources
    DEVICE_MANUAL = "device_manual"           # Manufacturer manuals
    REGULATION = "regulation"                 # Regulatory documents
    STANDARD = "standard"                    # Industry standards
    FORM = "form"                            # Hospital forms/templates
    VIDEO = "video"                          # Training videos
    TOOL = "tool"                            # Tools or equipment needed
    PROCEDURE = "procedure"                  # Procedures
    CONTACT = "contact"                      # Contact information
```

### 8.2 Reference Tracking Model

```python
@dataclass(frozen=True)
class Reference:
    """A reference linked to a recommendation."""
    
    reference_id: UUID
    reference_type: ReferenceType
    
    # Identification
    reference_identifier: str  # Internal ID or URL
    title: str
    
    # Description
    description: str | None
    excerpt: str | None  # Relevant excerpt
    
    # Access
    url: str | None
    access_restricted: bool
    access_level: str  # "public", "authenticated", "role_based"
    requires_roles: tuple[str, ...] | None
    
    # Quality
    relevance_to_recommendation: float  # [0.0, 1.0]
    quality_score: float | None
    
    # Verification
    url_verified: bool
    last_verified_at: datetime | None
    is_broken: bool  # Link is dead
    
    # Context
    linked_steps: tuple[int, ...]  # Which reasoning steps use this
    is_critical: bool  # Required for understanding
    is_supplementary: bool  # Additional reading
```

---

## 9. EVIDENCE RANKING

### 9.1 Ranking Algorithm

```python
def rank_evidence(
    evidence: list[Evidence],
    query_context: QueryContext,
    reasoning_goals: list[str],
) -> list[RankingResult]:
    """
    Rank evidence by relevance and quality.
    
    Scoring factors:
      1. Semantic relevance (embedding similarity)
      2. Evidence quality (reliability, freshness)
      3. Reasoning coverage (how many steps it supports)
      4. Conflict resolution (stronger evidence ranks higher)
    """
    
    results = []
    
    for e in evidence:
        # Semantic relevance (40%)
        semantic_score = calculate_semantic_relevance(
            e.content, query_context, reasoning_goals
        )
        
        # Quality score (30%)
        quality_score = (
            e.relevance_score * 0.3 +
            e.reliability_score * 0.3 +
            get_temporal_score(e) * 0.2 +
            get_verification_score(e) * 0.2
        )
        
        # Coverage score (20%)
        coverage_score = len(e.linked_reasoning_steps) / max_reasoning_steps
        
        # Conflict resolution (10%)
        conflict_score = calculate_conflict_resolution_score(e, evidence)
        
        # Final score
        final_score = (
            semantic_score * 0.40 +
            quality_score * 0.30 +
            coverage_score * 0.20 +
            conflict_score * 0.10
        )
        
        results.append(RankingResult(
            evidence=e,
            final_score=final_score,
            breakdown={
                "semantic": semantic_score,
                "quality": quality_score,
                "coverage": coverage_score,
                "conflict": conflict_score,
            }
        ))
    
    # Sort by final score descending
    return sorted(results, key=lambda r: r.final_score, reverse=True)


def calculate_semantic_relevance(
    evidence_content: str,
    query_context: QueryContext,
    goals: list[str],
) -> float:
    """
    Calculate semantic relevance using embeddings.
    """
    
    # Embed evidence content
    evidence_embedding = embed(evidence_content)
    
    # Embed query
    query_embedding = embed(query_context.query)
    
    # Embed goals
    goal_embeddings = [embed(g) for g in goals]
    
    # Similarity to query
    query_similarity = cosine_similarity(evidence_embedding, query_embedding)
    
    # Similarity to goals
    goal_similarities = [
        cosine_similarity(evidence_embedding, ge)
        for ge in goal_embeddings
    ]
    goal_similarity = max(goal_similarities) if goal_similarities else 0
    
    # Combined
    return (query_similarity * 0.6) + (goal_similarity * 0.4)
```

### 9.2 Conflict Detection

```python
def detect_evidence_conflicts(
    evidence: list[Evidence],
) -> list[ConflictRecord]:
    """
    Detect conflicts between evidence items.
    """
    
    conflicts = []
    
    for i, e1 in enumerate(evidence):
        for e2 in evidence[i+1:]:
            if are_conflicting(e1, e2):
                conflicts.append(ConflictRecord(
                    evidence_1=e1.evidence_id,
                    evidence_2=e2.evidence_id,
                    conflict_type=determine_conflict_type(e1, e2),
                    severity=determine_conflict_severity(e1, e2),
                    resolution=strategy=resolve_conflict(e1, e2),
                    resolution_confidence=calculate_resolution_confidence(e1, e2),
                ))
    
    return conflicts


def resolve_conflict(e1: Evidence, e2: Evidence) -> ConflictResolution:
    """
    Resolve conflict between two evidence items.
    """
    
    # Apply hierarchy
    if e1.source.credibility > e2.source.credibility:
        return ConflictResolution(
            winner=e1.evidence_id,
            loser=e2.evidence_id,
            strategy="hierarchy",
            explanation=f"{e1.source.name} has higher credibility",
        )
    
    # Apply recency
    if e1.data_age_days < e2.data_age_days:
        return ConflictResolution(
            winner=e1.evidence_id,
            loser=e2.evidence_id,
            strategy="recency",
            explanation="More recent data takes precedence",
        )
    
    # Apply completeness
    if e1.completeness > e2.completeness:
        return ConflictResolution(
            winner=e1.evidence_id,
            loser=e2.evidence_id,
            strategy="completeness",
            explanation="More complete evidence takes precedence",
        )
    
    # Cannot resolve automatically
    return ConflictResolution(
        winner=None,
        loser=None,
        strategy="unresolved",
        explanation="Manual resolution required",
        requires_human_review=True,
    )
```

---

## 10. FORMAT OUTPUTS

### 10.1 Format Types

```python
class ExplanationFormat(Enum):
    CLINICAL_BRIEF = "clinical_brief"      # 3-5 sentences for physician
    ENGINEERING_DETAIL = "engineering_detail"  # Full detail for engineer
    AUDIT_READY = "audit_ready"            # Complete audit trail
    PATIENT_SUMMARY = "patient_summary"      # Patient-facing summary
    REGULATORY = "regulatory"               # For regulatory submission
```

### 10.2 Clinical Brief Format

```markdown
## Clinical Recommendation

**Recommendation:** Replace RF coil assembly on MRI Scanner Unit 3

**Confidence:** High (82%) - Based on 3 sources

**Key Reasoning:**
• White noise in images indicates RF signal degradation
• RF coil connector issue most likely cause (based on symptom pattern)
• Compatible with 2 similar past incidents on this device

**Safety:** CAUTION - Device must be taken offline during repair

**Next Steps:**
1. Take MRI unit offline
2. Replace RF coil assembly (Siemens P/N: 123456789)
3. Perform image quality test
4. Return to service

**References:** KB-00042, KB-00123, Siemens Service Manual p.45
```

### 10.3 Engineering Detail Format

```markdown
## Full Technical Explanation

### Recommendation
Replace the RF coil assembly (Siemens P/N: 123456789) on MRI Scanner Unit 3 
(S/N: SN-2024-78945, Location: Radiology, Floor 2, Room MRI-201)

### Reasoning Chain

**Step 1: Problem Identification (Contribution: +0.05)**
White noise artifacts in MRI images indicate RF signal degradation. This symptom 
has been consistently associated with RF coil or cable issues in 94% of similar 
cases in our incident history.
Evidence: [E1] Symptom description, [E2] MRI physics principle KB-00123
Confidence: PROBABLE | Key: YES

**Step 2: Component Analysis (Contribution: +0.10)**
RF signal degradation can be caused by: (1) RF coil failure, (2) cable damage, 
(3) preamplifier failure. The intermittent nature suggests connector issue.
Evidence: [E3] Siemens Service Manual p.45, [E4] Incident history INC-2024-00521
Confidence: PROBABLE | Key: YES | Controversial: NO
Alternative considered: Preamplifier failure (would show different artifact pattern)

**Step 3: Hypothesis Refinement (Contribution: +0.15)**
The specific artifact pattern (intermittent white noise, no consistent band) 
points to RF coil connector rather than complete coil failure or cable damage.
Evidence: [E5] Symptom pattern analysis, [E2] Troubleshooting guide KB-00042
Confidence: LIKELY | Key: YES

**Step 4: Action Recommendation (Contribution: +0.20)**
Replace RF coil assembly as first-line intervention. Minimally invasive, 
addresses most likely cause, takes 2-3 hours.
Evidence: [E6] Maintenance procedure KB-00042
Safety implications: Device offline required, certified engineer required
Reversibility: FULL

**Step 5: Verification (Contribution: +0.05)**
After replacement, perform image quality test per QC procedure QC-2024-003.
Evidence: [E7] Quality control procedure
Confidence: CERTAIN | Key: NO

### Evidence Summary
| Source | Type | Relevance | Reliability | Used In |
|--------|------|-----------|-------------|---------|
| KB-00042 | KB Article | 0.95 | 0.90 | Steps 3, 4 |
| KB-00123 | KB Article | 0.88 | 0.85 | Steps 1, 3 |
| Siemens Manual | Manufacturer | 0.92 | 0.95 | Steps 2, 4 |
| INC-2024-00521 | Incident | 0.75 | 0.80 | Step 2 |

### Alternative Hypotheses Considered
1. **Preamplifier failure** - Rejected: Different artifact pattern
2. **Cable damage** - Rejected: Would show consistent band pattern
3. **Software issue** - Rejected: Hardware symptoms present

### Confidence Breakdown
| Component | Score | Weight |
|-----------|-------|--------|
| Data Quality | 0.85 | 25% |
| Evidence Sufficiency | 0.78 | 25% |
| Model Confidence | 0.82 | 20% |
| Historical Accuracy | 0.75 | 15% |
| Contextual Relevance | 0.80 | 15% |
| **Overall** | **0.80** | **100%** |

### Safety Analysis
- Safety Class: CAUTION
- Patient Risk: LOW (device offline during procedure)
- Staff Risk: LOW (standard maintenance)
- Required: Engineer certification (CLASS_C)
- Monitoring: Image quality test post-procedure

### References
1. [KB-00042] "MRI Display Troubleshooting Guide", EREN KB, 2024
2. [KB-00123] "MRI RF System Principles", EREN KB, 2024
3. [SM-001] "MAGNETOM Vida Service Manual", Siemens Healthineers, 2024, p.45

### Provenance
- Generated: 2026-07-15T14:30:00Z
- Model: gpt-4o-2024-05-13
- Prompt: clinical_rec_v2.3.1
- Sources: 4 (2 KB, 1 manufacturer, 1 incident)
- Human Review: Required (CLASS_C device)
```

### 10.4 Regulatory Audit Format

```markdown
## Audit Trail - AI-Generated Recommendation

**Recommendation ID:** REC-2024-00891-R01
**Incident ID:** INC-2024-00891
**Generated:** 2026-07-15T14:30:00Z
**Model:** gpt-4o-2024-05-13
**Prompt Version:** clinical_rec_v2.3.1
**Regulatory Context:** FDA 510(k), CE MDR, IEC 62366

### Input Data
| Data Type | Source | Retrieved At | Content Hash |
|-----------|--------|-------------|--------------|
| Incident | IncidentContext | 14:29:55Z | abc123... |
| Device | DeviceContext | 14:29:55Z | def456... |
| Knowledge | KnowledgeContext | 14:29:58Z | ghi789... |

### Model Parameters
- Temperature: 0.3
- Top_p: 0.95
- Max tokens: 4096
- Stop sequences: None

### Processing Pipeline
1. RAG_RETRIEVAL (850ms)
2. RERANKING (120ms)  
3. CONTEXT_BUILDING (45ms)
4. REASONING (2800ms)
5. CONFIDENCE_CALC (15ms)
6. SAFETY_VALIDATION (30ms)
Total: 3860ms

### Confidence Calculation
- Data Quality: 0.85 (completeness=0.92, freshness=0.87, accuracy=0.76)
- Evidence Sufficiency: 0.78 (5 sources, 3 strong)
- Model Confidence: 0.82
- Historical Accuracy: 0.75 (87% acceptance rate, 91% accuracy)
- Contextual Relevance: 0.80

### Safety Validation
- Patient Risk Assessment: LOW
- Staff Risk Assessment: LOW
- Required Verifications: Engineer certification
- Regulatory Compliance: IEC 60601-1, FDA 510(k)

### Human Review
- Required: YES (CLASS_C device)
- Status: PENDING
- Assigned To: [Biomedical Engineer Name]

### AI Disclosure
"This recommendation was generated by an AI system (EREN) and should be 
reviewed by a qualified biomedical engineer before implementation. 
Patient safety is the primary consideration."

Content Integrity Hash: sha256:xyz789...
Audit Timestamp: 2026-07-15T14:30:01Z
```

---

## 11. AUDIT TRAIL

### 11.1 Audit Event Types

```python
class AuditEventType(Enum):
    RECOMMENDATION_GENERATED = "recommendation_generated"
    RECOMMENDATION_VIEWED = "recommendation_viewed"
    RECOMMENDATION_ACCEPTED = "recommendation_accepted"
    RECOMMENDATION_REJECTED = "recommendation_rejected"
    RECOMMENDATION_MODIFIED = "recommendation_modified"
    HUMAN_REVIEW_COMPLETED = "human_review_completed"
    REASONING_CHAIN_INSPECTED = "reasoning_chain_inspected"
    EVIDENCE_ACCESSED = "evidence_accessed"
    SOURCE_VERIFIED = "source_verified"
    CONFLICT_DETECTED = "conflict_detected"
    CONFLICT_RESOLVED = "conflict_resolved"
    SAFETY_CLASSIFICATION_OVERRIDDEN = "safety_classification_overridden"
    CONFIDENCE_ESCALATED = "confidence_escapolated"
```

### 11.2 Audit Record

```python
@dataclass(frozen=True)
class ExplainabilityAuditRecord:
    """Complete audit record for explainability events."""
    
    audit_id: UUID
    event_type: AuditEventType
    
    # Who
    actor_id: EngineerId | SystemActor
    actor_role: str
    actor_ip: str | None
    
    # What
    recommendation_id: RecommendationId
    event_details: dict
    
    # When
    timestamp: datetime
    
    # Where
    session_id: SessionId | None
    endpoint: str | None
    
    # Context
    reasoning_chain_snapshot: ReasoningChain | None
    evidence_snapshot: tuple[Evidence, ...] | None
    confidence_snapshot: ConfidenceBreakdown | None
    
    # Integrity
    signature: str  # HMAC of record
```

---

*Documento generado para implementación. Fase 4 completa.*
