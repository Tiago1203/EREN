/**
 * Analytics Service
 * Consumes PHASE 1 and PHASE 3
 */

import type { Metric, ChartData, ChartConfig, DateRange, KPI, Trend } from '../types/analytics.types';

export class AnalyticsService {
  /**
   * Obtiene métricas del dashboard
   */
  async getDashboardMetrics(dateRange: DateRange): Promise<Metric[]> {
    // TODO: Integrar con PHASE 1
    return this.getMockMetrics();
  }

  /**
   * Obtiene datos para un gráfico
   */
  async getChartData(chartId: string, dateRange: DateRange): Promise<ChartData> {
    // TODO: Integrar con PHASE 1
    return this.getMockChartData(chartId);
  }

  /**
   * Obtiene KPIs
   */
  async getKPIs(dateRange: DateRange): Promise<KPI[]> {
    // TODO: Integrar con PHASE 3
    return this.getMockKPIs();
  }

  /**
   * Obtiene tendencias
   */
  async getTrends(dateRange: DateRange): Promise<Trend[]> {
    // TODO: Integrar con PHASE 3
    return this.getMockTrends();
  }

  // ============== MOCK DATA ==============

  private getMockMetrics(): Metric[] {
    return [
      {
        id: 'total-equipos',
        label: 'Total Equipos',
        value: 156,
        previousValue: 148,
        format: 'number',
        trend: 'up',
        trendValue: 5.4,
        status: 'success',
      },
      {
        id: 'disponibilidad',
        label: 'Tasa Disponibilidad',
        value: 94.5,
        unit: '%',
        previousValue: 92.1,
        format: 'percentage',
        trend: 'up',
        trendValue: 2.4,
        status: 'success',
      },
      {
        id: 'mtbf',
        label: 'MTBF',
        value: 245,
        unit: 'horas',
        previousValue: 230,
        format: 'time',
        trend: 'up',
        trendValue: 6.5,
        status: 'success',
      },
      {
        id: 'mttf',
        label: 'MTTR',
        value: 4.2,
        unit: 'horas',
        previousValue: 5.1,
        format: 'time',
        trend: 'down',
        trendValue: -17.6,
        status: 'success',
      },
      {
        id: 'incidentes-abiertos',
        label: 'Incidentes Abiertos',
        value: 12,
        previousValue: 18,
        format: 'number',
        trend: 'down',
        trendValue: -33.3,
        status: 'warning',
      },
      {
        id: 'mantenimientos-pendientes',
        label: 'Pendientes',
        value: 28,
        previousValue: 25,
        format: 'number',
        trend: 'up',
        trendValue: 12,
        status: 'info',
      },
      {
        id: 'cumplimiento',
        label: 'Cumplimiento PM',
        value: 87.5,
        unit: '%',
        previousValue: 85.2,
        format: 'percentage',
        trend: 'up',
        trendValue: 2.3,
        status: 'success',
      },
      {
        id: 'costo-promedio',
        label: 'Costo Promedio',
        value: 1250,
        unit: 'USD',
        previousValue: 1380,
        format: 'currency',
        trend: 'down',
        trendValue: -9.4,
        status: 'success',
      },
    ];
  }

  private getMockChartData(chartId: string): ChartData {
    const labels = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun'];
    
    const mockData: Record<string, ChartData> = {
      'mantenimientos': {
        labels,
        datasets: [
          { name: 'Preventivos', data: [45, 52, 48, 55, 50, 58], color: '#10b981' },
          { name: 'Correctivos', data: [12, 15, 10, 8, 14, 11], color: '#f59e0b' },
          { name: 'Predictivos', data: [5, 8, 12, 15, 18, 20], color: '#3b82f6' },
        ],
      },
      'incidentes': {
        labels,
        datasets: [
          { name: 'Abiertos', data: [18, 22, 15, 12, 10, 8], color: '#ef4444' },
          { name: 'Resueltos', data: [15, 20, 18, 14, 12, 15], color: '#22c55e' },
        ],
      },
      'disponibilidad': {
        labels,
        datasets: [
          { name: 'Disponibilidad %', data: [92, 93, 94, 93.5, 94.5, 95], color: '#10b981' },
        ],
      },
      'costos': {
        labels,
        datasets: [
          { name: 'Mantenimiento', data: [15000, 14500, 16000, 15500, 14800, 14200], color: '#6366f1' },
          { name: 'Repuestos', data: [5000, 4500, 5200, 4800, 5100, 4900], color: '#f59e0b' },
        ],
      },
    };

    return mockData[chartId] || {
      labels,
      datasets: [{ name: 'Valor', data: [30, 45, 52, 48, 55, 60], color: '#3b82f6' }],
    };
  }

  private getMockKPIs(): KPI[] {
    return [
      { id: 'kpi-1', name: 'Disponibilidad Global', value: 94.5, target: 95, status: 'warning', trend: 'up', period: 'month' },
      { id: 'kpi-2', name: 'Tiempo de Respuesta', value: 2.5, target: 2, status: 'success', trend: 'down', period: 'month' },
      { id: 'kpi-3', name: 'Cumplimiento PM', value: 87.5, target: 90, status: 'warning', trend: 'up', period: 'month' },
      { id: 'kpi-4', name: 'Cero Eventos Adversos', value: 0, target: 0, status: 'success', trend: 'stable', period: 'month' },
    ];
  }

  private getMockTrends(): Trend[] {
    return [
      { metricId: 'disponibilidad', direction: 'up', changePercent: 2.4, changeValue: 2.4 },
      { metricId: 'mtbf', direction: 'up', changePercent: 6.5, changeValue: 15 },
      { metricId: 'mttf', direction: 'down', changePercent: -17.6, changeValue: -0.9 },
      { metricId: 'costo-promedio', direction: 'down', changePercent: -9.4, changeValue: -130 },
    ];
  }
}

export const analyticsService = new AnalyticsService();
