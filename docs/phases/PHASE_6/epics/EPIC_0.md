# EPIC 0: Platform Foundation

*Versión: 1.0.0*
*Fecha: 2026-07-24*

---

## Objetivo

**Establecer la arquitectura base de la Hospital Platform con estructura modular feature-first.**

EPIC 0 es responsable de:
- Crear infraestructura raíz del frontend
- Establecer estructura modular feature-first
- Configurar routing y layouts globales
- Crear componentes compartidos
- Preparar el proyecto para FASE 6 y 7

---

## Dependencias

```
FASE 5 (Cognitive Multi-Agent System)
        │
        ▼
   EPIC 0 (Platform Foundation)
        │
        ├── EPIC 1 (Dashboard & Navigation)
        ├── EPIC 2 (Operations Center)
        ├── EPIC 3 (AI Center & Chat)
        ├── EPIC 4 (Knowledge Center)
        ├── EPIC 5 (Analytics & Reports)
        ├── EPIC 6 (Notifications & Workspace)
        └── EPIC 7 (Administration & Connectors)
```

---

## Arquitectura

```
┌─────────────────────────────────────────────────────────────────────────┐
│                   EPIC 0: Platform Foundation                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    PLATFORM CORE                                    │   │
│  │  ├── Shared Components ──────────────────── Componentes compartidos │   │
│  │  ├── Global Layout ─────────────────────── Layout global (Sidebar) │   │
│  │  ├── Module Registry ───────────────────── Registro de módulos   │   │
│  │  ├── Route Configuration ───────────────── Configuración de rutas │   │
│  │  ├── Theme Provider ────────────────────── Proveedor de tema     │   │
│  │  └── Auth Provider ─────────────────────── Proveedor de auth     │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    MODULE STRUCTURE                                │   │
│  │  └── modules/                                                     │   │
│  │      ├── dashboard/                                               │   │
│  │      ├── ai/                                                     │   │
│  │      ├── analytics/                                              │   │
│  │      ├── reports/                                                │   │
│  │      ├── notifications/                                           │   │
│  │      ├── operations/                                             │   │
│  │      ├── administration/                                         │   │
│  │      ├── connectors/                                             │   │
│  │      ├── knowledge/                                              │   │
│  │      └── workspace/                                              │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    SHARED LAYER                                    │   │
│  │  ├── shared/components/ ──────────────────── UI base components  │   │
│  │  ├── shared/hooks/ ──────────────────────── Hooks globales        │   │
│  │  ├── shared/lib/ ────────────────────────── Configuración         │   │
│  │  ├── shared/types/ ──────────────────────── Tipos compartidos    │   │
│  │  └── shared/utils/ ──────────────────────── Utilidades           │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Estructura de Archivos

```
apps/web/src/
├── app/                          # Rutas Next.js
│   ├── (auth)/                  # Auth routes
│   │   ├── login/
│   │   └── layout.tsx
│   ├── (dashboard)/             # Dashboard routes
│   │   ├── layout.tsx          # Sidebar/Nav global
│   │   └── page.tsx            # Redirect a /dashboard
│   ├── api/
│   └── layout.tsx              # Root layout
│
├── modules/                     # Feature-first modules 🆕
│   ├── dashboard/
│   ├── ai/
│   ├── analytics/
│   ├── reports/
│   ├── notifications/
│   ├── operations/
│   ├── administration/
│   ├── connectors/
│   ├── knowledge/
│   ├── workspace/
│   └── shared/                 # Utilidades compartidas
│       ├── components/         # UI base
│       ├── hooks/              # Hooks globales
│       ├── lib/               # Configuración
│       ├── types/              # Tipos globales
│       └── utils/             # Utilidades
```

---

## Componentes

### 1. Shared Components Library

Biblioteca de componentes UI base compartidos.

```typescript
// shared/components/Button.tsx
export interface ButtonProps {
  variant: 'primary' | 'secondary' | 'ghost' | 'danger';
  size: 'sm' | 'md' | 'lg';
  children: React.ReactNode;
  onClick?: () => void;
  disabled?: boolean;
  className?: string;
}
```

### 2. Global Layout

Layout global con sidebar y navegación.

```typescript
// app/(dashboard)/layout.tsx
export interface DashboardLayoutProps {
  children: React.ReactNode;
  sidebarCollapsed?: boolean;
}
```

### 3. Module Registry

Registro de módulos disponibles.

```typescript
// shared/lib/module-registry.ts
interface ModuleConfig {
  id: string;
  name: string;
  icon: string;
  path: string;
  enabled: boolean;
  permissions: string[];
}

class ModuleRegistry {
  private modules: Map<string, ModuleConfig> = new Map();
  
  register(config: ModuleConfig): void;
  getModule(id: string): ModuleConfig | undefined;
  getEnabledModules(): ModuleConfig[];
  hasPermission(moduleId: string, permission: string): boolean;
}
```

### 4. Route Configuration

Configuración centralizada de rutas.

```typescript
// shared/lib/route-config.ts
interface RouteConfig {
  path: string;
  module: string;
  component: string;
  permissions: string[];
  breadcrumb?: BreadcrumbItem[];
}

const ROUTES: RouteConfig[] = [
  { path: '/dashboard', module: 'dashboard', component: 'DashboardPage' },
  { path: '/ai', module: 'ai', component: 'AIChatPage' },
  // ...
];
```

### 5. Theme Provider

Proveedor de tema (claro/oscuro).

```typescript
// shared/components/ThemeProvider.tsx
interface ThemeProviderProps {
  children: React.ReactNode;
  defaultTheme?: 'light' | 'dark' | 'system';
}

