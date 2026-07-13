'use client'

import { useState, useEffect, Fragment } from 'react'
import { useAuth } from '@/hooks/useAuth'
import { supabase } from '@/lib/supabase'
import { fetchEquipos, fetchEstablecimientos, type Equipo, type Establecimiento } from '@/lib/queries'
import { Modal } from '@/components/ui/Modal'
import { ReadOnlyBanner } from '@/components/ui/ReadOnlyBanner'
import { uploadFileToBucket, getSignedUrlForPath, removeFileFromBucket } from '@/lib/storage'
import FileViewer from '@/components/ui/FileViewer'

const emptyEquipo = {
  establecimiento_id: '',
  codigo_unico: '',
  nombre_dispositivo: '',
  marca: '',
  modelo: '',
  numero_serie: '',
  area_ubicacion: '',
  criticidad: 'media',
  estado_final: 'activo',
  fecha_proxima_calibracion: '',
  imp: '',
  frecuencia_mantenimiento: '',
  fecha_ultimo_mantenimiento: '',
}

function estadoBadge(estado: string) {
  const map: Record<string, string> = {
    Operativo: 'badge-activo',
    Pendiente: 'badge-mantenimiento',
    Inactivo: 'badge-inactivo',
  }
  return map[estado] || 'badge-mantenimiento'
}

function ManualViewer({ path, establecimientoId }: { path: string; establecimientoId: number }) {
  const { profile, isAdmin } = useAuth()
  const [url, setUrl] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    let mounted = true
    const load = async () => {
      if (!path) return
      // Solo admin o usuario del establecimiento pueden obtener signed URL
      if (!isAdmin && profile?.establecimiento_id !== establecimientoId) return
      setLoading(true)
      const { signedURL, error } = await getSignedUrlForPath(['manuales', 'certificados'], path, 300)
      if (!mounted) return
      if (!error && signedURL) setUrl(signedURL)
      setLoading(false)
    }
    load()
    return () => { mounted = false }
  }, [path, isAdmin, profile, establecimientoId])

  if (!path) return <span>—</span>
  if (!isAdmin && profile?.establecimiento_id !== establecimientoId) return <span>Manual disponible (sin acceso)</span>
  if (loading) return <span>Cargando...</span>
  if (!url) return <span>No disponible</span>

  return (
    <div className="flex items-center gap-2">
      <a href={url} target="_blank" rel="noreferrer" className="text-[var(--primary)] hover:underline">Abrir manual</a>
    </div>
  )
}

