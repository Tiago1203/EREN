/**
 * KPIs Module Tests - PHASE 7 EPIC 5a
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'

vi.mock('@/lib/queries', () => ({
  fetchEquipos: vi.fn().mockResolvedValue({ data: [], error: null }),
  fetchEventos: vi.fn().mockResolvedValue({ data: [], error: null }),
  fetchEstablecimientos: vi.fn().mockResolvedValue({ data: [], error: null }),
}))
vi.mock('@/lib/kpis', () => ({
  calcularKpis: vi.fn().mockReturnValue([]),
}))

describe('KPIs Service', () => {
  beforeEach(() => vi.clearAllMocks())

  it('should export loadKpisData', async () => {
    const { loadKpisData } = await import('@/modules/kpis/services/kpis.service')
    expect(typeof loadKpisData).toBe('function')
  })

  it('should export loadKpisForEstablecimiento', async () => {
    const { loadKpisForEstablecimiento } = await import('@/modules/kpis/services/kpis.service')
    expect(typeof loadKpisForEstablecimiento).toBe('function')
  })

  it('should load KPIs without error', async () => {
    const { loadKpisData } = await import('@/modules/kpis/services/kpis.service')
    const result = await loadKpisData(false, 1)
    expect(result.error).toBe('')
    expect(Array.isArray(result.establecimientos)).toBe(true)
    expect(Array.isArray(result.equipos)).toBe(true)
  })
})
