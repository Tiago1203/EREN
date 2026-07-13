'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '@/hooks/useAuth'
import { useRouter } from 'next/navigation'
import { fetchEquipos, fetchEventos, fetchEstablecimientos, type Establecimiento } from '@/lib/queries'
import { calcularKpisBasicos } from '@/lib/kpis'
import { KpiGrid } from '@/components/ui/KpiGrid'
import { getSignedUrlForPath } from '@/lib/storage'
import { ReadOnlyBanner } from '@/components/ui/ReadOnlyBanner'

export default function DashboardPage() {
  const { profile, isAdmin, establecimientoId } = useAuth()
  const [establecimiento, setEstablecimiento] = useState<Establecimiento | null>(null)
  const [stats, setStats] = useState({ equipos: 0, mantenimientos: 0, establecimientos: 0 })
  const [kpis, setKpis] = useState<ReturnType<typeof calcularKpisBasicos>>([])
  const [loading, setLoading] = useState(true)
  const [certUrl, setCertUrl] = useState<string | null>(null)
  const router = useRouter()

  useEffect(() => {
    if (profile) loadDashboard()
  }, [profile, isAdmin, establecimientoId])

  const loadDashboard = async () => {
    try {
      setLoading(true)
      const [eqRes, evRes, estRes] = await Promise.all([
        fetchEquipos(isAdmin, establecimientoId),
        fetchEventos(isAdmin, establecimientoId),
        fetchEstablecimientos(isAdmin, establecimientoId),
      ])

      const equipos = eqRes.data || []
      const eventos = evRes.data || []
      const establecimientos = estRes.data || []

      if (!isAdmin && establecimientoId && establecimientos.length > 0) {
        setEstablecimiento(establecimientos[0])
      }

      setStats({
        equipos: equipos.length,
        mantenimientos: eventos.length,
        establecimientos: isAdmin ? establecimientos.length : 1,
      })

      setKpis(calcularKpisBasicos(equipos, eventos))
    } catch {
      // no bloquear dashboard
    } finally {
      setLoading(false)
    }
  }

  const cards = [
    { title: 'Equipos', value: stats.equipos, subtitle: 'Registrados', href: '/equipos', color: 'bg-teal-500', show: true },
    { title: 'Mantenimientos', value: stats.mantenimientos, subtitle: 'Eventos', href: '/mantenimientos', color: 'bg-emerald-500', show: true },
    { title: 'Establecimientos', value: stats.establecimientos, subtitle: 'Centros', href: '/establecimientos', color: 'bg-violet-500', show: isAdmin },
  ]

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="w-6 h-6 border-2 border-[var(--primary)] border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {!isAdmin && <ReadOnlyBanner />}

      <div>
        <h1 className="text-2xl font-bold">
          Bienvenido{profile?.nombre ? `, ${profile.nombre}` : ''}
        </h1>
        <p className="text-sm text-[var(--muted)] mt-1">
          {isAdmin
            ? 'Panel de administración — gestión completa del sistema'
            : `Vista de su establecimiento: ${establecimiento?.nombre_comercial || '...'}`}
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
        {cards.filter((c) => c.show).map((card) => (
          <button
            key={card.href}
            onClick={() => router.push(card.href)}
            className="card p-6 text-left hover:shadow-md transition-shadow group"
          >
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm font-medium text-[var(--muted)]">{card.title}</p>
                <p className="text-3xl font-bold mt-1">{card.value}</p>
                <p className="text-xs text-[var(--muted)] mt-1">{card.subtitle}</p>
              </div>
              <div className={`${card.color} rounded-lg p-2.5 group-hover:scale-105 transition-transform`}>
                <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </div>
            </div>
          </button>
        ))}
      </div>

      {/* KPIs */}
      <div>
        <h2 className="text-lg font-semibold mb-4">
          {isAdmin ? 'KPIs del Sistema' : 'KPIs de su Establecimiento'}
        </h2>
        <KpiGrid kpis={kpis} />
      </div>

      {/* Info establecimiento (para usuarios establecimiento) */}
      {establecimiento && !isAdmin && (
        <div className="card p-6">
          <h3 className="text-base font-semibold mb-4">Mi Establecimiento</h3>
          <dl className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
            {[
              ['RUC', establecimiento.ruc],
              ['Nombre Comercial', establecimiento.nombre_comercial],
              ['Tipología', establecimiento.tipologia],
              ['Responsable Técnico', establecimiento.responsable_tecnico_cedula],
              ...(establecimiento.direccion ? [['Dirección', establecimiento.direccion]] : []),
            ].map(([label, value]) => (
              <div key={label as string}>
                <dt className="text-[var(--muted)]">{label}</dt>
                <dd className="font-medium mt-0.5">{value}</dd>
              </div>
            ))}
          </dl>
            {establecimiento.url_certificado_acess && (
              <div className="mt-4">
                <button
                  className="btn-secondary text-sm"
                  onClick={async () => {
                    const { signedURL, error } = await getSignedUrlForPath(['certificados', 'manuales'], establecimiento.url_certificado_acess || '', 300)
                    if (error || !signedURL) {
                      alert('No se puede obtener el certificado. Revisa permisos.')
                      return
                    }
                    window.open(signedURL, '_blank')
                  }}
                >
                  Ver certificado
                </button>
              </div>
            )}
        </div>
      )}
    </div>
  )
}
