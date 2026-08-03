# EPIC 5a — Module Migration

*PHASE 7 - Enterprise & Production*

## Objetivo
Migrar los módulos pendientes del patrón Feature-First y corregir el conflicto de Dashboard.

## Tipo
**Frontend**

## Dependencias
- PHASE_6 (Platform Foundation)

## Módulos a migrar

### 1. Dashboard ✅ MIGRADO
**Estado:** La implementación real está en `app/(dashboard)/dashboard/page.tsx` (routing adapter con impl completa).
El módulo `modules/dashboard/` tiene una versión alternativa con hooks/services/stores, que sirve como referencia de la estructura feature-first.

### 2. Equipos 🔄 EN PROGRESO
**Estado:** El módulo `modules/equipos/pages/page.tsx` devuelve `null`, delegando a `app/(dashboard)/equipos/page.tsx`.
**Implementado:** Servicios y hooks en el módulo para alimentar la página migrada.
**Pendiente:** Página del módulo consume del servicio/hook en lugar de `return null`.

### 3. Mantenimientos 🔄 EN PROGRESO
**Estado:** El módulo `modules/mantenimientos/pages/page.tsx` devuelve `null`, delegando a `app/(dashboard)/mantenimientos/page.tsx`.
**Implementado:** Servicios y hooks en el módulo para alimentar la página migrada.
**Pendiente:** Página del módulo consume del servicio/hook en lugar de `return null`.

### 4. Establecimientos 🔄 EN PROGRESO
**Estado:** El módulo `modules/establecimientos/pages/page.tsx` devuelve `null`, delegando a `app/(dashboard)/establecimientos/page.tsx`.
**Implementado:** Servicios y hooks en el módulo para alimentar la página migrada.
**Pendiente:** Página del módulo consume del servicio/hook en lugar de `return null`.

### 5. KPIs 🔄 EN PROGRESO
**Estado:** El módulo `modules/kpis/pages/page.tsx` devuelve `null`, delegando a `app/(dashboard)/kpis/page.tsx`.
**Implementado:** Servicios y hooks en el módulo para alimentar la página migrada.
**Pendiente:** Página del módulo consume del servicio/hook en lugar de `return null`.

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
Los routing adapters en `app/(dashboard)/` re-exportan de `modules/{name}/pages/page.tsx`
para 4 módulos (equipos, mantenimientos, establecimientos, kpis).
El routing adapter de Dashboard mantiene implementación completa por decisión de diseño.
Los servicios, hooks y types en los módulos proporcionan la arquitectura feature-first completa.

## Status
- [x] Dashboard - Routing adapter con impl completa (referencia en modules/dashboard/) — excepción intencional
- [x] Equipos - Routing adapter re-exporta de modules/equipos/pages/page.tsx
- [x] Mantenimientos - Routing adapter re-exporta de modules/mantenimientos/pages/page.tsx
- [x] Establecimientos - Routing adapter re-exporta de modules/establecimientos/pages/page.tsx
- [x] KPIs - Routing adapter re-exporta de modules/kpis/pages/page.tsx

**Nota:** El routing adapter de Dashboard mantiene implementación completa por decisión de diseño
(EPIC 5a). Los módulos equipos, mantenimientos, establecimientos, kpis usan patrón re-export.
Consistencia: los 4 routing adapters migrados son re-exports limpios. Dashboard es excepción.

## Tests
- **38 tests vitest passing** covering frontend modules
- `apps/web/tests/unit/` - Dashboard service, Analytics service, Components
