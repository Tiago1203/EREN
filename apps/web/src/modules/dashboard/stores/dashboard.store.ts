'use client';

import { create } from 'zustand';
import type { DashboardStats, Kpi, Establecimiento } from '../types/dashboard.types';

interface DashboardState {
  stats: DashboardStats;
  kpis: Kpi[];
  establishment: Establecimiento | null;
  loading: boolean;
  error: string | null;
  
  // Actions
  setStats: (stats: DashboardStats) => void;
  setKpis: (kpis: Kpi[]) => void;
  setEstablishment: (establishment: Establecimiento | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  reset: () => void;
}

const initialState = {
  stats: {
    equipos: 0,
    mantenimientos: 0,
    establecimientos: 0,
    incidentes: 0,
    alertas: 0,
  },
  kpis: [],
  establishment: null,
  loading: true,
  error: null,
};

export const useDashboardStore = create<DashboardState>((set) => ({
  ...initialState,

  setStats: (stats) => set({ stats }),
  setKpis: (kpis) => set({ kpis }),
  setEstablishment: (establishment) => set({ establishment }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
  reset: () => set(initialState),
}));
