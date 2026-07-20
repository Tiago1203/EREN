# EREN - Especificación Técnica Completa
## Fase 3: AI Layer

> **Versión:** 1.0  
> **Fecha:** 2026-07-15  
> **Estado:** Ready for Implementation  
> **Depende de:** Fase 1, Fase 2, Fase 4 (Explainability), Fase 5 (Conversational)

---

## Tabla de Contenidos

1. [Arquitectura General de la AI Layer](#1-arquitectura-general)
2. [Conversation Controller](#2-conversation-controller)
3. [Reasoning Engine](#3-reasoning-engine)
4. [Prompt Builder](#4-prompt-builder)
5. [Memory Manager](#5-memory-manager)
6. [Context Builder](#6-context-builder)
7. [Recommendation Engine](#7-recommendation-engine)
8. [Safety Engine](#8-safety-engine)
9. [Confidence Engine](#9-confidence-engine)
10. [Explainability Engine](#10-explainability-engine)
11. [Feedback Engine](#11-feedback-engine)
12. [RAG Orchestrator](#12-rag-orchestrator)
13. [Tool Orchestrator](#13-tool-orchestrator)
14. [Knowledge Retriever](#14-knowledge-retriever)
15. [Planning Engine](#15-planning-engine)
16. [Response Composer](#16-response-composer)
17. [Secuencia Completa de una Interacción](#17-secuencia-completa)

---

## Supuestos Declarados

1. **LLM Provider:** OpenAI GPT-4o (primario), Anthropic Claude (fallback), Azure OpenAI (enterprise)
2. **Embedding Provider:** OpenAI text-embedding-3-large, Azure OpenAI embeddings
3. **Vector Store:** Qdrant o Weaviate para embeddings
4. **No Fine-Tuning:** Uso de prompting avanzado, RAG y retrieval. Fine-tuning en fase posterior.
5. **Conversation Memory:** Redis para sesión, PostgreSQL para persistencia larga
6. **Rate Limiting:** Redis + sliding window algorithm
7. **No streaming para decisiones clínicas:** Solo streaming para mensajes informativos
8. **Model Routing:** Por tipo de query (clinical vs operational vs general)
9. **Latency Target:** < 3 segundos para recomendación, < 10 segundos para investigación profunda
10. **AI Layer NO es un bounded context:** Es una capa de aplicación/orquestación

---

## 1. ARQUITECTURA GENERAL

### 1.1 Posicionamiento

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                            │
│    (Web App, Mobile, API, Clinical Workstation Integration)     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      AI LAYER (Orchestration)                    │
│                                                                  │
│  ┌────────────────┐  ┌─────────────┐  ┌────────────────────┐ │
│  │  Conversation   │  │   Memory    │  │    Context         │ │
│  │  Controller    │◄─┤  Manager    │◄─┤    Builder         │ │
│  └───────┬────────┘  └─────────────┘  └─────────┬──────────┘ │
│          │                                      │             │
│          ▼                                      ▼             │
│  ┌────────────────┐              ┌────────────────────────┐  │
│  │   Planning     │              │    Prompt              │  │
│  │   Engine       │─────────────►│    Builder             │  │
│  └───────┬────────┘              └─────────┬──────────────┘  │
│          │                                  │                 │
│          ▼                                  ▼                 │
│  ┌────────────────┐  ┌─────────────┐  ┌────────────────────┐ │
│  │  Reasoning     │  │   Safety    │  │   Confidence       │ │
│  │  Engine       │◄─┤  Engine     │◄─┤   Engine           │ │
│  └───────┬────────┘  └─────────────┘  └────────────────────┘ │
│          │                                                    │
│          ▼                                                    │
│  ┌────────────────┐  ┌─────────────┐  ┌────────────────────┐ │
│  │  Response      │  │  Explain-   │  │   Feedback         │ │
│  │  Composer      │◄─┤  ability    │◄─┤   Engine           │ │
│  └───────┬────────┘  │  Engine     │  └────────────────────┘ │
│          │          └─────────────┘                          │
│          ▼                                                    │
│  ┌────────────────┐  ┌─────────────┐  ┌────────────────────┐ │
│  │  Tool          │  │   RAG       │  │   Knowledge        │ │
│  │  Orchestrator  │◄─┤  Orchestr.  │◄─┤   Retriever       │ │
│  └───────┬────────┘  └─────────────┘  └────────────────────┘ │
│          │                                                    │
│          ▼                                                    │
│  ┌────────────────┐                                          │
│  │  Recommendation│                                          │
│  │  Engine        │                                          │
│  └───────┬────────┘                                          │
└──────────┼────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────────┐
│                     BOUNDED CONTEXTS                             │
│  ┌──────────┐  ┌──────────────┐  ┌───────────────────────┐   │
│  │ Incident │  │ Recommendation│  │     Knowledge         │   │
│  │ Context  │  │   Context    │  │      Context         │   │
│  └──────────┘  └──────────────┘  └───────────────────────┘   │
│                      ┌──────────────┐                         │
│                      │    Device    │                         │
│                      │   Context    │                         │
│                      └──────────────┘                         │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 AI Layer como Orquestador

```
Rol: La AI Layer es un ORCHESTRATOR, no un dominio.

Decisión arquitectónica:
  - La AI Layer NO tiene estado persistente propio
  - NO es un bounded context
  - NO tiene repositories propios
  - NO tiene aggregates propios
  - USA los bounded contexts existentes para datos

Patrón: Pure Orchestration (Simplified SSA)
  - AI Layer consulta contextos a través de APIs internas
  - AI Layer construye contexto para el LLM
  - AI Layer traduce respuestas del LLM a comandos/querys de contextos
  - AI Layer NUNCA modifica estado directamente
```

### 1.3 Capabilities

```
La AI Layer expone las siguientes capacidades:

C-001: Clinical Decision Support
  - Recibe: incident_id, question, context
  - Devuelve: Recommendation con explicación
  - Requiere: SafetyEngine approval

C-002: Troubleshooting Guidance
  - Recibe: device_id, symptoms, incident_history
  - Devuelve: Step-by-step guidance
  - Requiere: Knowledge retrieval + SafetyEngine

C-003: Incident Investigation
  - Recibe: incident_id
  - Devuelve: Investigation plan, findings summary
  - Requiere: ReasoningEngine + Knowledge retrieval

C-004: Preventive Maintenance Suggestions
  - Recibe: device_id, device_history
  - Devuelve: Maintenance recommendations
  - Requiere: Pattern analysis

C-005: Knowledge Query
  - Recibe: natural language query
  - Devuelve: Synthesized answer from knowledge base
  - Requiere: RAG + Knowledge retriever

C-006: Conversation with Context
  - Recibe: session_id, message
  - Devuelve: Response with context awareness
  - Requiere: MemoryManager + ConversationController
```

---

## 2. CONVERSATION CONTROLLER

### 2.1 Responsabilidad

Controlar el flujo conversacional entre el usuario y la AI Layer. Gestiona sesiones, hilos de conversación, turnos de diálogo, y mantiene la coherencia conversacional. Acts as the entry point and exit point de toda interacción.

### 2.2 Inputs y Outputs

```
Input:
  - Message: {session_id, conversation_id, message, message_type, attachments, metadata}
  - SessionStart: {tenant_id, user_id, user_role, context_type}
  - SessionResume: {session_id}

Output:
  - Response: {message, message_type, tools_used, reasoning_summary, metadata}
  - SessionInfo: {session_id, conversation_id, turn_count, context_summary}
```

### 2.3 Contrato

```python
class ConversationController:
    """
    Entry point for all user interactions with the AI Layer.
    Manages conversation lifecycle and orchestrates all AI components.
    """

    async def handle_message(
        self,
        session_id: SessionId,
        message: str,
        message_type: MessageType,  # USER, SYSTEM, TOOL_RESULT, CLARIFICATION
        attachments: list[Attachment] | None = None,
        context_type: ConversationContextType | None = None,
        force_regenerate: bool = False,
    ) -> ConversationResponse:
        """
        Process a user message and return a response.
        
        Steps:
          1. Load session and conversation from MemoryManager
          2. Classify message intent
          3. Determine required capabilities
          4. Check safety (SafetyEngine)
          5. Route to appropriate engine
          6. Build response
          7. Update memory
          8. Return response
        """

    async def start_session(
        self,
        tenant_id: TenantId,
        user_id: EngineerId,
        user_role: UserRole,
        initial_context: ConversationContextType | None = None,
    ) -> SessionInfo:
        """
        Create a new conversation session.
        """

    async def get_session_context(
        self,
        session_id: SessionId,
        include_recent_turns: int = 10,
    ) -> SessionContext:
        """
        Retrieve current session context for display or continuation.
        """
```

### 2.4 Message Types

```
USER: Mensaje directo del usuario
SYSTEM: Mensaje del sistema (notificaciones)
TOOL_RESULT: Resultado de una llamada a herramienta
CLARIFICATION: Solicitud de clarificación del AI
ESCALATION: Escalamiento a humano
FEEDBACK: Feedback del usuario sobre una respuesta anterior
REGENERATE: Solicitud de regenerar última respuesta
```

### 2.5 Conversation Context Types

```
CLINICAL_INVESTIGATION: Sesión de investigación de incidente clínico
DEVICE_TROUBLESHOOTING: Sesión de diagnóstico de dispositivo
KNOWLEDGE_QUERY: Consulta a la base de conocimientos
PREVENTIVE_MAINTENANCE: Sesión de mantenimiento preventivo
GENERAL_ASSISTANCE: Asistencia general
TRAINING: Sesión de entrenamiento
```

---

## 3. REASONING ENGINE

### 3.1 Responsabilidad

Aplicar diferentes estrategias de razonamiento para generar recomendaciones. Gestiona la selección de estrategia, la construcción de la cadena de razonamiento, y la integración de evidencia.

### 3.2 Contrato

```python
class ReasoningEngine:
    """
    Applies reasoning strategies to generate recommendations.
    Supports multiple reasoning paradigms.
    """

    async def reason(
        self,
        context: ReasoningContext,
        strategy: ReasoningStrategy,
        model: LLMModel,
    ) -> ReasoningResult:
        """
        Apply reasoning to generate a reasoning chain.
        
        ReasoningContext contains:
          - incident data
          - device data
          - knowledge articles
          - historical patterns
          - safety constraints
        
        ReasoningResult contains:
          - reasoning_chain: list[ReasoningStep]
          - conclusion: str
          - confidence_breakdown: ConfidenceBreakdown
          - alternative_hypotheses: list[Hypothesis]
          - evidence_used: list[Evidence]
          - model_used: str
          - reasoning_strategy: str
        """

    def select_strategy(
        self,
        incident_category: IncidentCategory,
        safety_level: SafetyLevel,
        urgency: RecommendationUrgency,
    ) -> ReasoningStrategy:
        """
        Select the most appropriate reasoning strategy.
        """
```

### 3.3 Reasoning Strategies

```
Strategy Selection Matrix:

| Category | Safety | Urgency | Strategy |
|----------|--------|---------|----------|
| HARDWARE_FAILURE | CLASS_C-D | CRITICAL | ChainOfThought + SafetyFirst |
| HARDWARE_FAILURE | CLASS_C-D | NORMAL | ChainOfThought + EvidenceBased |
| HARDWARE_FAILURE | CLASS_A-B | any | EvidenceBased |
| CALIBRATION | any | any | Procedural + ManufacturerSpecs |
| SOFTWARE_FAULT | any | CRITICAL | DiagnosticTree |
| LIFE_SUPPORT | CLASS_D | any | SafetyFirst + ZeroTolerance |
| SAFETY_ALERT | any | CRITICAL | SafetyFirst |
| DIAGNOSTIC_ERROR | any | any | DifferentialDiagnosis |
```

### 3.4 Estrategia: ChainOfThought

```
Purpose: Sequential reasoning through problem space
Use when: Complex multi-step problems

Prompt Structure:
  Task: "Think step by step about this incident"
  Steps:
    1. Understand the problem
    2. Identify relevant knowledge
    3. Analyze symptoms
    4. Generate hypotheses
    5. Evaluate evidence for each hypothesis
    6. Select best recommendation
    7. Consider contraindications
    8. Assess safety implications
```

### 3.5 Estrategia: SafetyFirst

```
Purpose: Prioritize patient and staff safety above all
Use when: CLASS_C or CLASS_D safety level, CRITICAL urgency

Priority Order:
  1. Patient safety
  2. Staff safety
  3. Equipment preservation
  4. Service continuity

Constraints:
  - Always recommend immediate escalation if patient harm possible
  - Never suggest actions that could worsen safety
  - Require human confirmation for safety-critical steps
```

### 3.6 Estrategia: EvidenceBased

```
Purpose: Ground all reasoning in retrieved evidence
Use when: Knowledge base has relevant articles

Evidence Hierarchy:
  1. Clinical guidelines and regulations (highest weight)
  2. Manufacturer documentation
  3. Hospital policies
  4. Incident history
  5. Community knowledge
```

---

## 4. PROMPT BUILDER

### 4.1 Responsabilidad

Construir prompts optimizados para cada tipo de interacción, incluyendo system prompts, few-shot examples, y contexto recuperado. Gestiona templates, versionado de prompts, y experimentación.

### 4.2 Contrato

```python
class PromptBuilder:
    """
    Constructs optimized prompts for different capabilities.
    Manages prompt templates and versions.
    """

    async def build_clinical_recommendation_prompt(
        self,
        incident: IncidentDTO,
        device: DeviceDTO | None,
        knowledge_articles: list[KnowledgeArticleDTO],
        conversation_history: list[Message],
        reasoning_strategy: ReasoningStrategy,
        safety_level: SafetyLevel,
        user_role: UserRole,
        prompt_version: str,
    ) -> Prompt:
        """
        Build a complete prompt for clinical recommendation.
        """

    async def build_troubleshooting_prompt(
        self,
        device: DeviceDTO,
        symptoms: list[Symptom],
        incident_history: list[IncidentDTO],
        knowledge_articles: list[KnowledgeArticleDTO],
        conversation_history: list[Message],
        prompt_version: str,
    ) -> Prompt:
        """
        Build a prompt for device troubleshooting.
        """

    async def build_knowledge_synthesis_prompt(
        self,
        query: str,
        retrieved_knowledge: list[KnowledgeArticleDTO],
        user_role: UserRole,
        prompt_version: str,
    ) -> Prompt:
        """
        Build a prompt for synthesizing knowledge from multiple sources.
        """
```

### 4.3 Prompt Structure

```
Standard Prompt Structure:

=== SYSTEM PROMPT ===
Role Definition
  You are EREN, a Clinical Engineering Decision Support System...
  Your purpose is to assist biomedical engineers in...
  
Safety Instructions
  - Patient safety is paramount
  - Always include safety warnings for dangerous procedures
  - Recommend escalation when uncertain
  - Never provide definitive diagnoses

Output Format
  - Always include confidence level
  - Always include evidence citations
  - Always include safety classification
  - Always include references

Constraints
  - Maximum N words per recommendation
  - Must cite sources for all claims
  - Cannot recommend actions outside biomedical engineering
  - Must follow hospital protocols

=== CONTEXT ===
[Built from ContextBuilder output]

=== RETRIEVED KNOWLEDGE ===
[From RAG Orchestrator]

=== CONVERSATION HISTORY ===
[From MemoryManager]

=== USER MESSAGE ===
[Actual user message]

=== OUTPUT SCHEMA ===
JSON schema for structured output
```

### 4.4 Few-Shot Examples

```
Examples by Scenario:

Scenario 1: High-risk hardware failure
  Example:
    Input: "MRI scanner showing white noise in images"
    Reasoning: "Step 1: Check RF coil connections..."
    Output: [structured recommendation with safety classification]
  Purpose: Demonstrate safety-first reasoning

Scenario 2: Calibration
  Example:
    Input: "Infusion pump calibration due"
    Reasoning: "Manufacturer specifies 90-day calibration..."
    Output: [step-by-step calibration procedure]
  Purpose: Demonstrate procedural reasoning

Scenario 3: Knowledge synthesis
  Example:
    Input: "How to handle power failure during dialysis?"
    Output: [synthesized answer from multiple protocols]
  Purpose: Demonstrate evidence aggregation
```

---

## 5. MEMORY MANAGER

### 5.1 Responsabilidad

Gestionar la memoria conversacional a corto y largo plazo. Maneja sesiones, turnos, resúmenes automáticos, y el contexto de ventana. Implementa diferentes niveles de memoria: working, episodic, semantic.

### 5.2 Contrato

```python
class MemoryManager:
    """
    Manages conversation memory across different time horizons.
    Implements working, episodic, and semantic memory layers.
    """

    async def add_message(
        self,
        session_id: SessionId,
        message: Message,
    ) -> None:
        """
        Add a message to session memory.
        Updates working memory and triggers summarization if needed.
        """

    async def get_conversation_context(
        self,
        session_id: SessionId,
        max_turns: int = 20,
        include_summaries: bool = True,
    ) -> ConversationContext:
        """
        Get conversation context for prompt injection.
        Manages context window automatically.
        """

    async def get_or_create_session(
        self,
        tenant_id: TenantId,
        session_id: SessionId,
        user_id: EngineerId,
    ) -> Session:
        """
        Retrieve existing session or create new one.
        """

    async def summarize_session(
        self,
        session_id: SessionId,
    ) -> SessionSummary:
        """
        Generate a summary of the current session.
        Stores summary for future reference.
        """

    async def store_episodic_memory(
        self,
        session_id: SessionId,
        episode_type: EpisodeType,  # INCIDENT, TROUBLESHOOTING, etc.
        summary: SessionSummary,
        key_outcomes: list[str],
    ) -> None:
        """
        Store episodic memory for future retrieval.
        """
```

### 5.3 Memory Layers

```
Layer 1: Working Memory (Short-term)
  - Contains: Current conversation turns
  - Duration: Current session
  - Storage: Redis
  - Size: Last 20 turns or 8000 tokens
  - Purpose: Immediate context for current conversation

Layer 2: Episodic Memory (Medium-term)
  - Contains: Session summaries
  - Duration: 30 days
  - Storage: PostgreSQL
  - Size: Last 100 sessions per user
  - Purpose: Recall past conversations

Layer 3: Semantic Memory (Long-term)
  - Contains: Learned patterns, user preferences, organization policies
  - Duration: Indefinite
  - Storage: PostgreSQL + Vector DB
  - Purpose: User-specific and organization-specific knowledge

Layer 4: Cross-Session Context
  - Contains: Incident context, device context
  - Duration: Until incident resolved or device repaired
  - Storage: PostgreSQL
  - Purpose: Maintain context across sessions for same incident
```

### 5.4 Context Window Management

```
Context Window Strategy: Sliding window with priority

Token Budget: 128,000 tokens (GPT-4o context)
Allocation:
  - System prompt: 4,000 tokens (fixed)
  - Retrieved knowledge: 60,000 tokens
  - Conversation history: 40,000 tokens
  - Output buffer: 24,000 tokens

Overflow Strategy:
  1. Prioritize recent conversation turns
  2. Truncate older turns
  3. If still overflow: Use summarization
  4. If still overflow: Increase model context (add cost)

Summarization Triggers:
  - When working memory exceeds 15,000 tokens
  - When session exceeds 30 turns
  - When switching incident context mid-session
```

### 5.5 Session State

```python
class SessionState:
    session_id: SessionId
    tenant_id: TenantId
    user_id: EngineerId
    user_role: UserRole
    
    # Conversation
    conversation_id: ConversationId
    turns: list[Turn]
    current_context_type: ConversationContextType
    incident_id: IncidentId | None  # Active incident context
    device_id: DeviceId | None  # Active device context
    
    # Memory layers
    working_memory: WorkingMemory
    episodic_summaries: list[SessionSummary]
    
    # State
    state: SessionStateType  # ACTIVE, SUSPENDED, CLOSED
    created_at: datetime
    last_activity_at: datetime
    metadata: dict
```

---

## 6. CONTEXT BUILDER

### 6.1 Responsabilidad

Reunir todos los datos de contexto necesarios para una interacción. Consulta los bounded contexts, combina la información, y la formatea para el Prompt Builder.

### 6.2 Contrato

```python
class ContextBuilder:
    """
    Constructs comprehensive context for AI interactions.
    Queries all bounded contexts and aggregates data.
    """

    async def build_incident_context(
        self,
        incident_id: IncidentId,
        tenant_id: TenantId,
        include_history: bool = True,
        include_related: bool = True,
    ) -> IncidentContextData:
        """
        Build comprehensive incident context.
        
        Aggregates from:
          - IncidentContext (incident data)
          - DeviceContext (device info)
          - KnowledgeContext (related articles)
          - RecommendationContext (active recommendations)
        """

    async def build_device_context(
        self,
        device_id: DeviceId,
        tenant_id: TenantId,
        include_history: bool = True,
        include_maintenance: bool = True,
    ) -> DeviceContextData:
        """
        Build comprehensive device context.
        
        Aggregates from:
          - DeviceContext (device data)
          - IncidentContext (incident history)
          - KnowledgeContext (device manuals)
          - RecommendationContext (device recommendations)
        """

    async def build_knowledge_query_context(
        self,
        query: str,
        tenant_id: TenantId,
        filters: KnowledgeFilters,
        user_role: UserRole,
    ) -> KnowledgeQueryContext:
        """
        Build context for knowledge synthesis query.
        """

    async def build_full_context(
        self,
        session_id: SessionId,
        capability: Capability,
        query: str,
    ) -> FullContextData:
        """
        Build complete context for any capability.
        Combines session, incident, device, and knowledge context.
        """
```

### 6.3 Context Data Structures

```python
@dataclass(frozen=True)
class IncidentContextData:
    incident: IncidentDTO
    device: DeviceDTO | None
    active_recommendations: list[RecommendationDTO]
    related_articles: list[KnowledgeArticleDTO]
    incident_history: list[IncidentDTO]  # Same device, last 6 months
    investigation_summary: str | None
    timeline: list[TimelineEvent]
    open_questions: list[str]
    suggested_next_steps: list[str]
    
@dataclass(frozen=True)  
class DeviceContextData:
    device: DeviceDTO
    recent_incidents: list[IncidentDTO]  # Last 10
    maintenance_history: list[MaintenanceRecord]
    calibration_history: list[CalibrationInfo]
    related_articles: list[KnowledgeArticleDTO]
    device_knowledge_summary: str  # Synthesized from articles
    operational_trends: list[TrendData]
    
@dataclass(frozen=True)
class KnowledgeQueryContext:
    original_query: str
    retrieved_articles: list[KnowledgeArticleDTO]
    synthesized_summary: str | None  # If multiple articles
    entity_extractions: list[ExtractedEntity]  # Devices, symptoms, etc.
    search_metadata: SearchMetadata
```

---

## 7. RECOMMENDATION ENGINE

### 7.1 Responsabilidad

Generar recomendaciones de IA completas, incluyendo explicación, confianza, evidencia y acciones. Orquesta la generación de recomendaciones desde la recepción de contexto hasta la composición final.

### 7.2 Contrato

```python
class RecommendationEngine:
    """
    Orchestrates the complete recommendation generation pipeline.
    """

    async def generate_recommendation(
        self,
        context: IncidentContextData,
        capability: Capability,
        generation_config: GenerationConfig,
    ) -> RecommendationResult:
        """
        Generate a complete AI recommendation.
        
        Pipeline:
          1. ContextBuilder → Build full context
          2. ReasoningEngine → Generate reasoning chain
          3. ConfidenceEngine → Calculate confidence
          4. ExplainabilityEngine → Build explanation
          5. SafetyEngine → Validate safety
          6. ResponseComposer → Compose final response
        
        RecommendationResult contains:
          - recommendation: RecommendationDTO
          - reasoning_chain: ReasoningChain
          - confidence_breakdown: ConfidenceBreakdown
          - explanation: Explanation
          - safety_classification: SafetyClassification
          - citations: list[Citation]
          - tool_calls: list[ToolCall]  # If tools were used
          - metadata: GenerationMetadata
        """

    async def generate_batch(
        self,
        context: IncidentContextData,
        max_recommendations: int = 5,
        diversity_threshold: float = 0.7,
    ) -> list[RecommendationResult]:
        """
        Generate multiple diverse recommendations.
        Ensures diversity in approach while maintaining quality.
        """
```

### 7.3 Pipeline

```
Input: IncidentContextData + GenerationConfig

Step 1: Intent Classification
  - Classify the type of recommendation needed
  - Determine reasoning strategy
  - Select model

Step 2: Context Enrichment
  - Call Knowledge Retriever for relevant articles
  - Call Tool Orchestrator for device data
  - Build expanded context

Step 3: Reasoning (ReasoningEngine)
  - Apply selected reasoning strategy
  - Generate reasoning chain
  - Identify hypotheses

Step 4: Confidence Calculation (ConfidenceEngine)
  - Calculate overall confidence
  - Breakdown by component
  - Determine if human review needed

Step 5: Explanation Generation (ExplainabilityEngine)
  - Build reasoning chain explanation
  - Generate citations
  - Create evidence summary

Step 6: Safety Validation (SafetyEngine)
  - Validate against safety rules
  - Classify safety level
  - Add safety warnings

Step 7: Response Composition (ResponseComposer)
  - Compose final recommendation
  - Format for user role
  - Add metadata

Output: RecommendationResult
```

---

## 8. SAFETY ENGINE

### 8.1 Responsabilidad

Validar todas las recomendaciones generadas contra reglas de seguridad clínica. Clasificar el nivel de riesgo, identificar contraindicaciones, y determinar si se requiere revisión humana o escalamiento.

### 8.2 Contrato

```python
class SafetyEngine:
    """
    Validates recommendations against clinical safety rules.
    Ensures patient and staff safety across all AI outputs.
    """

    async def validate_recommendation(
        self,
        recommendation: RecommendationDraft,
        context: IncidentContextData,
    ) -> SafetyValidationResult:
        """
        Validate a recommendation for safety.
        
        Checks:
          - Patient safety implications
          - Staff safety implications
          - Regulatory compliance
          - Contraindications
          - Drug/device interactions
          - Known failure modes
        
        Returns:
          - is_safe: bool
          - safety_class: SafetyClass
          - warnings: list[SafetyWarning]
          - contraindications: list[Contraindication]
          - required_verifications: list[str]
          - escalation_required: bool
          - human_review_required: bool
        """

    async def classify_safety_level(
        self,
        recommendation: RecommendationDraft,
        device: DeviceDTO,
        patient_impact: PatientImpact,
    ) -> SafetyClassification:
        """
        Classify the safety level of a recommendation.
        """

    async def check_against_recalls(
        self,
        device_id: DeviceId,
        device_model: str,
        manufacturer: str,
    ) -> RecallCheckResult:
        """
        Check if device has active recalls or safety alerts.
        """
```

### 8.3 Safety Rules

```
Rule S-001: Life Support Devices
  - If device is LIFE_SUPPORT type:
    - ALL recommendations require human confirmation
    - Escalation path is mandatory for P1
    - Safety class must be SAFE or CAUTION

Rule S-002: Patient Impact Present
  - If patient_impact != NO_IMPACT:
    - Escalation required
    - Safety class minimum: WARNING
    - Document justification for every action

Rule S-003: Multiple Devices
  - If recommendation involves multiple devices:
    - Validate each device independently
    - Check for cascading effects
    - Document device dependencies

Rule S-004: Regulatory Category
  - If category is SAFETY_ALERT or LIFE_SUPPORT:
    - Multi-person approval required
    - Document regulatory basis
    - Audit trail mandatory

Rule S-005: High-Confidence Low-Evidence
  - If confidence > 0.8 but evidence < 3 sources:
    - Add caveat about limited evidence
    - Require human confirmation
    - Log as potential bias risk
```

### 8.4 Safety Classification Response

```python
@dataclass(frozen=True)
class SafetyClassification:
    safety_class: SafetyClass  # SAFE, CAUTION, WARNING, CRITICAL, UNSAFE
    
    patient_safety_risk: RiskLevel  # NONE, LOW, MODERATE, HIGH, CRITICAL
    staff_safety_risk: RiskLevel
    
    warnings: tuple[SafetyWarning, ...]
    contraindications: tuple[Contraindication, ...]
    
    required_verifications: tuple[str, ...]
    monitoring_requirements: tuple[str, ...]
    
    escalation_required: bool
    escalation_path: tuple[str, ...]  # Roles to escalate to
    
    human_review_required: bool
    human_review_reason: str | None
    
    can_proceed: bool  # false if UNSAFE or CRITICAL
    proceed_conditions: tuple[str, ...] | None
```

---

## 9. CONFIDENCE ENGINE

### 9.1 Responsabilidad

Calcular y desglosar el nivel de confianza de cada recomendación. Determinar qué tan segura es la recomendación, qué factores contribuyen a la confianza, y qué información adicional mejoraría la confianza.

### 9.2 Contrato

```python
class ConfidenceEngine:
    """
    Calculates confidence scores for recommendations.
    Provides breakdown and improvement suggestions.
    """

    async def calculate_confidence(
        self,
        recommendation: RecommendationDraft,
        context: IncidentContextData,
        reasoning_chain: ReasoningChain,
        evidence: list[Evidence],
    ) -> ConfidenceResult:
        """
        Calculate comprehensive confidence score.
        
        ConfidenceResult contains:
          - overall_score: float [0.0, 1.0]
          - level: ConfidenceLevel
          - breakdown: ConfidenceBreakdown
          - contributing_factors: list[str]
          - detracting_factors: list[str]
          - improvement_suggestions: list[str]
          - needs_human_review: bool
          - review_reason: str | None
        """

    async def calculate_component_scores(
        self,
        recommendation: RecommendationDraft,
        context: IncidentContextData,
    ) -> ComponentScores:
        """
        Calculate individual component confidence scores.
        
        Components:
          - data_quality_score: Quality of retrieved data
          - evidence_sufficiency_score: Amount and quality of evidence
          - model_confidence_score: LLM's own confidence
          - historical_accuracy_score: Based on past feedback
          - contextual_relevance_score: How well context fits
        """

    async def estimate_improvement(
        self,
        current_confidence: Confidence,
        context: IncidentContextData,
    ) -> list[ImprovementSuggestion]:
        """
        Suggest what information would improve confidence.
        """
```

### 9.3 Confidence Calculation Formula

```
Overall Confidence = WeightedAverage(ComponentScores)

Weights (adjustable via config):
  - data_quality: 0.25
  - evidence_sufficiency: 0.25
  - model_confidence: 0.20
  - historical_accuracy: 0.15
  - contextual_relevance: 0.15

Component Score Calculations:

Data Quality Score:
  = (Completeness * 0.4) + (Freshness * 0.3) + (Accuracy * 0.3)
  Where:
    Completeness = filled_required_fields / total_required_fields
    Freshness = 1 - (age_in_days / max_age_days)
    Accuracy = historical_correct_rate for this data type

Evidence Sufficiency Score:
  = min(1.0, source_count / 3) * source_reliability_avg * recency_factor

Model Confidence Score:
  = Direct from LLM response (calibrated)

Historical Accuracy Score:
  = (accepted_count / total_count) * accuracy_weight
  Where accuracy_weight = avg(rating for accepted)

Contextual Relevance Score:
  = Semantic similarity between query and retrieved context
```

---

## 10. EXPLAINABILITY ENGINE

*(Referirse a especificación Fase 4 para detalle completo)*

### 10.1 Contrato resumido

```python
class ExplainabilityEngine:
    """
    Generates comprehensive explanations for recommendations.
    """

    async def generate_explanation(
        self,
        recommendation: RecommendationDraft,
        reasoning_chain: ReasoningChain,
        evidence: list[Evidence],
        format: ExplanationFormat,  # CLINICAL, ENGINEERING, AUDIT
    ) -> Explanation:
        """
        Generate a formatted explanation for the recommendation.
        """

    async def build_reasoning_chain_explanation(
        self,
        reasoning_chain: ReasoningChain,
    ) -> str:
        """
        Build a human-readable explanation of the reasoning chain.
        """

    async def generate_citations(
        self,
        evidence: list[Evidence],
        style: CitationStyle,  # APA, HARVARD, HOSPITAL_INTERNAL
    ) -> list[Citation]:
        """
        Generate properly formatted citations for all evidence.
        """
```

---

## 11. FEEDBACK ENGINE

### 11.1 Responsabilidad

Recolectar, procesar y almacenar feedback del usuario sobre las recomendaciones. Actualizar métricas de confianza histórica, detectar drift del modelo, y cerrar el loop de aprendizaje.

### 11.2 Contrato

```python
class FeedbackEngine:
    """
    Processes and stores user feedback on recommendations.
    Closes the learning loop for model improvement.
    """

    async def process_feedback(
        self,
        recommendation_id: RecommendationId,
        feedback: Feedback,
        user_id: EngineerId,
    ) -> FeedbackProcessingResult:
        """
        Process user feedback on a recommendation.
        
        Steps:
          1. Validate feedback
          2. Store in database
          3. Update recommendation confidence history
          4. Update knowledge article quality scores
          5. Trigger model performance metrics
          6. Flag for review if negative feedback
          7. Log to audit trail
        
        Returns:
          - feedback_id
          - processed_at
          - model_impact: Impact on model confidence
          - quality_alert: bool (true if flag for review)
        """

    async def aggregate_feedback(
        self,
        tenant_id: TenantId,
        time_range: TimeRange,
        group_by: FeedbackGroupBy,  # category, device_type, model, etc.
    ) -> FeedbackAggregate:
        """
        Aggregate feedback metrics for analytics.
        """

    async def detect_model_drift(
        self,
        tenant_id: TenantId,
        window_days: int = 30,
    ) -> ModelDriftReport:
        """
        Detect if model performance is drifting.
        
        Metrics tracked:
          - Acceptance rate trend
          - Average confidence vs actual accuracy
          - Time-to-resolution trend
          - Feedback sentiment trend
        """
```

### 11.3 Feedback Processing Pipeline

```
User Feedback Received
        │
        ▼
┌─────────────────┐
│ Validate Input  │ ← Sanitize, validate engineer_id, recommendation_id
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Store Feedback │ ← PostgreSQL + Event emit
└────────┬────────┘
         │
         ├──────────────────────────────────────┐
         │                                      │
         ▼                                      ▼
┌─────────────────┐                    ┌─────────────────┐
│ Update Rec     │                    │ Update Knowledge│
│ Confidence Hist │                    │ Article Scores  │
└────────┬────────┘                    └────────┬────────┘
         │                                      │
         ▼                                      ▼
┌─────────────────┐                    ┌─────────────────┐
│ Update Model    │                    │ Flag for Review │
│ Performance    │                    │ if Quality < 0.5 │
└────────┬────────┘                    └────────┬────────┘
         │                                      │
         ▼                                      ▼
┌─────────────────┐                    ┌─────────────────┐
│ Detect Drift    │                    │ Notify Knowledge│
│ if threshold    │                    │ Team            │
└─────────────────┘                    └─────────────────┘
```

---

## 12. RAG ORCHESTRATOR

### 12.1 Responsabilidad

Orquestar el pipeline de Retrieval-Augmented Generation. Gestiona la búsqueda de embeddings, el reranqueo, la síntesis de múltiples documentos, y la actualización de índices.

### 12.2 Contrato

```python
class RAGOrchestrator:
    """
    Orchestrates the RAG pipeline for knowledge retrieval.
    """

    async def retrieve_and_synthesize(
        self,
        query: str,
        context: RetrievalContext,
        max_documents: int = 10,
        max_tokens: int = 60000,
    ) -> RAGResult:
        """
        Retrieve relevant documents and synthesize a response.
        
        RAGResult contains:
          - synthesized_answer: str
          - retrieved_documents: list[RetrievedDocument]
          - citations: list[Citation]
          - confidence: float
          - knowledge_gaps: list[str]  # What we couldn't find
        """

    async def retrieve_documents(
        self,
        query: str,
        filters: RetrievalFilters,
        max_results: int = 20,
    ) -> list[RetrievedDocument]:
        """
        Retrieve relevant documents from vector store and database.
        """

    async def rerank_documents(
        self,
        query: str,
        documents: list[RetrievedDocument],
        context: IncidentContextData | None = None,
    ) -> list[RerankedDocument]:
        """
        Rerank documents using cross-encoder and context relevance.
        """

    async def update_index(
        self,
        article_id: KnowledgeId,
        action: IndexAction,  # INDEX, UPDATE, DELETE
    ) -> None:
        """
        Update the vector index when knowledge changes.
        """
```

### 12.3 RAG Pipeline

```
Query: "MRI scanner display flickering"

Step 1: Query Understanding
  - Entity extraction: MRI scanner, display, flickering
  - Intent: troubleshooting
  - Context: HARDWARE_FAILURE

Step 2: Multi-Query Generation (LLM)
  - "display issues MRI scanner"
  - "MRI screen problems"
  - "magnetic resonance imaging visual artifacts"
  - "MRI troubleshooting guide"

Step 3: Parallel Retrieval
  - Vector search (embedding similarity)
  - BM25 keyword search
  - Knowledge graph traversal (device→category→articles)
  - Metadata filtering

Step 4: Hybrid Fusion (RRF)
  - Reciprocal Rank Fusion of all results
  - Combine vector + keyword + graph scores
  - Top 20 candidates

Step 5: Contextual Reranking
  - Cross-encoder: query vs document relevance
  - Context reranking: incident vs document match
  - Diversity reranking: avoid duplicates

Step 6: Document Selection
  - Select top 10 by reranked score
  - Respect token budget (60,000 tokens)
  - Include document metadata for citations

Step 7: Synthesis (LLM)
  - Build prompt with retrieved docs
  - Generate synthesized answer
  - Cite all sources
```

---

## 13. TOOL ORCHESTRATOR

### 13.1 Responsabilidad

Gestionar las herramientas disponibles para el modelo. Definir tools, validar parámetros, ejecutar llamadas, y procesar resultados. Acts as el bridge entre el LLM y los bounded contexts.

### 13.2 Tool Registry

```
Available Tools:

T-001: get_device_info
  Description: "Get detailed information about a biomedical device"
  Parameters: device_id, include_history (bool)
  Returns: DeviceDTO
  Rate Limit: 100/min

T-002: get_incident_details
  Description: "Get detailed information about an incident"
  Parameters: incident_id, include_investigation (bool)
  Returns: IncidentDTO

T-003: get_knowledge_articles
  Description: "Search knowledge base for relevant articles"
  Parameters: query, categories, device_type, limit
  Returns: list[KnowledgeArticleDTO]

T-004: get_incident_history
  Description: "Get historical incidents for a device"
  Parameters: device_id, days_back, status_filter
  Returns: list[IncidentDTO]

T-005: get_device_maintenance_history
  Description: "Get maintenance history for a device"
  Parameters: device_id, limit
  Returns: list[MaintenanceRecord]

T-006: get_calibration_status
  Description: "Get current calibration status of a device"
  Parameters: device_id
  Returns: CalibrationStatusDTO

T-007: check_safety_recalls
  Description: "Check for active recalls or safety alerts"
  Parameters: device_model, manufacturer, device_id
  Returns: list[RecallAlert]

T-008: calculate_device_uptime
  Description: "Calculate uptime statistics for a device"
  Parameters: device_id, period_days
  Returns: UptimeStatsDTO

T-009: get_active_recommendations
  Description: "Get active recommendations for an incident"
  Parameters: incident_id
  Returns: list[RecommendationDTO]
```

### 13.3 Contrato

```python
class ToolOrchestrator:
    """
    Manages tool execution for LLM-initiated actions.
    """

    async def execute_tool_call(
        self,
        tool_call: ToolCall,
        session_id: SessionId,
    ) -> ToolResult:
        """
        Execute a single tool call from the LLM.
        
        Steps:
          1. Validate tool exists and session has access
          2. Validate parameters against schema
          3. Check rate limits
          4. Execute tool (route to appropriate context)
          5. Transform result to standard format
          6. Log execution
          7. Return result
        """

    async def execute_parallel_tools(
        self,
        tool_calls: list[ToolCall],
        session_id: SessionId,
    ) -> list[ToolResult]:
        """
        Execute multiple tool calls in parallel.
        Used when LLM requests multiple independent data points.
        """

    async def validate_tool_parameters(
        self,
        tool_name: str,
        parameters: dict,
    ) -> ValidationResult:
        """
        Validate tool parameters against schema.
        """
```

---

## 14. KNOWLEDGE RETRIEVER

### 14.1 Responsabilidad

Recuperar conocimiento relevante de la base de conocimientos. Implementa búsqueda semántica, filtrado, y ranking de artículos de conocimiento.

### 14.2 Contrato

```python
class KnowledgeRetriever:
    """
    Retrieves relevant knowledge articles for context.
    """

    async def retrieve_for_incident(
        self,
        incident: IncidentDTO,
        device: DeviceDTO | None,
        max_articles: int = 10,
    ) -> RetrievalResult:
        """
        Retrieve knowledge articles relevant to an incident.
        
        Strategy:
          1. Match by device_type
          2. Match by incident_category
          3. Match by symptoms
          4. Match by tags
          5. Combine scores with hybrid search
        """

    async def retrieve_for_device(
        self,
        device: DeviceDTO,
        context_type: str,  # "troubleshooting", "maintenance", "manual"
        max_articles: int = 5,
    ) -> list[KnowledgeArticleDTO]:
        """
        Retrieve knowledge articles for a device.
        """

    async def synthesize_knowledge(
        self,
        query: str,
        articles: list[KnowledgeArticleDTO],
    ) -> str:
        """
        Synthesize information from multiple articles into a coherent response.
        """
```

---

## 15. PLANNING ENGINE

### 15.1 Responsabilidad

Planificar acciones multi-paso para troubleshooting complejo. Genera planes de acción, los refina, y los tracks durante la ejecución.

### 15.2 Contrato

```python
class PlanningEngine:
    """
    Generates and manages action plans for complex troubleshooting.
    """

    async def create_troubleshooting_plan(
        self,
        incident: IncidentDTO,
        device: DeviceDTO,
        symptoms: list[Symptom],
        context: IncidentContextData,
    ) -> ActionPlan:
        """
        Create a structured action plan for troubleshooting.
        
        ActionPlan contains:
          - plan_id: UUID
          - steps: list[PlanStep]
          - estimated_duration_minutes: int
          - risk_level: RiskLevel
          - required_tools: list[str]
          - required_certifications: list[str]
          - safety_checks: list[str]
          - alternative_branches: list[PlanStep]
        """

    async def refine_plan(
        self,
        plan: ActionPlan,
        execution_feedback: list[StepResult],
    ) -> ActionPlan:
        """
        Refine plan based on execution feedback.
        Adapts remaining steps to actual outcomes.
        """

    async def validate_plan_safety(
        self,
        plan: ActionPlan,
    ) -> PlanSafetyResult:
        """
        Validate entire plan for safety.
        """
```

---

## 16. RESPONSE COMPOSER

### 16.1 Responsabilidad

Componer la respuesta final para el usuario. Formatea según el rol del usuario, el contexto, y el tipo de contenido. Genera respuestas estructuradas y no estructuradas.

### 16.2 Contrato

```python
class ResponseComposer:
    """
    Composes final responses for users.
    Formats output based on user role and context.
    """

    async def compose_clinical_recommendation(
        self,
        recommendation: RecommendationResult,
        user_role: UserRole,
        format: ResponseFormat,  # DETAILED, SUMMARY, CLINICAL_BRIEF
    ) -> ComposedResponse:
        """
        Compose a clinical recommendation response.
        
        ComposedResponse contains:
          - primary_message: str  # Main recommendation
          - explanation: str  # Why this recommendation
          - actions: list[ActionItem]  # What to do
          - safety_warnings: list[str]
          - citations: list[Citation]
          - confidence_display: str  # "High confidence - 3 sources"
          - next_steps: str
          - escalation_info: str | None
          - metadata: dict
        """

    async def compose_troubleshooting_guidance(
        self,
        plan: ActionPlan,
        user_role: UserRole,
    ) -> ComposedResponse:
        """
        Compose step-by-step troubleshooting guidance.
        """

    async def compose_knowledge_answer(
        self,
        synthesis: str,
        citations: list[Citation],
        sources: list[KnowledgeArticleDTO],
        user_role: UserRole,
    ) -> ComposedResponse:
        """
        Compose a synthesized knowledge answer.
        """
```

### 16.3 Response Formats by Role

```
BIOMEDICAL_ENGINEER:
  - Full technical detail
  - All safety information
  - Complete reasoning chain
  - References to standards and regulations
  - Manufacturer documentation links

CLINICAL_TECHNICIAN:
  - Simplified steps
  - Clear safety warnings
  - What to do / what NOT to do
  - When to escalate
  - Visual aids when possible

PHYSICIAN:
  - Clinical impact focus
  - Patient safety priority
  - Minimal technical jargon
  - Actionable next steps
  - Escalation path clear

NURSE:
  - Simple instructions
  - Immediate actions
  - Clear escalation criteria
  - Monitoring parameters

ADMINISTRATOR:
  - Summary metrics
  - Resource implications
  - Timeline
  - Compliance notes
```

---

## 17. SECUENCIA COMPLETA

### 17.1 Diagrama de Secuencia: Recommendation Generation

```
User                    AI Layer                    Bounded Contexts
 │                           │                              │
 │  "MRI scanner flickering"  │                              │
 │ ─────────────────────────►│                              │
 │                           │                              │
 │                           │ 1. START SESSION             │
 │                           │ ───────────────────────────►│
 │                           │    (verify user, load pref) │
 │                           │ ◄──────────────────────────│
 │                           │    SessionInfo              │
 │                           │                              │
 │                           │ 2. CONTEXT BUILDER           │
 │                           │ ┌──────────────────────────┐ │
 │                           │ │ 2a. GET INCIDENT         │ │
 │                           │ │ ───────────────────────►│ │
 │                           │ │ ◄──────────────────────│ │
 │                           │ │ 2b. GET DEVICE          │ │
 │                           │ │ ──────────────────────►│ │
 │                           │ │ ◄─────────────────────│ │
 │                           │ │ 2c. GET KNOWLEDGE      │ │
 │                           │ │ ──────────────────────►│ │
 │                           │ │ ◄─────────────────────│ │
 │                           │ │ 2d. GET RECOMMENDATIONS│ │
 │                           │ │ ─────────────────────►│ │
 │                           │ │ ◄─────────────────────│ │
 │                           │ └──────────────────────────┘ │
 │                           │                              │
 │                           │ 3. MEMORY MANAGER             │
 │                           │ (load conversation history)  │
 │                           │                              │
 │                           │ 4. SAFETY ENGINE (Pre-check) │
 │                           │ (validate request safety)    │
 │                           │                              │
 │                           │ 5. REASONING ENGINE          │
 │                           │ ┌──────────────────────────┐ │
 │                           │ │ 5a. SELECT STRATEGY      │ │
 │                           │ │ 5b. RAG ORCHESTRATOR    │ │
 │                           │ │ 5c. TOOL ORCHESTRATOR   │ │
 │                           │ │ 5d. BUILD REASONING     │ │
 │                           │ └──────────────────────────┘ │
 │                           │                              │
 │                           │ 6. CONFIDENCE ENGINE         │
 │                           │ (calculate confidence)       │
 │                           │                              │
 │                           │ 7. EXPLAINABILITY ENGINE      │
 │                           │ (build explanations)         │
 │                           │                              │
 │                           │ 8. SAFETY ENGINE (Post-check)│
 │                           │ (validate recommendation)   │
 │                           │                              │
 │                           │ 9. RESPONSE COMPOSER         │
 │                           │ (format for user role)       │
 │                           │                              │
 │                           │ 10. MEMORY MANAGER           │
 │                           │ (save to session)            │
 │                           │                              │
 │   Recommendation          │                              │
 │ ◄─────────────────────────│                              │
 │ (with explanation,        │                              │
 │  confidence, citations)   │                              │
 │                           │                              │
 │ [User Feedback]           │                              │
 │ ─────────────────────────►│                              │
 │                           │                              │
 │                           │ 11. FEEDBACK ENGINE          │
 │                           │ (process feedback)            │
 │                           │ ───────────────────────────►│
 │                           │    (update metrics)          │
```

### 17.2 Flujo Completo Detallado

```
Flow: Clinical Decision Support for Critical Incident

Step 0: User Input
  Message: "MRI Scanner showing white noise in images. Started 30 min ago."
  Session: active
  Incident: linked (or new)

Step 1: Conversation Controller
  1.1. Receive message
  1.2. Classify intent: CLINICAL_SUPPORT
  1.3. Load session from MemoryManager
  1.4. Add message to conversation
  1.5. Route to RecommendationEngine

Step 2: Context Builder
  2.1. Query IncidentContext → Get/create incident
  2.2. Query DeviceContext → Get MRI scanner info
  2.3. Query KnowledgeContext → Get troubleshooting articles
  2.4. Query RecommendationContext → Get existing recommendations
  2.5. Build IncidentContextData

Step 3: Memory Manager
  3.1. Load conversation history (last 20 turns)
  3.2. Check for relevant episodic memories
  3.3. Combine into conversation context

Step 4: Safety Engine (Pre-validation)
  4.1. Check device type: MRI (CLASS_C)
  4.2. Check symptoms: imaging quality issue
  4.3. Preliminary safety class: CAUTION
  4.4. Flag: Requires human confirmation

Step 5: Prompt Builder
  5.1. Load prompt template: clinical_recommendation_v2
  5.2. Inject context data
  5.3. Inject conversation history
  5.4. Inject few-shot examples
  5.5. Build full prompt

Step 6: Reasoning Engine
  6.1. Select strategy: ChainOfThought + EvidenceBased
  6.2. Call LLM with prompt
  6.3. Receive structured output:
    - reasoning_chain: [...]
    - recommendation: {...}
    - confidence: {...}
    - evidence: [...]

Step 7: Confidence Engine
  7.1. Calculate data_quality_score: 0.85
  7.2. Calculate evidence_sufficiency_score: 0.78
  7.3. Calculate model_confidence_score: 0.82
  7.4. Calculate historical_accuracy_score: 0.75
  7.5. Overall: 0.80 (HIGH confidence)
  7.6. Human review required: YES (CLASS_C device)

Step 8: Explainability Engine
  8.1. Build reasoning chain explanation
  8.2. Generate citations (KB-00042, KB-00123, manufacturer_spec)
  8.3. Create evidence summary
  8.4. Build clinical explanation format

Step 9: Safety Engine (Post-validation)
  9.1. Validate recommendation against safety rules
  9.2. Check for contraindications
  9.3. Check device recalls
  9.4. Safety class: CAUTION
  9.5. Add safety warnings
  9.6. Require engineer confirmation

Step 10: Response Composer
  10.1. Format for biomedical_engineer role
  10.2. Include reasoning chain (detailed)
  10.3. Include confidence breakdown
  10.4. Include citations
  10.5. Add safety warnings
  10.6. Add escalation info

Step 11: Memory Manager
  11.1. Save turn to working memory
  11.2. Update session state
  11.3. Check summarization trigger

Step 12: Return Response to User
  Response includes:
  - Recommendation with explanation
  - Confidence: 80% (High confidence - 3 sources)
  - Safety: CAUTION - Engineer confirmation required
  - Citations: [KB-00042, KB-00123, Siemens Spec]
  - Next step: Verify RF coil connections

Step 13 (Async): Feedback Engine
  13.1. Wait for user feedback
  13.2. On feedback: Update confidence history
  13.3. On negative feedback: Flag for review
```

---

*Documento generado para implementación. Fase 3 completa.*
