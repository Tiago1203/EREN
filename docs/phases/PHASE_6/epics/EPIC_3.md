# EPIC 3: AI Center & Chat

*Versión: 1.0.0*
*Fecha: 2026-07-24*

---

## Objetivo

**Integrar el Cognitive Operating System (PHASE 5) en una interfaz de usuario accesible.**

EPIC 3 es responsable de:
- Crear interfaz de chat conversacional con IA
- Proveer panel de selección de agentes especializados
- Implementar constructor de contexto clínico
- Gestionar historial de conversaciones
- Consumir AI Kernel de PHASE 2 y agentes de PHASE 5

---

## Dependencias

```
FASE 5 (Cognitive Multi-Agent System)
        │
        ├── PHASE 2 (AI Core)
        ├── EPIC 12 (Clinical Context)
        ├── EPIC 13 (Evidence Lifecycle)
        └── EPIC 14 (Uncertainty Quantification)
                │
                ▼
           PHASE 6 (Hospital Platform)
                │
                ▼
           EPIC 0 (Platform Foundation)
                │
                ▼
           EPIC 1 (Dashboard & Navigation)
                │
                ▼
           EPIC 2 (Operations Center)
                │
                ▼
           EPIC 3 (AI Center & Chat)
                │
                ▼
           EPIC 4 (Knowledge Center)
```

---

## Arquitectura

```
┌─────────────────────────────────────────────────────────────────────────┐
│                   EPIC 3: AI Center & Chat                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    AI MODULE                                       │   │
│  │  ├── components/ ──────────────────── ChatInterface, AgentPanel  │   │
│  │  ├── pages/ ──────────────────────── page.tsx (AI Center)        │   │
│  │  ├── hooks/ ─────────────────────── useChat, useAgents          │   │
│  │  ├── services/ ──────────────────── ChatService, AgentService    │   │
│  │  ├── stores/ ────────────────────── chat.store, agents.store     │   │
│  │  ├── types/ ─────────────────────── ai.types                     │   │
│  │  └── utils/ ─────────────────────── message-parser               │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    INTEGRATION LAYER                                │   │
│  │  ├── PHASE 2 AI Kernel ────────────── AI Kernel Client          │   │
│  │  ├── PHASE 5 Agents ────────────────── Agent Gateway              │   │
│  │  ├── PHASE 5 Clinical Context ──────── Context Builder          │   │
│  │  └── PHASE 5 Uncertainty ───────────── Uncertainty Display        │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Estructura de Archivos

```
apps/web/src/modules/
├── ai/                                 # Módulo AI
│   ├── components/
│   │   ├── ChatInterface.tsx
│   │   ├── ChatMessage.tsx
│   │   ├── ChatInput.tsx
│   │   ├── AgentPanel.tsx
│   │   ├── AgentCard.tsx
│   │   ├── AgentSelector.tsx
│   │   ├── ContextBuilder.tsx
│   │   ├── ConversationList.tsx
│   │   ├── ConversationItem.tsx
│   │   ├── AISettings.tsx
│   │   └── UncertaintyIndicator.tsx
│   ├── hooks/
│   │   ├── useChat.ts
│   │   ├── useAgents.ts
│   │   ├── useContextBuilder.ts
│   │   └── useConversation.ts
│   ├── services/
│   │   ├── chat.service.ts
│   │   ├── agent.service.ts
│   │   ├── context.service.ts
│   │   └── ai-config.service.ts
│   ├── stores/
│   │   ├── chat.store.ts
│   │   └── agents.store.ts
│   ├── types/
│   │   └── ai.types.ts
│   ├── utils/
│   │   └── message-parser.ts
│   └── pages/
│       └── page.tsx
```

---

## Componentes

### 1. ChatInterface

Interfaz principal de chat.

```typescript
// modules/ai/components/ChatInterface.tsx
export interface ChatInterfaceProps {
  agentId?: string;
  context?: ClinicalContext;
  onMessageSend?: (message: string) => void;
}
```

### 2. ChatMessage

Mensaje individual del chat.

```typescript
// modules/ai/components/ChatMessage.tsx
export interface ChatMessageProps {
  message: ChatMessage;
  showTimestamp?: boolean;
  showAgent?: boolean;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  agentId?: string;
  agentName?: string;
  confidence?: number;
  sources?: Source[];
  error?: string;
}
```

### 3. ChatInput

Input para enviar mensajes.

```typescript
// modules/ai/components/ChatInput.tsx
export interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
  maxLength?: number;
}
```

### 4. AgentPanel / AgentCard / AgentSelector

Panel de selección de agentes.

```typescript
// modules/ai/components/AgentSelector.tsx
export interface AgentSelectorProps {
  agents: Agent[];
  selectedAgentId?: string;
  onSelect: (agentId: string) => void;
  compact?: boolean;
}

