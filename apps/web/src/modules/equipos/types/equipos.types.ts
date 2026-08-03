/**
 * Equipos Types - Feature-First Migration
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
  criticidad: 'baja' | 'media' | 'alta' | 'critica'
  estado_final: 'Operativo' | 'Pendiente' | 'Inactivo'
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

export interface EquipoFormData {
  establecimiento_id: string
  codigo_unico: string
  nombre_dispositivo: string
  marca: string
  modelo: string
  numero_serie: string
  area_ubicacion: string
  criticidad: string
  estado_final: string
  fecha_proxima_calibracion: string
  imp: string
  frecuencia_mantenimiento: string
  fecha_ultimo_mantenimiento: string
}

export const EMPTY_EQUIPO_FORM: EquipoFormData = {
  establecimiento_id: '',
  codigo_unico: '',
  nombre_dispositivo: '',
  marca: '',
  modelo: '',
  numero_serie: '',
  area_ubicacion: '',
  criticidad: 'media',
  estado_final: 'Operativo',
  fecha_proxima_calibracion: '',
  imp: '',
  frecuencia_mantenimiento: '',
  fecha_ultimo_mantenimiento: '',
}

export type Criticidad = Equipo['criticidad']
export type EstadoEquipo = Equipo['estado_final']
