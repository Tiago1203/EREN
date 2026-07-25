/**
 * Tests para EPIC 1: Dashboard & Navigation
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import type { DashboardStats, Kpi, StatCard } from '@/modules/dashboard/types/dashboard.types';

// Mock modules
vi.mock('@/lib/queries', () => ({
  fetchEquipos: vi.fn().mockResolvedValue({ data: [] }),
  fetchEventos: vi.fn().mockResolvedValue({ data: [] }),
  fetchEstablecimientos: vi.fn().mockResolvedValue({ data: [] }),
}));

vi.mock('@/hooks/useAuth', () => ({
  useAuth: () => ({
    profile: { id: '1', nombre: 'Test User', email: 'test@test.com' },
    isAdmin: true,
    establecimientoId: undefined,
  }),
}));

describe('Dashboard Types', () => {
  it('should define DashboardStats correctly', () => {
    const stats: DashboardStats = {
      equipos: 10,
      mantenimientos: 5,
      establecimientos: 3,
      incidentes: 2,
      alertas: 1,
    };

    expect(stats.equipos).toBe(10);
    expect(stats.mantenimientos).toBe(5);
  });

  it('should define Kpi correctly', () => {
    const kpi: Kpi = {
      id: 'test-kpi',
      label: 'Test KPI',
      value: 100,
      unit: '%',
      trend: 'up',
      trendValue: 5,
      status: 'success',
    };

    expect(kpi.id).toBe('test-kpi');
    expect(kpi.value).toBe(100);
    expect(kpi.status).toBe('success');
  });

  it('should define StatCard correctly', () => {
    const card: StatCard = {
      id: 'test-card',
      title: 'Test Card',
      value: 42,
      subtitle: 'Test subtitle',
      icon: 'server',
      color: 'bg-blue-500',
      href: '/test',
      show: true,
    };

    expect(card.title).toBe('Test Card');
    expect(card.href).toBe('/test');
    expect(card.show).toBe(true);
  });
});

describe('DashboardService', () => {
  it('should calculate KPIs correctly', async () => {
    const { dashboardService } = await import('@/modules/dashboard/services/dashboard.service');
    
    const equipos = [
      { id: '1', nombre: 'Equipo 1' },
      { id: '2', nombre: 'Equipo 2' },
    ] as any[];
    
    const eventos = [
      { id: '1', tipo: 'preventivo', fecha: new Date().toISOString() },
      { id: '2', tipo: 'correctivo', fecha: new Date().toISOString() },
      { id: '3', tipo: 'preventivo', fecha: new Date().toISOString() },
    ] as any[];

    const kpis = dashboardService.getKpis(equipos, eventos);

    expect(kpis.find(k => k.id === 'total-equipos')?.value).toBe(2);
    expect(kpis.find(k => k.id === 'preventivos')?.value).toBe(2);
    expect(kpis.find(k => k.id === 'correctivos')?.value).toBe(1);
  });

  it('should handle empty data', async () => {
    const { dashboardService } = await import('@/modules/dashboard/services/dashboard.service');
    
    const kpis = dashboardService.getKpis([], []);

    expect(kpis.find(k => k.id === 'total-equipos')?.value).toBe(0);
    expect(kpis.find(k => k.id === 'tasa-disponibilidad')?.value).toBe('100');
  });
});

describe('DashboardStore', () => {
  it('should initialize with default values', async () => {
    const { useDashboardStore } = await import('@/modules/dashboard/stores/dashboard.store');
    
    const store = useDashboardStore.getState();
    
    expect(store.stats.equipos).toBe(0);
    expect(store.stats.mantenimientos).toBe(0);
    expect(store.loading).toBe(true);
    expect(store.error).toBeNull();
  });

  it('should update stats', async () => {
    const { useDashboardStore } = await import('@/modules/dashboard/stores/dashboard.store');
    
    act(() => {
      useDashboardStore.getState().setStats({
        equipos: 10,
        mantenimientos: 5,
        establecimientos: 2,
      });
    });

    const store = useDashboardStore.getState();
    expect(store.stats.equipos).toBe(10);
    expect(store.stats.mantenimientos).toBe(5);
  });

  it('should update loading state', async () => {
    const { useDashboardStore } = await import('@/modules/dashboard/stores/dashboard.store');
    
    act(() => {
      useDashboardStore.getState().setLoading(true);
    });
    expect(useDashboardStore.getState().loading).toBe(true);
    
    act(() => {
      useDashboardStore.getState().setLoading(false);
    });
    expect(useDashboardStore.getState().loading).toBe(false);
  });

  it('should reset state', async () => {
    const { useDashboardStore } = await import('@/modules/dashboard/stores/dashboard.store');
    
    act(() => {
      useDashboardStore.getState().setStats({ equipos: 10, mantenimientos: 5, establecimientos: 2 });
      useDashboardStore.getState().setError('Test error');
    });
    
    act(() => {
      useDashboardStore.getState().reset();
    });

    const store = useDashboardStore.getState();
    expect(store.stats.equipos).toBe(0);
    expect(store.error).toBeNull();
  });
});

describe('ModuleRegistry Integration', () => {
  it('should have dashboard module registered', async () => {
    const { moduleRegistry } = await import('@/modules/shared/lib/module-registry');
    
    const dashboardModule = moduleRegistry.getModule('dashboard');
    
    expect(dashboardModule).toBeDefined();
    expect(dashboardModule?.name).toBe('Dashboard');
    expect(dashboardModule?.path).toBe('/dashboard');
    expect(dashboardModule?.enabled).toBe(true);
  });

  it('should return enabled modules sorted by order', async () => {
    const { moduleRegistry } = await import('@/modules/shared/lib/module-registry');
    
    const modules = moduleRegistry.getEnabledModules();
    
    expect(modules.length).toBeGreaterThan(0);
    expect(modules[0].id).toBe('dashboard'); // Order 1
  });
});
