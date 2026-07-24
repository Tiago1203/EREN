'use client';

import { create } from 'zustand';
import type {
  ChatMessage,
  Conversation,
  ConversationSummary,
  ClinicalContext,
  ChatState,
} from '../types/ai.types';

interface ChatStore extends ChatState {
  // Actions - Messages
  addMessage: (message: ChatMessage) => void;
  setMessages: (messages: ChatMessage[]) => void;
  clearMessages: () => void;
  
  // Actions - Conversations
  setConversations: (conversations: ConversationSummary[]) => void;
  addConversation: (conversation: ConversationSummary) => void;
  removeConversation: (id: string) => void;
  setActiveConversation: (id: string | null) => void;
  
  // Actions - Context
  setContext: (context: ClinicalContext) => void;
  updateContext: (context: Partial<ClinicalContext>) => void;
  clearContext: () => void;
  
  // Actions - State
  setSending: (sending: boolean) => void;
  setError: (error: string | null) => void;
  
  // Actions - Reset
  reset: () => void;
}

const initialContext: ClinicalContext = {};

const initialState: ChatState = {
  messages: [],
  conversations: [],
  activeConversationId: null,
  sending: false,
  error: null,
  context: initialContext,
};

export const useChatStore = create<ChatStore>((set) => ({
  ...initialState,

  // Messages
  addMessage: (message) => set((state) => ({
    messages: [...state.messages, message],
  })),

  setMessages: (messages) => set({ messages }),

  clearMessages: () => set({ messages: [] }),

  // Conversations
  setConversations: (conversations) => set({ conversations }),

  addConversation: (conversation) => set((state) => ({
    conversations: [conversation, ...state.conversations],
  })),

  removeConversation: (id) => set((state) => ({
    conversations: state.conversations.filter((c) => c.id !== id),
    activeConversationId: state.activeConversationId === id ? null : state.activeConversationId,
  })),

  setActiveConversation: (id) => set({
    activeConversationId: id,
    messages: [],
  }),

  // Context
  setContext: (context) => set({ context }),

  updateContext: (update) => set((state) => ({
    context: { ...state.context, ...update },
  })),

  clearContext: () => set({ context: initialContext }),

  // State
  setSending: (sending) => set({ sending }),
  setError: (error) => set({ error }),

  // Reset
  reset: () => set(initialState),
}));
