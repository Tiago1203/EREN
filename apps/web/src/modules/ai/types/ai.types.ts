/**
 * Tipos para el módulo AI
 */

// ============== CHAT ==============

export type MessageRole = 'user' | 'assistant' | 'system';

export interface ChatMessage {
  id: string;
  conversationId: string;
  role: MessageRole;
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

export interface ChatRequest {
  message: string;
  context: ClinicalContext;
  agentId?: string;
  conversationId?: string;
}

export interface ChatResponse {
  message: ChatMessage;
  recommendations?: AIRecommendation[];
  sources?: Source[];
}

// ============== CONVERSATION ==============

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

export interface ConversationSummary {
  id: string;
  title: string;
  agentId?: string;
  agentName?: string;
  lastMessage?: string;
  lastMessageAt: Date;
  messageCount: number;
}

// ============== AGENTS ==============

export type AgentStatus = 'online' | 'offline' | 'busy';

export interface Agent {
  id: string;
  name: string;
  description: string;
  icon: string;
  capabilities: string[];
  specialties: string[];
  status: AgentStatus;
  model?: string;
  endpoint?: string;
}

export interface AgentRequest {
  agentId: string;
  query: string;
  context: ClinicalContext;
}

// ============== CLINICAL CONTEXT ==============

export interface ClinicalContext {
  patient?: PatientInfo;
  device?: DeviceInfo;
  location?: LocationInfo;
  temporal?: TemporalInfo;
  custom?: Record<string, unknown>;
}

export interface PatientInfo {
  id?: string;
  name?: string;
  age?: number;
  gender?: string;
  conditions?: string[];
  department?: string;
}

export interface DeviceInfo {
  id?: string;
  name?: string;
  type?: string;
  serialNumber?: string;
  manufacturer?: string;
  model?: string;
}

export interface LocationInfo {
  facility?: string;
  building?: string;
  floor?: string;
  department?: string;
  room?: string;
  bed?: string;
}

export interface TemporalInfo {
  startDate?: Date;
  endDate?: Date;
  shift?: 'morning' | 'afternoon' | 'night';
}

// ============== UNCERTAINTY ==============

export type UncertaintyLevel = 'low' | 'medium' | 'high' | 'unknown';

export interface UncertaintyInfo {
  level: UncertaintyLevel;
  score: number;
  message: string;
  factors: string[];
}

// ============== SOURCES ==============

export interface Source {
  id: string;
  title: string;
  type: 'article' | 'guideline' | 'protocol' | 'device_manual' | 'other';
  url?: string;
  citation?: string;
  relevance: number;
}

// ============== RECOMMENDATIONS ==============

export type RecommendationType = 'action' | 'suggestion' | 'warning' | 'info';
export type RecommendationPriority = 'low' | 'medium' | 'high';

export interface AIRecommendation {
  id: string;
  type: RecommendationType;
  title: string;
  description: string;
  confidence: number;
  priority: RecommendationPriority;
  actions?: RecommendedAction[];
  rationale?: string;
}

export interface RecommendedAction {
  label: string;
  description: string;
  endpoint?: string;
  icon?: string;
}

// ============== AI SETTINGS ==============

export interface AISettings {
  model: string;
  temperature: number;
  maxTokens: number;
  showConfidence: boolean;
  showSources: boolean;
  showUncertainty: boolean;
  streaming: boolean;
}

export const DEFAULT_AI_SETTINGS: AISettings = {
  model: 'gpt-4',
  temperature: 0.7,
  maxTokens: 2000,
  showConfidence: true,
  showSources: true,
  showUncertainty: true,
  streaming: true,
};

// ============== STATE ==============

export interface ChatState {
  messages: ChatMessage[];
  conversations: ConversationSummary[];
  activeConversationId: string | null;
  sending: boolean;
  error: string | null;
  context: ClinicalContext;
}

export interface AgentsState {
  agents: Agent[];
  selectedAgentId: string | null;
  loading: boolean;
  error: string | null;
}
