'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '@/hooks/useAuth'
import { supabase } from '@/lib/supabase'
import { fetchEquiposByEstablecimiento, type Equipo } from '@/lib/queries'
import { uploadFileToBucket, removeFileFromBucket } from '@/lib/storage'
import FileViewer from '@/components/ui/FileViewer'

interface Establecimiento {
  id: number
  ruc: string
  nombre_comercial: string
  tipologia: string
  direccion: string | null
  responsable_tecnico_cedula: string
  user_id: string | null
  url_certificado_acess: string | null
}

const emptyForm = {
  ruc: '',
  nombre_comercial: '',
  tipologia: '',
  direccion: '',
  responsable_tecnico_cedula: '',
  email: '',
  password: '',
}

const getCalibrationAlert = (date: string | null) => {
  if (!date) return null

  const target = new Date(date)
  target.setHours(0, 0, 0, 0)

  const today = new Date()
  today.setHours(0, 0, 0, 0)

  const diffDays = Math.ceil((target.getTime() - today.getTime()) / (1000 * 60 * 60 * 24))

  if (diffDays < 0) {
    return {
      tone: 'danger',
      label: `Vencida hace ${Math.abs(diffDays)} día${Math.abs(diffDays) === 1 ? '' : 's'}`,
    }
  }

  if (diffDays <= 7) {
    return {
      tone: 'warning',
      label: `En ${diffDays} día${diffDays === 1 ? '' : 's'}`,
    }
  }

  if (diffDays <= 30) {
    return {
      tone: 'info',
      label: `En ${diffDays} días`,
    }
  }

  return null
}

function getSupabaseErrorMessage(error: unknown, fallback: string) {
  if (typeof error === 'string') return error

  if (error && typeof error === 'object') {
    const maybe = error as { message?: string; details?: string; hint?: string; code?: string }
    if (maybe.message) return maybe.message
    const parts = [maybe.details, maybe.hint].filter(Boolean)
    if (parts.length > 0) return parts.join(' · ')
    if (maybe.code && maybe.code.trim()) return `${fallback} (código ${maybe.code})`
  }

  return fallback
}

