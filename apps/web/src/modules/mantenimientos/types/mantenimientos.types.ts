/**
 * Mantenimientos Types - Feature-First Migration
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
  imp: number | null
  frecuencia_mantenimiento: number | null
  fecha_ultimo_mantenimiento: string | null
  url_manual_tecnico: string | null
  created_at?: string
  updated_at?: string
  establecimientos?: {
    id: number
    nombre_comercial: string
    ruc: string
  }
  eventos_mantenimiento?: EventoMantenimiento[]
}

export interface EventoMantenimiento {
  id: number
  equipo_id: number
  tipo_evento: string
  fecha_ejecucion: string
  ingeniero_responsable: string
  descripcion_trabajo: string
  repuestos_cambiados?: string
  error_porcentual?: number
  incertidumbre?: number
  estado_final: string
  url_informe_mantenimiento?: string
  created_at?: string
  equipos?: Pick<Equipo, 'id' | 'nombre_dispositivo' | 'codigo_unico' | 'establecimiento_id' | 'url_manual_tecnico' | 'establecimientos'>
}

export interface Establecimiento {
  id: number
  ruc: string
  nombre_comercial: string
  tipologia: string
  direccion: string | null
  responsable_tecnico_cedula: string
  user_id: string | null
  url_certificado_acess: string | null
}

export interface MantenimientoFormData {
  establecimiento_id: string
  equipo_id: string
  tipo_evento: string
  fecha_ejecucion: string
  ingeniero_responsable: string
  descripcion_trabajo: string
  repuestos_cambiados: string
  error_porcentual: string
  incertidumbre: string
  estado_final: string
}

export const EMPTY_MANTENIMIENTO_FORM: MantenimientoFormData = {
  establecimiento_id: '',
  equipo_id: '',
  tipo_evento: '',
  fecha_ejecucion: new Date().toISOString().split('T')[0],
  ingeniero_responsable: '',
  descripcion_trabajo: '',
  repuestos_cambiados: '',
  error_porcentual: '',
  incertidumbre: '',
  estado_final: '',
}

export type TipoEvento = 'Preventivo' | 'Correctivo' | 'Calibración' | 'Predictivo'
export type EstadoMantenimiento = 'Inactivo' | 'Pendiente' | 'Operativo'
