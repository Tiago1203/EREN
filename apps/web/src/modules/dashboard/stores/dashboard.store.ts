'use client';

import { create } from 'zustand';
import type { DashboardStats, Establecimiento } from '../types/dashboard.types';
import type { KpiResult } from '@/lib/kpis';

interface DashboardState {
  stats: DashboardStats;
  kpis: KpiResult[];
  establishment: Establecimiento | null;
  loading: boolean;
  error: string | null;

  setStats: (stats: DashboardStats) => void;
  setKpis: (kpis: KpiResult[]) => void;
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
  kpis: [] as KpiResult[],
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