export function ThemeProvider({ children, defaultTheme = 'system' }: ThemeProviderProps) {
  // Implementación con next-themes
}
```

### 6. Auth Provider

Proveedor de autenticación.

```typescript
// shared/components/AuthProvider.tsx
interface AuthProviderProps {
  children: React.ReactNode;
}

interface User {
  id: string;
  email: string;
  profile: UserProfile;
  permissions: string[];
}

export function AuthProvider({ children }: AuthProviderProps) {
  // Implementación con Supabase
}
```

---

## Implementaciones

### SharedUIProvider

Proveedor de componentes UI compartidos.

```typescript
// shared/components/SharedUIProvider.tsx
export function SharedUIProvider({ children }: { children: React.ReactNode }) {
  return (
    <ThemeProvider>
      <AuthProvider>
        <ToastProvider>
          {children}
        </ToastProvider>
      </AuthProvider>
    </ThemeProvider>
  );
}
```

### ModuleRouter

Router modular que delega a módulos.

```typescript
// modules/module-router.ts
export class ModuleRouter {
  private registry: ModuleRegistry;
  
  constructor(registry: ModuleRegistry) {
    this.registry = registry;
  }
  
  getModuleRoutes(): RouteObject[] {
    const routes: RouteObject[] = [];
    for (const module of this.registry.getEnabledModules()) {
      routes.push({
        path: `/${module.id}/*`,
        element: React.lazy(() => import(`modules/${module.id}/pages/Page`)),
      });
    }
    return routes;
  }
}
```

### GlobalLayout

Layout global con sidebar.

```typescript
// app/(dashboard)/layout.tsx
export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex h-screen bg-background">
      <Sidebar />
      <main className="flex-1 overflow-auto">
        <Header />
        <div className="p-6">
          {children}
        </div>
      </main>
    </div>
  );
}
```

### ThemeConfig

Configuración de tema.

```typescript
// shared/lib/theme.ts
export const themeConfig = {
  colors: {
    primary: 'var(--primary)',
    secondary: 'var(--secondary)',
    background: 'var(--background)',
    foreground: 'var(--foreground)',
    muted: 'var(--muted)',
    accent: 'var(--accent)',
    destructive: 'var(--destructive)',
    border: 'var(--border)',
  },
  borderRadius: {
    sm: '0.125rem',
    md: '0.375rem',
    lg: '0.5rem',
    xl: '0.75rem',
  },
};
```

### FeatureFlags

Sistema de feature flags.

```typescript
// shared/lib/feature-flags.ts
interface FeatureFlags {
  AI_CENTER: boolean;
  ANALYTICS: boolean;
  KNOWLEDGE_BASE: boolean;
  REPORTS: boolean;
  CONNECTORS: boolean;
}

const flags: FeatureFlags = {
  AI_CENTER: true,
  ANALYTICS: true,
  KNOWLEDGE_BASE: true,
  REPORTS: true,
  CONNECTORS: false, // Preparado pero no habilitado
};

export function isFeatureEnabled(flag: keyof FeatureFlags): boolean {
  return flags[flag];
}
```

---

## Domain Objects

### ModuleConfig

```typescript
// shared/types/module.types.ts
export interface ModuleConfig {
  id: string;
  name: string;
  description: string;
  icon: string;
  path: string;
  enabled: boolean;
  permissions: string[];
  order: number;
}
```

### RouteConfig

```typescript
// shared/types/route.types.ts
export interface RouteConfig {
  path: string;
  module: string;
  component?: string;
  permissions: string[];
  exact?: boolean;
}
```

### ThemeConfig

```typescript
// shared/types/theme.types.ts
export interface ThemeConfig {
  mode: 'light' | 'dark' | 'system';
  primaryColor: string;
  accentColor: string;
  borderRadius: string;
}
```

### NavigationItem

```typescript
// shared/types/navigation.types.ts
export interface NavigationItem {
  id: string;
  label: string;
  icon: string;
  path: string;
  children?: NavigationItem[];
  permissions?: string[];
  badge?: string | number;
}
```

---

## Integración con FASE 5

```
FASE 5 (AI Kernel) ──► EPIC 0 (Platform Foundation)
                                  │
                                  ├── AI SDK Client
                                  ├── Agent Types
                                  └── Context Types
```

### AI SDK Integration

```typescript
// packages/ai-sdk/src/client.ts
export interface AIKernelClient {
  chat(message: string, context: ClinicalContext): Promise<AIResponse>;
  getAgents(): Promise<Agent[]>;
  getConversationHistory(): Promise<Conversation[]>;
}
```

---

## Concatenación

```
FASE 5 ──► EPIC 0 (Platform Foundation)
                    │
                    ├── EPIC 1 (Dashboard & Navigation)
                    ├── EPIC 2 (Operations Center)
                    ├── EPIC 3 (AI Center & Chat)
                    ├── EPIC 4 (Knowledge Center)
                    ├── EPIC 5 (Analytics & Reports)
                    ├── EPIC 6 (Notifications & Workspace)
                    └── EPIC 7 (Administration & Connectors)
```

---

## Estado

**✅ COMPLETO**

EPIC 0 proporciona la base sólida para el desarrollo de PHASE 6.

---

## Próximos Pasos

- EPIC 1: Dashboard & Navigation
- EPIC 2: Operations Center

---

*EREN PHASE 6 - EPIC 0*
*Architecture Board - 2026-07-24*
