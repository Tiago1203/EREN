# EPIC 1: Dashboard & Navigation

*Versión: 1.0.0*
*Fecha: 2026-07-24*

---

## Objetivo

**Migrar y potenciar el dashboard principal y sistema de navegación.**

EPIC 1 es responsable de:
- Migrar el dashboard existente al esquema modular
- Implementar navegación completa con sidebar
- Crear componentes reutilizables de visualización
- Implementar breadcrumbs y navegación contextual
- Crear header y user menu

---

## Dependencias

```
FASE 5 (Cognitive Multi-Agent System)
        │
        ▼
   PHASE 6 (Hospital Platform)
        │
        ▼
   EPIC 0 (Platform Foundation)
        │
        ▼
   EPIC 1 (Dashboard & Navigation)
        │
        ├── EPIC 2 (Operations Center)
        ├── EPIC 3 (AI Center)
        ├── EPIC 4 (Knowledge Center)
        └── ...
```

---

## Arquitectura

```
┌─────────────────────────────────────────────────────────────────────────┐
│                   EPIC 1: Dashboard & Navigation                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    DASHBOARD MODULE                               │   │
│  │  ├── components/ ──────────────────── DashboardGrid, StatCard     │   │
│  │  ├── pages/ ─────────────────────── page.tsx (migrado)           │   │
│  │  ├── hooks/ ─────────────────────── useDashboardData              │   │
│  │  ├── services/ ──────────────────── dashboard.service             │   │
│  │  ├── api/ ──────────────────────── dashboard.queries             │   │
│  │  ├── stores/ ───────────────────── dashboard.store               │   │
│  │  ├── types/ ─────────────────────── dashboard.types               │   │
│  │  └── utils/ ─────────────────────── kpi-calculator               │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    NAVIGATION MODULE                                │   │
│  │  ├── components/ ──────────────────── Sidebar, Header, Breadcrumbs  │   │
│  │  ├── hooks/ ─────────────────────── useNavigation                 │   │
│  │  ├── types/ ─────────────────────── navigation.types              │   │
│  │  └── utils/ ─────────────────────── route-utils                  │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    SHARED NAVIGATION COMPONENTS                    │   │
│  │  ├── BreadcrumbNav ────────────────── Breadcrumbs component       │   │
│  │  ├── Header ───────────────────────── Header with user menu       │   │
│  │  ├── UserMenuDropdown ───────────────── User menu dropdown        │   │
│  │  └── QuickActionsBar ────────────────── Quick actions bar         │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Estructura de Archivos

```
apps/web/src/modules/
├── dashboard/                         # Módulo Dashboard
│   ├── components/
│   │   ├── DashboardGrid.tsx
│   │   ├── StatCard.tsx
│   │   ├── WelcomeHeader.tsx
│   │   ├── KpiSection.tsx
│   │   └── EstablishmentInfo.tsx
│   ├── hooks/
│   │   └── useDashboardData.ts
│   ├── services/
│   │   └── dashboard.service.ts
│   ├── api/
│   │   └── dashboard.queries.ts
│   ├── stores/
│   │   └── dashboard.store.ts
│   ├── types/
│   │   └── dashboard.types.ts
│   ├── utils/
│   │   └── kpi-calculator.ts
│   └── pages/
│       └── page.tsx
│
├── navigation/                        # Módulo Navigation 🆕
│   ├── components/
│   │   ├── Sidebar.tsx              # Sidebar con módulos
│   │   ├── Header.tsx               # Header con user menu
│   │   ├── BreadcrumbNav.tsx        # Breadcrumbs
│   │   ├── UserMenuDropdown.tsx     # User menu dropdown
│   │   └── QuickActionsBar.tsx     # Quick actions
│   ├── hooks/
│   │   └── useNavigation.ts
│   ├── types/
│   │   └── navigation.types.ts
│   └── utils/
│       └── route-utils.ts
│
└── shared/
    └── components/                  # Componentes compartidos existentes
```

---

## Componentes

### 1. Dashboard Module

#### DashboardGrid

Grid de estadísticas del dashboard.

```typescript
// modules/dashboard/components/DashboardGrid.tsx
export interface DashboardGridProps {
  stats: DashboardStats;
  onCardClick: (card: StatCard) => void;
}

export function DashboardGrid({ stats, onCardClick }: DashboardGridProps) {
  // Grid responsivo de tarjetas
}
```

#### StatCard

Tarjeta de estadística individual.

```typescript
// modules/dashboard/components/StatCard.tsx
export interface StatCardProps {
  title: string;
  value: number;
  subtitle: string;
  icon: React.ReactNode;
  color: string;
  href?: string;
  onClick?: () => void;
}
```

#### WelcomeHeader

Header de bienvenida personalizado.

```typescript
// modules/dashboard/components/WelcomeHeader.tsx
export interface WelcomeHeaderProps {
  userName: string;
  userRole: 'admin' | 'manager' | 'user';
  establishmentName?: string;
}
```

### 2. Navigation Module

#### Sidebar

Sidebar de navegación con módulos.

```typescript
// modules/navigation/components/Sidebar.tsx
export interface SidebarProps {
  collapsed?: boolean;
  onToggle?: () => void;
}
```

#### Header

Header con información de usuario y acciones rápidas.

```typescript
// modules/navigation/components/Header.tsx
export interface HeaderProps {
  title?: string;
  showBreadcrumbs?: boolean;
  actions?: React.ReactNode;
}
```

#### BreadcrumbNav

Navegación de breadcrumbs.

```typescript
// modules/navigation/components/BreadcrumbNav.tsx
export interface BreadcrumbItem {
  label: string;
  href?: string;
}

