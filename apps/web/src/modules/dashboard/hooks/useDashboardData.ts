'use client';

import { useEffect } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { useDashboardStore } from '../stores/dashboard.store';
import { dashboardService } from '../services/dashboard.service';
import { fetchEquipos, fetchEventos, fetchEstablecimientos } from '@/lib/queries';
import type { DashboardStats, Kpi } from '../types/dashboard.types';

export interface UseDashboardDataReturn {
  stats: DashboardStats;
  kpis: Kpi[];
  establishment: ReturnType<typeof useDashboardStore>['establishment'];
  loading: boolean;
  error: string | null;
  isAdmin: boolean;
  profile: ReturnType<typeof useAuth>['profile'];
  refreshData: () => Promise<void>;
}

export function useDashboardData(): UseDashboardDataReturn {
  const { profile, isAdmin, establecimientoId } = useAuth();
  const {
    stats,
    kpis,
    establishment,
    loading,
    error,
    setStats,
    setKpis,
    setEstablishment,
    setLoading,
    setError,
  } = useDashboardStore();

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [eqRes, evRes, estRes] = await Promise.all([
        fetchEquipos(isAdmin, establecimientoId),
        fetchEventos(isAdmin, establecimientoId),
        fetchEstablecimientos(isAdmin, establecimientoId),
      ]);

      const equipos = eqRes.data || [];
      const eventos = evRes.data || [];
      const establecimientos = estRes.data || [];

      // Establecimiento info
      if (!isAdmin && establecimientoId && establecimientos.length > 0) {
        setEstablishment(establecimientos[0]);
      }

      // Stats
      setStats({
        equipos: equipos.length,
        mantenimientos: eventos.length,
        establecimientos: isAdmin ? establecimientos.length : 1,
      });

      // KPIs
      const calculatedKpis = dashboardService.getKpis(equipos, eventos);
      setKpis(calculatedKpis);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error loading dashboard');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (profile) {
      loadData();
    }
  }, [profile, isAdmin, establecimientoId]);

  return {
    stats,
    kpis,
    establishment,
    loading,
    error,
    isAdmin,
    profile,
    refreshData: loadData,
  };
}
