/**
 * Establecimientos Types - Feature-First Migration
 * PHASE 7 - EPIC 5a
 */

export interface Establecimiento {
  id: number
  ruc: string
  nombre_comercial: string
  tipologia: string
  direccion: string | null
  responsable_tecnico_cedula: string
  user_id: string | null
  url_certificado_acess: string | null
  created_at?: string
}

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
}

export interface EstablecimientoFormData {
  ruc: string
  nombre_comercial: string
  tipologia: string
  direccion: string
  responsable_tecnico_cedula: string
  email: string
  password: string
}

export const EMPTY_ESTABLECIMIENTO_FORM: EstablecimientoFormData = {
  ruc: '',
  nombre_comercial: '',
  tipologia: '',
  direccion: '',
  responsable_tecnico_cedula: '',
  email: '',
  password: '',
}
