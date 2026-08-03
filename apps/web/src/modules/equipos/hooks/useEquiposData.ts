/**
 * useEquiposData Hook - Feature-First Migration
 * PHASE 7 - EPIC 5a
 */

import { useState, useCallback } from 'react'
import type { Equipo, Establecimiento, EquipoFormData } from '../types/equipos.types'
import { EMPTY_EQUIPO_FORM } from '../types/equipos.types'
import {
  loadEquipos,
  saveEquipo,
  deleteEquipo,
} from '../services/equipos.service'

export interface UseEquiposDataReturn {
  equipos: Equipo[]
  establecimientos: Establecimiento[]
  loading: boolean
  error: string
  search: string
  selectedEstablecimientoId: string
  showModal: boolean
  saving: boolean
  editingId: number | null
  form: EquipoFormData
  selectedFile: File | null
  expandedId: number | null
  loadData: () => Promise<void>
  setSearch: (v: string) => void
  setSelectedEstablecimientoId: (v: string) => void
  openCreate: (defaultEstablecimientoId?: string) => void
  openEdit: (eq: Equipo) => void
  setForm: (f: EquipoFormData) => void
  setSelectedFile: (f: File | null) => void
  setExpandedId: (id: number | null) => void
  handleSubmit: (e: React.FormEvent) => Promise<void>
  handleDelete: (id: number) => Promise<void>
  closeModal: () => void
  filteredEquipos: Equipo[]
}

export function useEquiposData(
  isAdmin: boolean,
  establecimientoId: number | undefined
): UseEquiposDataReturn {
  const [equipos, setEquipos] = useState<Equipo[]>([])
  const [establecimientos, setEstablecimientos] = useState<Establecimiento[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [search, setSearch] = useState('')
  const [selectedEstablecimientoId, setSelectedEstablecimientoId] = useState('')
  const [showModal, setShowModal] = useState(false)
  const [saving, setSaving] = useState(false)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [form, setForm] = useState<EquipoFormData>(EMPTY_EQUIPO_FORM)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [expandedId, setExpandedId] = useState<number | null>(null)

  const loadData = useCallback(async () => {
    const result = await loadEquipos(isAdmin, establecimientoId)
    setEquipos(result.equipos)
    setEstablecimientos(result.establecimientos)
    setError(result.error)
    setLoading(false)
  }, [isAdmin, establecimientoId])

  const openCreate = useCallback((defaultEstablecimientoId?: string) => {
    setEditingId(null)
    setForm({
      ...EMPTY_EQUIPO_FORM,
      establecimiento_id: defaultEstablecimientoId || establecimientos[0]?.id?.toString() || '',
    })
    setSelectedFile(null)
    setShowModal(true)
  }, [establecimientos])

  const openEdit = useCallback((eq: Equipo) => {
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
      frecuencia_mantenimiento:
        eq.frecuencia_mantenimiento != null ? String(eq.frecuencia_mantenimiento) : '',
      fecha_ultimo_mantenimiento: eq.fecha_ultimo_mantenimiento?.split('T')[0] || '',
    })
    setSelectedFile(null)
    setShowModal(true)
  }, [])

  const handleSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault()
    if (!isAdmin) return
    setSaving(true)
    setError('')

    const result = await saveEquipo(form, editingId, selectedFile)
    if (result.error) setError(result.error)

    setSaving(false)
    setSelectedFile(null)
    if (!result.error) {
      setShowModal(false)
      loadData()
    }
  }, [isAdmin, form, editingId, selectedFile, loadData])

  const handleDelete = useCallback(async (id: number) => {
    if (!isAdmin || !confirm('¿Eliminar este equipo?')) return
    const result = await deleteEquipo(id)
    if (result.error) setError(result.error)
    else loadData()
  }, [isAdmin, loadData])

  const closeModal = useCallback(() => {
    setShowModal(false)
    setSelectedFile(null)
  }, [])

  const filteredEquipos = equipos.filter((e) => {
    const matchesText =
      e.nombre_dispositivo.toLowerCase().includes(search.toLowerCase()) ||
      e.codigo_unico.toLowerCase().includes(search.toLowerCase()) ||
      e.marca.toLowerCase().includes(search.toLowerCase())

    const matchesEstablishment =
      !selectedEstablecimientoId ||
      e.establecimiento_id === Number(selectedEstablecimientoId)

    return matchesText && matchesEstablishment
  })

  return {
    equipos,
    establecimientos,
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
    loadData,
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
    filteredEquipos,
  }
}
