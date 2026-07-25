'use client';

import { useCallback, useEffect } from 'react';
import { useChatStore } from '../stores/chat.store';
import { chatService } from '../services/chat.service';
import type { ChatMessage, ClinicalContext } from '../types/ai.types';

export interface UseChatReturn {
  // Data
  messages: ChatMessage[];
  conversations: ReturnType<typeof useChatStore>['conversations'];
  activeConversationId: string | null;
  sending: boolean;
  error: string | null;
  context: ClinicalContext;

  // Actions
  sendMessage: (message: string) => Promise<void>;
  loadConversations: () => Promise<void>;
  selectConversation: (id: string) => Promise<void>;
  deleteConversation: (id: string) => Promise<void>;
  setContext: (context: ClinicalContext) => void;
  updateContext: (context: Partial<ClinicalContext>) => void;
  clearContext: () => void;
  clearMessages: () => void;
  startNewChat: () => void;
}

export function useChat(): UseChatReturn {
  const {
    messages,
    conversations,
    activeConversationId,
    sending,
    error,
    context,
    setMessages,
    addMessage,
    clearMessages,
    setConversations,
    setActiveConversation,
    removeConversation,
    setContext,
    updateContext,
    clearContext,
    setSending,
    setError,
  } = useChatStore();

  const sendMessage = useCallback(async (message: string) => {
    if (!message.trim() || sending) return;

    try {
      setSending(true);
      setError(null);

      // Add user message
      const userMessage: ChatMessage = {
        id: `msg-${Date.now()}`,
        conversationId: activeConversationId || 'new',
        role: 'user',
        content: message,
        timestamp: new Date(),
      };
      addMessage(userMessage);

      // Get AI response
      const response = await chatService.sendMessage(
        message,
        context,
        undefined,
        activeConversationId || undefined
      );

      // Add assistant message
      addMessage(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error sending message');
      
      // Add error message
      const errorMessage: ChatMessage = {
        id: `msg-${Date.now()}`,
        conversationId: activeConversationId || 'new',
        role: 'assistant',
        content: 'Lo siento, occurredió un error al procesar tu mensaje.',
        timestamp: new Date(),
        error: err instanceof Error ? err.message : 'Unknown error',
      };
      addMessage(errorMessage);
    } finally {
      setSending(false);
    }
  }, [context, activeConversationId, sending, addMessage, setSending, setError]);

  const loadConversations = useCallback(async () => {
    try {
      const convs = await chatService.getConversations();
      setConversations(convs);
    } catch (err) {
      console.error('Error loading conversations:', err);
    }
  }, [setConversations]);

  const selectConversation = useCallback(async (id: string) => {
    try {
      setActiveConversation(id);
      const conversation = await chatService.getConversation(id);
      if (conversation) {
        setMessages(conversation.messages);
      }
    } catch (err) {
      console.error('Error loading conversation:', err);
    }
  }, [setActiveConversation, setMessages]);

  const deleteConversation = useCallback(async (id: string) => {
    try {
      await chatService.deleteConversation(id);
      removeConversation(id);
    } catch (err) {
      console.error('Error deleting conversation:', err);
    }
  }, [removeConversation]);

  const startNewChat = useCallback(() => {
    clearMessages();
    setActiveConversation(null);
  }, [clearMessages, setActiveConversation]);

  useEffect(() => {
    loadConversations();
  }, []);

  return {
    messages,
    conversations,
    activeConversationId,
    sending,
    error,
    context,
    sendMessage,
    loadConversations,
    selectConversation,
    deleteConversation,
    setContext,
    updateContext,
    clearContext,
    clearMessages,
    startNewChat,
  };
}
