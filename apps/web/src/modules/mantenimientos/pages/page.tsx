/**
 * Mantenimientos Page - Feature-First Migration
 * PHASE 7 - EPIC 5a
 *
 * Esta página consume useMantenimientosData y renderiza la UI.
 * La implementación se migró del routing adapter en app/(dashboard)/mantenimientos/page.tsx
 */

'use client'

import { useEffect } from 'react'
import { useAuth } from '@/hooks/useAuth'
import { Modal } from '@/components/ui/Modal'
import { ReadOnlyBanner } from '@/components/ui/ReadOnlyBanner'
import { FileViewer } from '@/components/ui/FileViewer'
import { useMantenimientosData } from '../hooks/useMantenimientosData'

export default function MantenimientosPage() {
  const { profile, isAdmin } = useAuth()
  const {
    loading,
    error,
    selectedEstablecimientoId,
    showModal,
    saving,
    editingId,
    form,
    selectedReportFile,
    equipos,
    establecimientos,
    filteredEventos,
    loadData,
    setSelectedEstablecimientoId,
    openCreate,
    openEdit,
    setForm,
    setSelectedReportFile,
    handleSubmit,
    handleDelete,
    closeModal,
  } = useMantenimientosData(isAdmin, profile?.establecimiento_id)

  useEffect(() => {
    if (profile) loadData()
  }, [profile, isAdmin])

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
          <h1 className="text-2xl font-bold">Mantenimientos</h1>
          <p className="text-sm text-[var(--muted)] mt-0.5">
            {filteredEventos.length} eventos{' '}
            {isAdmin ? 'en el sistema' : 'de su establecimiento'}
          </p>
        </div>
        <div className="flex items-center gap-2">
          {isAdmin && (
            <select
              className="input-field min-w-[220px]"
              value={selectedEstablecimientoId}
              onChange={(e) => setSelectedEstablecimientoId(e.target.value)}
            >
              <option value="">Todos los establecimientos</option>
              {establecimientos.map((est) => (
                <option key={est.id} value={String(est.id)}>
                  {est.nombre_comercial} ({est.ruc})
                </option>
              ))}
            </select>
          )}
          {isAdmin && (
            <button onClick={() => openCreate()} className="btn-primary">
              + Nuevo Mantenimiento
            </button>
          )}
        </div>
      </div>

      {error && <div className="alert-error">{error}</div>}

      {filteredEventos.length === 0 ? (
        <div className="card p-12 text-center">
          <p className="text-[var(--muted)]">No hay eventos de mantenimiento registrados</p>
        </div>
      ) : (
        <div className="space-y-3">
          {filteredEventos.map((evento) => (
            <div key={evento.id} className="card p-5">
              <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-3">
                <div className="flex-1">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="badge badge-establecimiento">{evento.tipo_evento}</span>
                    <span className="text-xs text-[var(--muted)]">
                      {new Date(evento.fecha_ejecucion).toLocaleDateString('es-EC', {
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric',
                      })}
                    </span>
                    {isAdmin && evento.equipos?.establecimientos?.nombre_comercial && (
                      <span className="text-xs text-[var(--muted)]">
                        • {evento.equipos.establecimientos.nombre_comercial}
                      </span>
                    )}
                  </div>
                  <h3 className="font-medium mt-2">
                    {evento.equipos?.nombre_dispositivo || `Equipo #${evento.equipo_id}`}
                  </h3>
                  {evento.equipos?.codigo_unico && (
                    <p className="text-xs text-[var(--muted)] font-mono">
                      {evento.equipos.codigo_unico}
                    </p>
                  )}
                  <p className="text-sm text-[var(--muted)] mt-2">{evento.descripcion_trabajo}</p>
                  <div className="flex flex-wrap gap-4 mt-2 text-xs text-[var(--muted)]">
                    <span>Ingeniero: {evento.ingeniero_responsable}</span>
                    {evento.error_porcentual != null && (
                      <span>Error: {evento.error_porcentual}%</span>
                    )}
                    {evento.incertidumbre != null && (
                      <span>Incertidumbre: {evento.incertidumbre}</span>
                    )}
                    {evento.repuestos_cambiados && (
                      <span>Repuestos: {evento.repuestos_cambiados}</span>
                    )}
                  </div>
                  <div className="mt-3">
                    <p className="text-xs font-medium text-[var(--muted)] mb-1">
                      Informe de mantenimiento
                    </p>
                    {evento.url_informe_mantenimiento ? (
                      <FileViewer
                        path={evento.url_informe_mantenimiento}
                        establecimientoId={evento.equipos?.establecimiento_id ?? 0}
                        onDeleted={() => loadData()}
                      />
                    ) : (
                      <span className="text-xs text-[var(--muted)]">Sin informe adjunto</span>
                    )}
                  </div>
                </div>
                <div className="flex items-start gap-2 self-start">
                  <span
                    className={`badge ${
                      evento.estado_final === 'Operativo'
                        ? 'badge-activo'
                        : 'badge-mantenimiento'
                    }`}
                  >
                    {evento.estado_final}
                  </span>
                  {isAdmin && (
                    <>
                      <button
                        onClick={() => openEdit(evento)}
                        className="text-xs text-[var(--primary)] hover:underline"
                      >
                        Editar
                      </button>
                      <button
                        onClick={() => handleDelete(evento.id)}
                        className="text-xs text-[var(--danger)] hover:underline"
                      >
                        Eliminar
                      </button>
                    </>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {isAdmin && (
        <Modal
          open={showModal}
          onClose={closeModal}
          title={editingId ? 'Editar Mantenimiento' : 'Nuevo Mantenimiento'}
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
                  onChange={(e) => {
                    setForm({ ...form, establecimiento_id: e.target.value, equipo_id: '' })
                  }}
                >
                  <option value="">Seleccionar establecimiento...</option>
                  {establecimientos.map((est) => (
                    <option key={est.id} value={est.id}>
                      {est.nombre_comercial} ({est.ruc})
                    </option>
                  ))}
                </select>
              </div>
              <div className="sm:col-span-2">
                <label className="block text-sm font-medium mb-1">Equipo</label>
                <select
                  className="input-field"
                  required
                  value={form.equipo_id}
                  onChange={(e) => setForm({ ...form, equipo_id: e.target.value })}
                  disabled={!form.establecimiento_id}
                >
                  <option value="">
                    {form.establecimiento_id
                      ? 'Seleccionar equipo...'
                      : 'Primero elige un establecimiento'}
                  </option>
                  {equipos
                    .filter(
                      (eq) =>
                        !form.establecimiento_id ||
                        String(eq.establecimiento_id) === form.establecimiento_id
                    )
                    .map((eq) => (
                      <option key={eq.id} value={eq.id}>
                        {eq.nombre_dispositivo} ({eq.codigo_unico}) —{' '}
                        {eq.establecimientos?.nombre_comercial}
                      </option>
                    ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Tipo de evento</label>
                <select
                  className="input-field"
                  value={form.tipo_evento}
                  onChange={(e) => setForm({ ...form, tipo_evento: e.target.value })}
                >
                  <option value="Preventivo">Preventivo</option>
                  <option value="Correctivo">Correctivo</option>
                  <option value="Calibración">Calibración</option>
                  <option value="Predictivo">Predictivo</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Fecha ejecución</label>
                <input
                  type="date"
                  className="input-field"
                  required
                  value={form.fecha_ejecucion}
                  onChange={(e) => setForm({ ...form, fecha_ejecucion: e.target.value })}
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Ingeniero responsable</label>
                <input
                  className="input-field"
                  required
                  value={form.ingeniero_responsable}
                  onChange={(e) => setForm({ ...form, ingeniero_responsable: e.target.value })}
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Estado final</label>
                <select
                  className="input-field"
                  value={form.estado_final}
                  onChange={(e) => setForm({ ...form, estado_final: e.target.value })}
                >
                  <option value="Inactivo">Inactivo</option>
                  <option value="Pendiente">Pendiente</option>
                  <option value="Operativo">Operativo</option>
                </select>
              </div>
              <div className="sm:col-span-2">
                <label className="block text-sm font-medium mb-1">
                  Descripción del trabajo
                </label>
                <textarea
                  className="input-field"
                  rows={3}
                  required
                  value={form.descripcion_trabajo}
                  onChange={(e) => setForm({ ...form, descripcion_trabajo: e.target.value })}
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Error porcentual (%)</label>
                <input
                  type="number"
                  step="0.01"
                  className="input-field"
                  value={form.error_porcentual}
                  onChange={(e) => setForm({ ...form, error_porcentual: e.target.value })}
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Incertidumbre</label>
                <input
                  type="number"
                  step="0.01"
                  className="input-field"
                  value={form.incertidumbre}
                  onChange={(e) => setForm({ ...form, incertidumbre: e.target.value })}
                />
              </div>
              <div className="sm:col-span-2">
                <label className="block text-sm font-medium mb-1">Repuestos cambiados</label>
                <input
                  className="input-field"
                  value={form.repuestos_cambiados}
                  onChange={(e) => setForm({ ...form, repuestos_cambiados: e.target.value })}
                />
              </div>
              <div className="sm:col-span-2">
                <label className="block text-sm font-medium mb-1">
                  Informe de mantenimiento (PDF)
                </label>
                <input
                  type="file"
                  accept="application/pdf"
                  className="w-full"
                  onChange={(e) => setSelectedReportFile(e.target.files?.[0] ?? null)}
                />
                {selectedReportFile && (
                  <p className="text-xs text-[var(--muted)] mt-1">
                    Seleccionado: {selectedReportFile.name}
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
