'use client';

import { useCallback, useEffect } from 'react';
import { useAnalyticsStore } from '../stores/analytics.store';
import { analyticsService } from '../services/analytics.service';
import type { DateRange } from '../types/analytics.types';

export interface UseAnalyticsReturn {
  // Data
  metrics: ReturnType<typeof useAnalyticsStore>['metrics'];
  charts: ReturnType<typeof useAnalyticsStore>['charts'];
  chartData: ReturnType<typeof useAnalyticsStore>['chartData'];
  dateRange: DateRange;
  
  // State
  loading: boolean;
  error: string | null;
  
  // Actions
  loadMetrics: (dateRange?: DateRange) => Promise<void>;
  loadChartData: (chartId: string, dateRange?: DateRange) => Promise<void>;
  setDateRange: (range: DateRange) => void;
}

export function useAnalytics(): UseAnalyticsReturn {
  const {
    metrics,
    charts,
    chartData,
    dateRange,
    loading,
    error,
    setMetrics,
    setCharts,
    setChartData,
    setDateRange: storeSetDateRange,
    setLoading,
    setError,
  } = useAnalyticsStore();

  const loadMetrics = useCallback(async (range?: DateRange) => {
    try {
      setLoading(true);
      setError(null);
      const data = await analyticsService.getDashboardMetrics(range || dateRange);
      setMetrics(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error loading metrics');
    } finally {
      setLoading(false);
    }
  }, [dateRange, setMetrics, setLoading, setError]);

  const loadChartData = useCallback(async (chartId: string, range?: DateRange) => {
    try {
      const data = await analyticsService.getChartData(chartId, range || dateRange);
      setChartData(chartId, data);
    } catch (err) {
      console.error('Error loading chart data:', err);
    }
  }, [dateRange, setChartData]);

  const setDateRange = useCallback((range: DateRange) => {
    storeSetDateRange(range);
  }, [storeSetDateRange]);

  useEffect(() => {
    loadMetrics();
    
    // Load default charts
    const defaultCharts = ['mantenimientos', 'incidentes', 'disponibilidad', 'costos'];
    defaultCharts.forEach((chartId) => loadChartData(chartId));
  }, []);

  return {
    metrics,
    charts,
    chartData,
    dateRange,
    loading,
    error,
    loadMetrics,
    loadChartData,
    setDateRange,
  };
}