export default function EquiposPage() {
  const { profile, isAdmin, establecimientoId } = useAuth()
  const [equipos, setEquipos] = useState<Equipo[]>([])
  const [establecimientos, setEstablecimientos] = useState<Establecimiento[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [search, setSearch] = useState('')
  const [selectedEstablecimientoId, setSelectedEstablecimientoId] = useState('')
  const [showModal, setShowModal] = useState(false)
  const [saving, setSaving] = useState(false)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [form, setForm] = useState(emptyEquipo)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [expandedId, setExpandedId] = useState<number | null>(null)

  useEffect(() => {
    if (profile) loadData()
  }, [profile, isAdmin, establecimientoId])

  const loadData = async () => {
    try {
      setLoading(true)
      setError('')
      const [eqRes, estRes] = await Promise.all([
        fetchEquipos(isAdmin, establecimientoId),
        isAdmin ? fetchEstablecimientos(true, null) : Promise.resolve({ data: [], error: null }),
      ])
      if (eqRes.error) throw eqRes.error
      setEquipos(eqRes.data || [])
      if (estRes.data) setEstablecimientos(estRes.data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al cargar equipos')
    } finally {
      setLoading(false)
    }
  }

  const openCreate = () => {
    setEditingId(null)
    setForm({ ...emptyEquipo, establecimiento_id: establecimientos[0]?.id?.toString() || '' })
    setShowModal(true)
  }

  const openEdit = (eq: Equipo) => {
    setEditingId(eq.id)
    setForm({
      establecimiento_id: String(eq.establecimiento_id),
      codigo_unico: eq.codigo_unico,
      nombre_dispositivo: eq.nombre_dispositivo,
      marca: eq.marca,
      modelo: eq.modelo,
      numero_serie: eq.numero_serie,
      area_ubicacion: eq.area_ubicacion,
      criticidad: eq.criticidad,
      estado_final: eq.estado_final,
      fecha_proxima_calibracion: eq.fecha_proxima_calibracion?.split('T')[0] || '',
      imp: eq.imp != null ? String(eq.imp) : '',
      frecuencia_mantenimiento: eq.frecuencia_mantenimiento != null ? String(eq.frecuencia_mantenimiento) : '',
      fecha_ultimo_mantenimiento: eq.fecha_ultimo_mantenimiento?.split('T')[0] || '',
    })
    setShowModal(true)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!isAdmin) return
    setSaving(true)
    setError('')

    const payload = {
      establecimiento_id: Number(form.establecimiento_id),
      codigo_unico: form.codigo_unico,
      nombre_dispositivo: form.nombre_dispositivo,
      marca: form.marca,
      modelo: form.modelo,
      numero_serie: form.numero_serie,
      area_ubicacion: form.area_ubicacion,
      criticidad: form.criticidad,
      estado_final: form.estado_final,
      fecha_proxima_calibracion: form.fecha_proxima_calibracion || null,
      imp: form.imp ? Number(form.imp) : null,
      frecuencia_mantenimiento: form.frecuencia_mantenimiento ? Number(form.frecuencia_mantenimiento) : null,
      fecha_ultimo_mantenimiento: form.fecha_ultimo_mantenimiento || null,
    }

    try {
      let equipoId = editingId
      if (editingId) {
        const { error } = await supabase.from('equipos').update(payload).eq('id', editingId)
        if (error) throw error
      } else {
        const { data: newEq, error } = await supabase.from('equipos').insert(payload).select().single()
        if (error) throw error
        equipoId = newEq.id
      }

      // Si hay archivo seleccionado, subirlo y actualizar la fila
      if (selectedFile && equipoId) {
        // tamaño máximo 10MB
        const maxBytes = 10 * 1024 * 1024
        if (selectedFile.size > maxBytes) throw new Error('Archivo demasiado grande. Máx 10MB')
        // eliminar archivo previo si existe
        const { data: old } = await supabase.from('equipos').select('url_manual_tecnico').eq('id', equipoId).single()
        const oldPath = old?.url_manual_tecnico
        if (oldPath) {
          await removeFileFromBucket('manuales', oldPath)
        }

        const filename = `${Date.now()}_${selectedFile.name.replace(/[^a-zA-Z0-9.\-_]/g, '_')}`
        const path = `manuales/${payload.establecimiento_id}/${equipoId}_${filename}`
        const { error: upErr } = await uploadFileToBucket('manuales', path, selectedFile)
        if (upErr) throw upErr
        const { error: updErr } = await supabase.from('equipos').update({ url_manual_tecnico: path }).eq('id', equipoId)
        if (updErr) throw updErr
      }
      setShowModal(false)
      loadData()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al guardar equipo')
    } finally {
      setSaving(false)
      setSelectedFile(null)
    }
  }

  const handleDelete = async (id: number) => {
    if (!isAdmin || !confirm('¿Eliminar este equipo?')) return
    const { error } = await supabase.from('equipos').delete().eq('id', id)
    if (error) setError(error.message)
    else loadData()
  }

  const filtered = equipos.filter((e) => {
    const matchesText =
      e.nombre_dispositivo.toLowerCase().includes(search.toLowerCase()) ||
      e.codigo_unico.toLowerCase().includes(search.toLowerCase()) ||
      e.marca.toLowerCase().includes(search.toLowerCase())

    const matchesEstablishment = !selectedEstablecimientoId || e.establecimiento_id === Number(selectedEstablecimientoId)

    return matchesText && matchesEstablishment
  })

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
            {isAdmin ? `${equipos.length} equipos en todos los establecimientos` : `${equipos.length} equipos de su establecimiento`}
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
                <option key={est.id} value={est.id}>{est.nombre_comercial}</option>
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
            <button onClick={openCreate} className="btn-primary whitespace-nowrap">+ Nuevo Equipo</button>
          )}
        </div>
      </div>

      {error && <div className="alert-error">{error}</div>}

      {filtered.length === 0 ? (
        <div className="card p-12 text-center">
          <p className="text-[var(--muted)]">{search ? 'Sin resultados' : 'No hay equipos registrados'}</p>
        </div>
      ) : (
        <div className="card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-[var(--card-border)] bg-slate-50">
                  <th className="text-left px-4 py-3 font-medium text-[var(--muted)]">Equipo</th>
                  {isAdmin && <th className="text-left px-4 py-3 font-medium text-[var(--muted)] hidden md:table-cell">Establecimiento</th>}
                  <th className="text-left px-4 py-3 font-medium text-[var(--muted)] hidden sm:table-cell">Código</th>
                  <th className="text-left px-4 py-3 font-medium text-[var(--muted)] hidden lg:table-cell">Criticidad</th>
                  <th className="text-left px-4 py-3 font-medium text-[var(--muted)]">Estado</th>
                  <th className="text-left px-4 py-3 font-medium text-[var(--muted)] hidden lg:table-cell">Próx. calibración</th>
                  {isAdmin && <th className="text-right px-4 py-3 font-medium text-[var(--muted)]">Acciones</th>}
                </tr>
              </thead>
              <tbody className="divide-y divide-[var(--card-border)]">
                {filtered.map((equipo) => (
                  <Fragment key={equipo.id}>
                    <tr
                      className="hover:bg-slate-50 transition-colors cursor-pointer"
                      onClick={() => setExpandedId(expandedId === equipo.id ? null : equipo.id)}
                    >
                      <td className="px-4 py-3">
                        <p className="font-medium">{equipo.nombre_dispositivo}</p>
                        <p className="text-xs text-[var(--muted)]">{equipo.marca} / {equipo.modelo}</p>
                      </td>
                      {isAdmin && (
                        <td className="px-4 py-3 text-[var(--muted)] hidden md:table-cell">
                          {equipo.establecimientos?.nombre_comercial || `#${equipo.establecimiento_id}`}
                        </td>
                      )}
                      <td className="px-4 py-3 font-mono text-xs hidden sm:table-cell">{equipo.codigo_unico}</td>
                      <td className="px-4 py-3 hidden lg:table-cell">
                        <span className="badge badge-establecimiento">{equipo.criticidad}</span>
                      </td>
                      <td className="px-4 py-3">
                        <span className={`badge ${estadoBadge(equipo.estado_final)}`}>{equipo.estado_final}</span>
                      </td>
                      <td className="px-4 py-3 text-xs text-[var(--muted)] hidden lg:table-cell">
                        {equipo.fecha_proxima_calibracion
                          ? new Date(equipo.fecha_proxima_calibracion).toLocaleDateString('es-EC')
                          : '—'}
                      </td>
                      {isAdmin && (
                        <td className="px-4 py-3 text-right" onClick={(e) => e.stopPropagation()}>
                          <button onClick={() => openEdit(equipo)} className="text-xs text-[var(--primary)] hover:underline mr-3">Editar</button>
                          <button onClick={() => handleDelete(equipo.id)} className="text-xs text-[var(--danger)] hover:underline">Eliminar</button>
                        </td>
                      )}
                    </tr>
                    {expandedId === equipo.id && (
                      <tr className="bg-slate-50">
                        <td colSpan={isAdmin ? 7 : 5} className="px-4 py-3">
                          <dl className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
                            <div><dt className="text-[var(--muted)]">Serie</dt><dd className="font-medium">{equipo.numero_serie}</dd></div>
                            <div><dt className="text-[var(--muted)]">Área</dt><dd className="font-medium">{equipo.area_ubicacion}</dd></div>
                            <div><dt className="text-[var(--muted)]">IMP</dt><dd className="font-medium">{equipo.imp ?? '—'}</dd></div>
                            <div><dt className="text-[var(--muted)]">RUC Est.</dt><dd className="font-medium">{equipo.establecimientos?.ruc || '—'}</dd></div>
                            <div>
                              <dt className="text-[var(--muted)]">Manual</dt>
                              <dd className="font-medium">
                                {equipo.url_manual_tecnico ? (
                                  <FileViewer path={equipo.url_manual_tecnico} establecimientoId={equipo.establecimiento_id} onDeleted={() => loadData()} />
                                ) : (
                                  '—'
                                )}
                              </dd>
                            </div>
                            <div className="sm:col-span-4">
                              <dt className="text-[var(--muted)]">Historial de mantenimiento</dt>
                              <dd className="font-medium mt-1 space-y-2">
                                {(() => {
                                  const mantenimientos = [...(equipo.eventos_mantenimiento || [])]
                                    .sort((a, b) => new Date(b.fecha_ejecucion).getTime() - new Date(a.fecha_ejecucion).getTime())

                                  if (mantenimientos.length === 0) {
                                    return <span className="text-[var(--muted)]">Sin registros</span>
                                  }

                                  return mantenimientos.slice(0, 5).map((m) => (
                                    <div key={m.id} className="rounded border border-[var(--card-border)] bg-white px-3 py-2">
                                      <div className="flex flex-wrap items-center justify-between gap-2">
                                        <span className="font-medium">{m.tipo_evento}</span>
                                        <span className="text-[11px] text-[var(--muted)]">
                                          {new Date(m.fecha_ejecucion).toLocaleDateString('es-EC')}
                                        </span>
                                      </div>
                                      <p className="text-xs text-[var(--muted)] mt-1">{m.descripcion_trabajo || 'Sin descripción'}</p>
                                      <p className="text-[11px] text-[var(--muted)] mt-1">Estado: {m.estado_final}</p>
                                    </div>
                                  ))
                                })()}
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
        <Modal open={showModal} onClose={() => setShowModal(false)} title={editingId ? 'Editar Equipo' : 'Nuevo Equipo'} wide>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="sm:col-span-2">
                <label className="block text-sm font-medium mb-1">Establecimiento</label>
                <select className="input-field" required value={form.establecimiento_id} onChange={(e) => setForm({ ...form, establecimiento_id: e.target.value })}>
                  <option value="">Seleccionar...</option>
                  {establecimientos.map((e) => (
                    <option key={e.id} value={e.id}>{e.nombre_comercial} ({e.ruc})</option>
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
                  <input className="input-field" required value={form[key as keyof typeof form]} onChange={(e) => setForm({ ...form, [key]: e.target.value })} />
                </div>
              ))}
              <div>
                <label className="block text-sm font-medium mb-1">Criticidad</label>
                <select className="input-field" value={form.criticidad} onChange={(e) => setForm({ ...form, criticidad: e.target.value })}>
                  <option value="baja">Baja</option>
                  <option value="media">Media</option>
                  <option value="alta">Alta</option>
                  <option value="critica">Crítica</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Estado</label>
                <select className="input-field" value={form.estado_final} onChange={(e) => setForm({ ...form, estado_final: e.target.value })}>
                  <option value="Operativo">Activo</option>
                  <option value="Pendiente">Mantenimiento</option>
                  <option value="Inactivo">Inactivo</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Próximo mantenimiento</label>
                <input type="date" className="input-field" value={form.fecha_proxima_calibracion} onChange={(e) => setForm({ ...form, fecha_proxima_calibracion: e.target.value })} />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">IMP</label>
                <input type="number" step="0.01" className="input-field" value={form.imp} onChange={(e) => setForm({ ...form, imp: e.target.value })} />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Frecuencia mantenimiento (días)</label>
                <input type="number" className="input-field" value={form.frecuencia_mantenimiento} onChange={(e) => setForm({ ...form, frecuencia_mantenimiento: e.target.value })} placeholder="Según manual" />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Último mantenimiento</label>
                <input type="date" className="input-field" value={form.fecha_ultimo_mantenimiento} onChange={(e) => setForm({ ...form, fecha_ultimo_mantenimiento: e.target.value })} />
              </div>
              <div className="sm:col-span-2">
                <label className="block text-sm font-medium mb-1">Manual técnico (pdf, jpg, docx)</label>
                <input type="file" accept="application/pdf,image/*,application/vnd.openxmlformats-officedocument.wordprocessingml.document,application/msword" className="w-full" onChange={(e) => setSelectedFile(e.target.files?.[0] ?? null)} />
                {selectedFile && <p className="text-xs text-[var(--muted)] mt-1">Seleccionado: {selectedFile.name}</p>}
              </div>
            </div>
            <div className="flex justify-end gap-3 pt-2">
              <button type="button" onClick={() => setShowModal(false)} className="btn-secondary">Cancelar</button>
              <button type="submit" disabled={saving} className="btn-primary">{saving ? 'Guardando...' : 'Guardar'}</button>
            </div>
          </form>
        </Modal>
      )}
    </div>
  )
}
