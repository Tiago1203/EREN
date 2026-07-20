# EREN - Especificación Técnica Completa
## Fase 5: Modelo Conversacional

> **Versión:** 1.0  
> **Fecha:** 2026-07-15  
> **Estado:** Ready for Implementation  
> **Depende de:** Fase 1 (Session), Fase 3 (AI Layer - ConversationController)

---

## Tabla de Contenidos

1. [Filosofía Conversacional](#1-filosofía-conversacional)
2. [Conversation Model](#2-conversation-model)
3. [Conversation Thread](#3-conversation-thread)
4. [Conversation Session](#4-conversation-session)
5. [Message Types](#5-message-types)
6. [Memory Architecture](#6-memory-architecture)
7. [Tool Calls](#7-tool-calls)
8. [Reasoning in Conversation](#8-reasoning-in-conversation)
9. [Feedback Loop](#9-feedback-loop)
10. [Context Window Management](#10-context-window-management)
11. [Persistence & Reconstruction](#11-persistence--reconstruction)

---

## Supuestos Declarados

1. **Session Duration:** Sesiones de hasta 8 horas para incidentes complejos, 30 días de retención
2. **Multi-turn Support:** Soporte para conversaciones de hasta 100+ turnos
3. **Concurrency:** Un usuario puede tener múltiples sesiones activas (diferentes incidentes)
4. **Attachment Support:** Soporte para imágenes (capturas de pantalla), logs, PDFs
5. **Role-based Context:** El rol del usuario afecta qué información se muestra
6. **Handoff:** Soporte para transferir conversación entre usuarios (handoff)
7. **Mobile Support:** Interacciones móviles con constraints de bandwidth
8. **Accessibility:** Cumplimiento WCAG 2.1 AA

---

## 1. FILOSOFÍA CONVERSACIONAL

### 1.1 Principios

**Principio 1: Clinical Safety**
- Toda conversación debe priorizar la seguridad del paciente
- El sistema debe interrumpir y warnear si detecta riesgos
- El clínico siempre tiene la decisión final

**Principio 2: Context Preservation**
- El sistema mantiene contexto completo a través de la conversación
- Referencias a turnos anteriores son siempre trazables
- El sistema nunca "olvida" información relevante

**Principio 3: Gradual Disclosure**
- Información compleja se presenta gradualmente
- Resúmenes ejecutivos primero, detalles bajo demanda
- Diferentes niveles de detalle para diferentes roles

**Principio 4: Proactive Assistance**
- El sistema anticipa necesidades basada en contexto
- Sugiere siguiente paso lógico
- Alert sobre inconsistencias o gaps de información

**Principio 5: Transparency**
- El sistema siempre indica cuando usa AI
- Clarifica qué información es factual vs inferida
- Hace visible su nivel de confianza

### 1.2 Tipos de Interacción

```
Type A: Active Investigation
  - Sesión activa sobre incidente
  - El sistema guía la investigación
  - Respuestas estructuradas con acciones

Type B: Knowledge Query
  - Consulta a la base de conocimientos
  - Respuestas informativas
  - Menor urgencia

Type C: Monitoring
  - Seguimiento pasivo de incidentes
  - El sistema alerta proactivamente
  - Respuestas breves

Type D: Handoff
  - Transferencia entre usuarios
  - Contexto completo preservado
  - Turno de交接

Type E: Training
  - Sesión de aprendizaje
  - Explicaciones educativas
  - Sin presión de tiempo
```

---

## 2. CONVERSATION MODEL

### 2.1 Core Entities

```python
@dataclass(frozen=True)
class Conversation:
    """
    Root entity for a conversation.
    Groups related turns around a specific context.
    """
    
    conversation_id: ConversationId
    tenant_id: TenantId
    
    # Context
    conversation_type: ConversationType  # INVESTIGATION, QUERY, MONITORING, HANDOFF, TRAINING
    primary_context_id: IncidentId | DeviceId | None  # Main context anchor
    secondary_context_ids: tuple[UUID, ...]  # Related contexts
    
    # Participants
    participants: tuple[Participant, ...]
    active_participant_id: EngineerId
    
    # Structure
    threads: tuple[ConversationThread, ...]
    root_thread_id: UUID
    
    # State
    status: ConversationStatus  # ACTIVE, SUSPENDED, CLOSED, ARCHIVED
    priority: Priority | None
    
    # Timeline
    created_at: datetime
    last_activity_at: datetime
    closed_at: datetime | None
    
    # Metadata
    title: str | None  # Auto-generated or user-provided
    tags: tuple[str, ...]
    metadata: dict
    
    # Access
    access_level: AccessLevel  # PRIVATE, TEAM, ORGANIZATION
    linked_conversations: tuple[ConversationId, ...]  # Related conversations
```

### 2.2 Conversation Types

```python
class ConversationType(Enum):
    INVESTIGATION = "investigation"      # Active incident/device investigation
    KNOWLEDGE_QUERY = "knowledge_query"  # Information lookup
    MONITORING = "monitoring"             # Passive monitoring
    HANDOFF = "handoff"                  # User transfer
    TRAINING = "training"                 # Educational session
    GENERAL = "general"                  # General assistance
```

### 2.3 Conversation Status

```python
class ConversationStatus(Enum):
    ACTIVE = "active"              # Ongoing conversation
    SUSPENDED = "suspended"       # Paused (user away, waiting for action)
    WAITING_RESPONSE = "waiting_response"  # Awaiting user/AI response
    CLOSED = "closed"            # Manually closed
    ARCHIVED = "archived"        # Automatically archived after closure
    EXPIRED = "expired"         # Session timeout
```

---

## 3. CONVERSATION THREAD

### 3.1 Thread Model

```python
@dataclass(frozen=True)
class ConversationThread:
    """
    A thread within a conversation.
    Threads allow branching conversations.
    """
    
    thread_id: UUID
    conversation_id: ConversationId
    parent_thread_id: UUID | None  # For branching
    
    # Content
    subject: str
    messages: tuple[Message, ...]
    
    # State
    status: ThreadStatus  # ACTIVE, RESOLVED, CLOSED
    priority: Priority | None
    
    # Participants
    participants: tuple[EngineerId, ...]
    assigned_to: EngineerId | None
    
    # Timeline
    created_at: datetime
    resolved_at: datetime | None
    last_message_at: datetime
    
    # Branching
    branch_point_message_id: UUID | None  # Message where thread branched
    merge_target_thread_id: UUID | None  # If this thread merges into another
```

### 3.2 Thread Operations

```
Thread Creation:
  - New thread can be created from any message
  - Thread inherits parent context
  - Thread can diverge and optionally merge back

Thread Branching:
  - Message can spawn a new thread
  - Original thread continues in parallel
  - Branching message is the "fork point"

Thread Merging:
  - Branch can be merged back to main thread
  - Merge creates summary message
  - Original branch is marked as MERGED

Example:
  Thread: "MRI display issue"
    Message 1: "MRI showing artifacts"  [spawns branch]
    Message 2: "Continuing with original issue"
    ---
    Branch Thread: "Root cause investigation"
      Message 1: "Let's check RF coils"
      Message 2: "Found worn connector"
    ---
    Message 3: "Root cause found - replacing RF coil"  [merge summary]
```

---

## 4. CONVERSATION SESSION

### 4.1 Session Model

```python
@dataclass(frozen=True)
class Session:
    """
    A user session within a conversation.
    Tracks per-user state in multi-party conversations.
    """
    
    session_id: SessionId
    conversation_id: ConversationId
    tenant_id: TenantId
    
    # User
    user_id: EngineerId
    user_role: UserRole
    user_name: str
    
    # State
    session_type: SessionType  # PRIMARY, VIEWER, HANDOFF_TARGET
    status: SessionStatus  # ACTIVE, AWAY, DISCONNECTED, CLOSED
    
    # Presence
    joined_at: datetime
    last_active_at: datetime
    away_at: datetime | None
    
    # Position
    current_thread_id: UUID
    last_read_message_id: UUID
    unread_count: int
    
    # Context
    active_incident_id: IncidentId | None
    active_device_id: DeviceId | None
    
    # Preferences
    notification_preferences: NotificationPreferences
    display_preferences: DisplayPreferences
    language_preference: str  # ISO 639-1
    
    # Memory
    local_memory: dict  # User-specific session memory
    
    # Security
    permissions: tuple[str, ...]
    session_token: str  # JWT or session token
```

### 4.2 Session Lifecycle

```
Session Lifecycle:

┌─────────┐    User opens       ┌───────────┐
│  NONE   │───────────────────►│  ACTIVE   │
└─────────┘                    └─────┬─────┘
      ▲                              │
      │ User closes                  │ User away (>5min)
      │ Session timeout              ▼
      │                            ┌────────┐
      │◄───────────────────────────│  AWAY  │
      │ User returns               └────────┘
      │                                    │
      │                                    │ User disconnects
      │                                    ▼
      │                            ┌───────────────┐
      │◄───────────────────────────│  DISCONNECTED  │
      │ Session cleanup            └───────────────┘
      │                                    │
      │                                    │ Session timeout (30 days)
      ▼                                    ▼
┌─────────┐                        ┌─────────┐
│  NONE   │                        │ EXPIRED │
└─────────┘                        └─────────┘
```

---

## 5. MESSAGE TYPES

### 5.1 Message Model

```python
@dataclass(frozen=True)
class Message:
    """A single message in a conversation."""
    
    message_id: UUID
    thread_id: UUID
    conversation_id: ConversationId
    
    # Content
    message_type: MessageType
    content: str
    content_format: ContentFormat  # MARKDOWN, PLAIN, HTML
    
    # Sender
    sender_type: SenderType  # USER, AI, SYSTEM, TOOL
    sender_id: str  # EngineerId or system identifier
    sender_name: str
    
    # Threading
    parent_message_id: UUID | None  # For replies
    in_reply_to: UUID | None  # Which message this responds to
    
    # AI-specific
    reasoning: ReasoningMetadata | None  # AI reasoning if applicable
    confidence: Confidence | None  # AI confidence if applicable
    safety_classification: SafetyClassification | None
    
    # Tool calls
    tool_calls: tuple[ToolCall, ...] | None
    tool_results: tuple[ToolResult, ...] | None
    
    # Attachments
    attachments: tuple[Attachment, ...] | None
    
    # State
    status: MessageStatus  # SENDING, SENT, DELIVERED, READ, FAILED
    is_edited: bool
    is_deleted: bool
    is_pinned: bool
    
    # Feedback
    user_feedback: Feedback | None
    thumbs_up: int  # Count
    thumbs_down: int  # Count
    
    # References
    referenced_entities: tuple[EntityReference, ...] | None  # Devices, incidents, etc.
    citations: tuple[Citation, ...] | None
    
    # Context
    intent: str | None  # Classified intent
    entities_extracted: tuple[ExtractedEntity, ...] | None
    
    # Timestamps
    created_at: datetime
    sent_at: datetime | None
    delivered_at: datetime | None
    read_at: datetime | None
    edited_at: datetime | None
```

### 5.2 Message Types

```python
class MessageType(Enum):
    # User messages
    USER_TEXT = "user_text"              # Direct text input
    USER_COMMAND = "user_command"       # Slash commands
    USER_ATTACHMENT = "user_attachment"  # File/image upload
    USER_REACTION = "user_reaction"     # Thumbs up/down
    USER_FEEDBACK = "user_feedback"     # Detailed feedback
    
    # AI messages
    AI_RECOMMENDATION = "ai_recommendation"  # Recommendation with full context
    AI_QUESTION = "ai_question"           # AI asking for clarification
    AI_SUGGESTION = "ai_suggestion"        # Next action suggestion
    AI_WARNING = "ai_warning"             # Safety warning
    AI_ESCALATION = "ai_escalation"       # Escalation notification
    AI_SUMMARY = "ai_summary"             # Auto-generated summary
    AI_CLARIFICATION = "ai_clarification" # Requesting clarification
    
    # System messages
    SYSTEM_NOTIFICATION = "system_notification"  # System alerts
    SYSTEM_STATUS = "system_status"        # Status updates
    SYSTEM_HANDOVER = "system_handover"    # Handoff notification
    SYSTEM_TIMER = "system_timer"         # Reminder/timer
    SYSTEM_ASSIGNMENT = "system_assignment"  # Assignment change
    
    # Tool messages
    TOOL_RESULT = "tool_result"          # Result from tool execution
    TOOL_ERROR = "tool_error"           # Tool execution error
    TOOL_PROGRESS = "tool_progress"      # Progress update
```

### 5.3 Structured Message Formats

```python
# AI Recommendation Message
@dataclass(frozen=True)
class AIRecommendationMessage:
    """Structured AI recommendation message."""
    
    message_id: UUID
    
    # Summary (always visible)
    summary: str  # One-line summary
    confidence_display: str  # "High confidence (82%)"
    safety_indicator: str  # "CAUTION" or "SAFE"
    
    # Full recommendation (expandable)
    full_recommendation: RecommendationDTO
    
    # Reasoning (expandable)
    reasoning_summary: str
    reasoning_chain: ReasoningChain | None
    
    # Evidence (expandable)
    top_evidence: tuple[Evidence, ...]  # Top 3
    all_evidence_count: int
    
    # Actions (always visible)
    primary_action: ActionItem
    alternative_actions: tuple[ActionItem, ...]
    
    # References
    citations: tuple[Citation, ...]
    knowledge_articles: tuple[KnowledgeArticleDTO, ...]
    
    # Safety
    safety_warnings: tuple[str, ...]
    required_verifications: tuple[str, ...]
    escalation_info: str | None
    
    # Metadata
    generated_at: datetime
    model_used: str
    expires_at: datetime | None
    human_review_required: bool
    human_review_status: str | None  # pending, approved, rejected


# AI Question Message
@dataclass(frozen=True)
class AIQuestionMessage:
    """AI asking for clarification."""
    
    message_id: UUID
    
    question: str
    question_type: QuestionType  # SPECIFIC_FACT, CLARIFICATION, CONFIRMATION
    
    # Context
    context: str  # Why we need this information
    relevant_to: str  # Which part of the recommendation this affects
    
    # Options (if multiple choice)
    options: tuple[str, ...] | None
    
    # Impact
    confidence_impact_if_missing: float  # How confidence changes without answer
    recommendation_blocked: bool  # True if can't proceed without answer


# System Handover Message
@dataclass(frozen=True)
class SystemHandoverMessage:
    """Handoff notification."""
    
    message_id: UUID
    
    handover_type: HandoverType  # USER_TRANSFER, ESCALATION, ASSIGNMENT_CHANGE
    
    from_user: UserSummary | None
    to_user: UserSummary | None
    
    context_summary: str
    critical_information: tuple[str, ...]  # Must-read items
    
    handover_token: str  # Encrypted handover context
    
    requires_acknowledgment: bool
    acknowledgment_deadline: datetime | None
```

---

## 6. MEMORY ARCHITECTURE

### 6.1 Memory Layers

```
┌─────────────────────────────────────────────────────────────┐
│                    EPISODIC MEMORY                            │
│  (Session summaries, key outcomes)                           │
│  - Stored: PostgreSQL                                         │
│  - Duration: 30 days                                          │
│  - Access: Fast retrieval by session/date                     │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   WORKING MEMORY                             │
│  (Current session, recent turns)                            │
│  - Stored: Redis (hot) + PostgreSQL (warm)                   │
│  - Duration: Current session only                            │
│  - Size: 10MB max per session                                │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   SEMANTIC MEMORY                            │
│  (User preferences, learned patterns)                        │
│  - Stored: PostgreSQL + Redis                                 │
│  - Duration: Indefinite (until user deletes)                 │
│  - Content: Preferences, patterns, learned facts             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                 CROSS-SESSION CONTEXT                         │
│  (Incident context, device context)                          │
│  - Stored: PostgreSQL                                         │
│  - Duration: Until incident resolved/device repaired          │
│  - Access: By incident/device ID                              │
└─────────────────────────────────────────────────────────────┘
```

### 6.2 Memory Models

```python
@dataclass(frozen=True)
class WorkingMemory:
    """Short-term memory for current session."""
    
    session_id: SessionId
    
    # Content
    recent_turns: list[Turn]  # Last N turns
    current_topic: str | None
    pending_questions: tuple[PendingQuestion, ...]
    active_recommendations: tuple[RecommendationId, ...]
    
    # State
    context_window_tokens: int
    memory_pressure: str  # "low", "medium", "high"
    
    # Summarization
    needs_summarization: bool
    last_summarization_at: datetime | None
    summary_threshold_turns: int  # Auto-summarize after N turns


@dataclass(frozen=True)
class EpisodicMemory:
    """Medium-term memory: session summaries."""
    
    episode_id: UUID
    session_id: SessionId
    tenant_id: TenantId
    user_id: EngineerId
    
    # Content
    episode_type: EpisodeType  # INVESTIGATION, QUERY, TROUBLESHOOTING
    summary: str  # 500 chars max
    key_outcomes: tuple[str, ...]  # 3-5 key findings
    action_items: tuple[str, ...]  # Open action items
    
    # Context
    primary_context_id: IncidentId | DeviceId | None
    primary_context_title: str | None
    
    # Participants
    participants: tuple[EngineerId, ...]
    
    # Quality
    usefulness_rating: float | None  # User rating
    was_resolved: bool
    
    # Timestamps
    session_start: datetime
    session_end: datetime
    stored_at: datetime


@dataclass(frozen=True)
class SemanticMemory:
    """Long-term memory: user preferences and patterns."""
    
    user_id: EngineerId
    tenant_id: TenantId
    
    # Preferences
    communication_style: str  # "concise", "detailed", "technical"
    notification_preferences: NotificationPreferences
    display_preferences: DisplayPreferences
    preferred_explanation_depth: str  # "brief", "standard", "comprehensive"
    
    # Learned patterns
    frequently_used_devices: tuple[DeviceId, ...]
    common_incident_types: tuple[str, ...]
    preferred_workflows: tuple[str, ...]
    
    # Knowledge state
    trained_topics: tuple[str, ...]  # Topics user has been trained on
    expertise_level: str  # "beginner", "intermediate", "expert"
    
    # Personal facts
    personal_facts: dict  # Name, department, shift, etc.
    
    # Updated
    last_updated: datetime
```

### 6.3 Turn Model

```python
@dataclass(frozen=True)
class Turn:
    """A single turn in the conversation."""
    
    turn_id: UUID
    session_id: SessionId
    
    # Structure
    user_message: Message
    ai_response: Message | None  # None if turn is still processing
    tool_calls_made: tuple[ToolCall, ...]
    tool_results: tuple[ToolResult, ...]
    
    # AI processing
    reasoning_strategy_used: str | None
    confidence_score: float | None
    safety_classification: str | None
    
    # Timing
    user_sent_at: datetime
    ai_generated_at: datetime | None
    total_latency_ms: int | None
    
    # Context
    context_snapshot: TurnContext  # Snapshot of context at turn time
    referenced_entities: tuple[EntityReference, ...]
    
    # Outcome
    user_satisfaction: int | None  # 1-5 if rated
    was_helpful: bool | None
    follow_up_questions: tuple[str, ...]
    
    # Token usage
    input_tokens: int
    output_tokens: int
    total_tokens: int
```

---

## 7. TOOL CALLS

### 7.1 Tool Call Model

```python
@dataclass(frozen=True)
class ToolCall:
    """A call to an external tool."""
    
    tool_call_id: UUID
    message_id: UUID
    
    # Tool
    tool_name: str
    tool_display_name: str  # Human-readable name
    
    # Parameters
    parameters: dict
    parameters_schema: dict  # For validation display
    
    # Execution
    status: ToolCallStatus  # PENDING, RUNNING, COMPLETED, FAILED
    started_at: datetime | None
    completed_at: datetime | None
    duration_ms: int | None
    
    # Result
    result: ToolResult | None
    error: str | None
    error_code: str | None
    
    # Display
    display_format: ToolDisplayFormat  # EXPANDED, COLLAPSED, HIDDEN
    user_visible: bool  # Show in conversation


@dataclass(frozen=True)
class ToolResult:
    """Result from a tool execution."""
    
    tool_call_id: UUID
    
    # Content
    result_type: str  # "data", "file", "status", "error"
    content: str | dict  # Structured result
    summary: str  # Short summary for display
    
    # Quality
    is_partial: bool  # True if truncated
    is_stale: bool  # True if data might be outdated
    
    # Cache
    cached: bool
    cached_at: datetime | None
    cache_ttl_seconds: int | None
    
    # Usage
    used_in_response: bool
    token_cost: int | None
```

### 7.2 Tool Display in Conversation

```
Conversation Display Format:

┌─────────────────────────────────────────────────────────┐
│ User: How do I calibrate the infusion pump?             │
│                                    14:30:00 [Read ✓]   │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ 🛠️ Retrieving calibration procedure...                  │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ 🔧 get_calibration_procedure(device_id="pump-001")  │ │
│ │    Status: Running...                                │ │
│ └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ 🔧 Tool Result (completed in 120ms)                     │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ Calibration Procedure CP-2024-0042                    │ │
│ │ • Required: Certified engineer                        │ │
│ │ • Duration: 45 minutes                              │ │
│ │ • Next due: 2026-08-01                             │ │
│ │ [View full procedure →]                             │ │
│ └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ 🤖 AI: Based on the device specifications and our        │
│ calibration history, here's the procedure for the       │
│ infusion pump (Model: Alaris 8100):                     │
│                                                          │
│ **Recommended Calibration Steps:**                        │
│ 1. Verify pump is idle and unloaded                     │
│ 2. Access calibration mode (Code: 4-7-2)                │
│ ...                                                     │
│                                                          │
│ ⚠️ CAUTION: Ensure patient safety during calibration     │
│                                                          │
│ Confidence: 88% | Evidence: 3 sources                    │
│                                         14:30:05 [✓✓]  │
└─────────────────────────────────────────────────────────┘
```

---

## 8. REASONING IN CONVERSATION

### 8.1 Reasoning Visibility Levels

```python
class ReasoningVisibility(Enum):
    """
    How much reasoning is shown to the user.
    """
    
    HIDDEN = "hidden"               # Show only final response
    SUMMARY = "summary"             # Show reasoning summary
    KEY_STEPS = "key_steps"         # Show key reasoning steps
    FULL = "full"                  # Show complete reasoning chain
    EXPERT = "expert"               # Show everything including caveats
```

### 8.2 Reasoning Display

```
┌─────────────────────────────────────────────────────────┐
│ User: Why is the MRI showing these artifacts?             │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ 🤖 AI: Let me analyze this step by step...               │
│                                                          │
│ **Reasoning Summary:**                                  │
│ 1. Analyzing the artifact pattern (white noise)         │
│ 2. Cross-referencing with incident history              │
│ 3. Checking device-specific knowledge                    │
│ 4. Forming hypothesis                                    │
│                                                          │
│ **Key Finding:**                                        │
│ Based on the artifact pattern (intermittent white noise │
│ with no consistent band), this is most consistent with  │
│ an RF coil connector issue.                             │
│                                                          │
│ **Evidence:**                                           │
│ • 3 similar incidents on this device type               │
│ • RF system troubleshooting guide (KB-00042)            │
│ • Manufacturer service bulletin (SM-2024-015)           │
│                                                          │
│ Confidence: 78% (Medium-High)                          │
│ [Show full reasoning ↓]                                 │
└─────────────────────────────────────────────────────────┘

Expanded view (on click):
┌─────────────────────────────────────────────────────────┐
│ 🤖 AI: Let me analyze this step by step...               │
│                                                          │
│ **Reasoning Chain:**                                    │
│                                                          │
│ Step 1: Problem Analysis                                 │
│ The white noise pattern indicates RF signal             │
│ degradation. This is confirmed by 94% of similar         │
│ cases in our history.                                   │
│ Evidence: KB-00042, Incident INC-2024-00521            │
│                                                          │
│ Step 2: Component Analysis                               │
│ RF issues can be caused by:                             │
│ • RF coil failure (60% of cases)                        │
│ • Cable damage (25% of cases)                          │
│ • Preamplifier failure (10% of cases)                   │
│ • Software issue (5% of cases)                        │
│                                                          │
│ Step 3: Pattern Matching                                 │
│ The intermittent nature and specific pattern of         │
│ artifacts points to RF coil connector issue rather       │
│ than complete coil failure.                              │
│ Evidence: KB-00042, Service Manual p.45                │
│                                                          │
│ **Alternative Hypotheses Considered:**                  │
│ • Preamplifier failure - Different artifact pattern      │
│ • Cable damage - Would show consistent band pattern      │
│ • Software issue - No hardware symptoms present          │
│                                                          │
│ Confidence: 78%                                         │
│ Quality: 0.85 | Evidence: 0.78 | Model: 0.82           │
│ Human Review: Not required (CLASS_B device)            │
│                                         [Hide reasoning] │
└─────────────────────────────────────────────────────────┘
```

---

## 9. FEEDBACK LOOP

### 9.1 Feedback Types

```python
@dataclass(frozen=True)
class MessageFeedback:
    """Feedback on a specific message."""
    
    feedback_id: UUID
    message_id: UUID
    user_id: EngineerId
    
    # Quick feedback
    thumbs_up: bool | None
    thumbs_down: bool | None
    
    # Detailed feedback
    rating: int | None  # 1-5
    was_helpful: bool | None
    was_accurate: bool | None
    was_actionable: bool | None
    was_safe: bool | None
    was_timely: bool | None
    
    # Free text
    comments: str | None
    what_was_wrong: str | None
    what_was_right: str | None
    suggested_improvement: str | None
    
    # Context
    follow_up_question: str | None
    alternative_action_taken: str | None
    outcome_confirmed: bool | None
    
    # Timestamps
    created_at: datetime
    responded_at: datetime | None
```

### 9.2 Feedback Integration

```
User Feedback Flow:

1. User sees message
   ↓
2. Quick feedback: 👍/👎 (immediate)
   ↓ OR detailed feedback
3. Rating 1-5 (after action)
   ↓
4. Outcome confirmation (after resolution)
   ↓
5. Feedback stored
   ↓
6. Feedback Engine processes
   ↓
7. Metrics updated
   ↓
8. Model improvement triggered (if needed)
```

---

## 10. CONTEXT WINDOW MANAGEMENT

### 10.1 Context Budget

```
Token Budget: 128,000 tokens (GPT-4o)

Allocation per Conversation Type:

INVESTIGATION (Incident):
  - System prompt: 4,000 tokens
  - Incident context: 30,000 tokens
  - Device context: 15,000 tokens
  - Knowledge retrieval: 40,000 tokens
  - Conversation history: 25,000 tokens
  - Output buffer: 14,000 tokens
  ────────────────────────────────
  Total: 128,000 tokens

KNOWLEDGE_QUERY:
  - System prompt: 4,000 tokens
  - Retrieved knowledge: 60,000 tokens
  - Conversation history: 30,000 tokens
  - Output buffer: 34,000 tokens
  ────────────────────────────────
  Total: 128,000 tokens

MONITORING:
  - System prompt: 4,000 tokens
  - Status data: 20,000 tokens
  - Conversation history: 10,000 tokens
  - Output buffer: 94,000 tokens
  ────────────────────────────────
  Total: 128,000 tokens
```

### 10.2 Context Window Strategy

```
Overflow Strategy (when context exceeds budget):

Strategy 1: Progressive Truncation
  1. Truncate oldest conversation turns first
  2. Keep last N turns + summary of older turns
  3. Re-check budget

Strategy 2: Semantic Truncation
  1. Identify semantically important turns
  2. Remove less important turns
  3. Prioritize: recent > relevant > frequent

Strategy 3: Summary Injection
  1. When working memory exceeds 50%
  2. Generate summary of older turns
  3. Replace turns with summary
  4. Store full turns in episodic memory

Strategy 4: Context Reconstruction
  1. When budget is exhausted
  2. Keep only last 5 turns in working memory
  3. Store full conversation in session
  4. On next turn: retrieve needed context from session
```

### 10.3 Summarization Triggers

```
Automatic Summarization Triggers:
  - Working memory > 50% capacity
  - Session > 30 turns
  - Context switch (different incident/device)
  - User requests summary
  - Session pause > 30 minutes
  - System load high

Summary Format:
  - Max 500 tokens
  - Include: topic, key findings, open questions, user preferences
  - Exclude: routine exchanges, tool results, acknowledgments
```

---

## 11. PERSISTENCE & RECONSTRUCTION

### 11.1 Persistence Strategy

```
Storage Tiers:

Tier 1: Hot (Redis)
  - Active sessions
  - Recent messages (< 7 days)
  - Session state
  - Presence data
  - TTL: 8 hours (inactive), 30 days (active)

Tier 2: Warm (PostgreSQL)
  - Sessions (< 30 days)
  - All messages (< 30 days)
  - Episodic memories
  - Turn data
  - Full retention

Tier 3: Cold (PostgreSQL + S3)
  - Archived conversations (> 30 days)
  - Attachments
  - Message content
  - Search indexes
  - Indefinite retention (per compliance)
```

### 11.2 Session Reconstruction

```python
async def reconstruct_session(
    session_id: SessionId,
    start_turn: int = 0,
    end_turn: int | None = None,
    include_reasoning: bool = False,
    include_metadata: bool = True,
) -> ReconstructedSession:
    """
    Reconstruct a session for display or continuation.
    """
    
    # 1. Load session metadata
    session = await session_store.get(session_id)
    
    # 2. Load turns (paginated)
    turns = await turn_store.get_range(
        session_id=session_id,
        start=start_turn,
        end=end_turn,
    )
    
    # 3. Reconstruct messages
    messages = []
    for turn in turns:
        user_msg = await message_store.get(turn.user_message_id)
        ai_msg = await message_store.get(turn.ai_message_id) if turn.ai_message_id else None
        
        messages.append(ReconstructedMessage(
            turn_number=turn.turn_number,
            user_message=user_msg,
            ai_message=ai_msg,
            tool_calls=turn.tool_calls if include_metadata else None,
            reasoning=turn.reasoning if include_reasoning and ai_msg else None,
            context_snapshot=turn.context_snapshot if include_metadata else None,
        ))
    
    # 4. Reconstruct memory state
    working_memory = await memory_store.get_working_memory(session_id)
    if working_memory.needs_summarization:
        # Retrieve older turns from episodic memory
        episodic = await memory_store.get_episodic(session_id)
        working_memory = merge_with_summary(working_memory, episodic)
    
    return ReconstructedSession(
        session=session,
        messages=messages,
        working_memory=working_memory,
        context_window=calculate_remaining_context(),
    )
```

### 11.3 Resume Session

```
Session Resume Flow:

1. User selects session to resume
   ↓
2. Load session metadata
   ↓
3. Load recent turns (last 20)
   ↓
4. Load episodic summary (if session was summarized)
   ↓
5. Reconstruct working memory state
   ↓
6. Identify pending items
   ↓
7. Generate resume context
   ↓
8. Display session with resume message:
   "Resuming session from [timestamp]. 
    [Summary of where we left off].
    You had [N] pending questions."
```

### 11.4 Auto-Summary

```python
async def generate_session_summary(
    session: Session,
    turns: list[Turn],
) -> SessionSummary:
    """
    Generate an auto-summary of the session.
    """
    
    # Extract key information
    topics_discussed = extract_topics(turns)
    decisions_made = extract_decisions(turns)
    recommendations_given = extract_recommendations(turns)
    actions_taken = extract_actions(turns)
    pending_items = extract_pending(turns)
    
    # Identify outcomes
    outcomes = identify_outcomes(turns)
    
    # Generate summary
    summary_prompt = f"""
    Generate a 500-token summary of this session:
    
    Topics: {topics_discussed}
    Key Decisions: {decisions_made}
    Recommendations: {recommendations_given}
    Actions Taken: {actions_taken}
    Outcomes: {outcomes}
    Pending: {pending_items}
    
    Format:
    - One-line overview
    - 3-5 key points
    - Current status
    - Open items
    """
    
    summary = await llm.generate(summary_prompt)
    
    return SessionSummary(
        overview=summary.overview,
        key_points=summary.key_points,
        current_status=summary.current_status,
        open_items=summary.open_items,
        generated_at=datetime.now(),
    )
```

---

## 12. CONVERSATION CONTEXT MANAGEMENT

### 12.1 Context Types

```python
@dataclass(frozen=True)
class ConversationContext:
    """
    Current context of a conversation.
    Used to maintain context across turns.
    """
    
    # Identity
    conversation_id: ConversationId
    session_id: SessionId
    tenant_id: TenantId
    
    # Primary context
    active_incident: IncidentDTO | None
    active_device: DeviceDTO | None
    active_recommendation: RecommendationDTO | None
    
    # Related contexts
    related_incidents: tuple[IncidentDTO, ...]
    related_devices: tuple[DeviceDTO, ...]
    related_articles: tuple[KnowledgeArticleDTO, ...]
    
    # State
    current_phase: ConversationPhase  # INVESTIGATING, DECIDING, ACTING, MONITORING
    pending_actions: tuple[str, ...]
    open_questions: tuple[str, ...]
    decisions_made: tuple[str, ...]
    
    # User state
    user_goals: tuple[str, ...]
    user_preferences: UserPreferences
    
    # Progress
    progress_percentage: float
    estimated_time_remaining: int | None  # minutes
    completion_criteria: tuple[str, ...]
```

### 12.2 Conversation Phases

```python
class ConversationPhase(Enum):
    """Phases of an investigation conversation."""
    
    ENGAGEMENT = "engagement"         # Initial engagement, understanding problem
    INVESTIGATION = "investigation"  # Gathering information, analyzing
    DECISION = "decision"             # Evaluating options, making recommendation
    ACTION = "action"                 # Planning and executing actions
    MONITORING = "monitoring"         # Post-action monitoring
    RESOLUTION = "resolution"         # Confirming resolution, closing
    FOLLOW_UP = "follow_up"           # Scheduled follow-up
```

---

*Documento generado para implementación. Fase 5 completa.*