export interface Agent {
  id: string;
  name: string;
  description: string;
  icon: string;
  capabilities: string[];
  status: 'online' | 'offline' | 'busy';
}
```

### 5. ContextBuilder

Constructor de contexto clínico.

```typescript
// modules/ai/components/ContextBuilder.tsx
export interface ContextBuilderProps {
  context: ClinicalContext;
  onUpdate: (context: ClinicalContext) => void;
  onClear: () => void;
}

export interface ClinicalContext {
  patient?: PatientInfo;
  device?: DeviceInfo;
  location?: LocationInfo;
  temporal?: TemporalInfo;
  custom?: Record<string, any>;
}
```

### 6. ConversationList / ConversationItem

Lista de conversaciones.

```typescript
// modules/ai/components/ConversationList.tsx
export interface ConversationListProps {
  conversations: Conversation[];
  selectedId?: string;
  onSelect: (id: string) => void;
  onDelete?: (id: string) => void;
  onNewChat: () => void;
}

export interface Conversation {
  id: string;
  title: string;
  agentId?: string;
  lastMessage?: string;
  lastMessageAt: Date;
  messageCount: number;
}
```

### 7. AISettings

Configuración de IA.

```typescript
// modules/ai/components/AISettings.tsx
export interface AISettingsProps {
  settings: AISettings;
  onUpdate: (settings: AISettings) => void;
}

export interface AISettings {
  model: string;
  temperature: number;
  maxTokens: number;
  showConfidence: boolean;
  showSources: boolean;
}
```

### 8. UncertaintyIndicator

Indicador de incertidumbre.

```typescript
// modules/ai/components/UncertaintyIndicator.tsx
export interface UncertaintyIndicatorProps {
  level: UncertaintyLevel;
  message?: string;
  expandable?: boolean;
}

export type UncertaintyLevel = 'low' | 'medium' | 'high' | 'unknown';
```

---

## Implementaciones

### ChatService

```typescript
// modules/ai/services/chat.service.ts
export class ChatService {
  private client: AIKernelClient;

  async sendMessage(
    message: string,
    context: ClinicalContext,
    agentId?: string
  ): Promise<ChatResponse>;

  async streamMessage(
    message: string,
    context: ClinicalContext,
    agentId?: string,
    onChunk: (chunk: string) => void
  ): Promise<void>;

  async getConversations(): Promise<Conversation[]>;
  async getConversation(id: string): Promise<ConversationDetail>;
  async createConversation(agentId?: string): Promise<Conversation>;
  async deleteConversation(id: string): Promise<void>;
}
```

### AgentService

```typescript
// modules/ai/services/agent.service.ts
export class AgentService {
  async getAgents(): Promise<Agent[]>;
  async getAgent(id: string): Promise<Agent | null>;
  async getAgentCapabilities(id: string): Promise<string[]>;
  async getAgentStatus(id: string): Promise<AgentStatus>;
}
```

### ContextBuilderService

```typescript
// modules/ai/services/context.service.ts
export class ContextBuilderService {
  buildContext(partial: Partial<ClinicalContext>): ClinicalContext;
  validateContext(context: ClinicalContext): ValidationResult;
  mergeContext(existing: ClinicalContext, update: Partial<ClinicalContext>): ClinicalContext;
}
```

### AIConfigService

```typescript
// modules/ai/services/ai-config.service.ts
export class AIConfigService {
  getSettings(): AISettings;
  updateSettings(settings: Partial<AISettings>): AISettings;
  resetSettings(): AISettings;
}
```

---

## Domain Objects

### ChatMessage

```typescript
// modules/ai/types/ai.types.ts
export interface ChatMessage {
  id: string;
  conversationId: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  agentId?: string;
  agentName?: string;
  confidence?: number;
  uncertainty?: UncertaintyInfo;
  sources?: Source[];
  recommendations?: AIRecommendation[];
  error?: string;
}

