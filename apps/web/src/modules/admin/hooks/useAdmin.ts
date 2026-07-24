'use client';

import { useCallback, useEffect } from 'react';
import { useAdminStore } from '../stores/admin.store';
import { adminService } from '../services/admin.service';
import type { User, Role, SystemSetting, AuditLog } from '../types/admin.types';

export interface UseAdminReturn {
  // Data
  users: User[];
  roles: Role[];
  settings: SystemSetting[];
  auditLogs: AuditLog[];
  selectedUser: User | null;
  
  // State
  loading: boolean;
  error: string | null;
  
  // User Actions
  loadUsers: () => Promise<void>;
  createUser: (data: Partial<User>) => Promise<User>;
  updateUser: (id: string, data: Partial<User>) => Promise<void>;
  deleteUser: (id: string) => Promise<void>;
  selectUser: (user: User | null) => void;
  
  // Role Actions
  loadRoles: () => Promise<void>;
  
  // Settings Actions
  loadSettings: () => Promise<void>;
  updateSetting: (key: string, value: unknown) => Promise<void>;
  
  // Audit Actions
  loadAuditLogs: () => Promise<void>;
}

export function useAdmin(): UseAdminReturn {
  const {
    users,
    roles,
    settings,
    auditLogs,
    selectedUser,
    loading,
    error,
    setUsers,
    setRoles,
    setSettings,
    setAuditLogs,
    setSelectedUser,
    setLoading,
    setError,
  } = useAdminStore();

  // Load Users
  const loadUsers = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await adminService.getUsers();
      setUsers(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error loading users');
    } finally {
      setLoading(false);
    }
  }, [setUsers, setLoading, setError]);

  // Create User
  const createUser = useCallback(async (data: Partial<User>) => {
    return adminService.createUser(data);
  }, []);

  // Update User
  const updateUser = useCallback(async (id: string, data: Partial<User>) => {
    await adminService.updateUser(id, data);
    loadUsers();
  }, [loadUsers]);

  // Delete User
  const deleteUser = useCallback(async (id: string) => {
    await adminService.deleteUser(id);
    loadUsers();
  }, [loadUsers]);

  // Select User
  const selectUser = useCallback((user: User | null) => {
    setSelectedUser(user);
  }, [setSelectedUser]);

  // Load Roles
  const loadRoles = useCallback(async () => {
    try {
      const data = await adminService.getRoles();
      setRoles(data);
    } catch (err) {
      console.error('Error loading roles:', err);
    }
  }, [setRoles]);

  // Load Settings
  const loadSettings = useCallback(async () => {
    try {
      const data = await adminService.getSettings();
      setSettings(data);
    } catch (err) {
      console.error('Error loading settings:', err);
    }
  }, [setSettings]);

  // Update Setting
  const updateSetting = useCallback(async (key: string, value: unknown) => {
    await adminService.updateSetting(key, value);
    loadSettings();
  }, [loadSettings]);

  // Load Audit Logs
  const loadAuditLogs = useCallback(async () => {
    try {
      const data = await adminService.getAuditLogs();
      setAuditLogs(data);
    } catch (err) {
      console.error('Error loading audit logs:', err);
    }
  }, [setAuditLogs]);

  // Initial Load
  useEffect(() => {
    loadUsers();
    loadRoles();
    loadSettings();
    loadAuditLogs();
  }, []);

  return {
    users,
    roles,
    settings,
    auditLogs,
    selectedUser,
    loading,
    error,
    loadUsers,
    createUser,
    updateUser,
    deleteUser,
    selectUser,
    loadRoles,
    loadSettings,
    updateSetting,
    loadAuditLogs,
  };
}