export interface BreadcrumbNavProps {
  items: BreadcrumbItem[];
}
```

#### UserMenuDropdown

Menú desplegable de usuario.

```typescript
// modules/navigation/components/UserMenuDropdown.tsx
export interface UserMenuDropdownProps {
  user: {
    name: string;
    email: string;
    avatar?: string;
    role: string;
  };
  onSignOut: () => void;
  onProfile?: () => void;
  onSettings?: () => void;
}
```

#### QuickActionsBar

Barra de acciones rápidas.

```typescript
// modules/navigation/components/QuickActionsBar.tsx
export interface QuickAction {
  id: string;
  label: string;
  icon: React.ReactNode;
  onClick: () => void;
  disabled?: boolean;
}

export interface QuickActionsBarProps {
  actions: QuickAction[];
}
```

---

## Implementaciones

### DashboardService

```typescript
// modules/dashboard/services/dashboard.service.ts
export class DashboardService {
  async getStats(userId: string, isAdmin: boolean, establishmentId?: string): Promise<DashboardStats>;
  async getKpis(equipos: Equipo[], eventos: Evento[]): Promise<Kpi[]>;
  async getEstablishmentInfo(establishmentId: string): Promise<Establecimiento>;
}
```

### DashboardStore

```typescript
// modules/dashboard/stores/dashboard.store.ts
interface DashboardState {
  stats: DashboardStats;
  kpis: Kpi[];
  establishment: Establecimiento | null;
  loading: boolean;
  error: string | null;
}

export const useDashboardStore = create<DashboardState>((set) => ({
  // ...
}));
```

### useDashboardData Hook

```typescript
// modules/dashboard/hooks/useDashboardData.ts
export function useDashboardData() {
  const { profile, isAdmin, establecimientoId } = useAuth();
  const { stats, kpis, loading, loadData } = useDashboardStore();

  useEffect(() => {
    if (profile) loadData(isAdmin, establecimientoId);
  }, [profile, isAdmin, establecimientoId]);

  return { stats, kpis, loading, isAdmin, profile };
}
```

### NavigationService

```typescript
// modules/navigation/services/navigation.service.ts
export class NavigationService {
  getBreadcrumbs(pathname: string): BreadcrumbItem[];
  getModuleForPath(pathname: string): ModuleConfig | undefined;
  canAccessModule(moduleId: string, userRole: string): boolean;
}
```

### useNavigation Hook

```typescript
// modules/navigation/hooks/useNavigation.ts
export function useNavigation() {
  const pathname = usePathname();
  const breadcrumbs = NavigationService.getBreadcrumbs(pathname);
  const currentModule = NavigationService.getModuleForPath(pathname);

  return { breadcrumbs, currentModule, pathname };
}
```

---

## Domain Objects

### DashboardStats

```typescript
// modules/dashboard/types/dashboard.types.ts
export interface DashboardStats {
  equipos: number;
  mantenimientos: number;
  establecimientos: number;
  incidentes?: number;
  alertas?: number;
}

export interface StatCard {
  id: string;
  title: string;
  value: number;
  subtitle: string;
  icon: string;
  color: string;
  href: string;
  show: boolean;
}

export interface Kpi {
  id: string;
  label: string;
  value: number | string;
  unit?: string;
  trend?: 'up' | 'down' | 'stable';
  trendValue?: number;
}
```

### NavigationRoute

```typescript
// modules/navigation/types/navigation.types.ts
export interface NavigationItem {
  id: string;
  label: string;
  icon: string;
  path: string;
  children?: NavigationItem[];
  adminOnly?: boolean;
  badge?: string | number;
}

export interface BreadcrumbItem {
  label: string;
  path?: string;
}

export interface UserMenuItem {
  id: string;
  label: string;
  icon?: string;
  onClick: () => void;
  divider?: boolean;
}
```

---

## Integración con FASE 1

```
PHASE 1 (Business Domain)
        │
        ├── Device Context ──▶ Equipos
        ├── Incident Context ──▶ Incidentes
        ├── Capacity Context ──▶ Establecimientos
        └── WorkOrder Context ──▶ Mantenimientos
                │
                ▼
           EPIC 1 (Dashboard)
                │
                ├── DashboardGrid
                ├── StatCards
                └── KPIs
```

### Consumiendo PHASE 1

```typescript
// modules/dashboard/api/dashboard.queries.ts
import { fetchEquipos, fetchEventos, fetchEstablecimientos } from '@/lib/queries';
import { deviceRepository } from '@eren/core/device-repository'; // futuro
```

---

## Estado

**🚧 EN PROGRESO**

EPIC 1 está en desarrollo.

---

## Tareas

- [x] Crear documentación EPIC 1
- [x] Crear tipos para dashboard
- [x] Migrar componentes del dashboard
- [x] Crear servicios del dashboard
- [x] Crear hooks del dashboard
- [x] Migrar página del dashboard
- [x] Crear componentes de navegación
- [ ] Crear tests unitarios
- [ ] Actualizar layout global

---

## Próximos Pasos

- EPIC 2: Operations Center
- EPIC 3: AI Center & Chat

---

*EREN PHASE 6 - EPIC 1*
*Architecture Board - 2026-07-24*
