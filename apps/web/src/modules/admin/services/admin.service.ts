/**
 * Admin Service
 */

import type { User, Role, SystemSetting, AuditLog, AuditFilters } from '../types/admin.types';

export class AdminService {
  private baseUrl: string;

  constructor(baseUrl: string = '/api/admin') {
    this.baseUrl = baseUrl;
  }

  // ============== USERS ==============

  async getUsers(): Promise<User[]> {
    return this.getMockUsers();
  }

  async getUser(id: string): Promise<User | null> {
    const users = this.getMockUsers();
    return users.find((u) => u.id === id) || null;
  }

  async createUser(data: Partial<User>): Promise<User> {
    const user: User = {
      id: `user-${Date.now()}`,
      email: data.email || '',
      name: data.name || '',
      role: data.role || this.getMockRoles()[0],
      status: 'pending',
      createdAt: new Date(),
      updatedAt: new Date(),
    };
    return user;
  }

  async updateUser(id: string, data: Partial<User>): Promise<User> {
    const user = await this.getUser(id);
    if (!user) throw new Error('User not found');
    return { ...user, ...data, updatedAt: new Date() };
  }

  async deleteUser(id: string): Promise<void> {
    console.log('Delete user:', id);
  }

  // ============== ROLES ==============

  async getRoles(): Promise<Role[]> {
    return this.getMockRoles();
  }

  async getRole(id: string): Promise<Role | null> {
    const roles = this.getMockRoles();
    return roles.find((r) => r.id === id) || null;
  }

  async createRole(data: Partial<Role>): Promise<Role> {
    const role: Role = {
      id: `role-${Date.now()}`,
      name: data.name || '',
      description: data.description || '',
      permissions: data.permissions || [],
      isSystem: false,
      userCount: 0,
      createdAt: new Date(),
      updatedAt: new Date(),
    };
    return role;
  }

  async updateRole(id: string, data: Partial<Role>): Promise<Role> {
    const role = await this.getRole(id);
    if (!role) throw new Error('Role not found');
    return { ...role, ...data, updatedAt: new Date() };
  }

  // ============== SETTINGS ==============

  async getSettings(): Promise<SystemSetting[]> {
    return this.getMockSettings();
  }

  async updateSetting(key: string, value: unknown): Promise<void> {
    console.log('Update setting:', key, value);
  }

  // ============== AUDIT ==============

  async getAuditLogs(filters?: AuditFilters): Promise<AuditLog[]> {
    return this.getMockAuditLogs();
  }

  // ============== MOCK DATA ==============

  private getMockUsers(): User[] {
    return [
      {
        id: 'user-1',
        email: 'carlos@hospital.com',
        name: 'Carlos García',
        role: this.getMockRoles()[0],
        status: 'active',
        department: 'Ingeniería Biomédica',
        lastLogin: new Date(Date.now() - 2 * 60 * 60 * 1000),
        createdAt: new Date(Date.now() - 180 * 24 * 60 * 60 * 1000),
        updatedAt: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000),
      },
      {
        id: 'user-2',
        email: 'maria@hospital.com',
        name: 'María López',
        role: this.getMockRoles()[1],
        status: 'active',
        department: 'UCI',
        lastLogin: new Date(Date.now() - 30 * 60 * 1000),
        createdAt: new Date(Date.now() - 90 * 24 * 60 * 60 * 1000),
        updatedAt: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000),
      },
      {
        id: 'user-3',
        email: 'juan@hospital.com',
        name: 'Juan Pérez',
        role: this.getMockRoles()[2],
        status: 'active',
        department: 'Mantenimiento',
        lastLogin: new Date(Date.now() - 4 * 60 * 60 * 1000),
        createdAt: new Date(Date.now() - 60 * 24 * 60 * 60 * 1000),
        updatedAt: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000),
      },
    ];
  }

  private getMockRoles(): Role[] {
    return [
      {
        id: 'role-admin',
        name: 'Administrador',
        description: 'Acceso completo al sistema',
        permissions: [
          { id: 'p1', name: 'admin.all', description: 'Acceso total', resource: '*', action: 'admin' },
        ],
        isSystem: true,
        userCount: 2,
        createdAt: new Date(),
        updatedAt: new Date(),
      },
      {
        id: 'role-engineer',
        name: 'Ingeniero Biomédico',
        description: 'Gestión de equipos y mantenimiento',
        permissions: [
          { id: 'p2', name: 'devices.read', description: 'Ver equipos', resource: 'devices', action: 'read' },
          { id: 'p3', name: 'devices.write', description: 'Editar equipos', resource: 'devices', action: 'write' },
          { id: 'p4', name: 'workorders.read', description: 'Ver órdenes', resource: 'workorders', action: 'read' },
          { id: 'p5', name: 'workorders.write', description: 'Crear órdenes', resource: 'workorders', action: 'write' },
        ],
        isSystem: true,
        userCount: 5,
        createdAt: new Date(),
        updatedAt: new Date(),
      },
      {
        id: 'role-technician',
        name: 'Técnico',
        description: 'Ejecución de mantenimientos',
        permissions: [
          { id: 'p6', name: 'workorders.read', description: 'Ver órdenes', resource: 'workorders', action: 'read' },
          { id: 'p7', name: 'workorders.write', description: 'Actualizar órdenes', resource: 'workorders', action: 'write' },
        ],
        isSystem: true,
        userCount: 8,
        createdAt: new Date(),
        updatedAt: new Date(),
      },
    ];
  }

  private getMockSettings(): SystemSetting[] {
    return [
      {
        id: 's1',
        key: 'system.name',
        label: 'Nombre del Sistema',
        value: 'EREN - Hospital Platform',
        type: 'string',
        category: 'general',
        description: 'Nombre visible de la plataforma',
        isPublic: true,
        updatedAt: new Date(),
        updatedBy: 'admin',
      },
      {
        id: 's2',
        key: 'notifications.email',
        label: 'Notificaciones por Email',
        value: true,
        type: 'boolean',
        category: 'notifications',
        description: 'Habilitar envío de emails',
        isPublic: false,
        updatedAt: new Date(),
        updatedBy: 'admin',
      },
      {
        id: 's3',
        key: 'session.timeout',
        label: 'Timeout de Sesión (min)',
        value: 30,
        type: 'number',
        category: 'security',
        description: 'Tiempo de inactividad antes de cerrar sesión',
        isPublic: false,
        updatedAt: new Date(),
        updatedBy: 'admin',
      },
    ];
  }

  private getMockAuditLogs(): AuditLog[] {
    return [
      {
        id: 'audit-1',
        timestamp: new Date(Date.now() - 10 * 60 * 1000),
        userId: 'user-1',
        userName: 'Carlos García',
        action: 'update',
        resource: 'workorder',
        resourceId: 'WO-042',
        description: 'Actualizó orden de trabajo WO-042',
      },
      {
        id: 'audit-2',
        timestamp: new Date(Date.now() - 30 * 60 * 1000),
        userId: 'user-2',
        userName: 'María López',
        action: 'create',
        resource: 'incident',
        resourceId: 'INC-024',
        description: 'Reportó incidente INC-024',
      },
      {
        id: 'audit-3',
        timestamp: new Date(Date.now() - 1 * 60 * 60 * 1000),
        userId: 'user-1',
        userName: 'Carlos García',
        action: 'login',
        resource: 'session',
        description: 'Inició sesión',
        ipAddress: '192.168.1.100',
      },
    ];
  }
}

export const adminService = new AdminService();
