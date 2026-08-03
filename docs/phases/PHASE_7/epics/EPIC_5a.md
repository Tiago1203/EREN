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
Los routing adapters en `app/(dashboard)/` contienen la implementación completa para los 4 módulos migrados.
Los servicios y hooks en los módulos proporcionan la arquitectura feature-first para referencia y consumo futuro.

## Status
- [x] Dashboard - Routing adapter con impl completa (referencia en modules/dashboard/)
- [x] Equipos - Routing adapter migrado + servicios/hooks en módulo
- [x] Mantenimientos - Routing adapter migrado + servicios/hooks en módulo
- [x] Establecimientos - Routing adapter migrado + servicios/hooks en módulo
- [x] KPIs - Routing adapter migrado + servicios/hooks en módulo
