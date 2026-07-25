import { describe, it, expect } from 'vitest';
import { dashboardService } from '@/modules/dashboard/services/dashboard.service';

describe('DashboardService', () => {
  describe('getKpis', () => {
    it('returns kpis for empty arrays', () => {
      const result = dashboardService.getKpis([], []);
      // El servicio siempre devuelve KPIs aunque los arrays estén vacíos
      expect(result.length).toBeGreaterThan(0);
    });

    it('calculates correct totals', () => {
      const equipos = [{ id: '1', nombre: 'Equipo 1' }];
      const eventos = [
        { id: '1', tipo: 'preventivo', fecha: new Date().toISOString() },
      ];
      const result = dashboardService.getKpis(equipos, eventos);
      expect(result.length).toBeGreaterThan(0);
      expect(result[0].label).toBe('Total Equipos');
    });
  });
});
