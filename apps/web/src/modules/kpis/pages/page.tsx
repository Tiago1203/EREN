/**
 * KPIs Page - Feature-First Migration
 * PHASE 7 - EPIC 5a
 *
 * Esta página consume useKpisData y renderiza la UI.
 * La implementación se migró del routing adapter en app/(dashboard)/kpis/page.tsx
 */

'use client'

import { useAuth } from '@/hooks/useAuth'
import { KpiGrid } from '@/components/ui/KpiGrid'
import { useKpisData } from '../hooks/useKpisData'
import type { Equipo } from '../types/kpis.types'

export default function KpisPage() {
  const { isAdmin } = useAuth()
  const {
    establecimientos,
    equipos,
    selectedEstablecimiento,
    selectedEquipo,
    kpis,
    loading,
    viewMode,
    setSelectedEstablecimiento,
    setSelectedEquipo,
    setViewMode,
    calcularProximoMantenimiento,
  } = useKpisData(isAdmin, undefined)

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="w-6 h-6 border-2 border-[var(--primary)] border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  const selectedEst = establecimientos.find((e) => e.id === selectedEstablecimiento)
  const selectedEq = equipos.find((e) => e.id === selectedEquipo)

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">KPIs de Ingeniería Clínica</h1>
        <p className="text-sm text-[var(--muted)] mt-1">
          Análisis de indicadores por establecimiento y equipo
        </p>
      </div>

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

      {selectedEst && viewMode === 'establecimiento' && (
        <div className="card p-4">
          <h3 className="text-sm font-semibold mb-2">Establecimiento: {selectedEst.nombre_comercial}</h3>
          <p className="text-xs text-[var(--muted)]">
            RUC: {selectedEst.ruc} | Tipología: {selectedEst.tipologia}
          </p>
        </div>
      )}

      {selectedEq && viewMode === 'equipo' && (
        <div className="card p-4">
          <h3 className="text-sm font-semibold mb-2">Equipo: {selectedEq.nombre_dispositivo}</h3>
          <p className="text-xs text-[var(--muted)]">
            Código: {selectedEq.codigo_unico} | Marca: {selectedEq.marca} {selectedEq.modelo}
          </p>

          {selectedEq.frecuencia_mantenimiento && selectedEq.fecha_ultimo_mantenimiento && (
            <div className="mt-3 p-3 rounded-lg border">
              {(() => {
                const { proxima, estado, diasRestantes } = calcularProximoMantenimiento(selectedEq as Equipo)
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

      {(viewMode === 'establecimiento' && selectedEstablecimiento) || (viewMode === 'equipo' && selectedEquipo) ? (
        <KpiGrid kpis={kpis as any} showCategories={true} />
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
