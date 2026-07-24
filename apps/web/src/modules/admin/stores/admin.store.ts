'use client';

import { create } from 'zustand';
import type { User, Role, SystemSetting, AuditLog, AdminState } from '../types/admin.types';

interface AdminStore extends AdminState {
  // Actions - Users
  setUsers: (users: User[]) => void;
  addUser: (user: User) => void;
  updateUser: (id: string, update: Partial<User>) => void;
  removeUser: (id: string) => void;
  setSelectedUser: (user: User | null) => void;

  // Actions - Roles
  setRoles: (roles: Role[]) => void;
  addRole: (role: Role) => void;
  updateRole: (id: string, update: Partial<Role>) => void;

  // Actions - Settings
  setSettings: (settings: SystemSetting[]) => void;
  updateSetting: (key: string, value: unknown) => void;

  // Actions - Audit
  setAuditLogs: (logs: AuditLog[]) => void;
  addAuditLog: (log: AuditLog) => void;

  // Actions - State
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;

  // Actions - Reset
  reset: () => void;
}

const initialState: AdminState = {
  users: [],
  roles: [],
  settings: [],
  auditLogs: [],
  selectedUser: null,
  loading: false,
  error: null,
};

export const useAdminStore = create<AdminStore>((set) => ({
  ...initialState,

  // Users
  setUsers: (users) => set({ users }),
  addUser: (user) => set((state) => ({ users: [...state.users, user] })),
  updateUser: (id, update) => set((state) => ({
    users: state.users.map((u) => (u.id === id ? { ...u, ...update } : u)),
    selectedUser: state.selectedUser?.id === id
      ? { ...state.selectedUser, ...update }
      : state.selectedUser,
  })),
  removeUser: (id) => set((state) => ({
    users: state.users.filter((u) => u.id !== id),
    selectedUser: state.selectedUser?.id === id ? null : state.selectedUser,
  })),
  setSelectedUser: (user) => set({ selectedUser: user }),

  // Roles
  setRoles: (roles) => set({ roles }),
  addRole: (role) => set((state) => ({ roles: [...state.roles, role] })),
  updateRole: (id, update) => set((state) => ({
    roles: state.roles.map((r) => (r.id === id ? { ...r, ...update } : r)),
  })),

  // Settings
  setSettings: (settings) => set({ settings }),
  updateSetting: (key, value) => set((state) => ({
    settings: state.settings.map((s) =>
      s.key === key ? { ...s, value, updatedAt: new Date() } : s
    ),
  })),

  // Audit
  setAuditLogs: (logs) => set({ auditLogs: logs }),
  addAuditLog: (log) => set((state) => ({
    auditLogs: [log, ...state.auditLogs],
  })),

  // State
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),

  // Reset
  reset: () => set(initialState),
}));