export interface UncertaintyInfo {
  level: UncertaintyLevel;
  message: string;
  factors: string[];
}

export type UncertaintyLevel = 'low' | 'medium' | 'high' | 'unknown';
```

### Conversation

```typescript
export interface Conversation {
  id: string;
  title: string;
  agentId?: string;
  agentName?: string;
  messages: ChatMessage[];
  context: ClinicalContext;
  createdAt: Date;
  updatedAt: Date;
  messageCount: number;
}
```

### Agent

```typescript
export interface Agent {
  id: string;
  name: string;
  description: string;
  icon: string;
  capabilities: string[];
  specialties: string[];
  status: 'online' | 'offline' | 'busy';
  model?: string;
  endpoint?: string;
}
```

### ClinicalContext

```typescript
export interface ClinicalContext {
  patient?: {
    id?: string;
    name?: string;
    age?: number;
    gender?: string;
    conditions?: string[];
  };
  device?: {
    id?: string;
    name?: string;
    type?: string;
    serialNumber?: string;
  };
  location?: {
    facility?: string;
    department?: string;
    room?: string;
  };
  temporal?: {
    startDate?: Date;
    endDate?: Date;
  };
  custom?: Record<string, any>;
}
```

### AIRecommendation

```typescript
export interface AIRecommendation {
  id: string;
  type: 'action' | 'suggestion' | 'warning' | 'info';
  title: string;
  description: string;
  confidence: number;
  priority: 'low' | 'medium' | 'high';
  actions?: RecommendedAction[];
}

export interface RecommendedAction {
  label: string;
  description: string;
  endpoint?: string;
}
```

---

## Integración con PHASE 2 y PHASE 5

```
PHASE 2 (AI Core)
        │
        ├── AI Kernel
        ├── Context Builder
        ├── Memory Manager
        └── LLM Providers
                │
                ▼
PHASE 5 (Multi-Agent System)
        │
        ├── Biomedical Agent
        ├── Diagnostic Agent
        ├── Knowledge Agent
        ├── Research Agent
        ├── Planning Agent
        ├── Clinical Context (EPIC 12)
        ├── Evidence Lifecycle (EPIC 13)
        └── Uncertainty (EPIC 14)
                │
                ▼
           EPIC 3 (AI Center)
                │
                ├── ChatInterface
                ├── AgentSelector
                ├── ContextBuilder
                └── UncertaintyIndicator
```

### AI Kernel Client

```typescript
// packages/ai-sdk/src/client.ts
export interface AIKernelClient {
  chat(request: ChatRequest): Promise<ChatResponse>;
  streamChat(
    request: ChatRequest,
    onChunk: (chunk: string) => void
  ): Promise<void>;
  getAgents(): Promise<Agent[]>;
  getConversationHistory(conversationId: string): Promise<ChatMessage[]>;
}
```

---

## Estado

**🚧 EN PROGRESO**

EPIC 3 está en desarrollo.

---

## Tareas

- [x] Crear documentación EPIC 3
- [x] Crear tipos para AI
- [x] Crear servicios del módulo
- [x] Crear stores Zustand
- [x] Crear hooks
- [x] Crear componentes
- [x] Crear página de AI Center
- [ ] Crear tests unitarios
- [ ] Integrar con PHASE 2 y PHASE 5

---

## Próximos Pasos

- EPIC 4: Knowledge Center
- EPIC 5: Analytics & Reports

---

*EREN PHASE 6 - EPIC 3*
*Architecture Board - 2026-07-24*
