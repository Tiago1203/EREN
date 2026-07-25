/**
 * Servicio de Dashboard
 * Consume datos del Business Domain (PHASE 1)
 */

import type { DashboardStats, Establecimiento } from '../types/dashboard.types';
import type { KpiResult } from '@/lib/kpis';
import { fetchEquipos, fetchEventos, fetchEstablecimientos } from '@/lib/queries';

export interface Equipo {
  id: string;
  nombre: string;
}

export interface Evento {
  id: string;
  tipo: string;
  fecha: string;
}

export class DashboardService {
  async getStats(
    isAdmin: boolean,
    establishmentId?: string | null
  ): Promise<DashboardStats> {
    try {
      const estId = establishmentId ? parseInt(establishmentId, 10) : null;
      const [eqRes, evRes, estRes] = await Promise.all([
        fetchEquipos(isAdmin, estId),
        fetchEventos(isAdmin, estId),
        fetchEstablecimientos(isAdmin, estId),
      ]);

      const equipos = eqRes.data || [];
      const eventos = evRes.data || [];
      const establecimientos = estRes.data || [];

      return {
        equipos: equipos.length,
        mantenimientos: eventos.length,
        establecimientos: isAdmin ? establecimientos.length : 1,
        incidentes: 0,
        alertas: 0,
      };
    } catch (error) {
      console.error('Error fetching dashboard stats:', error);
      return {
        equipos: 0,
        mantenimientos: 0,
        establecimientos: 0,
        incidentes: 0,
        alertas: 0,
      };
    }
  }

  getKpis(equipos: Equipo[], eventos: Evento[]): KpiResult[] {
    const totalEquipos = equipos.length;
    const totalEventos = eventos.length;
    const preventivos = eventos.filter(e => e.tipo === 'preventivo').length;
    const correctivos = eventos.filter(e => e.tipo === 'correctivo').length;
    const eventosUltimoMes = eventos.filter(e => {
      const fecha = new Date(e.fecha);
      const ahora = new Date();
      const haceUnMes = new Date(ahora.setMonth(ahora.getMonth() - 1));
      return fecha >= haceUnMes;
    }).length;
    const disponibilidad = totalEquipos > 0
      ? ((totalEquipos - correctivos) / totalEquipos * 100).toFixed(1)
      : '100';

    return [
      { label: 'Total Equipos', value: String(totalEquipos), status: 'neutral' },
      { label: 'Eventos Totales', value: String(totalEventos), status: 'neutral' },
      { label: 'Preventivos', value: `${preventivos} eventos`, status: 'ok' },
      { label: 'Correctivos', value: `${correctivos} eventos`, status: 'warning' },
      { label: 'Eventos Último Mes', value: String(eventosUltimoMes), status: 'neutral' },
      { label: 'Tasa Disponibilidad', value: `${disponibilidad}%`, status: 'ok' },
    ];
  }

  async getEstablishmentInfo(establishmentId: string): Promise<Establecimiento | null> {
    try {
      const estId = parseInt(establishmentId, 10);
      const response = await fetchEstablecimientos(true, estId);
      const establishments = response.data || [];
      return establishments.length > 0 ? establishments[0] : null;
    } catch (error) {
      console.error('Error fetching establishment:', error);
      return null;
    }
  }
}

export const dashboardService = new DashboardService();
