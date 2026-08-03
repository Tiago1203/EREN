/**
 * KPIs Service - Feature-First Migration
 * PHASE 7 - EPIC 5a
 */

import { fetchEquipos, fetchEventos, fetchEstablecimientos } from '@/lib/queries'
import { calcularKpis } from '@/lib/kpis'
import type { Equipo, Establecimiento } from '../types/kpis.types'

export interface KpisFetchResult {
  establecimientos: Establecimiento[]
  equipos: Equipo[]
  eventos: any[]
  error: string
}

export async function loadKpisData(
  isAdmin: boolean,
  establecimientoId: number | undefined
): Promise<KpisFetchResult> {
  try {
    const [eqRes, evRes, estRes] = await Promise.all([
      fetchEquipos(isAdmin, isAdmin ? undefined : establecimientoId),
      fetchEventos(isAdmin, isAdmin ? undefined : establecimientoId),
      fetchEstablecimientos(isAdmin, isAdmin ? undefined : establecimientoId),
    ])

    return {
      establecimientos: estRes.data || [],
      equipos: eqRes.data || [],
      eventos: evRes.data || [],
      error: '',
    }
  } catch (err) {
    return {
      establecimientos: [],
      equipos: [],
      eventos: [],
      error: err instanceof Error ? err.message : 'Error al cargar datos de KPIs',
    }
  }
}

export async function loadKpisForEstablecimiento(
  establecimientoId: number
): Promise<{ kpis: ReturnType<typeof calcularKpis>; error: string }> {
  try {
    const [eqRes, evRes] = await Promise.all([
      fetchEquipos(false, establecimientoId),
      fetchEventos(false, establecimientoId),
    ])

    const equipos = eqRes.data || []
    const eventos = evRes.data || []
    const kpis = calcularKpis(equipos as any, eventos as any)

    return { kpis, error: '' }
  } catch (err) {
    return {
      kpis: [],
      error: err instanceof Error ? err.message : 'Error al cargar KPIs',
    }
  }
}

export async function loadKpisForEquipo(
  equipo: Equipo
): Promise<{ kpis: ReturnType<typeof calcularKpis>; error: string }> {
  try {
    const kpis = calcularKpis([equipo] as any, equipo.eventos_mantenimiento || [])
    return { kpis, error: '' }
  } catch (err) {
    return {
      kpis: [],
      error: err instanceof Error ? err.message : 'Error al cargar KPIs del equipo',
    }
  }
}
