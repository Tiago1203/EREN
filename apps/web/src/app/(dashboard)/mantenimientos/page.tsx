'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '@/hooks/useAuth'
import { supabase } from '@/lib/supabase'
import { fetchEventos, fetchEquipos, fetchEstablecimientos, type EventoMantenimiento, type Equipo, type Establecimiento } from '@/lib/queries'
import { Modal } from '@/components/ui/Modal'
import { ReadOnlyBanner } from '@/components/ui/ReadOnlyBanner'
import { uploadFileToBucket, removeFileFromBucket } from '@/lib/storage'
import FileViewer from '@/components/ui/FileViewer'

const emptyEvento = {
  establecimiento_id: '',
  equipo_id: '',
  tipo_evento: '',
  fecha_ejecucion: new Date().toISOString().split('T')[0],
  ingeniero_responsable: '',
  descripcion_trabajo: '',
  repuestos_cambiados: '',
  error_porcentual: '',
  incertidumbre: '',
  estado_final: '',
}

export default function MantenimientosPage() {
  const { profile, isAdmin, establecimientoId } = useAuth()
  const [eventos, setEventos] = useState<EventoMantenimiento[]>([])
  const [equipos, setEquipos] = useState<Equipo[]>([])
  const [establecimientos, setEstablecimientos] = useState<Establecimiento[]>([])
  const [selectedEstablecimientoId, setSelectedEstablecimientoId] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [showModal, setShowModal] = useState(false)
  const [saving, setSaving] = useState(false)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [form, setForm] = useState(emptyEvento)
  const [selectedReportFile, setSelectedReportFile] = useState<File | null>(null)

  useEffect(() => {
    if (profile) loadData()
  }, [profile, isAdmin, establecimientoId])

  const loadData = async () => {
    try {
      setLoading(true)
      setError('')
      const [evRes, eqRes, estRes] = await Promise.all([
        fetchEventos(isAdmin, establecimientoId),
        fetchEquipos(isAdmin, establecimientoId),
        isAdmin ? fetchEstablecimientos(true, null) : Promise.resolve({ data: [], error: null }),
      ])
      if (evRes.error) throw evRes.error
      if (eqRes.error) throw eqRes.error
      const nextEventos = evRes.data || []
      const nextEquipos = eqRes.data || []
      setEventos(nextEventos)
      setEquipos(nextEquipos)
      setEstablecimientos(estRes.data || [])
      if (!isAdmin) {
        setSelectedEstablecimientoId(establecimientoId ? String(establecimientoId) : '')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al cargar mantenimientos')
    } finally {
      setLoading(false)
    }
  }

  const openCreate = () => {
    setEditingId(null)
    setSelectedReportFile(null)
    setForm({ ...emptyEvento, establecimiento_id: selectedEstablecimientoId || '', equipo_id: '' })
    setShowModal(true)
  }

  const openEdit = (ev: EventoMantenimiento) => {
    const equipo = equipos.find((item) => item.id === ev.equipo_id)
    setEditingId(ev.id)
    setSelectedReportFile(null)
    setForm({
      establecimiento_id: equipo?.establecimiento_id ? String(equipo.establecimiento_id) : '',
      equipo_id: String(ev.equipo_id),
      tipo_evento: ev.tipo_evento,
      fecha_ejecucion: ev.fecha_ejecucion?.split('T')[0] || '',
      ingeniero_responsable: ev.ingeniero_responsable,
      descripcion_trabajo: ev.descripcion_trabajo,
      repuestos_cambiados: ev.repuestos_cambiados || '',
      error_porcentual: ev.error_porcentual != null ? String(ev.error_porcentual) : '',
      incertidumbre: ev.incertidumbre != null ? String(ev.incertidumbre) : '',
      estado_final: ev.estado_final,
    })
    setShowModal(true)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!isAdmin) return
    setSaving(true)

    const payload = {
      equipo_id: Number(form.equipo_id),
      tipo_evento: form.tipo_evento,
      fecha_ejecucion: form.fecha_ejecucion,
      ingeniero_responsable: form.ingeniero_responsable,
      descripcion_trabajo: form.descripcion_trabajo,
      repuestos_cambiados: form.repuestos_cambiados || null,
      error_porcentual: form.error_porcentual ? Number(form.error_porcentual) : null,
      incertidumbre: form.incertidumbre ? Number(form.incertidumbre) : null,
      estado_final: form.estado_final,
    }

    try {
      let eventoId = editingId
      if (editingId) {
        const { error } = await supabase.from('eventos_mantenimiento').update(payload).eq('id', editingId)
        if (error) throw error
      } else {
        const { data, error } = await supabase.from('eventos_mantenimiento').insert(payload).select('id').single()
        if (error) throw error
        eventoId = data?.id ?? null
      }

      if (selectedReportFile && eventoId) {
        const oldPath = (eventos.find((item) => item.id === eventoId)?.url_informe_mantenimiento) || null
        if (oldPath) {
          await removeFileFromBucket(['informes', 'certificados', 'manuales'], oldPath)
        }

        const filename = `${Date.now()}_${selectedReportFile.name.replace(/[^a-zA-Z0-9.\-_]/g, '_')}`
        const path = `informes/${eventoId}/${filename}`
        const { error: upErr } = await uploadFileToBucket(['informes'], path, selectedReportFile)
        if (upErr) throw upErr

        const { error: updateErr } = await supabase.from('eventos_mantenimiento').update({ url_informe_mantenimiento: path }).eq('id', eventoId)
        if (updateErr) throw updateErr
      }

      setShowModal(false)
      setSelectedReportFile(null)
      loadData()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al guardar')
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async (id: number) => {
    if (!isAdmin || !confirm('¿Eliminar este evento?')) return
    const { error } = await supabase.from('eventos_mantenimiento').delete().eq('id', id)
    if (error) setError(error.message)
    else loadData()
  }

  const filteredEventos = selectedEstablecimientoId
    ? eventos.filter((evento) => String(evento.equipos?.establecimiento_id ?? '') === selectedEstablecimientoId)
    : eventos

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
            {filteredEventos.length} eventos {isAdmin ? 'en el sistema' : 'de su establecimiento'}
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
                <option key={est.id} value={String(est.id)}>{est.nombre_comercial} ({est.ruc})</option>
              ))}
            </select>
          )}
          {isAdmin && (
            <button onClick={openCreate} className="btn-primary">+ Nuevo Mantenimiento</button>
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
                      {new Date(evento.fecha_ejecucion).toLocaleDateString('es-EC', { year: 'numeric', month: 'long', day: 'numeric' })}
                    </span>
                    {isAdmin && evento.equipos?.establecimientos?.nombre_comercial && (
                      <span className="text-xs text-[var(--muted)]">• {evento.equipos.establecimientos.nombre_comercial}</span>
                    )}
                  </div>
                  <h3 className="font-medium mt-2">
                    {evento.equipos?.nombre_dispositivo || `Equipo #${evento.equipo_id}`}
                  </h3>
                  {evento.equipos?.codigo_unico && (
                    <p className="text-xs text-[var(--muted)] font-mono">{evento.equipos.codigo_unico}</p>
                  )}
                  <p className="text-sm text-[var(--muted)] mt-2">{evento.descripcion_trabajo}</p>
                  <div className="flex flex-wrap gap-4 mt-2 text-xs text-[var(--muted)]">
                    <span>Ingeniero: {evento.ingeniero_responsable}</span>
                    {evento.error_porcentual != null && <span>Error: {evento.error_porcentual}%</span>}
                    {evento.incertidumbre != null && <span>Incertidumbre: {evento.incertidumbre}</span>}
                    {evento.repuestos_cambiados && <span>Repuestos: {evento.repuestos_cambiados}</span>}
                  </div>
                  <div className="mt-3">
                    <p className="text-xs font-medium text-[var(--muted)] mb-1">Informe de mantenimiento</p>
                    {evento.url_informe_mantenimiento ? (
                      <FileViewer path={evento.url_informe_mantenimiento} establecimientoId={evento.equipos?.establecimiento_id ?? 0} onDeleted={() => loadData()} />
                    ) : (
                      <span className="text-xs text-[var(--muted)]">Sin informe adjunto</span>
                    )}
                  </div>
                </div>
                <div className="flex items-start gap-2 self-start">
                  <span className={`badge ${evento.estado_final === 'Operativo' ? 'badge-activo' : 'badge-mantenimiento'}`}> 
                    {evento.estado_final}
                  </span>
                  {isAdmin && (
                    <>
                      <button onClick={() => openEdit(evento)} className="text-xs text-[var(--primary)] hover:underline">Editar</button>
                      <button onClick={() => handleDelete(evento.id)} className="text-xs text-[var(--danger)] hover:underline">Eliminar</button>
                    </>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {isAdmin && (
        <Modal open={showModal} onClose={() => setShowModal(false)} title={editingId ? 'Editar Mantenimiento' : 'Nuevo Mantenimiento'} wide>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="sm:col-span-2">
                <label className="block text-sm font-medium mb-1">Establecimiento</label>
                <select
                  className="input-field"
                  required
                  value={form.establecimiento_id}
                  onChange={(e) => {
                    const nextEstablecimientoId = e.target.value
                    setForm({ ...form, establecimiento_id: nextEstablecimientoId, equipo_id: '' })
                  }}
                >
                  <option value="">Seleccionar establecimiento...</option>
                  {establecimientos.map((est) => (
                    <option key={est.id} value={est.id}>{est.nombre_comercial} ({est.ruc})</option>
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
                  <option value="">{form.establecimiento_id ? 'Seleccionar equipo...' : 'Primero elige un establecimiento'}</option>
                  {equipos
                    .filter((eq) => !form.establecimiento_id || String(eq.establecimiento_id) === form.establecimiento_id)
                    .map((eq) => (
                      <option key={eq.id} value={eq.id}>
                        {eq.nombre_dispositivo} ({eq.codigo_unico}) — {eq.establecimientos?.nombre_comercial}
                      </option>
                    ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Tipo de evento</label>
                <select className="input-field" value={form.tipo_evento} onChange={(e) => setForm({ ...form, tipo_evento: e.target.value })}>
                  <option value="Preventivo">Preventivo</option>
                  <option value="Correctivo">Correctivo</option>
                  <option value="Calibración">Calibración</option>
                  <option value="Predictivo">Predictivo</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Fecha ejecución</label>
                <input type="date" className="input-field" required value={form.fecha_ejecucion} onChange={(e) => setForm({ ...form, fecha_ejecucion: e.target.value })} />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Ingeniero responsable</label>
                <input className="input-field" required value={form.ingeniero_responsable} onChange={(e) => setForm({ ...form, ingeniero_responsable: e.target.value })} />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Estado final</label>
                <select className="input-field" value={form.estado_final} onChange={(e) => setForm({ ...form, estado_final: e.target.value })}>
                  <option value="Inactivo">Inactivo</option>
                  <option value="Pendiente">Pendiente</option>      
                  <option value="Operativo">Operativo</option>
                </select>
              </div>
              <div className="sm:col-span-2">
                <label className="block text-sm font-medium mb-1">Descripción del trabajo</label>
                <textarea className="input-field" rows={3} required value={form.descripcion_trabajo} onChange={(e) => setForm({ ...form, descripcion_trabajo: e.target.value })} />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Error porcentual (%)</label>
                <input type="number" step="0.01" className="input-field" value={form.error_porcentual} onChange={(e) => setForm({ ...form, error_porcentual: e.target.value })} />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Incertidumbre</label>
                <input type="number" step="0.01" className="input-field" value={form.incertidumbre} onChange={(e) => setForm({ ...form, incertidumbre: e.target.value })} />
              </div>
              <div className="sm:col-span-2">
                <label className="block text-sm font-medium mb-1">Repuestos cambiados</label>
                <input className="input-field" value={form.repuestos_cambiados} onChange={(e) => setForm({ ...form, repuestos_cambiados: e.target.value })} />
              </div>
              <div className="sm:col-span-2">
                <label className="block text-sm font-medium mb-1">Informe de mantenimiento (PDF)</label>
                <input
                  type="file"
                  accept="application/pdf"
                  className="w-full"
                  onChange={(e) => setSelectedReportFile(e.target.files?.[0] ?? null)}
                />
                {selectedReportFile && <p className="text-xs text-[var(--muted)] mt-1">Seleccionado: {selectedReportFile.name}</p>}
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
