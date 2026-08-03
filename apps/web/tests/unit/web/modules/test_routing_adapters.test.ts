/**
 * Routing Adapters Tests - PHASE 7 EPIC 5a
 * Tests that routing adapters correctly re-export from feature-first modules
 */

import { describe, it, expect } from 'vitest'
import { existsSync } from 'fs'
import { resolve } from 'path'

// root = /workspace/project/EREN/ (7 levels up from tests/unit/web/modules/)
const root = resolve(__dirname, '../../../../../..')

describe('Routing Adapters', () => {
  const modules = [
    'equipos',
    'mantenimientos',
    'establecimientos',
    'kpis',
  ]

  for (const mod of modules) {
    describe(mod, () => {
      it('should have routing adapter in app/(dashboard)', () => {
        const adapterPath = resolve(root, `apps/web/src/app/(dashboard)/${mod}/page.tsx`)
        expect(existsSync(adapterPath)).toBe(true)
      })

      it('should have module page at modules/{mod}/pages/page.tsx', () => {
        const modulePath = resolve(root, `apps/web/src/modules/${mod}/pages/page.tsx`)
        expect(existsSync(modulePath)).toBe(true)
      })

      it('should have service at modules/{mod}/services/{mod}.service.ts', () => {
        const servicePath = resolve(root, `apps/web/src/modules/${mod}/services/${mod}.service.ts`)
        expect(existsSync(servicePath)).toBe(true)
      })

      it('should have hook at modules/{mod}/hooks/use{Mod}Data.ts', () => {
        const hookName = 'use' + mod[0].toUpperCase() + mod.slice(1) + 'Data'
        const hookPath = resolve(root, `apps/web/src/modules/${mod}/hooks/${hookName}.ts`)
        expect(existsSync(hookPath)).toBe(true)
      })
    })
  }
})
