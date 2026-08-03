/**
 * Mantenimientos Module Tests - PHASE 7 EPIC 5a
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'

vi.mock('@/lib/supabase', () => ({
  supabase: { from: vi.fn() },
}))
vi.mock('@/lib/storage', () => ({
  uploadFileToBucket: vi.fn().mockResolvedValue({ error: null }),
  removeFileFromBucket: vi.fn().mockResolvedValue({ error: null }),
}))
vi.mock('@/lib/queries', () => ({
  fetchEventos: vi.fn().mockResolvedValue({ data: [], error: null }),
  fetchEquipos: vi.fn().mockResolvedValue({ data: [], error: null }),
  fetchEstablecimientos: vi.fn().mockResolvedValue({ data: [], error: null }),
}))

describe('Mantenimientos Types', () => {
  it('should export EMPTY_MANTENIMIENTO_FORM', async () => {
    const { EMPTY_MANTENIMIENTO_FORM } = await import('@/modules/mantenimientos/types/mantenimientos.types')
    expect(EMPTY_MANTENIMIENTO_FORM).toBeDefined()
    expect(EMPTY_MANTENIMIENTO_FORM.fecha_ejecucion).toBeDefined()
  })
})

describe('Mantenimientos Service', () => {
  beforeEach(() => vi.clearAllMocks())

  it('should export loadMantenimientos', async () => {
    const { loadMantenimientos } = await import('@/modules/mantenimientos/services/mantenimientos.service')
    expect(typeof loadMantenimientos).toBe('function')
  })

  it('should export saveMantenimiento', async () => {
    const { saveMantenimiento } = await import('@/modules/mantenimientos/services/mantenimientos.service')
    expect(typeof saveMantenimiento).toBe('function')
  })

  it('should load mantenimientos without error', async () => {
    const { loadMantenimientos } = await import('@/modules/mantenimientos/services/mantenimientos.service')
    const result = await loadMantenimientos(false, 1)
    expect(result.error).toBe('')
    expect(Array.isArray(result.eventos)).toBe(true)
  })
})
