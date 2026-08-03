/**
 * Establecimientos Service - Feature-First Migration
 * PHASE 7 - EPIC 5a
 */

import { supabase } from '@/lib/supabase'
import { fetchEquiposByEstablecimiento } from '@/lib/queries'
import { uploadFileToBucket, removeFileFromBucket } from '@/lib/storage'
import type { Establecimiento, Equipo } from '../types/establecimientos.types'

export interface EstablecimientoWithEquipos extends Establecimiento {
  equipos?: Equipo[]
}

export async function loadEstablecimientoWithEquipos(
  establecimientoId: number | undefined
): Promise<{ establecimiento: EstablecimientoWithEquipos | null; error: string }> {
  if (!establecimientoId) return { establecimiento: null, error: '' }

  try {
    const { data: est, error: estErr } = await supabase
      .from('establecimientos')
      .select('*')
      .eq('id', establecimientoId)
      .single()

    if (estErr) throw estErr

    const { data: equipos } = await fetchEquiposByEstablecimiento(establecimientoId)

    return { establecimiento: { ...est, equipos: equipos || [] }, error: '' }
  } catch (err) {
    return {
      establecimiento: null,
      error: err instanceof Error ? err.message : 'Error al cargar establecimiento',
    }
  }
}

export interface SaveEstablecimientoPayload {
  ruc: string
  nombre_comercial: string
  tipologia: string
  direccion: string
  responsable_tecnico_cedula: string
  email: string
  password: string
}

export async function saveEstablecimiento(
  payload: SaveEstablecimientoPayload,
  selectedCertificate: File | null
): Promise<{ error: string }> {
  try {
    const { data: authData, error: authErr } = await supabase.auth.signUp({
      email: payload.email,
      password: payload.password,
    })
    if (authErr) throw authErr

    const userId = authData.user?.id
    if (!userId) throw new Error('No se pudo crear el usuario')

    const { data: est, error: estErr } = await supabase
      .from('establecimientos')
      .insert({
        ruc: payload.ruc,
        nombre_comercial: payload.nombre_comercial,
        tipologia: payload.tipologia,
        direccion: payload.direccion || null,
        responsable_tecnico_cedula: payload.responsable_tecnico_cedula,
        user_id: userId,
      })
      .select()
      .single()

    if (estErr) {
      if (userId) await supabase.auth.admin.deleteUser(userId)
      throw estErr
    }

    if (selectedCertificate && est.id) {
      const filename = `${Date.now()}_${selectedCertificate.name.replace(/[^a-zA-Z0-9.\-_]/g, '_')}`
      const path = `certificados/${est.id}/${filename}`
      const { error: upErr } = await uploadFileToBucket('certificados', path, selectedCertificate)
      if (!upErr) {
        await supabase
          .from('establecimientos')
          .update({ url_certificado_acess: path })
          .eq('id', est.id)
      }
    }

    return { error: '' }
  } catch (err) {
    return {
      error: err instanceof Error ? err.message : 'Error al crear establecimiento',
    }
  }
}

export async function loadEquiposByEstablecimiento(
  establecimientoId: number
): Promise<{ equipos: Equipo[]; error: string }> {
  try {
    const { equipos } = await fetchEquiposByEstablecimiento(establecimientoId)
    return { equipos: equipos || [], error: '' }
  } catch (err) {
    return {
      equipos: [],
      error: err instanceof Error ? err.message : 'Error al cargar equipos',
    }
  }
}
