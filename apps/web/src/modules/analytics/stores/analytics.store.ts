'use client';

import { create } from 'zustand';
import type { Metric, ChartConfig, ChartData, DateRange, AnalyticsState } from '../types/analytics.types';

interface AnalyticsStore extends AnalyticsState {
  // Actions - Metrics
  setMetrics: (metrics: Metric[]) => void;
  addMetric: (metric: Metric) => void;
  updateMetric: (id: string, metric: Partial<Metric>) => void;
  
  // Actions - Charts
  setCharts: (charts: ChartConfig[]) => void;
  setChartData: (chartId: string, data: ChartData) => void;
  
  // Actions - Date Range
  setDateRange: (range: DateRange) => void;
  
  // Actions - State
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  
  // Actions - Reset
  reset: () => void;
}

const initialDateRange: DateRange = {
  start: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000),
  end: new Date(),
};

const initialState: AnalyticsState = {
  metrics: [],
  charts: [],
  chartData: {},
  dateRange: initialDateRange,
  loading: false,
  error: null,
};

export const useAnalyticsStore = create<AnalyticsStore>((set) => ({
  ...initialState,

  // Metrics
  setMetrics: (metrics) => set({ metrics }),
  addMetric: (metric) => set((state) => ({ metrics: [...state.metrics, metric] })),
  updateMetric: (id, update) => set((state) => ({
    metrics: state.metrics.map((m) => (m.id === id ? { ...m, ...update } : m)),
  })),

  // Charts
  setCharts: (charts) => set({ charts }),
  setChartData: (chartId, data) => set((state) => ({
    chartData: { ...state.chartData, [chartId]: data },
  })),

  // Date Range
  setDateRange: (dateRange) => set({ dateRange }),

  // State
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),

  // Reset
  reset: () => set(initialState),
}));
