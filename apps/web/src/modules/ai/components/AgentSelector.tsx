'use client';

import type { Agent } from '../types/ai.types';

interface AgentSelectorProps {
  agents: Agent[];
  selectedAgentId?: string | null;
  onSelect: (agentId: string) => void;
  compact?: boolean;
}

export function AgentSelector({ agents, selectedAgentId, onSelect, compact = false }: AgentSelectorProps) {
  if (compact) {
    return (
      <select
        value={selectedAgentId || ''}
        onChange={(e) => onSelect(e.target.value)}
        className="px-3 py-2 rounded-lg border border-[var(--border)] bg-[var(--background)] text-sm"
      >
        <option value="">Seleccionar agente</option>
        {agents.map((agent) => (
          <option key={agent.id} value={agent.id} disabled={agent.status !== 'online'}>
            {agent.name} {!agent.status.includes('online') && `(${agent.status})`}
          </option>
        ))}
      </select>
    );
  }

  return (
    <div className="grid grid-cols-2 lg:grid-cols-3 gap-3">
      {agents.map((agent) => (
        <AgentCard
          key={agent.id}
          agent={agent}
          selected={selectedAgentId === agent.id}
          onClick={() => agent.status === 'online' && onSelect(agent.id)}
        />
      ))}
    </div>
  );
}

interface AgentCardProps {
  agent: Agent;
  selected: boolean;
  onClick: () => void;
}

function AgentCard({ agent, selected, onClick }: AgentCardProps) {
  const statusColors = {
    online: 'bg-green-500',
    offline: 'bg-gray-400',
    busy: 'bg-yellow-500',
  };

  return (
    <button
      onClick={onClick}
      disabled={agent.status !== 'online'}
      className={`
        p-4 rounded-lg border text-left transition-all
        ${selected
          ? 'border-[var(--primary)] bg-[var(--primary)]/10'
          : 'border-[var(--border)] bg-[var(--card)] hover:border-[var(--primary)]/50'
        }
        ${agent.status !== 'online' ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
      `}
    >
      <div className="flex items-start justify-between mb-2">
        <div className="w-10 h-10 rounded-lg bg-[var(--primary)]/20 flex items-center justify-center">
          <AgentIcon name={agent.icon} />
        </div>
        <span className={`w-2 h-2 rounded-full ${statusColors[agent.status]}`} />
      </div>
      
      <h3 className="font-medium text-sm mb-1">{agent.name}</h3>
      <p className="text-xs text-muted line-clamp-2">{agent.description}</p>
      
      <div className="flex flex-wrap gap-1 mt-2">
        {agent.capabilities.slice(0, 2).map((cap) => (
          <span key={cap} className="px-2 py-0.5 text-xs bg-[var(--background)] rounded">
            {cap}
          </span>
        ))}
      </div>
    </button>
  );
}

function AgentIcon({ name }: { name: string }) {
  const icons: Record<string, JSX.Element> = {
    Wrench: (
      <svg className="w-5 h-5 text-[var(--primary)]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
      </svg>
    ),
    Search: (
      <svg className="w-5 h-5 text-[var(--primary)]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
      </svg>
    ),
    BookOpen: (
      <svg className="w-5 h-5 text-[var(--primary)]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
      </svg>
    ),
    Calendar: (
      <svg className="w-5 h-5 text-[var(--primary)]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
      </svg>
    ),
    SearchCode: (
      <svg className="w-5 h-5 text-[var(--primary)]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
      </svg>
    ),
  };

  return icons[name] || (
    <svg className="w-5 h-5 text-[var(--primary)]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
    </svg>
  );
}

export default AgentSelector;
