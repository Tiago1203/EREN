/**
 * Equipos Module Tests - PHASE 7 EPIC 5a
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'

vi.mock('@/lib/supabase', () => ({
  supabase: { from: vi.fn() },
}))
vi.mock('@/lib/storage', () => ({
  uploadFileToBucket: vi.fn().mockResolvedValue({ error: null }),
  getSignedUrlForPath: vi.fn().mockResolvedValue({ signedURL: 'https://example.com', error: null }),
  removeFileFromBucket: vi.fn().mockResolvedValue({ error: null }),
}))
vi.mock('@/lib/queries', () => ({
  fetchEquipos: vi.fn().mockResolvedValue({ data: [], error: null }),
  fetchEstablecimientos: vi.fn().mockResolvedValue({ data: [], error: null }),
}))

describe('Equipos Types', () => {
  it('should export EMPTY_EQUIPO_FORM constant', async () => {
    const { EMPTY_EQUIPO_FORM } = await import('@/modules/equipos/types/equipos.types')
    expect(EMPTY_EQUIPO_FORM).toBeDefined()
    expect(EMPTY_EQUIPO_FORM.establecimiento_id).toBe('')
    expect(EMPTY_EQUIPO_FORM.criticidad).toBe('media')
  })
})

describe('Equipos Service', () => {
  beforeEach(() => vi.clearAllMocks())

  it('should export loadEquipos', async () => {
    const { loadEquipos } = await import('@/modules/equipos/services/equipos.service')
    expect(typeof loadEquipos).toBe('function')
  })

  it('should export saveEquipo', async () => {
    const { saveEquipo } = await import('@/modules/equipos/services/equipos.service')
    expect(typeof saveEquipo).toBe('function')
  })

  it('should export deleteEquipo', async () => {
    const { deleteEquipo } = await import('@/modules/equipos/services/equipos.service')
    expect(typeof deleteEquipo).toBe('function')
  })

  it('should load equipos without error', async () => {
    const { loadEquipos } = await import('@/modules/equipos/services/equipos.service')
    const result = await loadEquipos(false, 1)
    expect(result.error).toBe('')
    expect(Array.isArray(result.equipos)).toBe(true)
  })
})
