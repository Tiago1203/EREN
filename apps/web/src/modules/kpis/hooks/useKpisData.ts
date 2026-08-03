/**
 * useKpisData Hook - Feature-First Migration
 * PHASE 7 - EPIC 5a
 */

import { useState, useCallback, useEffect } from 'react'
import type { Equipo, Establecimiento, KpiData, ViewMode } from '../types/kpis.types'
import { loadKpisData, loadKpisForEstablecimiento, loadKpisForEquipo } from '../services/kpis.service'

export interface UseKpisDataReturn {
  establecimientos: Establecimiento[]
  equipos: Equipo[]
  selectedEstablecimiento: number | null
  selectedEquipo: number | null
  kpis: KpiData[]
  loading: boolean
  viewMode: ViewMode
  loadEstablecimientos: () => Promise<void>
  setSelectedEstablecimiento: (id: number | null) => void
  setSelectedEquipo: (id: number | null) => void
  setViewMode: (mode: ViewMode) => void
  calcularProximoMantenimiento: (equipo: Equipo) => {
    proxima: Date | null
    estado: 'ok' | 'warning' | 'danger' | 'info'
    diasRestantes: number
  }
}

export function useKpisData(
  isAdmin: boolean,
  establecimientoId: number | undefined
): UseKpisDataReturn {
  const [establecimientos, setEstablecimientos] = useState<Establecimiento[]>([])
  const [equipos, setEquipos] = useState<Equipo[]>([])
  const [selectedEstablecimiento, setSelectedEstablecimiento] = useState<number | null>(null)
  const [selectedEquipo, setSelectedEquipo] = useState<number | null>(null)
  const [kpis, setKpis] = useState<KpiData[]>([])
  const [loading, setLoading] = useState(true)
  const [viewMode, setViewMode] = useState<ViewMode>('establecimiento')

  const loadKpisForSelection = useCallback(async () => {
    if (viewMode === 'establecimiento' && selectedEstablecimiento) {
      setLoading(true)
      const result = await loadKpisForEstablecimiento(selectedEstablecimiento)
      setKpis(result.kpis as KpiData[])
      setLoading(false)
    } else if (viewMode === 'equipo' && selectedEquipo) {
      setLoading(true)
      const equipo = equipos.find((e) => e.id === selectedEquipo)
      if (equipo) {
        const result = await loadKpisForEquipo(equipo)
        setKpis(result.kpis as KpiData[])
      }
      setLoading(false)
    }
  }, [viewMode, selectedEstablecimiento, selectedEquipo, equipos])

  const loadEstablecimientos = useCallback(async () => {
    try {
      setLoading(true)
      const result = await loadKpisData(isAdmin, establecimientoId)
      setEstablecimientos(result.establecimientos)
      setEquipos(result.equipos)
      if (result.establecimientos.length > 0) {
        setSelectedEstablecimiento(result.establecimientos[0].id)
      }
    } finally {
      setLoading(false)
    }
  }, [isAdmin, establecimientoId])

  useEffect(() => {
    loadEstablecimientos()
  }, [loadEstablecimientos])

  useEffect(() => {
    if (selectedEstablecimiento) {
      loadKpisForSelection()
    }
  }, [selectedEstablecimiento, viewMode])

  useEffect(() => {
    if (selectedEquipo && viewMode === 'equipo') {
      loadKpisForSelection()
    }
  }, [selectedEquipo, viewMode])

  const calcularProximoMantenimiento = useCallback((equipo: Equipo) => {
    if (!equipo.frecuencia_mantenimiento || !equipo.fecha_ultimo_mantenimiento) {
      return { proxima: null, estado: 'info' as const, diasRestantes: 0 }
    }

    const ultimo = new Date(equipo.fecha_ultimo_mantenimiento)
    const proxima = new Date(ultimo)
    proxima.setDate(proxima.getDate() + equipo.frecuencia_mantenimiento)

    const hoy = new Date()
    const diasRestantes = Math.ceil(
      (proxima.getTime() - hoy.getTime()) / (1000 * 60 * 60 * 24)
    )

    let estado: 'ok' | 'warning' | 'danger' | 'info' = 'ok'
    if (diasRestantes < 0) estado = 'danger'
    else if (diasRestantes <= 7) estado = 'warning'

    return { proxima, estado, diasRestantes }
  }, [])

  return {
    establecimientos,
    equipos,
    selectedEstablecimiento,
    selectedEquipo,
    kpis,
    loading,
    viewMode,
    loadEstablecimientos,
    setSelectedEstablecimiento,
    setSelectedEquipo,
    setViewMode,
    calcularProximoMantenimiento,
  }
}
