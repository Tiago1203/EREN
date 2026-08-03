/**
 * Establecimientos Page - Feature-First Migration
 * PHASE 7 - EPIC 5a
 *
 * Esta página consume useEstablecimientosData y renderiza la UI.
 * La implementación se migró del routing adapter en app/(dashboard)/establecimientos/page.tsx
 */

'use client'

import { useAuth } from '@/hooks/useAuth'
import { ReadOnlyBanner } from '@/components/ui/ReadOnlyBanner'
import { useEstablecimientosData, getCalibrationAlert } from '../hooks/useEstablecimientosData'

export default function EstablecimientosPage() {
  const { isAdmin } = useAuth()
  const {
    establecimiento,
    equipos,
    loading,
    error,
    saving,
    showModal,
    formData,
    selectedCertificate,
    setShowModal,
    setFormData,
    setSelectedCertificate,
    handleSubmit,
    closeModal,
  } = useEstablecimientosData(isAdmin ? undefined : undefined, isAdmin)

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
          <h1 className="text-2xl font-bold">Mi Establecimiento</h1>
          {establecimiento && (
            <p className="text-sm text-[var(--muted)] mt-0.5">
              {establecimiento.nombre_comercial} — RUC {establecimiento.ruc}
            </p>
          )}
        </div>
        {isAdmin && (
          <button
            onClick={() => setShowModal(true)}
            className="btn-primary whitespace-nowrap"
          >
            + Nuevo Establecimiento
          </button>
        )}
      </div>

      {error && <div className="alert-error">{error}</div>}

      {isAdmin ? (
        <div className="card p-12 text-center">
          <p className="text-[var(--muted)]">Vista de administrador: usa el panel de administración para gestionar establecimientos.</p>
        </div>
      ) : establecimiento ? (
        <div className="space-y-4">
          <div className="card p-6">
            <h2 className="text-base font-semibold mb-4">Datos del Establecimiento</h2>
            <dl className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
              {[
                ['RUC', establecimiento.ruc],
                ['Nombre Comercial', establecimiento.nombre_comercial],
                ['Tipología', establecimiento.tipologia],
                ['Dirección', establecimiento.direccion || '—'],
                ['Responsable Técnico', establecimiento.responsable_tecnico_cedula],
              ].map(([label, value]) => (
                <div key={label as string}>
                  <dt className="text-[var(--muted)]">{label}</dt>
                  <dd className="font-medium mt-0.5">{value}</dd>
                </div>
              ))}
            </dl>
          </div>

          {equipos.length > 0 && (
            <div className="card overflow-hidden">
              <div className="p-4 border-b border-[var(--card-border)]">
                <h2 className="text-base font-semibold">
                  Equipos Registrados ({equipos.length})
                </h2>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-[var(--card-border)] bg-slate-50">
                      <th className="text-left px-4 py-3 font-medium text-[var(--muted)]">Equipo</th>
                      <th className="text-left px-4 py-3 font-medium text-[var(--muted)] hidden sm:table-cell">Código</th>
                      <th className="text-left px-4 py-3 font-medium text-[var(--muted)] hidden md:table-cell">Marca / Modelo</th>
                      <th className="text-left px-4 py-3 font-medium text-[var(--muted)]">Estado</th>
                      <th className="text-left px-4 py-3 font-medium text-[var(--muted)] hidden lg:table-cell">Próxima calibración</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[var(--card-border)]">
                    {equipos.map((equipo) => {
                      const alert = getCalibrationAlert(equipo.fecha_proxima_calibracion)
                      return (
                        <tr key={equipo.id} className="hover:bg-slate-50">
                          <td className="px-4 py-3 font-medium">{equipo.nombre_dispositivo}</td>
                          <td className="px-4 py-3 text-[var(--muted)] font-mono text-xs hidden sm:table-cell">{equipo.codigo_unico}</td>
                          <td className="px-4 py-3 hidden md:table-cell">{equipo.marca} / {equipo.modelo}</td>
                          <td className="px-4 py-3">
                            <span className="badge badge-establecimiento">{equipo.estado_final}</span>
                          </td>
                          <td className="px-4 py-3 hidden lg:table-cell">
                            {equipo.fecha_proxima_calibracion ? (
                              <span className={`text-xs ${
                                alert?.tone === 'danger' ? 'text-red-600 font-medium' :
                                alert?.tone === 'warning' ? 'text-amber-600 font-medium' :
                                alert?.tone === 'info' ? 'text-blue-600 font-medium' :
                                'text-[var(--muted)]'
                              }`}>
                                {new Date(equipo.fecha_proxima_calibracion).toLocaleDateString('es-EC')}
                                {alert && ` (${alert.label})`}
                              </span>
                            ) : '—'}
                          </td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      ) : (
        <div className="card p-12 text-center">
          <p className="text-[var(--muted)]">No se encontró información del establecimiento.</p>
        </div>
      )}

      {showModal && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
          <div className="card p-6 max-w-md w-full max-h-[90vh] overflow-y-auto">
            <h2 className="text-lg font-semibold mb-4">Nuevo Establecimiento</h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              {[
                { key: 'ruc', label: 'RUC', required: true },
                { key: 'nombre_comercial', label: 'Nombre Comercial', required: true },
                { key: 'tipologia', label: 'Tipología', required: true },
                { key: 'direccion', label: 'Dirección', required: false },
                { key: 'responsable_tecnico_cedula', label: 'Responsable Técnico (Cédula)', required: true },
                { key: 'email', label: 'Correo del establecimiento', required: true, type: 'email' },
                { key: 'password', label: 'Contraseña temporal', required: true, type: 'password' },
              ].map(({ key, label, required, type = 'text' }) => (
                <div key={key}>
                  <label className="block text-sm font-medium mb-1.5">{label}</label>
                  <input
                    type={type}
                    required={required}
                    className="input-field"
                    value={formData[key as keyof typeof formData]}
                    onChange={(e) => setFormData({ ...formData, [key]: e.target.value })}
                  />
                </div>
              ))}
              <div>
                <label className="block text-sm font-medium mb-1.5">Certificado PDF (opcional)</label>
                <input
                  type="file"
                  accept="application/pdf"
                  className="w-full"
                  onChange={(e) => setSelectedCertificate(e.target.files?.[0] ?? null)}
                />
                {selectedCertificate && (
                  <p className="text-xs text-[var(--muted)] mt-1">
                    Seleccionado: {selectedCertificate.name}
                  </p>
                )}
              </div>
              <div className="flex justify-end gap-3 pt-2">
                <button type="button" onClick={closeModal} className="btn-secondary">
                  Cancelar
                </button>
                <button type="submit" disabled={saving} className="btn-primary">
                  {saving ? 'Creando...' : 'Crear'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
