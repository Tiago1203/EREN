/**
 * Mantenimientos Service - Feature-First Migration
 * PHASE 7 - EPIC 5a
 */

import { supabase } from '@/lib/supabase'
import { fetchEventos, fetchEquipos, fetchEstablecimientos } from '@/lib/queries'
import { uploadFileToBucket, removeFileFromBucket } from '@/lib/storage'
import type { EventoMantenimiento, Equipo, Establecimiento } from '../types/mantenimientos.types'

export interface MantenimientosFetchResult {
  eventos: EventoMantenimiento[]
  equipos: Equipo[]
  establecimientos: Establecimiento[]
  error: string
}

export async function loadMantenimientos(
  isAdmin: boolean,
  establecimientoId: number | undefined
): Promise<MantenimientosFetchResult> {
  try {
    const [evRes, eqRes, estRes] = await Promise.all([
      fetchEventos(isAdmin, establecimientoId),
      fetchEquipos(isAdmin, establecimientoId),
      isAdmin ? fetchEstablecimientos(true, null) : Promise.resolve({ data: [], error: null }),
    ])

    if (evRes.error) throw evRes.error
    if (eqRes.error) throw eqRes.error

    return {
      eventos: evRes.data || [],
      equipos: eqRes.data || [],
      establecimientos: estRes.data || [],
      error: '',
    }
  } catch (err) {
    return {
      eventos: [],
      equipos: [],
      establecimientos: [],
      error: err instanceof Error ? err.message : 'Error al cargar mantenimientos',
    }
  }
}

export interface SaveMantenimientoPayload {
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

export async function saveMantenimiento(
  payload: SaveMantenimientoPayload,
  editingId: number | null,
  selectedReportFile: File | null,
  existingEventos: EventoMantenimiento[]
): Promise<{ error: string }> {
  const dbPayload = {
    equipo_id: Number(payload.equipo_id),
    tipo_evento: payload.tipo_evento,
    fecha_ejecucion: payload.fecha_ejecucion,
    ingeniero_responsable: payload.ingeniero_responsable,
    descripcion_trabajo: payload.descripcion_trabajo,
    repuestos_cambiados: payload.repuestos_cambiados || null,
    error_porcentual: payload.error_porcentual ? Number(payload.error_porcentual) : null,
    incertidumbre: payload.incertidumbre ? Number(payload.incertidumbre) : null,
    estado_final: payload.estado_final,
  }

  try {
    let eventoId = editingId

    if (editingId) {
      const { error } = await supabase
        .from('eventos_mantenimiento')
        .update(dbPayload)
        .eq('id', editingId)
      if (error) throw error
    } else {
      const { data, error } = await supabase
        .from('eventos_mantenimiento')
        .insert(dbPayload)
        .select('id')
        .single()
      if (error) throw error
      eventoId = data?.id ?? null
    }

    if (selectedReportFile && eventoId) {
      const oldPath =
        existingEventos.find((e) => e.id === eventoId)?.url_informe_mantenimiento || null
      if (oldPath) {
        await removeFileFromBucket(['informes', 'certificados', 'manuales'], oldPath)
      }

      const filename = `${Date.now()}_${selectedReportFile.name.replace(/[^a-zA-Z0-9.\-_]/g, '_')}`
      const path = `informes/${eventoId}/${filename}`
      const { error: upErr } = await uploadFileToBucket(['informes'], path, selectedReportFile)
      if (upErr) throw upErr

      const { error: updateErr } = await supabase
        .from('eventos_mantenimiento')
        .update({ url_informe_mantenimiento: path })
        .eq('id', eventoId)
      if (updateErr) throw updateErr
    }

    return { error: '' }
  } catch (err) {
    return { error: err instanceof Error ? err.message : 'Error al guardar' }
  }
}

export async function deleteMantenimiento(id: number): Promise<{ error: string }> {
  try {
    const { error } = await supabase.from('eventos_mantenimiento').delete().eq('id', id)
    if (error) throw error
    return { error: '' }
  } catch (err) {
    return { error: err instanceof Error ? err.message : 'Error al eliminar' }
  }
}
