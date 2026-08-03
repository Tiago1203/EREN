/**
 * Establecimientos Module Tests - PHASE 7 EPIC 5a
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'

vi.mock('@/lib/supabase', () => ({
  supabase: {
    from: vi.fn(() => ({
      select: vi.fn(() => ({ eq: vi.fn().mockResolvedValue({ data: null, error: null }) })),
      insert: vi.fn(() => ({ select: vi.fn(() => ({ single: vi.fn().mockResolvedValue({ data: null, error: null }) })) })),
      update: vi.fn().mockResolvedValue({ error: null }),
    })),
    auth: {
      signUp: vi.fn().mockResolvedValue({ user: { id: 'test' }, error: null }),
      admin: { deleteUser: vi.fn().mockResolvedValue({ error: null }) },
    },
  },
}))
vi.mock('@/lib/storage', () => ({
  uploadFileToBucket: vi.fn().mockResolvedValue({ error: null }),
  removeFileFromBucket: vi.fn().mockResolvedValue({ error: null }),
}))
vi.mock('@/lib/queries', () => ({
  fetchEquiposByEstablecimiento: vi.fn().mockResolvedValue({ equipos: [], error: null }),
}))

describe('Establecimientos Types', () => {
  it('should export EMPTY_ESTABLECIMIENTO_FORM', async () => {
    const { EMPTY_ESTABLECIMIENTO_FORM } = await import('@/modules/establecimientos/types/establecimientos.types')
    expect(EMPTY_ESTABLECIMIENTO_FORM).toBeDefined()
    expect(EMPTY_ESTABLECIMIENTO_FORM.ruc).toBe('')
    expect(EMPTY_ESTABLECIMIENTO_FORM.nombre_comercial).toBe('')
  })
})

describe('Establecimientos Service', () => {
  beforeEach(() => vi.clearAllMocks())

  it('should export loadEquiposByEstablecimiento', async () => {
    const { loadEquiposByEstablecimiento } = await import('@/modules/establecimientos/services/establecimientos.service')
    expect(typeof loadEquiposByEstablecimiento).toBe('function')
  })

  it('should export saveEstablecimiento', async () => {
    const { saveEstablecimiento } = await import('@/modules/establecimientos/services/establecimientos.service')
    expect(typeof saveEstablecimiento).toBe('function')
  })

  it('should load equipos without error', async () => {
    const { loadEquiposByEstablecimiento } = await import('@/modules/establecimientos/services/establecimientos.service')
    const result = await loadEquiposByEstablecimiento(1)
    expect(result.error).toBe('')
    expect(Array.isArray(result.equipos)).toBe(true)
  })
})
