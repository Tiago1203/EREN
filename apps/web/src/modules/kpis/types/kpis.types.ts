/**
 * KPIs Types - Feature-First Migration
 * PHASE 7 - EPIC 5a
 */

export interface Equipo {
  id: number
  establecimiento_id: number
  codigo_unico: string
  nombre_dispositivo: string
  marca: string
  modelo: string
  numero_serie: string
  area_ubicacion: string
  criticidad: string
  estado_final: string
  fecha_proxima_calibracion: string | null
  frecuencia_mantenimiento: number | null
  fecha_ultimo_mantenimiento: string | null
}

export interface Establecimiento {
  id: number
  ruc: string
  nombre_comercial: string
  tipologia: string
  direccion: string | null
  responsable_tecnico_cedula: string
}

export interface KpiData {
  id: string
  label: string
  value: number
  unit: string
  category: string
  status: 'ok' | 'warning' | 'danger' | 'info'
  description?: string
}

export type ViewMode = 'establecimiento' | 'equipo'
