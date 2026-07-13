import { supabase } from './supabase'

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
  url_manual_tecnico: string | null
  imp: number | null
  frecuencia_mantenimiento: number | null
  fecha_ultimo_mantenimiento: string | null
  establecimientos?: Pick<Establecimiento, 'nombre_comercial' | 'ruc'>
  eventos_mantenimiento?: EventoMantenimiento[]
}

export interface EventoMantenimiento {
  id: number
  equipo_id: number
  tipo_evento: string
  fecha_ejecucion: string
  ingeniero_responsable: string
  descripcion_trabajo: string
  repuestos_cambiados: string | null
  error_porcentual: number | null
  incertidumbre: number | null
  estado_final: string
  url_informe_mantenimiento: string | null
  equipos?: {
    nombre_dispositivo: string
    codigo_unico: string
    establecimiento_id: number
    establecimientos?: Pick<Establecimiento, 'nombre_comercial'>
  }
}

export async function fetchEstablecimientos(isAdmin: boolean, establecimientoId: number | null) {
  let query = supabase.from('establecimientos').select('*').order('nombre_comercial')
  if (!isAdmin && establecimientoId) {
    query = query.eq('id', establecimientoId)
  }
  return query
}

export async function fetchEquipos(isAdmin: boolean, establecimientoId: number | null) {
  let query = supabase
    .from('equipos')
    .select('*, establecimientos(nombre_comercial, ruc), eventos_mantenimiento(*)')
    .order('nombre_dispositivo')

  if (!isAdmin && establecimientoId) {
    query = query.eq('establecimiento_id', establecimientoId)
  }
  return query
}

export async function fetchEquiposByEstablecimiento(establecimientoId: number) {
  return supabase
    .from('equipos')
    .select('*, establecimientos(nombre_comercial, ruc), eventos_mantenimiento(*)')
    .eq('establecimiento_id', establecimientoId)
    .order('nombre_dispositivo')
}

export async function fetchEventos(isAdmin: boolean, establecimientoId: number | null) {
  const { data, error } = await supabase
    .from('eventos_mantenimiento')
    .select(`
      *,
      equipos (
        nombre_dispositivo,
        codigo_unico,
        establecimiento_id,
        establecimientos (nombre_comercial)
      )
    `)
    .order('fecha_ejecucion', { ascending: false })

  if (error) return { data: null, error }

  let filtered = data || []
  if (!isAdmin && establecimientoId) {
    filtered = filtered.filter((e) => e.equipos?.establecimiento_id === establecimientoId)
  }

  return { data: filtered, error: null }
}

export async function fetchEquipoIdsForEstablecimiento(establecimientoId: number) {
  const { data } = await supabase
    .from('equipos')
    .select('id')
    .eq('establecimiento_id', establecimientoId)
  return (data || []).map((e) => e.id)
}
