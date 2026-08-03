/**
 * Equipos Page - Feature-First Migration
 * PHASE 7 - EPIC 5a
 *
 * Esta página consume useEquiposData y renderiza la UI.
 * La implementación se migró del routing adapter en app/(dashboard)/equipos/page.tsx
 */

'use client'

import { Fragment } from 'react'
import { useAuth } from '@/hooks/useAuth'
import { Modal } from '@/components/ui/Modal'
import { ReadOnlyBanner } from '@/components/ui/ReadOnlyBanner'
import { useEquiposData } from '../hooks/useEquiposData'

function estadoBadge(estado: string) {
  const map: Record<string, string> = {
    Operativo: 'badge-activo',
    Pendiente: 'badge-mantenimiento',
    Inactivo: 'badge-inactivo',
  }
  return map[estado] || 'badge-mantenimiento'
}

export default function EquiposPage() {
  const { profile, isAdmin } = useAuth()
  const {
    loading,
    error,
    search,
    selectedEstablecimientoId,
    showModal,
    saving,
    editingId,
    form,
    selectedFile,
    expandedId,
    establecimientos,
    filteredEquipos,
    setSearch,
    setSelectedEstablecimientoId,
    openCreate,
    openEdit,
    setForm,
    setSelectedFile,
    setExpandedId,
    handleSubmit,
    handleDelete,
    closeModal,
  } = useEquiposData(isAdmin, profile?.establecimiento_id)

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="w-6 h-6 border-2 border-[var(--primary)] border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {!isAdmin && <ReadOnlyBanner />}

      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">Equipos Médicos</h1>
          <p className="text-sm text-[var(--muted)] mt-0.5">
            {isAdmin
              ? `${filteredEquipos.length} equipos en todos los establecimientos`
              : `${filteredEquipos.length} equipos de su establecimiento`}
          </p>
        </div>
        <div className="flex flex-col sm:flex-row gap-2">
          {isAdmin && (
            <select
              className="input-field sm:w-56"
              value={selectedEstablecimientoId}
              onChange={(e) => setSelectedEstablecimientoId(e.target.value)}
            >
              <option value="">Todos los establecimientos</option>
              {establecimientos.map((est) => (
                <option key={est.id} value={est.id}>
                  {est.nombre_comercial}
                </option>
              ))}
            </select>
          )}
          <input
            type="search"
            placeholder="Buscar..."
            className="input-field sm:w-56"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          {isAdmin && (
            <button onClick={() => openCreate()} className="btn-primary whitespace-nowrap">
              + Nuevo Equipo
            </button>
          )}
        </div>
      </div>

      {error && <div className="alert-error">{error}</div>}

      {filteredEquipos.length === 0 ? (
        <div className="card p-12 text-center">
          <p className="text-[var(--muted)]">
            {search ? 'Sin resultados' : 'No hay equipos registrados'}
          </p>
        </div>
      ) : (
        <div className="card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-[var(--card-border)] bg-slate-50">
                  <th className="text-left px-4 py-3 font-medium text-[var(--muted)]">Equipo</th>
                  {isAdmin && (
                    <th className="text-left px-4 py-3 font-medium text-[var(--muted)] hidden md:table-cell">
                      Establecimiento
                    </th>
                  )}
                  <th className="text-left px-4 py-3 font-medium text-[var(--muted)] hidden sm:table-cell">
                    Código
                  </th>
                  <th className="text-left px-4 py-3 font-medium text-[var(--muted)] hidden lg:table-cell">
                    Criticidad
                  </th>
                  <th className="text-left px-4 py-3 font-medium text-[var(--muted)]">Estado</th>
                  <th className="text-left px-4 py-3 font-medium text-[var(--muted)] hidden lg:table-cell">
                    Próx. calibración
                  </th>
                  {isAdmin && (
                    <th className="text-right px-4 py-3 font-medium text-[var(--muted)]">Acciones</th>
                  )}
                </tr>
              </thead>
              <tbody className="divide-y divide-[var(--card-border)]">
                {filteredEquipos.map((equipo) => (
                  <Fragment key={equipo.id}>
                    <tr
                      className="hover:bg-slate-50 transition-colors cursor-pointer"
                      onClick={() =>
                        setExpandedId(expandedId === equipo.id ? null : equipo.id)
                      }
                    >
                      <td className="px-4 py-3">
                        <p className="font-medium">{equipo.nombre_dispositivo}</p>
                        <p className="text-xs text-[var(--muted)]">
                          {equipo.marca} / {equipo.modelo}
                        </p>
                      </td>
                      {isAdmin && (
                        <td className="px-4 py-3 text-[var(--muted)] hidden md:table-cell">
                          {equipo.establecimientos?.nombre_comercial ||
                            `#${equipo.establecimiento_id}`}
                        </td>
                      )}
                      <td className="px-4 py-3 font-mono text-xs hidden sm:table-cell">
                        {equipo.codigo_unico}
                      </td>
                      <td className="px-4 py-3 hidden lg:table-cell">
                        <span className="badge badge-establecimiento">{equipo.criticidad}</span>
                      </td>
                      <td className="px-4 py-3">
                        <span className={`badge ${estadoBadge(equipo.estado_final)}`}>
                          {equipo.estado_final}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-xs text-[var(--muted)] hidden lg:table-cell">
                        {equipo.fecha_proxima_calibracion
                          ? new Date(equipo.fecha_proxima_calibracion).toLocaleDateString('es-EC')
                          : '—'}
                      </td>
                      {isAdmin && (
                        <td
                          className="px-4 py-3 text-right"
                          onClick={(e) => e.stopPropagation()}
                        >
                          <button
                            onClick={() => openEdit(equipo)}
                            className="text-xs text-[var(--primary)] hover:underline mr-3"
                          >
                            Editar
                          </button>
                          <button
                            onClick={() => handleDelete(equipo.id)}
                            className="text-xs text-[var(--danger)] hover:underline"
                          >
                            Eliminar
                          </button>
                        </td>
                      )}
                    </tr>
                    {expandedId === equipo.id && (
                      <tr className="bg-slate-50">
                        <td colSpan={isAdmin ? 7 : 5} className="px-4 py-3">
                          <dl className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
                            <div>
                              <dt className="text-[var(--muted)]">Serie</dt>
                              <dd className="font-medium">{equipo.numero_serie}</dd>
                            </div>
                            <div>
                              <dt className="text-[var(--muted)]">Área</dt>
                              <dd className="font-medium">{equipo.area_ubicacion}</dd>
                            </div>
                            <div>
                              <dt className="text-[var(--muted)]">IMP</dt>
                              <dd className="font-medium">{equipo.imp ?? '—'}</dd>
                            </div>
                            <div>
                              <dt className="text-[var(--muted)]">RUC Est.</dt>
                              <dd className="font-medium">
                                {equipo.establecimientos?.ruc || '—'}
                              </dd>
                            </div>
                          </dl>
                        </td>
                      </tr>
                    )}
                  </Fragment>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {isAdmin && (
        <Modal
          open={showModal}
          onClose={closeModal}
          title={editingId ? 'Editar Equipo' : 'Nuevo Equipo'}
          wide
        >
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="sm:col-span-2">
                <label className="block text-sm font-medium mb-1">Establecimiento</label>
                <select
                  className="input-field"
                  required
                  value={form.establecimiento_id}
                  onChange={(e) => setForm({ ...form, establecimiento_id: e.target.value })}
                >
                  <option value="">Seleccionar...</option>
                  {establecimientos.map((e) => (
                    <option key={e.id} value={e.id}>
                      {e.nombre_comercial} ({e.ruc})
                    </option>
                  ))}
                </select>
              </div>
              {[
                { key: 'codigo_unico', label: 'Código único' },
                { key: 'nombre_dispositivo', label: 'Nombre del dispositivo' },
                { key: 'marca', label: 'Marca' },
                { key: 'modelo', label: 'Modelo' },
                { key: 'numero_serie', label: 'Número de serie' },
                { key: 'area_ubicacion', label: 'Área / Ubicación' },
              ].map(({ key, label }) => (
                <div key={key}>
                  <label className="block text-sm font-medium mb-1">{label}</label>
                  <input
                    className="input-field"
                    required
                    value={form[key as keyof typeof form]}
                    onChange={(e) => setForm({ ...form, [key]: e.target.value })}
                  />
                </div>
              ))}
              <div>
                <label className="block text-sm font-medium mb-1">Criticidad</label>
                <select
                  className="input-field"
                  value={form.criticidad}
                  onChange={(e) => setForm({ ...form, criticidad: e.target.value })}
                >
                  <option value="baja">Baja</option>
                  <option value="media">Media</option>
                  <option value="alta">Alta</option>
                  <option value="critica">Crítica</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Estado</label>
                <select
                  className="input-field"
                  value={form.estado_final}
                  onChange={(e) => setForm({ ...form, estado_final: e.target.value })}
                >
                  <option value="Operativo">Activo</option>
                  <option value="Pendiente">Mantenimiento</option>
                  <option value="Inactivo">Inactivo</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Próximo mantenimiento</label>
                <input
                  type="date"
                  className="input-field"
                  value={form.fecha_proxima_calibracion}
                  onChange={(e) =>
                    setForm({ ...form, fecha_proxima_calibracion: e.target.value })
                  }
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">IMP</label>
                <input
                  type="number"
                  step="0.01"
                  className="input-field"
                  value={form.imp}
                  onChange={(e) => setForm({ ...form, imp: e.target.value })}
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Frecuencia mantenimiento (días)</label>
                <input
                  type="number"
                  className="input-field"
                  value={form.frecuencia_mantenimiento}
                  onChange={(e) =>
                    setForm({ ...form, frecuencia_mantenimiento: e.target.value })
                  }
                  placeholder="Según manual"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Último mantenimiento</label>
                <input
                  type="date"
                  className="input-field"
                  value={form.fecha_ultimo_mantenimiento}
                  onChange={(e) =>
                    setForm({ ...form, fecha_ultimo_mantenimiento: e.target.value })
                  }
                />
              </div>
              <div className="sm:col-span-2">
                <label className="block text-sm font-medium mb-1">
                  Manual técnico (pdf, jpg, docx)
                </label>
                <input
                  type="file"
                  accept="application/pdf,image/*,application/vnd.openxmlformats-officedocument.wordprocessingml.document,application/msword"
                  className="w-full"
                  onChange={(e) => setSelectedFile(e.target.files?.[0] ?? null)}
                />
                {selectedFile && (
                  <p className="text-xs text-[var(--muted)] mt-1">
                    Seleccionado: {selectedFile.name}
                  </p>
                )}
              </div>
            </div>
            <div className="flex justify-end gap-3 pt-2">
              <button type="button" onClick={closeModal} className="btn-secondary">
                Cancelar
              </button>
              <button type="submit" disabled={saving} className="btn-primary">
                {saving ? 'Guardando...' : 'Guardar'}
              </button>
            </div>
          </form>
        </Modal>
      )}
    </div>
  )
}
