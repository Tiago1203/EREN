'use client';

import { useEffect, useCallback } from 'react';
import { useOperationsStore } from '../stores/operations.store';
import { operationsService } from '../services/operations.service';
import type {
  WorkOrderFilters,
  IncidentFilters,
  AlertFilters,
  TimelineFilters,
} from '../types/operations.types';

export interface UseOperationsReturn {
  // Data
  workOrders: ReturnType<typeof useOperationsStore>['workOrders'];
  incidents: ReturnType<typeof useOperationsStore>['incidents'];
  alerts: ReturnType<typeof useOperationsStore>['alerts'];
  deviceStatuses: ReturnType<typeof useOperationsStore>['deviceStatuses'];
  stats: ReturnType<typeof useOperationsStore>['stats'];
  
  // State
  loading: boolean;
  error: string | null;
  activeTab: ReturnType<typeof useOperationsStore>['pageState']['activeTab'];
  
  // Actions
  loadData: () => Promise<void>;
  loadWorkOrders: (filters?: WorkOrderFilters) => Promise<void>;
  loadIncidents: (filters?: IncidentFilters) => Promise<void>;
  loadAlerts: (filters?: AlertFilters) => Promise<void>;
  loadDeviceStatuses: () => Promise<void>;
  loadStats: () => Promise<void>;
  loadTimeline: (filters?: TimelineFilters) => Promise<void>;
  
  // Tab
  setActiveTab: (tab: 'overview' | 'workorders' | 'incidents' | 'alerts' | 'timeline') => void;
  
  // Alert Actions
  acknowledgeAlert: (id: string) => void;
  dismissAlert: (id: string) => void;
}

export function useOperations(): UseOperationsReturn {
  const {
    workOrders,
    incidents,
    alerts,
    deviceStatuses,
    stats,
    loading,
    error,
    pageState,
    setWorkOrders,
    setIncidents,
    setAlerts,
    setDeviceStatuses,
    setStats,
    setLoading,
    setError,
    setPageState,
    acknowledgeAlert: storeAcknowledgeAlert,
    dismissAlert: storeDismissAlert,
  } = useOperationsStore();

  const loadData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const [wo, inc, al, dev, st] = await Promise.all([
        operationsService.getWorkOrders(),
        operationsService.getIncidents(),
        operationsService.getAlerts(),
        operationsService.getDeviceStatuses(),
        operationsService.getStats(),
      ]);

      setWorkOrders(wo);
      setIncidents(inc);
      setAlerts(al);
      setDeviceStatuses(dev);
      setStats(st);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error loading operations data');
    } finally {
      setLoading(false);
    }
  }, [setWorkOrders, setIncidents, setAlerts, setDeviceStatuses, setStats, setLoading, setError]);

  const loadWorkOrders = useCallback(async (filters?: WorkOrderFilters) => {
    try {
      const data = await operationsService.getWorkOrders(filters);
      setWorkOrders(data);
    } catch (err) {
      console.error('Error loading work orders:', err);
    }
  }, [setWorkOrders]);

  const loadIncidents = useCallback(async (filters?: IncidentFilters) => {
    try {
      const data = await operationsService.getIncidents(filters);
      setIncidents(data);
    } catch (err) {
      console.error('Error loading incidents:', err);
    }
  }, [setIncidents]);

  const loadAlerts = useCallback(async (filters?: AlertFilters) => {
    try {
      const data = await operationsService.getAlerts(filters);
      setAlerts(data);
    } catch (err) {
      console.error('Error loading alerts:', err);
    }
  }, [setAlerts]);

  const loadDeviceStatuses = useCallback(async () => {
    try {
      const data = await operationsService.getDeviceStatuses();
      setDeviceStatuses(data);
    } catch (err) {
      console.error('Error loading device statuses:', err);
    }
  }, [setDeviceStatuses]);

  const loadStats = useCallback(async () => {
    try {
      const data = await operationsService.getStats();
      setStats(data);
    } catch (err) {
      console.error('Error loading stats:', err);
    }
  }, [setStats]);

  const loadTimeline = useCallback(async (_filters?: TimelineFilters) => {
    // Timeline se construye desde los datos existentes
    // En una implementación real, haríamos una llamada específica
    await loadData();
  }, [loadData]);

  const setActiveTab = useCallback((tab: 'overview' | 'workorders' | 'incidents' | 'alerts' | 'timeline') => {
    setPageState({ activeTab: tab });
  }, [setPageState]);

  const acknowledgeAlert = useCallback((id: string) => {
    storeAcknowledgeAlert(id);
  }, [storeAcknowledgeAlert]);

  const dismissAlert = useCallback((id: string) => {
    storeDismissAlert(id);
  }, [storeDismissAlert]);

  useEffect(() => {
    loadData();
  }, []);

  return {
    workOrders,
    incidents,
    alerts,
    deviceStatuses,
    stats,
    loading,
    error,
    activeTab: pageState.activeTab,
    loadData,
    loadWorkOrders,
    loadIncidents,
    loadAlerts,
    loadDeviceStatuses,
    loadStats,
    loadTimeline,
    setActiveTab,
    acknowledgeAlert,
    dismissAlert,
  };
}
