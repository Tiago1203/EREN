/**
 * Servicio de Dashboard
 * Consume datos del Business Domain (PHASE 1)
 */

import type { DashboardStats, Kpi, Establecimiento } from '../types/dashboard.types';
import { fetchEquipos, fetchEventos, fetchEstablecimientos } from '@/lib/queries';

export interface Equipo {
  id: string;
  nombre: string;
  // ... otros campos
}

export interface Evento {
  id: string;
  tipo: string;
  fecha: string;
  // ... otros campos
}

export class DashboardService {
  /**
   * Obtiene estadísticas del dashboard
   */
  async getStats(
    isAdmin: boolean,
    establishmentId?: string
  ): Promise<DashboardStats> {
    try {
      const [eqRes, evRes, estRes] = await Promise.all([
        fetchEquipos(isAdmin, establishmentId),
        fetchEventos(isAdmin, establishmentId),
        fetchEstablecimientos(isAdmin, establishmentId),
      ]);

      const equipos = eqRes.data || [];
      const eventos = evRes.data || [];
      const establecimientos = estRes.data || [];

      return {
        equipos: equipos.length,
        mantenimientos: eventos.length,
        establecimientos: isAdmin ? establecimientos.length : 1,
        incidentes: 0, // TODO: Integrar con PHASE 1 Incident Context
        alertas: 0, // TODO: Integrar con PHASE 1 Alert
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

  /**
   * Calcula KPIs basado en equipos y eventos
   */
  getKpis(equipos: Equipo[], eventos: Evento[]): Kpi[] {
    const totalEquipos = equipos.length;
    const totalEventos = eventos.length;
    
    // Cálculo de mantenimientos preventivos vs correctivos
    const preventivos = eventos.filter(e => e.tipo === 'preventivo').length;
    const correctivos = eventos.filter(e => e.tipo === 'correctivo').length;
    
    // Tasa de disponibilidad (ejemplo)
    const eventosUltimoMes = eventos.filter(e => {
      const fecha = new Date(e.fecha);
      const ahora = new Date();
      const haceUnMes = new Date(ahora.setMonth(ahora.getMonth() - 1));
      return fecha >= haceUnMes;
    }).length;

    return [
      {
        id: 'total-equipos',
        label: 'Total Equipos',
        value: totalEquipos,
        status: 'info',
      },
      {
        id: 'total-eventos',
        label: 'Eventos Totales',
        value: totalEventos,
        status: 'info',
      },
      {
        id: 'preventivos',
        label: 'Preventivos',
        value: preventivos,
        unit: 'eventos',
        status: 'success',
      },
      {
        id: 'correctivos',
        label: 'Correctivos',
        value: correctivos,
        unit: 'eventos',
        status: 'warning',
      },
      {
        id: 'eventos-mes',
        label: 'Eventos Último Mes',
        value: eventosUltimoMes,
        status: 'info',
      },
      {
        id: 'tasa-disponibilidad',
        label: 'Tasa Disponibilidad',
        value: totalEquipos > 0 
          ? ((totalEquipos - correctivos) / totalEquipos * 100).toFixed(1) 
          : '100',
        unit: '%',
        status: 'success',
      },
    ];
  }

  /**
   * Obtiene información del establecimiento
   */
  async getEstablishmentInfo(
    establishmentId: string
  ): Promise<Establecimiento | null> {
    try {
      const response = await fetchEstablecimientos(true, establishmentId);
      const establishments = response.data || [];
      return establishments.length > 0 ? establishments[0] : null;
    } catch (error) {
      console.error('Error fetching establishment:', error);
      return null;
    }
  }
}

export const dashboardService = new DashboardService();
