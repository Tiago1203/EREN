'use client';

import { create } from 'zustand';
import type { Agent, AgentsState } from '../types/ai.types';

interface AgentsStore extends AgentsState {
  // Actions
  setAgents: (agents: Agent[]) => void;
  setSelectedAgent: (id: string | null) => void;
  updateAgentStatus: (id: string, status: Agent['status']) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  reset: () => void;
}

const initialState: AgentsState = {
  agents: [],
  selectedAgentId: null,
  loading: false,
  error: null,
};

// Predefined agents from PHASE 5
const defaultAgents: Agent[] = [
  {
    id: 'biomedical',
    name: 'Agente Biomédico',
    description: 'Especialista en mantenimiento y reparación de equipos biomédicos',
    icon: 'Wrench',
    capabilities: ['Diagnóstico de equipos', 'Mantenimiento preventivo', 'Reparación'],
    specialties: ['Equipos biomédicos', 'Instrumentación clínica'],
    status: 'online',
    model: 'gpt-4',
  },
  {
    id: 'diagnostic',
    name: 'Agente de Diagnóstico',
    description: 'Análisis de problemas técnicos y diagnóstico de fallas',
    icon: 'Search',
    capabilities: ['Análisis de síntomas', 'Diagnóstico diferencial', 'Resolución de problemas'],
    specialties: ['Diagnóstico clínico', 'Análisis de causa raíz'],
    status: 'online',
    model: 'gpt-4',
  },
  {
    id: 'knowledge',
    name: 'Agente de Conocimiento',
    description: 'Gestión y búsqueda de conocimiento institucional',
    icon: 'BookOpen',
    capabilities: ['Búsqueda de artículos', 'Consulta de protocolos', 'Gestión de conocimiento'],
    specialties: ['Base de conocimiento', 'Procedimientos', 'Guías clínicas'],
    status: 'online',
    model: 'gpt-4',
  },
  {
    id: 'research',
    name: 'Agente de Investigación',
    description: 'Búsqueda de evidencia científica y literatura médica',
    icon: 'SearchCode',
    capabilities: ['Búsqueda bibliográfica', 'Análisis de estudios', 'Síntesis de evidencia'],
    specialties: ['Literatura médica', 'EBM', 'Investigación clínica'],
    status: 'online',
    model: 'gpt-4',
  },
  {
    id: 'planning',
    name: 'Agente de Planificación',
    description: 'Planificación de mantenimientos y optimización de recursos',
    icon: 'Calendar',
    capabilities: ['Programación de mantenimiento', 'Optimización de rutas', 'Asignación de recursos'],
    specialties: ['Gestión de mantenimientos', 'Planificación de capacidad'],
    status: 'online',
    model: 'gpt-4',
  },
];

export const useAgentsStore = create<AgentsStore>((set) => ({
  ...initialState,
  agents: defaultAgents,

  setAgents: (agents) => set({ agents }),

  setSelectedAgent: (id) => set({ selectedAgentId: id }),

  updateAgentStatus: (id, status) => set((state) => ({
    agents: state.agents.map((agent) =>
      agent.id === id ? { ...agent, status } : agent
    ),
  })),

  setLoading: (loading) => set({ loading }),

  setError: (error) => set({ error }),

  reset: () => set({ ...initialState, agents: defaultAgents }),
}));
