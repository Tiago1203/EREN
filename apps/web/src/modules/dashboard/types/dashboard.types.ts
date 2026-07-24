/**
 * Tipos para el módulo Dashboard
 */

export interface DashboardStats {
  equipos: number;
  mantenimientos: number;
  establecimientos: number;
  incidentes?: number;
  alertas?: number;
}

export interface StatCard {
  id: string;
  title: string;
  value: number;
  subtitle: string;
  icon: string;
  color: string;
  href: string;
  show: boolean;
}

export interface Kpi {
  id: string;
  label: string;
  value: number | string;
  unit?: string;
  trend?: 'up' | 'down' | 'stable';
  trendValue?: number;
  status?: 'success' | 'warning' | 'danger' | 'info';
}

export interface KpiGridProps {
  kpis: Kpi[];
  title?: string;
}

export interface DashboardUser {
  id: string;
  nombre: string;
  email: string;
  isAdmin: boolean;
  establishmentId?: string;
}

export interface Establecimiento {
  id: string;
  ruc: string;
  nombre_comercial: string;
  tipologia: string;
  responsable_tecnico_cedula: string;
  direccion?: string;
  url_certificado_acess?: string;
}

export interface DashboardPageState {
  stats: DashboardStats;
  kpis: Kpi[];
  establishment: Establecimiento | null;
  loading: boolean;
  error: string | null;
}
