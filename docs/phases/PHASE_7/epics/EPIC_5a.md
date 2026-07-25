# EPIC 5a — Module Migration

*PHASE 7 - Enterprise & Production*

## Objetivo
Migrar los módulos pendientes del patrón Feature-First y corregir el conflicto de Dashboard.

## Tipo
**Frontend**

## Dependencias
- PHASE_6 (Platform Foundation)

## Módulos a migrar

### 1. Dashboard ⚠️ CONFLICTO
**Problema:** `app/(dashboard)/dashboard/page.tsx` tiene impl OLD, `modules/dashboard/pages/page.tsx` tiene impl NEW migrada.
**Solución:** Convertir `app/` en routing adapter que re-exporte del módulo.

### 2. Equipos ❌ PLACEHOLDER
**Problema:** `modules/equipos/pages/page.tsx` devuelve `null`, impl real en `app/`.
**Solución:** Migrar CRUD + file upload a hooks/services/stores en el módulo.

### 3. Mantenimientos ❌ PLACEHOLDER
**Problema:** `modules/mantenimientos/pages/page.tsx` devuelve `null`, impl real en `app/`.
**Solución:** Migrar CRUD + file upload a hooks/services/stores en el módulo.

### 4. Establecimientos ❌ PLACEHOLDER
**Problema:** `modules/establecimientos/pages/page.tsx` es placeholder.
**Solución:** Migrar impl completa de `app/` al módulo.

### 5. KPIs ❌ PLACEHOLDER
**Problema:** `modules/kpis/pages/page.tsx` es placeholder.
**Solución:** Migrar impl completa de `app/` al módulo.

## Estructura objetivo por módulo

```
modules/{module}/
├── components/
│   └── {Module}Grid.tsx
├── hooks/
│   └── use{Module}Data.ts
├── services/
│   └── {module}.service.ts
├── stores/
│   └── {module}.store.ts
├── types/
│   └── {module}.types.ts
└── pages/
    └── page.tsx        # Migrado + use hook
```

## Resultado
Todos los módulos del frontend siguiendo el patrón Feature-First unificado.

## Status
- [ ] Dashboard - Fix routing adapter
- [ ] Equipos - Migrate to feature-first
- [ ] Mantenimientos - Migrate to feature-first
- [ ] Establecimientos - Migrate to feature-first
- [ ] KPIs - Migrate to feature-first
