/**
 * Module Registry - Registro central de módulos
 */

import { isFeatureEnabled } from './feature-flags';

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

export const MODULE_REGISTRY: ModuleConfig[] = [
  {
    id: 'dashboard',
    name: 'Dashboard',
    description: 'Panel principal y métricas',
    icon: 'LayoutDashboard',
    path: '/dashboard',
    enabled: true,
    permissions: [],
    order: 1,
  },
  {
    id: 'equipos',
    name: 'Equipos',
    description: 'Gestión de equipos médicos',
    icon: 'Monitor',
    path: '/equipos',
    enabled: true,
    permissions: [],
    order: 2,
  },
  {
    id: 'mantenimientos',
    name: 'Mantenimientos',
    description: 'Gestión de mantenimientos',
    icon: 'Wrench',
    path: '/mantenimientos',
    enabled: true,
    permissions: [],
    order: 3,
  },
  {
    id: 'establecimientos',
    name: 'Establecimientos',
    description: 'Gestión de establecimientos',
    icon: 'Building',
    path: '/establecimientos',
    enabled: true,
    permissions: [],
    order: 4,
  },
  {
    id: 'kpis',
    name: 'KPIs',
    description: 'Indicadores clave de rendimiento',
    icon: 'BarChart3',
    path: '/kpis',
    enabled: true,
    permissions: [],
    order: 5,
  },
  {
    id: 'ai',
    name: 'AI Center',
    description: 'Centro de inteligencia artificial',
    icon: 'Bot',
    path: '/ai',
    enabled: isFeatureEnabled('AI_CENTER'),
    permissions: [],
    order: 10,
  },
  {
    id: 'analytics',
    name: 'Analytics',
    description: 'Análisis y métricas avanzadas',
    icon: 'LineChart',
    path: '/analytics',
    enabled: isFeatureEnabled('ANALYTICS'),
    permissions: [],
    order: 11,
  },
  {
    id: 'reports',
    name: 'Reportes',
    description: 'Generación de reportes',
    icon: 'FileText',
    path: '/reports',
    enabled: isFeatureEnabled('REPORTS'),
    permissions: [],
    order: 12,
  },
  {
    id: 'operations',
    name: 'Operaciones',
    description: 'Centro de operaciones',
    icon: 'Activity',
    path: '/operations',
    enabled: isFeatureEnabled('OPERATIONS'),
    permissions: [],
    order: 13,
  },
  {
    id: 'notifications',
    name: 'Notificaciones',
    description: 'Centro de notificaciones',
    icon: 'Bell',
    path: '/notifications',
    enabled: isFeatureEnabled('NOTIFICATIONS'),
    permissions: [],
    order: 14,
  },
  {
    id: 'workspace',
    name: 'Workspace',
    description: 'Área de trabajo colaborativo',
    icon: 'Briefcase',
    path: '/workspace',
    enabled: isFeatureEnabled('WORKSPACE'),
    permissions: [],
    order: 15,
  },
  {
    id: 'knowledge',
    name: 'Conocimiento',
    description: 'Centro de conocimiento',
    icon: 'BookOpen',
    path: '/knowledge',
    enabled: isFeatureEnabled('KNOWLEDGE_BASE'),
    permissions: [],
    order: 16,
  },
  {
    id: 'administration',
    name: 'Administración',
    description: 'Panel de administración',
    icon: 'Settings',
    path: '/administration',
    enabled: isFeatureEnabled('ADMINISTRATION'),
    permissions: [],
    order: 20,
  },
  {
    id: 'connectors',
    name: 'Conectores',
    description: 'Integraciones con sistemas externos',
    icon: 'Plug',
    path: '/connectors',
    enabled: isFeatureEnabled('CONNECTORS'),
    permissions: [],
    order: 21,
  },
];

class ModuleRegistry {
  private modules: Map<string, ModuleConfig> = new Map();
  private static instance: ModuleRegistry;

  private constructor() {
    this.registerModules();
  }

  static getInstance(): ModuleRegistry {
    if (!ModuleRegistry.instance) {
      ModuleRegistry.instance = new ModuleRegistry();
    }
    return ModuleRegistry.instance;
  }

  private registerModules(): void {
    for (const module of MODULE_REGISTRY) {
      if (module.enabled) {
        this.modules.set(module.id, module);
      }
    }
  }

  register(config: ModuleConfig): void {
    if (config.enabled) {
      this.modules.set(config.id, config);
    }
  }

  getModule(id: string): ModuleConfig | undefined {
    return this.modules.get(id);
  }

  getEnabledModules(): ModuleConfig[] {
    return Array.from(this.modules.values()).sort((a, b) => a.order - b.order);
  }

  hasPermission(moduleId: string, permission: string): boolean {
    const module = this.modules.get(moduleId);
    return module ? module.permissions.includes(permission) : false;
  }

  isModuleEnabled(id: string): boolean {
    return this.modules.has(id);
  }
}

export const moduleRegistry = ModuleRegistry.getInstance();
export { ModuleRegistry };
