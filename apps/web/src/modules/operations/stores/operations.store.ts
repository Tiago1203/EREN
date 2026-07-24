'use client';

import { create } from 'zustand';
import type {
  WorkOrder,
  Incident,
  Alert,
  DeviceStatus,
  OperationsStats,
  OperationsFilters,
  OperationsPageState,
} from '../types/operations.types';

interface OperationsState {
  // Data
  workOrders: WorkOrder[];
  incidents: Incident[];
  alerts: Alert[];
  deviceStatuses: DeviceStatus[];
  stats: OperationsStats;
  
  // State
  loading: boolean;
  error: string | null;
  filters: OperationsFilters;
  pageState: OperationsPageState;
  
  // Actions - Data
  setWorkOrders: (workOrders: WorkOrder[]) => void;
  setIncidents: (incidents: Incident[]) => void;
  setAlerts: (alerts: Alert[]) => void;
  setDeviceStatuses: (statuses: DeviceStatus[]) => void;
  setStats: (stats: OperationsStats) => void;
  
  // Actions - State
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  setFilters: (filters: Partial<OperationsFilters>) => void;
  setPageState: (state: Partial<OperationsPageState>) => void;
  
  // Actions - CRUD
  updateWorkOrder: (id: string, data: Partial<WorkOrder>) => void;
  updateIncident: (id: string, data: Partial<Incident>) => void;
  acknowledgeAlert: (id: string) => void;
  dismissAlert: (id: string) => void;
  
  // Actions - Reset
  reset: () => void;
}

const initialStats: OperationsStats = {
  totalWorkOrders: 0,
  pendingWorkOrders: 0,
  inProgressWorkOrders: 0,
  completedWorkOrders: 0,
  totalIncidents: 0,
  openIncidents: 0,
  criticalIncidents: 0,
  totalAlerts: 0,
  criticalAlerts: 0,
  devicesOnline: 0,
  devicesOffline: 0,
  devicesWarning: 0,
};

const initialFilters: OperationsFilters = {
  workOrders: {},
  incidents: {},
  alerts: {},
  timeline: {},
};

const initialPageState: OperationsPageState = {
  activeTab: 'overview',
};

export const useOperationsStore = create<OperationsState>((set) => ({
  // Initial Data
  workOrders: [],
  incidents: [],
  alerts: [],
  deviceStatuses: [],
  stats: initialStats,
  
  // Initial State
  loading: false,
  error: null,
  filters: initialFilters,
  pageState: initialPageState,
  
  // Data Actions
  setWorkOrders: (workOrders) => set({ workOrders }),
  setIncidents: (incidents) => set({ incidents }),
  setAlerts: (alerts) => set({ alerts }),
  setDeviceStatuses: (deviceStatuses) => set({ deviceStatuses }),
  setStats: (stats) => set({ stats }),
  
  // State Actions
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
  setFilters: (filters) => set((state) => ({
    filters: { ...state.filters, ...filters }
  })),
  setPageState: (pageState) => set((state) => ({
    pageState: { ...state.pageState, ...pageState }
  })),
  
  // CRUD Actions
  updateWorkOrder: (id, data) => set((state) => ({
    workOrders: state.workOrders.map((wo) =>
      wo.id === id ? { ...wo, ...data } : wo
    ),
  })),
  
  updateIncident: (id, data) => set((state) => ({
    incidents: state.incidents.map((inc) =>
      inc.id === id ? { ...inc, ...data } : inc
    ),
  })),
  
  acknowledgeAlert: (id) => set((state) => ({
    alerts: state.alerts.map((alert) =>
      alert.id === id
        ? { ...alert, acknowledged: true, acknowledgedAt: new Date().toISOString() }
        : alert
    ),
  })),
  
  dismissAlert: (id) => set((state) => ({
    alerts: state.alerts.filter((alert) => alert.id !== id),
  })),
  
  // Reset
  reset: () => set({
    workOrders: [],
    incidents: [],
    alerts: [],
    deviceStatuses: [],
    stats: initialStats,
    loading: false,
    error: null,
    filters: initialFilters,
    pageState: initialPageState,
  }),
}));
