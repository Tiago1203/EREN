/**
 * Chat Service
 * Consumes AI Kernel from PHASE 2
 */

import type {
  ChatMessage,
  ChatRequest,
  ChatResponse,
  Conversation,
  ConversationSummary,
  ClinicalContext,
  AIRecommendation,
  Source,
  UncertaintyInfo,
} from '../types/ai.types';

export class ChatService {
  private baseUrl: string;

  constructor(baseUrl: string = '/api/ai') {
    this.baseUrl = baseUrl;
  }

  /**
   * Envía un mensaje y obtiene respuesta
   */
  async sendMessage(
    message: string,
    context: ClinicalContext,
    agentId?: string,
    conversationId?: string
  ): Promise<ChatMessage> {
    const request: ChatRequest = {
      message,
      context,
      agentId,
      conversationId,
    };

    // TODO: Integrar con AI Kernel de PHASE 2
    // Por ahora retornar mock
    return this.getMockResponse(message, context, agentId);
  }

  /**
   * Streaming de respuesta
   */
  async streamMessage(
    message: string,
    context: ClinicalContext,
    agentId: string | undefined,
    onChunk: (chunk: string) => void
  ): Promise<void> {
    // TODO: Implementar streaming con AI Kernel
    const response = await this.sendMessage(message, context, agentId);
    onChunk(response.content);
  }

  /**
   * Obtiene lista de conversaciones
   */
  async getConversations(): Promise<ConversationSummary[]> {
    // TODO: Integrar con backend
    return this.getMockConversations();
  }

  /**
   * Obtiene detalle de conversación
   */
  async getConversation(id: string): Promise<Conversation | null> {
    // TODO: Integrar con backend
    return this.getMockConversationDetail(id);
  }

  /**
   * Crea nueva conversación
   */
  async createConversation(agentId?: string): Promise<ConversationSummary> {
    const conversation: ConversationSummary = {
      id: `conv-${Date.now()}`,
      title: 'Nueva conversación',
      agentId,
      agentName: agentId || 'General',
      lastMessageAt: new Date(),
      messageCount: 0,
    };
    return conversation;
  }

  /**
   * Elimina conversación
   */
  async deleteConversation(id: string): Promise<void> {
    // TODO: Integrar con backend
    console.log('Delete conversation:', id);
  }

  // ============== MOCK DATA ==============

  private getMockResponse(
    message: string,
    context: ClinicalContext,
    agentId?: string
  ): ChatMessage {
    const agentNames: Record<string, string> = {
      biomedical: 'Agente Biomédico',
      diagnostic: 'Agente de Diagnóstico',
      knowledge: 'Agente de Conocimiento',
      research: 'Agente de Investigación',
      planning: 'Agente de Planificación',
    };

    const responses: Record<string, string> = {
      default: `He recibido tu consulta sobre: "${message.substring(0, 50)}..."

Basándome en el contexto clínico y los datos disponibles, puedo ayudarte con:

1. **Análisis del problema**
   - Revisión de parámetros técnicos
   - Identificación de posibles causas

2. **Recomendaciones**
   - Acciones sugeridas basadas en mejores prácticas
   - Pasos de diagnóstico adicionales

3. **Recursos relacionados**
   - Artículos de la base de conocimiento
   - Protocolos aplicables

¿Hay algún aspecto específico que quieras que profundice?`,
    };

    return {
      id: `msg-${Date.now()}`,
      conversationId: 'current',
      role: 'assistant',
      content: responses.default,
      timestamp: new Date(),
      agentId: agentId || 'general',
      agentName: agentNames[agentId || ''] || 'EREN AI',
      confidence: 0.85,
      uncertainty: {
        level: 'medium',
        score: 0.15,
        message: 'Respuesta basada en conocimiento general',
        factors: ['Contexto limitado', 'Datos parciales'],
      },
      sources: [
        {
          id: 'src-1',
          title: 'Manual de Mantenimiento Preventivo',
          type: 'device_manual',
          relevance: 0.9,
        },
      ],
      recommendations: [
        {
          id: 'rec-1',
          type: 'action',
          title: 'Revisar historial de mantenimiento',
          description: 'Consultar registros de mantenimiento preventivo del equipo',
          confidence: 0.9,
          priority: 'high',
          actions: [
            {
              label: 'Ver historial',
              description: 'Abrir historial de mantenimientos',
            },
          ],
        },
      ],
    };
  }

  private getMockConversations(): ConversationSummary[] {
    return [
      {
        id: 'conv-1',
        title: 'Diagnóstico Bomba de Infusión',
        agentId: 'biomedical',
        agentName: 'Agente Biomédico',
        lastMessage: 'El problema parece estar relacionado con...',
        lastMessageAt: new Date(Date.now() - 2 * 60 * 60 * 1000),
        messageCount: 12,
      },
      {
        id: 'conv-2',
        title: 'Búsqueda de protocolos UCI',
        agentId: 'knowledge',
        agentName: 'Agente de Conocimiento',
        lastMessage: 'Encontré 3 protocolos relevantes...',
        lastMessageAt: new Date(Date.now() - 24 * 60 * 60 * 1000),
        messageCount: 8,
      },
      {
        id: 'conv-3',
        title: 'Planificación mantenimiento mensual',
        agentId: 'planning',
        agentName: 'Agente de Planificación',
        lastMessage: 'He generado el cronograma optimizado...',
        lastMessageAt: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000),
        messageCount: 15,
      },
    ];
  }

  private getMockConversationDetail(id: string): Conversation | null {
    const conversations = this.getMockConversations();
    const summary = conversations.find((c) => c.id === id);
    
    if (!summary) return null;

    return {
      id: summary.id,
      title: summary.title,
      agentId: summary.agentId,
      agentName: summary.agentName,
      messages: [
        {
          id: 'msg-1',
          conversationId: id,
          role: 'user',
          content: 'Tengo un problema con una bomba de infusión en UCI...',
          timestamp: new Date(Date.now() - 24 * 60 * 60 * 1000),
        },
        {
          id: 'msg-2',
          conversationId: id,
          role: 'assistant',
          content: 'Entendido. ¿Podrías describirme los síntomas que observas?',
          timestamp: new Date(Date.now() - 23 * 60 * 60 * 1000),
          agentId: summary.agentId,
          agentName: summary.agentName,
          confidence: 0.9,
        },
      ],
      context: {},
      createdAt: new Date(Date.now() - 24 * 60 * 60 * 1000),
      updatedAt: new Date(),
      messageCount: summary.messageCount,
    };
  }
}

export const chatService = new ChatService();
