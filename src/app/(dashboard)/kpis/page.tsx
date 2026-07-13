'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '@/hooks/useAuth'
import { fetchEquipos, fetchEventos, fetchEstablecimientos, type Establecimiento, type Equipo } from '@/lib/queries'
import { calcularKpis } from '@/lib/kpis'
import { KpiGrid } from '@/components/ui/KpiGrid'

export default function KpisPage() {
  const { isAdmin, establecimientoId } = useAuth()
  const [establecimientos, setEstablecimientos] = useState<Establecimiento[]>([])
  const [selectedEstablecimiento, setSelectedEstablecimiento] = useState<number | null>(null)
  const [equipos, setEquipos] = useState<Equipo[]>([])
  const [selectedEquipo, setSelectedEquipo] = useState<number | null>(null)
  const [kpis, setKpis] = useState<ReturnType<typeof calcularKpis>>([])
  const [loading, setLoading] = useState(true)
  const [viewMode, setViewMode] = useState<'establecimiento' | 'equipo'>('establecimiento')

  useEffect(() => {
    loadEstablecimientos()
  }, [isAdmin])

  useEffect(() => {
    if (selectedEstablecimiento) {
      loadEquipos(selectedEstablecimiento)
    }
  }, [selectedEstablecimiento])

  useEffect(() => {
    if (viewMode === 'establecimiento' && selectedEstablecimiento) {
      loadKpisEstablecimiento(selectedEstablecimiento)
    } else if (viewMode === 'equipo' && selectedEquipo) {
      loadKpisEquipo(selectedEquipo)
    }
  }, [viewMode, selectedEstablecimiento, selectedEquipo])

  const loadEstablecimientos = async () => {
    try {
      setLoading(true)
      const { data } = await fetchEstablecimientos(isAdmin, isAdmin ? null : establecimientoId)
      setEstablecimientos(data || [])
      if (data && data.length > 0) {
        setSelectedEstablecimiento(data[0].id)
      }
    } catch (err) {
      console.error('Error al cargar establecimientos:', err)
    } finally {
      setLoading(false)
    }
  }

  const loadEquipos = async (estId: number) => {
    try {
      const { data } = await fetchEquipos(false, estId)
      setEquipos(data || [])
    } catch (err) {
      console.error('Error al cargar equipos:', err)
    }
  }

  const loadKpisEstablecimiento = async (estId: number) => {
    try {
      setLoading(true)
      const [eqRes, evRes] = await Promise.all([
        fetchEquipos(false, estId),
        fetchEventos(false, estId),
      ])

      const equiposData = eqRes.data || []
      const eventos = evRes.data || []

      setKpis(calcularKpis(equiposData, eventos))
    } catch (err) {
      console.error('Error al cargar KPIs:', err)
    } finally {
      setLoading(false)
    }
  }

  const loadKpisEquipo = async (equipoId: number) => {
    try {
      setLoading(true)
      const equipo = equipos.find(e => e.id === equipoId)
      if (!equipo) return

      const eventos = equipo.eventos_mantenimiento || []
      setKpis(calcularKpis([equipo], eventos))
    } catch (err) {
      console.error('Error al cargar KPIs del equipo:', err)
    } finally {
      setLoading(false)
    }
  }

  // Calcular fecha del próximo mantenimiento según manual
  const calcularProximoMantenimiento = (equipo: Equipo) => {
    if (!equipo.frecuencia_mantenimiento || !equipo.fecha_ultimo_mantenimiento) {
      return { proxima: null, estado: 'info' as const }
    }

    const ultimo = new Date(equipo.fecha_ultimo_mantenimiento)
    const proxima = new Date(ultimo)
    proxima.setDate(proxima.getDate() + equipo.frecuencia_mantenimiento)

    const hoy = new Date()
    const diasRestantes = Math.ceil((proxima.getTime() - hoy.getTime()) / (1000 * 60 * 60 * 24))

    let estado: 'ok' | 'warning' | 'danger' | 'info' = 'ok'
    if (diasRestantes < 0) estado = 'danger'
    else if (diasRestantes <= 7) estado = 'warning'

    return { proxima, estado, diasRestantes }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="w-6 h-6 border-2 border-[var(--primary)] border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  const selectedEst = establecimientos.find(e => e.id === selectedEstablecimiento)
  const selectedEq = equipos.find(e => e.id === selectedEquipo)

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">KPIs de Ingeniería Clínica</h1>
        <p className="text-sm text-[var(--muted)] mt-1">
          Análisis de indicadores por establecimiento y equipo
        </p>
      </div>

      {/* Selector de establecimiento */}
      {isAdmin && establecimientos.length > 0 && (
        <div className="card p-4">
          <label className="block text-sm font-medium mb-2">Seleccionar Establecimiento</label>
          <select
            className="input-field"
            value={selectedEstablecimiento || ''}
            onChange={(e) => {
              setSelectedEstablecimiento(Number(e.target.value))
              setSelectedEquipo(null)
              setViewMode('establecimiento')
            }}
          >
            {establecimientos.map((est) => (
              <option key={est.id} value={est.id}>
                {est.nombre_comercial}
              </option>
            ))}
          </select>
        </div>
      )}

      {/* Selector de modo de vista */}
      {selectedEstablecimiento && (
        <div className="card p-4">
          <div className="flex gap-4">
            <button
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                viewMode === 'establecimiento'
                  ? 'bg-[var(--primary)] text-white'
                  : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
              }`}
              onClick={() => setViewMode('establecimiento')}
            >
              Por Establecimiento
            </button>
            <button
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                viewMode === 'equipo'
                  ? 'bg-[var(--primary)] text-white'
                  : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
              }`}
              onClick={() => setViewMode('equipo')}
            >
              Por Equipo
            </button>
          </div>
        </div>
      )}

      {/* Selector de equipo */}
      {viewMode === 'equipo' && equipos.length > 0 && (
        <div className="card p-4">
          <label className="block text-sm font-medium mb-2">Seleccionar Equipo</label>
          <select
            className="input-field"
            value={selectedEquipo || ''}
            onChange={(e) => setSelectedEquipo(Number(e.target.value))}
          >
            <option value="">Seleccionar equipo...</option>
            {equipos.map((eq) => (
              <option key={eq.id} value={eq.id}>
                {eq.nombre_dispositivo} - {eq.codigo_unico}
              </option>
            ))}
          </select>
        </div>
      )}

      {/* Info del establecimiento/equipo seleccionado */}
      {selectedEst && viewMode === 'establecimiento' && (
        <div className="card p-4">
          <h3 className="text-sm font-semibold mb-2">Establecimiento: {selectedEst.nombre_comercial}</h3>
          <p className="text-xs text-[var(--muted)]">RUC: {selectedEst.ruc} | Tipología: {selectedEst.tipologia}</p>
        </div>
      )}

      {selectedEq && viewMode === 'equipo' && (
        <div className="card p-4">
          <h3 className="text-sm font-semibold mb-2">Equipo: {selectedEq.nombre_dispositivo}</h3>
          <p className="text-xs text-[var(--muted)]">Código: {selectedEq.codigo_unico} | Marca: {selectedEq.marca} {selectedEq.modelo}</p>
          
          {/* Alerta de mantenimiento */}
          {selectedEq.frecuencia_mantenimiento && selectedEq.fecha_ultimo_mantenimiento && (
            <div className="mt-3 p-3 rounded-lg border">
              {(() => {
                const { proxima, estado, diasRestantes } = calcularProximoMantenimiento(selectedEq)
                const statusColors = {
                  ok: 'border-emerald-200 bg-emerald-50 text-emerald-700',
                  warning: 'border-amber-200 bg-amber-50 text-amber-700',
                  danger: 'border-red-200 bg-red-50 text-red-700',
                  info: 'border-slate-200 bg-slate-50 text-slate-700',
                }
                return (
                  <div className={statusColors[estado]}>
                    <p className="text-sm font-medium">
                      {estado === 'danger' ? '⚠️ Mantenimiento vencido' : estado === 'warning' ? '⏰ Mantenimiento próximo' : '✅ Mantenimiento al día'}
                    </p>
                    <p className="text-xs mt-1">
                      {proxima ? `Próximo mantenimiento: ${proxima.toLocaleDateString('es-EC')} (${diasRestantes} días)` : 'Configure fecha y frecuencia'}
                    </p>
                  </div>
                )
              })()}
            </div>
          )}
        </div>
      )}

      {/* KPIs */}
      {(viewMode === 'establecimiento' && selectedEstablecimiento) || (viewMode === 'equipo' && selectedEquipo) ? (
        <KpiGrid kpis={kpis} showCategories={true} />
      ) : (
        <div className="card p-8 text-center">
          <p className="text-[var(--muted)]">
            {viewMode === 'establecimiento' ? 'Seleccione un establecimiento para ver los KPIs' : 'Seleccione un equipo para ver los KPIs'}
          </p>
        </div>
      )}
    </div>
  )
}
