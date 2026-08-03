/**
 * useMantenimientosData Hook - Feature-First Migration
 * PHASE 7 - EPIC 5a
 */

import { useState, useCallback } from 'react'
import type {
  EventoMantenimiento,
  Equipo,
  Establecimiento,
  MantenimientoFormData,
} from '../types/mantenimientos.types'
import { EMPTY_MANTENIMIENTO_FORM } from '../types/mantenimientos.types'
import { loadMantenimientos, saveMantenimiento, deleteMantenimiento } from '../services/mantenimientos.service'

export interface UseMantenimientosDataReturn {
  eventos: EventoMantenimiento[]
  equipos: Equipo[]
  establecimientos: Establecimiento[]
  loading: boolean
  error: string
  selectedEstablecimientoId: string
  showModal: boolean
  saving: boolean
  editingId: number | null
  form: MantenimientoFormData
  selectedReportFile: File | null
  loadData: () => Promise<void>
  setSelectedEstablecimientoId: (v: string) => void
  openCreate: (defaultEstablecimientoId?: string) => void
  openEdit: (ev: EventoMantenimiento) => void
  setForm: (f: MantenimientoFormData) => void
  setSelectedReportFile: (f: File | null) => void
  handleSubmit: (e: React.FormEvent) => Promise<void>
  handleDelete: (id: number) => Promise<void>
  closeModal: () => void
  filteredEventos: EventoMantenimiento[]
}

export function useMantenimientosData(
  isAdmin: boolean,
  establecimientoId: number | undefined
): UseMantenimientosDataReturn {
  const [eventos, setEventos] = useState<EventoMantenimiento[]>([])
  const [equipos, setEquipos] = useState<Equipo[]>([])
  const [establecimientos, setEstablecimientos] = useState<Establecimiento[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [selectedEstablecimientoId, setSelectedEstablecimientoId] = useState('')
  const [showModal, setShowModal] = useState(false)
  const [saving, setSaving] = useState(false)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [form, setForm] = useState<MantenimientoFormData>(EMPTY_MANTENIMIENTO_FORM)
  const [selectedReportFile, setSelectedReportFile] = useState<File | null>(null)

  const loadData = useCallback(async () => {
    const result = await loadMantenimientos(isAdmin, establecimientoId)
    setEventos(result.eventos)
    setEquipos(result.equipos)
    setEstablecimientos(result.establecimientos)
    setError(result.error)
    setLoading(false)

    if (!isAdmin && establecimientoId) {
      setSelectedEstablecimientoId(String(establecimientoId))
    }
  }, [isAdmin, establecimientoId])

  const openCreate = useCallback((defaultEstablecimientoId?: string) => {
    setEditingId(null)
    setSelectedReportFile(null)
    setForm({
      ...EMPTY_MANTENIMIENTO_FORM,
      establecimiento_id: defaultEstablecimientoId || selectedEstablecimientoId || '',
      equipo_id: '',
    })
    setShowModal(true)
  }, [selectedEstablecimientoId])

  const openEdit = useCallback((ev: EventoMantenimiento) => {
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
  }, [equipos])

  const handleSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault()
    if (!isAdmin) return
    setSaving(true)

    const result = await saveMantenimiento(form, editingId, selectedReportFile, eventos)
    if (result.error) setError(result.error)

    setSaving(false)
    setSelectedReportFile(null)
    if (!result.error) {
      setShowModal(false)
      loadData()
    }
  }, [isAdmin, form, editingId, selectedReportFile, eventos, loadData])

  const handleDelete = useCallback(async (id: number) => {
    if (!isAdmin || !confirm('¿Eliminar este evento?')) return
    const result = await deleteMantenimiento(id)
    if (result.error) setError(result.error)
    else loadData()
  }, [isAdmin, loadData])

  const closeModal = useCallback(() => {
    setShowModal(false)
    setSelectedReportFile(null)
  }, [])

  const filteredEventos = selectedEstablecimientoId
    ? eventos.filter(
        (evento) =>
          String(evento.equipos?.establecimiento_id ?? '') === selectedEstablecimientoId
      )
    : eventos

  return {
    eventos,
    equipos,
    establecimientos,
    loading,
    error,
    selectedEstablecimientoId,
    showModal,
    saving,
    editingId,
    form,
    selectedReportFile,
    loadData,
    setSelectedEstablecimientoId,
    openCreate,
    openEdit,
    setForm,
    setSelectedReportFile,
    handleSubmit,
    handleDelete,
    closeModal,
    filteredEventos,
  }
}
