/**
 * useEstablecimientosData Hook - Feature-First Migration
 * PHASE 7 - EPIC 5a
 */

import { useState, useCallback, useEffect } from 'react'
import type { Establecimiento, Equipo, EstablecimientoFormData } from '../types/establecimientos.types'
import { EMPTY_ESTABLECIMIENTO_FORM } from '../types/establecimientos.types'
import { loadEstablecimientoWithEquipos, loadEquiposByEstablecimiento, saveEstablecimiento } from '../services/establecimientos.service'

export interface CalibrationAlert {
  tone: 'danger' | 'warning' | 'info'
  label: string
}

export function getCalibrationAlert(date: string | null): CalibrationAlert | null {
  if (!date) return null
  const target = new Date(date)
  target.setHours(0, 0, 0, 0)
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const diffDays = Math.ceil((target.getTime() - today.getTime()) / (1000 * 60 * 60 * 24))
  if (diffDays < 0) return { tone: 'danger', label: `Vencida hace ${Math.abs(diffDays)} día${Math.abs(diffDays) === 1 ? '' : 's'}` }
  if (diffDays <= 7) return { tone: 'warning', label: `En ${diffDays} día${diffDays === 1 ? '' : 's'}` }
  if (diffDays <= 30) return { tone: 'info', label: `En ${diffDays} días` }
  return null
}

export interface UseEstablecimientosDataReturn {
  establecimiento: (Establecimiento & { equipos?: Equipo[] }) | null
  equipos: Equipo[]
  loading: boolean
  error: string
  saving: boolean
  showModal: boolean
  formData: EstablecimientoFormData
  selectedCertificate: File | null
  loadData: () => Promise<void>
  setShowModal: (v: boolean) => void
  setFormData: (f: EstablecimientoFormData) => void
  setSelectedCertificate: (f: File | null) => void
  handleSubmit: (e: React.FormEvent) => Promise<void>
  closeModal: () => void
}

export function useEstablecimientosData(
  establecimientoId: number | undefined,
  isAdmin: boolean
): UseEstablecimientosDataReturn {
  const [establecimiento, setEstablecimiento] = useState<(Establecimiento & { equipos?: Equipo[] }) | null>(null)
  const [equipos, setEquipos] = useState<Equipo[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)
  const [showModal, setShowModal] = useState(false)
  const [formData, setFormData] = useState<EstablecimientoFormData>(EMPTY_ESTABLECIMIENTO_FORM)
  const [selectedCertificate, setSelectedCertificate] = useState<File | null>(null)

  const loadData = useCallback(async () => {
    if (isAdmin) {
      setLoading(false)
      return
    }
    const result = await loadEstablecimientoWithEquipos(establecimientoId)
    setEstablecimiento(result.establecimiento)
    if (result.establecimiento?.equipos) {
      setEquipos(result.establecimiento.equipos)
    }
    setError(result.error)
    setLoading(false)
  }, [establecimientoId, isAdmin])

  const loadEquipos = useCallback(async (estId: number) => {
    const result = await loadEquiposByEstablecimiento(estId)
    setEquipos(result.equipos)
    if (result.error) setError(result.error)
  }, [])

  useEffect(() => {
    loadData()
  }, [loadData])

  useEffect(() => {
    if (establecimiento?.id) {
      loadEquipos(establecimiento.id)
    }
  }, [establecimiento?.id, loadEquipos])

  const handleSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    setError('')
    const result = await saveEstablecimiento(formData, selectedCertificate)
    if (result.error) setError(result.error)
    setSaving(false)
    setSelectedCertificate(null)
    if (!result.error) {
      setShowModal(false)
      setFormData(EMPTY_ESTABLECIMIENTO_FORM)
    }
  }, [formData, selectedCertificate])

  const closeModal = useCallback(() => {
    setShowModal(false)
    setSelectedCertificate(null)
    setFormData(EMPTY_ESTABLECIMIENTO_FORM)
  }, [])

  return {
    establecimiento,
    equipos,
    loading,
    error,
    saving,
    showModal,
    formData,
    selectedCertificate,
    loadData,
    setShowModal,
    setFormData,
    setSelectedCertificate,
    handleSubmit,
    closeModal,
  }
}
