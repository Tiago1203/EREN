'use client'

import type { KpiResult } from '@/lib/kpis'

const statusColors: Record<KpiResult['status'], string> = {
  ok: 'border-emerald-200 bg-emerald-50',
  warning: 'border-amber-200 bg-amber-50',
  danger: 'border-red-200 bg-red-50',
  neutral: 'border-slate-200 bg-slate-50',
}

const valueColors: Record<KpiResult['status'], string> = {
  ok: 'text-emerald-700',
  warning: 'text-amber-700',
  danger: 'text-red-700',
  neutral: 'text-slate-700',
}

interface KpiGridProps {
  kpis: KpiResult[]
  showCategories?: boolean // Para mostrar categorías en la página de KPIs
}

export function KpiGrid({ kpis, showCategories = false }: KpiGridProps) {
  // Si showCategories es true, separar KPIs en categorías
  if (showCategories) {
    const kpisBasicos = kpis.slice(0, 10)
    const kpisIngenieria = kpis.slice(10)

    return (
      <div className="space-y-6">
        <div>
          <h3 className="text-sm font-semibold text-[var(--muted)] mb-3">KPIs Generales</h3>
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
            {kpisBasicos.map((kpi) => (
              <div key={kpi.label} className={`rounded-lg border p-4 ${statusColors[kpi.status]}`}>
                <p className="text-xs font-medium text-[var(--muted)]">{kpi.label}</p>
                <p className={`text-2xl font-bold mt-1 ${valueColors[kpi.status]}`}>{kpi.value}</p>
                {kpi.detail && <p className="text-xs text-[var(--muted)] mt-0.5">{kpi.detail}</p>}
              </div>
            ))}
          </div>
        </div>

        <div>
          <h3 className="text-sm font-semibold text-[var(--muted)] mb-3">KPIs de Ingeniería Clínica</h3>
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
            {kpisIngenieria.map((kpi) => (
              <div key={kpi.label} className={`rounded-lg border p-4 ${statusColors[kpi.status]}`}>
                <p className="text-xs font-medium text-[var(--muted)]">{kpi.label}</p>
                <p className={`text-xl font-bold mt-1 ${valueColors[kpi.status]}`}>{kpi.value}</p>
                {kpi.detail && <p className="text-xs text-[var(--muted)] mt-0.5">{kpi.detail}</p>}
              </div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  // Si showCategories es false, mostrar todos en una sola grilla (para dashboard)
  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
      {kpis.map((kpi) => (
        <div key={kpi.label} className={`rounded-lg border p-4 ${statusColors[kpi.status]}`}>
          <p className="text-xs font-medium text-[var(--muted)]">{kpi.label}</p>
          <p className={`text-2xl font-bold mt-1 ${valueColors[kpi.status]}`}>{kpi.value}</p>
          {kpi.detail && <p className="text-xs text-[var(--muted)] mt-0.5">{kpi.detail}</p>}
        </div>
      ))}
    </div>
  )
}
