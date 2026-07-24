/**
 * Constantes compartidas
 */

export const APP_NAME = 'EREN';
export const APP_VERSION = '1.0.0';
export const APP_DESCRIPTION = 'Cognitive Operating System for Clinical Engineering';

// Paths
export const PATHS = {
  DASHBOARD: '/dashboard',
  EQUIPOS: '/equipos',
  MANTENIMIENTOS: '/mantenimientos',
  ESTABLECIMIENTOS: '/establecimientos',
  KPIs: '/kpis',
  AI: '/ai',
  ANALYTICS: '/analytics',
  REPORTS: '/reports',
  NOTIFICATIONS: '/notifications',
  OPERATIONS: '/operations',
  WORKSPACE: '/workspace',
  KNOWLEDGE: '/knowledge',
  ADMINISTRATION: '/administration',
  CONNECTORS: '/connectors',
} as const;

// API
export const API_TIMEOUT = 30000;
export const API_RETRY_ATTEMPTS = 3;

// Pagination
export const DEFAULT_PAGE_SIZE = 20;
export const PAGE_SIZE_OPTIONS = [10, 20, 50, 100];

// Storage Keys
export const STORAGE_KEYS = {
  THEME: 'eren-theme',
  SIDEBAR_COLLAPSED: 'eren-sidebar-collapsed',
  LAST_TAB: 'eren-last-tab',
} as const;

// Roles
export const ROLES = {
  ADMIN: 'admin',
  MANAGER: 'manager',
  TECHNICIAN: 'technician',
  USER: 'user',
  VIEWER: 'viewer',
} as const;
