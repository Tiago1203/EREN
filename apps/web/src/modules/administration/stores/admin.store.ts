/**
 * PHASE 7 - EPIC 5: Admin Store
 * Zustand store para estado del panel administrativo
 * Integración: EPIC 4 (observability)
 */

import { create } from "zustand";
import {
  adminService,
  SystemOverview,
  User,
  Role,
  SystemSetting,
} from "../services/admin.service";

type AdminTab =
  | "overview"
  | "users"
  | "roles"
  | "settings"
  | "tenants"
  | "monitoring"
  | "audit";

interface AdminState {
  // Navigation
  activeTab: AdminTab;
  setActiveTab: (tab: AdminTab) => void;

  // Overview
  overview: SystemOverview | null;
  loadingOverview: boolean;
  fetchOverview: () => Promise<void>;

  // Users
  users: User[];
  usersLoading: boolean;
  usersCount: number;
  userFilters: Record<string, string>;
  setUserFilters: (filters: Record<string, string>) => void;
  fetchUsers: (params?: { tenant_id?: string; status?: string }) => Promise<void>;
  createUser: (payload: Parameters<typeof adminService.createUser>[0]) => Promise<void>;
  updateUser: (userId: string, updates: Partial<User>) => Promise<void>;
  suspendUser: (userId: string) => Promise<void>;

  // Roles
  roles: Role[];
  rolesLoading: boolean;
  fetchRoles: (tenantId?: string) => Promise<void>;
  createRole: (payload: Parameters<typeof adminService.createRole>[0]) => Promise<void>;

  // Settings
  settings: SystemSetting[];
  settingsLoading: boolean;
  fetchSettings: (category?: string) => Promise<void>;
  updateSetting: (key: string, value: string) => Promise<void>;

  // Tenants
  tenants: Array<{ tenant_id: string; name: string; status: string; subscription_tier: string }>;
  tenantsLoading: boolean;
  tenantsCount: number;
  fetchTenants: (params?: { status?: string }) => Promise<void>;

  // Error handling
  error: string | null;
  setError: (error: string | null) => void;
}

export const useAdminStore = create<AdminState>((set, get) => ({
  // ── Navigation ──────────────────────────────────────────
  activeTab: "overview",
  setActiveTab: (tab) => set({ activeTab: tab }),

  // ── Overview ───────────────────────────────────────────
  overview: null,
  loadingOverview: false,
  fetchOverview: async () => {
    set({ loadingOverview: true, error: null });
    try {
      const overview = await adminService.getOverview();
      set({ overview, loadingOverview: false });
    } catch (err) {
      set({
        error: err instanceof Error ? err.message : "Failed to load overview",
        loadingOverview: false,
      });
    }
  },

  // ── Users ───────────────────────────────────────────────
  users: [],
  usersLoading: false,
  usersCount: 0,
  userFilters: {},
  setUserFilters: (filters) => set({ userFilters: filters }),
  fetchUsers: async (params) => {
    set({ usersLoading: true, error: null });
    try {
      const result = await adminService.listUsers({
        tenant_id: params?.tenant_id,
        status: params?.status,
      });
      set({ users: result.users, usersCount: result.count, usersLoading: false });
    } catch (err) {
      set({
        error: err instanceof Error ? err.message : "Failed to load users",
        usersLoading: false,
      });
    }
  },
  createUser: async (payload) => {
    try {
      await adminService.createUser(payload);
      await get().fetchUsers();
    } catch (err) {
      set({ error: err instanceof Error ? err.message : "Failed to create user" });
    }
  },
  updateUser: async (userId, updates) => {
    try {
      await adminService.updateUser(userId, updates);
      await get().fetchUsers();
    } catch (err) {
      set({ error: err instanceof Error ? err.message : "Failed to update user" });
    }
  },
  suspendUser: async (userId) => {
    try {
      await adminService.suspendUser(userId);
      await get().fetchUsers();
    } catch (err) {
      set({ error: err instanceof Error ? err.message : "Failed to suspend user" });
    }
  },

  // ── Roles ───────────────────────────────────────────────
  roles: [],
  rolesLoading: false,
  fetchRoles: async (tenantId) => {
    set({ rolesLoading: true, error: null });
    try {
      const result = await adminService.listRoles(tenantId);
      set({ roles: result.roles, rolesLoading: false });
    } catch (err) {
      set({ error: err instanceof Error ? err.message : "Failed to load roles", rolesLoading: false });
    }
  },
  createRole: async (payload) => {
    try {
      await adminService.createRole(payload);
      await get().fetchRoles();
    } catch (err) {
      set({ error: err instanceof Error ? err.message : "Failed to create role" });
    }
  },

  // ── Settings ────────────────────────────────────────────
  settings: [],
  settingsLoading: false,
  fetchSettings: async (category) => {
    set({ settingsLoading: true, error: null });
    try {
      const settings = await adminService.getSettings(category);
      set({ settings, settingsLoading: false });
    } catch (err) {
      set({ error: err instanceof Error ? err.message : "Failed to load settings", settingsLoading: false });
    }
  },
  updateSetting: async (key, value) => {
    try {
      await adminService.updateSetting(key, value);
      await get().fetchSettings();
    } catch (err) {
      set({ error: err instanceof Error ? err.message : "Failed to update setting" });
    }
  },

  // ── Tenants ─────────────────────────────────────────────
  tenants: [],
  tenantsLoading: false,
  tenantsCount: 0,
  fetchTenants: async (params) => {
    set({ tenantsLoading: true, error: null });
    try {
      const result = await adminService.listTenants(params);
      set({ tenants: result.tenants, tenantsCount: result.count, tenantsLoading: false });
    } catch (err) {
      set({ error: err instanceof Error ? err.message : "Failed to load tenants", tenantsLoading: false });
    }
  },

  // ── Error ──────────────────────────────────────────────
  error: null,
  setError: (error) => set({ error }),
}));
