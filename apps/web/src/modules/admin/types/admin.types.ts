/**
 * Tipos para el módulo Admin
 */

// ============== USERS ==============

export type UserStatus = 'active' | 'inactive' | 'pending' | 'suspended';

export interface User {
  id: string;
  email: string;
  name: string;
  avatar?: string;
  role: Role;
  status: UserStatus;
  department?: string;
  lastLogin?: Date;
  createdAt: Date;
  updatedAt: Date;
}

// ============== ROLES & PERMISSIONS ==============

export type PermissionAction = 'read' | 'write' | 'delete' | 'admin';

export interface Permission {
  id: string;
  name: string;
  description: string;
  resource: string;
  action: PermissionAction;
}

export interface Role {
  id: string;
  name: string;
  description: string;
  permissions: Permission[];
  isSystem: boolean;
  userCount: number;
  createdAt: Date;
  updatedAt: Date;
}

// ============== SETTINGS ==============

export type SettingType = 'string' | 'number' | 'boolean' | 'select' | 'json';
export type SettingCategory = 'general' | 'security' | 'notifications' | 'integrations' | 'appearance';

export interface SettingOption {
  value: string;
  label: string;
}

export interface SystemSetting {
  id: string;
  key: string;
  label: string;
  value: unknown;
  type: SettingType;
  category: SettingCategory;
  options?: SettingOption[];
  description?: string;
  isPublic: boolean;
  updatedAt: Date;
  updatedBy: string;
}

// ============== AUDIT ==============

export type AuditAction = 'create' | 'update' | 'delete' | 'login' | 'logout' | 'export' | 'sync';

export interface AuditChange {
  field: string;
  oldValue: unknown;
  newValue: unknown;
}

export interface AuditLog {
  id: string;
  timestamp: Date;
  userId: string;
  userName: string;
  action: AuditAction;
  resource: string;
  resourceId?: string;
  description: string;
  changes?: AuditChange[];
  ipAddress?: string;
  userAgent?: string;
}

export interface AuditFilters {
  userId?: string;
  action?: AuditAction;
  resource?: string;
  dateFrom?: Date;
  dateTo?: Date;
}

// ============== ADMIN STATE ==============

export interface AdminState {
  users: User[];
  roles: Role[];
  settings: SystemSetting[];
  auditLogs: AuditLog[];
  selectedUser: User | null;
  loading: boolean;
  error: string | null;
}
