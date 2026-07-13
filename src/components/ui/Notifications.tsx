'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '@/hooks/useAuth'
import { fetchEquipos } from '@/lib/queries'

interface MaintenanceAlert {
  equipoId: number
  equipoNombre: string
  equipoCodigo: string
  proximaFecha: Date
  diasRestantes: number
  estado: 'danger' | 'warning' | 'ok'
}

export function NotificationBell() {
  const { isAdmin, establecimientoId } = useAuth()
  const [alerts, setAlerts] = useState<MaintenanceAlert[]>([])
  const [isOpen, setIsOpen] = useState(false)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    loadAlerts()
  }, [isAdmin, establecimientoId])

  const loadAlerts = async () => {
    try {
      setLoading(true)
      const { data: equipos } = await fetchEquipos(isAdmin, isAdmin ? null : establecimientoId)
      
      if (!equipos) {
        setAlerts([])
        return
      }

      const hoy = new Date()
      const alertas: MaintenanceAlert[] = []

      equipos.forEach((equipo) => {
        if (!equipo.frecuencia_mantenimiento || !equipo.fecha_ultimo_mantenimiento) return

        const ultimo = new Date(equipo.fecha_ultimo_mantenimiento)
        const proxima = new Date(ultimo)
        proxima.setDate(proxima.getDate() + equipo.frecuencia_mantenimiento)

        const diasRestantes = Math.ceil((proxima.getTime() - hoy.getTime()) / (1000 * 60 * 60 * 24))

        // Solo alertar si está vencido o faltan menos de 7 días
        if (diasRestantes < 7) {
          let estado: 'danger' | 'warning' | 'ok' = 'ok'
          if (diasRestantes < 0) estado = 'danger'
          else if (diasRestantes <= 7) estado = 'warning'

          alertas.push({
            equipoId: equipo.id,
            equipoNombre: equipo.nombre_dispositivo,
            equipoCodigo: equipo.codigo_unico,
            proximaFecha: proxima,
            diasRestantes,
            estado,
          })
        }
      })

      // Ordenar por días restantes (más urgentes primero)
      alertas.sort((a, b) => a.diasRestantes - b.diasRestantes)
      setAlerts(alertas)
    } catch (err) {
      console.error('Error al cargar alertas:', err)
    } finally {
      setLoading(false)
    }
  }

  const dangerCount = alerts.filter(a => a.estado === 'danger').length
  const warningCount = alerts.filter(a => a.estado === 'warning').length
  const totalCount = dangerCount + warningCount

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2 rounded-lg hover:bg-slate-100 transition-colors"
        title="Notificaciones de mantenimiento"
      >
        <svg className="w-5 h-5 text-slate-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
        </svg>
        {totalCount > 0 && (
          <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
            {totalCount}
          </span>
        )}
      </button>

      {isOpen && (
        <>
          <div className="fixed inset-0 z-40" onClick={() => setIsOpen(false)} />
          <div className="absolute right-0 top-12 w-80 bg-white rounded-lg shadow-xl border border-slate-200 z-50 max-h-96 overflow-y-auto">
            <div className="p-4 border-b border-slate-200">
              <h3 className="font-semibold text-sm">Alertas de Mantenimiento</h3>
              <p className="text-xs text-slate-500 mt-1">
                {totalCount === 0 ? 'Sin alertas' : `${totalCount} mantenimiento${totalCount !== 1 ? 's' : ''} pendiente${totalCount !== 1 ? 's' : ''}`}
              </p>
            </div>

            <div className="divide-y divide-slate-100">
              {alerts.length === 0 ? (
                <div className="p-4 text-center text-sm text-slate-500">
                  No hay alertas de mantenimiento
                </div>
              ) : (
                alerts.map((alert) => (
                  <div
                    key={alert.equipoId}
                    className={`p-4 hover:bg-slate-50 cursor-pointer ${
                      alert.estado === 'danger' ? 'border-l-4 border-red-500' : 'border-l-4 border-amber-500'
                    }`}
                  >
                    <div className="flex items-start gap-3">
                      <div className={`mt-0.5 ${
                        alert.estado === 'danger' ? 'text-red-500' : 'text-amber-500'
                      }`}>
                        {alert.estado === 'danger' ? (
                          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                          </svg>
                        ) : (
                          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                        )}
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium truncate">{alert.equipoNombre}</p>
                        <p className="text-xs text-slate-500">{alert.equipoCodigo}</p>
                        <p className={`text-xs mt-1 font-medium ${
                          alert.estado === 'danger' ? 'text-red-600' : 'text-amber-600'
                        }`}>
                          {alert.estado === 'danger' 
                            ? `Vencido hace ${Math.abs(alert.diasRestantes)} días`
                            : `Faltan ${alert.diasRestantes} días`
                          }
                        </p>
                        <p className="text-xs text-slate-400 mt-0.5">
                          Próximo: {alert.proximaFecha.toLocaleDateString('es-EC')}
                        </p>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>

            <div className="p-3 border-t border-slate-200">
              <button
                onClick={loadAlerts}
                disabled={loading}
                className="w-full text-xs text-center text-slate-500 hover:text-slate-700"
              >
                {loading ? 'Actualizando...' : 'Actualizar'}
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  )
}