export default function EstablecimientosPage() {
  const { isAdmin } = useAuth()
  const [establecimientos, setEstablecimientos] = useState<Establecimiento[]>([])
  const [uploadingId, setUploadingId] = useState<number | null>(null)
  const [loading, setLoading] = useState(true)
  const [selectedEstablecimiento, setSelectedEstablecimiento] = useState<Establecimiento | null>(null)
  const [equipos, setEquipos] = useState<Equipo[]>([])
  const [detailLoading, setDetailLoading] = useState(false)
  const [detailError, setDetailError] = useState('')
  const [showModal, setShowModal] = useState(false)
  const [saving, setSaving] = useState(false)
  const [formData, setFormData] = useState(emptyForm)
  const [selectedCertificate, setSelectedCertificate] = useState<File | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    if (isAdmin) {
      fetchEstablecimientos()
      setSelectedEstablecimiento(null)
      setEquipos([])
    }
  }, [isAdmin])

  const fetchEstablecimientos = async () => {
    try {
      setLoading(true)
      const { data, error } = await supabase.from('establecimientos').select('*').order('nombre_comercial')
      if (error) throw error
      setEstablecimientos(data || [])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al cargar establecimientos')
    } finally {
      setLoading(false)
    }
  }

  const fetchEquiposForEstablecimiento = async (est: Establecimiento) => {
    setSelectedEstablecimiento(est)
    setDetailError('')
    setDetailLoading(true)

    try {
      const { data, error } = await fetchEquiposByEstablecimiento(est.id)
      if (error) throw error
      setEquipos(data || [])
    } catch (err) {
      setDetailError(err instanceof Error ? err.message : 'Error al cargar equipos')
      setEquipos([])
    } finally {
      setDetailLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    setError('')

    const requiredFields = [
      formData.ruc,
      formData.nombre_comercial,
      formData.tipologia,
      formData.responsable_tecnico_cedula,
      formData.email,
      formData.password,
    ]

    if (requiredFields.some((value) => !String(value).trim())) {
      setError('Todos los campos obligatorios deben completarse antes de guardar el establecimiento.')
      setSaving(false)
      return
    }

    // Verificar si el RUC ya existe
    const { data: existingRuc } = await supabase
      .from('establecimientos')
      .select('id')
      .eq('ruc', formData.ruc.trim())
      .single()

    if (existingRuc) {
      setError('Ya existe un establecimiento con este RUC. Por favor use un RUC diferente.')
      setSaving(false)
      return
    }

    let createdEstablecimientoId: number | null = null

    try {
      const { data: estData, error: estError } = await supabase
        .from('establecimientos')
        .insert({
          ruc: formData.ruc,
          nombre_comercial: formData.nombre_comercial,
          tipologia: formData.tipologia,
          direccion: formData.direccion || null,
          responsable_tecnico_cedula: formData.responsable_tecnico_cedula,
        })
        .select()
        .single()

      if (estError) throw estError
      createdEstablecimientoId = estData?.id ?? null

      let certificadoPath: string | null = null
      if (selectedCertificate) {
        const maxBytes = 10 * 1024 * 1024
        if (selectedCertificate.size > maxBytes) throw new Error('El archivo es demasiado grande. Máx 10MB')

        const filename = `${Date.now()}_${selectedCertificate.name.replace(/[^a-zA-Z0-9.\-_]/g, '_')}`
        const path = `certificados/${estData.id}/${filename}`
        const { error: upErr } = await uploadFileToBucket(['certificados', 'manuales'], path, selectedCertificate)
        if (upErr) throw upErr
        certificadoPath = path
      }

      if (certificadoPath) {
        const { error: updateError } = await supabase
          .from('establecimientos')
          .update({ url_certificado_acess: certificadoPath })
          .eq('id', estData.id)

        if (updateError) throw updateError
      }

      // Crear usuario usando endpoint API con service role key (evita límite de correos)
      const response = await fetch('/api/create-user', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: formData.email.trim(),
          password: formData.password,
          role: 'establecimiento',
          establecimientoId: estData.id,
        }),
      })

      const responseText = await response.text()

      if (!response.ok) {
        let errorData
        try {
          errorData = JSON.parse(responseText)
        } catch {
          throw new Error(`Error del servidor (${response.status}): ${responseText.substring(0, 200)}`)
        }
        throw new Error(errorData.error || 'Error al crear el usuario')
      }

      let userId
      try {
        const data = JSON.parse(responseText)
        userId = data.userId
      } catch {
        throw new Error('Respuesta inválida del servidor')
      }

      if (!userId) throw new Error('No se pudo crear el usuario del establecimiento.')

      const { error: updateError } = await supabase
        .from('establecimientos')
        .update({ user_id: userId })
        .eq('id', estData.id)

      if (updateError) throw updateError

      setShowModal(false)
      setFormData(emptyForm)
      setSelectedCertificate(null)
      fetchEstablecimientos()

      alert(
        `Establecimiento creado.\n\nEmail: ${formData.email.trim()}\nContraseña: ${formData.password}\n\nEl usuario debe cambiar su contraseña al primer inicio.`
      )
    } catch (err) {
      console.error('Error al crear establecimiento', err)
      console.error('Error type:', typeof err)
      console.error('Error keys:', err && typeof err === 'object' ? Object.keys(err) : 'N/A')
      console.error('Error stringified:', JSON.stringify(err))
      if (createdEstablecimientoId) {
        await supabase.from('establecimientos').delete().eq('id', createdEstablecimientoId)
      }
      setError(getSupabaseErrorMessage(err, 'Error al crear establecimiento'))
    } finally {
      setSaving(false)
    }
  }

  const calibrationAlerts = (selectedEstablecimiento ? equipos : [])
    .map((equipo) => {
      const alert = getCalibrationAlert(equipo.fecha_proxima_calibracion)
      if (!alert) return null
      return {
        ...alert,
        equipo: equipo.nombre_dispositivo,
        codigo: equipo.codigo_unico,
      }
    })
    .filter(Boolean)
    .sort((a, b) => (a?.equipo || '').localeCompare(b?.equipo || ''))

  if (!isAdmin) {
    return (
      <div className="card p-8 text-center">
        <p className="text-[var(--danger)]">Acceso denegado. Solo administradores pueden gestionar establecimientos.</p>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="w-6 h-6 border-2 border-[var(--primary)] border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">Establecimientos</h1>
          <p className="text-sm text-[var(--muted)] mt-0.5">{establecimientos.length} centros registrados</p>
        </div>
        <button onClick={() => setShowModal(true)} className="btn-primary">
          + Nuevo Establecimiento
        </button>
      </div>

      {error && <div className="alert-error">{error}</div>}

      {establecimientos.length === 0 ? (
        <div className="card p-12 text-center">
          <p className="text-[var(--muted)]">No hay establecimientos registrados</p>
        </div>
      ) : (
        <div className="card overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-[var(--card-border)] bg-slate-50">
                <th className="text-left px-4 py-3 font-medium text-[var(--muted)]">Nombre</th>
                <th className="text-left px-4 py-3 font-medium text-[var(--muted)] hidden sm:table-cell">RUC</th>
                <th className="text-left px-4 py-3 font-medium text-[var(--muted)] hidden md:table-cell">Tipología</th>
                <th className="text-left px-4 py-3 font-medium text-[var(--muted)] hidden lg:table-cell">Responsable</th>
                <th className="text-left px-4 py-3 font-medium text-[var(--muted)]">Certificado</th>
                <th className="text-left px-4 py-3 font-medium text-[var(--muted)]">Acciones</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[var(--card-border)]">
              {establecimientos.map((est) => (
                <tr
                  key={est.id}
                  className="hover:bg-slate-50 cursor-pointer"
                  onClick={() => fetchEquiposForEstablecimiento(est)}
                >
                  <td className="px-4 py-3 font-medium">{est.nombre_comercial}</td>
                  <td className="px-4 py-3 text-[var(--muted)] font-mono text-xs hidden sm:table-cell">{est.ruc}</td>
                  <td className="px-4 py-3 hidden md:table-cell">{est.tipologia}</td>
                  <td className="px-4 py-3 text-[var(--muted)] hidden lg:table-cell">{est.responsable_tecnico_cedula}</td>
                  <td className="px-4 py-3">
                    {est.url_certificado_acess ? (
                      <FileViewer path={est.url_certificado_acess} establecimientoId={est.id} onDeleted={() => fetchEstablecimientos()} />
                    ) : (
                      <span className="text-[var(--muted)]">—</span>
                    )}
                    <div className="mt-2">
                      <button
                        className="text-xs btn-secondary"
                        onClick={async (event) => {
                          event.stopPropagation()
                          if (!isAdmin) return
                          const input = document.createElement('input')
                          input.type = 'file'
                          input.accept = 'application/pdf,image/*,application/vnd.openxmlformats-officedocument.wordprocessingml.document,application/msword'
                          input.onchange = async () => {
                            const file = input.files?.[0]
                            if (!file) return
                            try {
                              setUploadingId(est.id)
                              const maxBytes = 10 * 1024 * 1024
                              if (file.size > maxBytes) throw new Error('Archivo demasiado grande. Máx 10MB')
                              if (est.url_certificado_acess) await removeFileFromBucket('manuales', est.url_certificado_acess)
                              const filename = `${Date.now()}_${file.name.replace(/[^a-zA-Z0-9.\-_]/g, '_')}`
                              const path = `certificados/${est.id}/${filename}`
                              const { error: upErr } = await uploadFileToBucket(['certificados'], path, file)
                              if (upErr) throw upErr
                              const { error: updErr } = await supabase.from('establecimientos').update({ url_certificado_acess: path }).eq('id', est.id)
                              if (updErr) throw updErr
                              fetchEstablecimientos()
                              if (selectedEstablecimiento?.id === est.id) {
                                setSelectedEstablecimiento({ ...est, url_certificado_acess: path })
                              }
                            } catch (err) {
                              alert(err instanceof Error ? err.message : 'Error al subir certificado')
                            } finally {
                              setUploadingId(null)
                            }
                          }
                          input.click()
                        }}
                      >
                        Subir / Reemplazar
                      </button>
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <button
                      className="text-xs text-red-600 hover:text-red-800 font-medium"
                      onClick={async (event) => {
                        event.stopPropagation()
                        if (!isAdmin) return
                        if (!confirm(`¿Está seguro de eliminar el establecimiento "${est.nombre_comercial}"? Esta acción también eliminará todos los equipos y eventos de mantenimiento asociados.`)) {
                          return
                        }
                        try {
                          const { error } = await supabase.from('establecimientos').delete().eq('id', est.id)
                          if (error) throw error
                          fetchEstablecimientos()
                          setSelectedEstablecimiento(null)
                          setEquipos([])
                        } catch (err) {
                          alert(err instanceof Error ? err.message : 'Error al eliminar establecimiento')
                        }
                      }}
                    >
                      Eliminar
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {selectedEstablecimiento && (
        <div className="card p-6">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-4">
            <div>
              <h2 className="text-xl font-semibold">Dispositivos en {selectedEstablecimiento.nombre_comercial}</h2>
              <p className="text-sm text-[var(--muted)]">{equipos.length} equipos asociados</p>
            </div>
            <button onClick={() => setSelectedEstablecimiento(null)} className="btn-secondary text-sm">
              Cerrar detalles
            </button>
          </div>

          {detailError && <div className="alert-error">{detailError}</div>}

          {calibrationAlerts.length > 0 ? (
            <div className="mb-4 grid gap-3 md:grid-cols-2">
              {calibrationAlerts.map((alert, index) => (
                <div
                  key={`${alert?.equipo}-${index}`}
                  className={`rounded-lg border p-3 text-sm ${
                    alert?.tone === 'danger'
                      ? 'border-red-300 bg-red-50 text-red-700'
                      : alert?.tone === 'warning'
                      ? 'border-amber-300 bg-amber-50 text-amber-700'
                      : 'border-sky-300 bg-sky-50 text-sky-700'
                  }`}
                >
                  <p className="font-semibold">{alert?.equipo}</p>
                  <p className="mt-1">{alert?.codigo}</p>
                  <p className="mt-1">Próxima calibración {alert?.label}</p>
                </div>
              ))}
            </div>
          ) : (
            <div className="mb-4 rounded-lg border border-[var(--card-border)] bg-slate-50 p-3 text-sm text-[var(--muted)]">
              No hay calibraciones próximas en los próximos 30 días.
            </div>
          )}

          {detailLoading ? (
            <div className="flex items-center justify-center py-10">
              <div className="w-6 h-6 border-2 border-[var(--primary)] border-t-transparent rounded-full animate-spin" />
            </div>
          ) : equipos.length === 0 ? (
            <div className="card p-8 text-center">
              <p className="text-[var(--muted)]">No hay equipos registrados en este establecimiento.</p>
            </div>
          ) : (
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
                  {equipos.map((equipo) => (
                    <tr key={equipo.id} className="hover:bg-slate-50">
                      <td className="px-4 py-3 font-medium">{equipo.nombre_dispositivo}</td>
                      <td className="px-4 py-3 text-[var(--muted)] font-mono text-xs hidden sm:table-cell">{equipo.codigo_unico}</td>
                      <td className="px-4 py-3 hidden md:table-cell">{equipo.marca} / {equipo.modelo}</td>
                      <td className="px-4 py-3"><span className="badge badge-establecimiento">{equipo.estado_final}</span></td>
                      <td className="px-4 py-3 text-xs text-[var(--muted)] hidden lg:table-cell">
                        {equipo.fecha_proxima_calibracion ? new Date(equipo.fecha_proxima_calibracion).toLocaleDateString('es-EC') : '—'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
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
                {selectedCertificate && <p className="text-xs text-[var(--muted)] mt-1">Seleccionado: {selectedCertificate.name}</p>}
              </div>
              <div className="flex justify-end gap-3 pt-2">
                <button type="button" onClick={() => setShowModal(false)} className="btn-secondary">
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
