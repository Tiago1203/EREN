/**
 * Equipos Service - Feature-First Migration
 * PHASE 7 - EPIC 5a
 */

import { supabase } from '@/lib/supabase'
import { fetchEquipos, fetchEstablecimientos } from '@/lib/queries'
import { uploadFileToBucket, getSignedUrlForPath, removeFileFromBucket } from '@/lib/storage'
import type { Equipo, Establecimiento } from '../types/equipos.types'

export interface EquiposFetchResult {
  equipos: Equipo[]
  establecimientos: Establecimiento[]
  error: string
}

export async function loadEquipos(
  isAdmin: boolean,
  establecimientoId: number | undefined
): Promise<EquiposFetchResult> {
  try {
    const [eqRes, estRes] = await Promise.all([
      fetchEquipos(isAdmin, establecimientoId),
      isAdmin ? fetchEstablecimientos(true, null) : Promise.resolve({ data: [], error: null }),
    ])

    if (eqRes.error) throw eqRes.error

    return {
      equipos: eqRes.data || [],
      establecimientos: estRes.data || [],
      error: '',
    }
  } catch (err) {
    return {
      equipos: [],
      establecimientos: [],
      error: err instanceof Error ? err.message : 'Error al cargar equipos',
    }
  }
}

export interface SaveEquipoPayload {
  establecimiento_id: number
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

export async function saveEquipo(
  payload: SaveEquipoPayload,
  editingId: number | null,
  selectedFile: File | null
): Promise<{ error: string }> {
  const dbPayload = {
    establecimiento_id: payload.establecimiento_id,
    codigo_unico: payload.codigo_unico,
    nombre_dispositivo: payload.nombre_dispositivo,
    marca: payload.marca,
    modelo: payload.modelo,
    numero_serie: payload.numero_serie,
    area_ubicacion: payload.area_ubicacion,
    criticidad: payload.criticidad,
    estado_final: payload.estado_final,
    fecha_proxima_calibracion: payload.fecha_proxima_calibracion || null,
    imp: payload.imp ? Number(payload.imp) : null,
    frecuencia_mantenimiento: payload.frecuencia_mantenimiento
      ? Number(payload.frecuencia_mantenimiento)
      : null,
    fecha_ultimo_mantenimiento: payload.fecha_ultimo_mantenimiento || null,
  }

  try {
    let equipoId = editingId

    if (editingId) {
      const { error } = await supabase.from('equipos').update(dbPayload).eq('id', editingId)
      if (error) throw error
    } else {
      const { data: newEq, error } = await supabase
        .from('equipos')
        .insert(dbPayload)
        .select()
        .single()
      if (error) throw error
      equipoId = newEq.id
    }

    if (selectedFile && equipoId) {
      const maxBytes = 10 * 1024 * 1024
      if (selectedFile.size > maxBytes) throw new Error('Archivo demasiado grande. Máx 10MB')

      const { data: old } = await supabase
        .from('equipos')
        .select('url_manual_tecnico')
        .eq('id', equipoId)
        .single()
      const oldPath = old?.url_manual_tecnico
      if (oldPath) await removeFileFromBucket('manuales', oldPath)

      const filename = `${Date.now()}_${selectedFile.name.replace(/[^a-zA-Z0-9.\-_]/g, '_')}`
      const path = `manuales/${dbPayload.establecimiento_id}/${equipoId}_${filename}`
      const { error: upErr } = await uploadFileToBucket('manuales', path, selectedFile)
      if (upErr) throw upErr
      const { error: updErr } = await supabase
        .from('equipos')
        .update({ url_manual_tecnico: path })
        .eq('id', equipoId)
      if (updErr) throw updErr
    }

    return { error: '' }
  } catch (err) {
    return { error: err instanceof Error ? err.message : 'Error al guardar equipo' }
  }
}

export async function deleteEquipo(id: number): Promise<{ error: string }> {
  try {
    const { error } = await supabase.from('equipos').delete().eq('id', id)
    if (error) throw error
    return { error: '' }
  } catch (err) {
    return { error: err instanceof Error ? err.message : 'Error al eliminar' }
  }
}

export async function getManualSignedUrl(
  path: string,
  establecimientoId: number,
  isAdmin: boolean,
  profileEstablecimientoId: number | undefined
): Promise<string | null> {
  if (!path) return null
  if (!isAdmin && profileEstablecimientoId !== establecimientoId) return null

  const { signedURL } = await getSignedUrlForPath(['manuales', 'certificados'], path, 300)
  return signedURL || null
}
