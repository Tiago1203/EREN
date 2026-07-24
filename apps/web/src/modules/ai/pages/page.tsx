'use client';

import { useState, useRef, useEffect } from 'react';
import { useChat } from '../hooks/useChat';
import { useAgentsStore } from '../stores/agents.store';
import { ChatMessage } from '../components/ChatMessage';
import { ChatInput } from '../components/ChatInput';
import { AgentSelector } from '../components/AgentSelector';
import type { Agent } from '../types/ai.types';

export default function AIPage() {
  const {
    messages,
    conversations,
    sending,
    error,
    sendMessage,
    loadConversations,
    selectConversation,
    startNewChat,
  } = useChat();

  const { agents, selectedAgentId, setSelectedAgent } = useAgentsStore();
  const [showAgents, setShowAgents] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const selectedAgent = agents.find((a) => a.id === selectedAgentId);

  return (
    <div className="flex h-[calc(100vh-4rem)]">
      {/* Sidebar - Conversations */}
      <div className={`w-80 border-r border-[var(--border)] bg-[var(--card)] ${showHistory ? 'block' : 'hidden md:block'}`}>
        <div className="p-4 border-b border-[var(--border)]">
          <button onClick={startNewChat} className="w-full btn-primary">
            <svg className="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            Nuevo Chat
          </button>
        </div>

        <div className="overflow-y-auto h-[calc(100%-4rem)] p-2">
          <p className="text-xs text-muted px-3 py-2">Conversaciones recientes</p>
          {conversations.map((conv) => (
            <button
              key={conv.id}
              onClick={() => selectConversation(conv.id)}
              className="w-full text-left p-3 rounded-lg hover:bg-[var(--background)] transition-colors"
            >
              <p className="font-medium text-sm truncate">{conv.title}</p>
              <p className="text-xs text-muted truncate">{conv.lastMessage || 'Sin mensajes'}</p>
              <p className="text-xs text-muted mt-1">
                {new Date(conv.lastMessageAt).toLocaleDateString()}
              </p>
            </button>
          ))}
          {conversations.length === 0 && (
            <p className="text-sm text-muted text-center py-8">No hay conversaciones</p>
          )}
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="p-4 border-b border-[var(--border)] flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={() => setShowHistory(!showHistory)}
              className="md:hidden btn-secondary"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
            
            <div>
              <h1 className="text-xl font-bold">Centro de IA</h1>
              {selectedAgent && (
                <p className="text-sm text-muted">
                  Usando: {selectedAgent.name}
                </p>
              )}
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowAgents(!showAgents)}
              className="btn-secondary"
            >
              <svg className="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
              Agentes
            </button>
          </div>
        </div>

        {/* Agent Selector */}
        {showAgents && (
          <div className="p-4 border-b border-[var(--border)] bg-[var(--card)]">
            <h2 className="text-lg font-semibold mb-4">Seleccionar Agente</h2>
            <AgentSelector
              agents={agents}
              selectedAgentId={selectedAgentId}
              onSelect={(id) => {
                setSelectedAgent(id);
                setShowAgents(false);
              }}
            />
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="mx-4 mt-4 p-4 bg-red-100 border border-red-300 rounded-lg text-red-700">
            {error}
          </div>
        )}

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <div className="w-20 h-20 rounded-full bg-[var(--primary)]/10 flex items-center justify-center mb-4">
                <svg className="w-10 h-10 text-[var(--primary)]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                </svg>
              </div>
              <h2 className="text-xl font-semibold mb-2">Bienvenido al Centro de IA</h2>
              <p className="text-muted max-w-md">
                Selecciona un agente especializado y hazme cualquier pregunta sobre equipos biomédicos,
                mantenimientos, protocolos o cualquier otra consulta del sistema.
              </p>
              
              {/* Quick suggestions */}
              <div className="mt-6 flex flex-wrap gap-2 justify-center">
                {['Diagnóstico de equipo', 'Protocolos de mantenimiento', 'Búsqueda de artículos'].map((suggestion) => (
                  <button
                    key={suggestion}
                    onClick={() => sendMessage(suggestion)}
                    className="px-4 py-2 rounded-full border border-[var(--border)] text-sm hover:bg-[var(--background)] transition-colors"
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <>
              {messages.map((message) => (
                <ChatMessage key={message.id} message={message} />
              ))}
              <div ref={messagesEndRef} />
            </>
          )}

          {/* Loading indicator */}
          {sending && (
            <div className="flex justify-start mb-4">
              <div className="bg-[var(--card)] border border-[var(--border)] rounded-lg px-4 py-3">
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 border-2 border-[var(--primary)] border-t-transparent rounded-full animate-spin" />
                  <span className="text-sm text-muted">Pensando...</span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Input */}
        <ChatInput
          onSend={sendMessage}
          disabled={sending}
          placeholder="Escribe tu pregunta sobre equipos biomédicos..."
        />
      </div>
    </div>
  );
}
