/**
 * PHASE 7 - EPIC 5: Admin Service
 * API calls para el panel de administración
 */

import { supabase } from "@/lib/supabase";

export interface SystemOverview {
  total_users: number;
  active_users: number;
  inactive_users: number;
  total_roles: number;
  total_settings: number;
  total_admin_operations: number;
  recent_operations: AdminOperation[];
}

export interface AdminOperation {
  operation_id: string;
  operation_type: string;
  performed_by: string;
  target_type: string;
  target_id: string;
  status: string;
  timestamp: string;
}

export interface User {
  user_id: string;
  email: string;
  full_name: string;
  status: "active" | "inactive" | "suspended" | "pending";
  tenant_id?: string;
  department?: string;
  role_ids: string[];
  created_at: string;
  updated_at: string;
  last_login?: string;
  failed_login_attempts: number;
  must_change_password: boolean;
}

export interface Role {
  role_id: string;
  name: string;
  role_type: string;
  description: string;
  permissions: Permission[];
  tenant_id?: string;
  is_system: boolean;
  created_at: string;
}

export interface Permission {
  permission_id: string;
  name: string;
  resource: string;
  action: string;
  description: string;
  scope: string;
}

export interface SystemSetting {
  setting_id: string;
  key: string;
  value: string;
  category: string;
  description: string;
  is_encrypted: boolean;
  is_readonly: boolean;
  updated_by?: string;
  updated_at: string;
}

export interface Tenant {
  tenant_id: string;
  name: string;
  status: string;
  subscription_tier: string;
  created_at: string;
}

class AdminService {
  private baseUrl = "/api/v1/admin";

  // ── System Overview ────────────────────────────────────
  async getOverview(): Promise<SystemOverview> {
    const { data, error } = await supabase
      .from("admin_overview")
      .select("*")
      .single();

    if (error) throw error;

    // Fallback si no hay datos en BD
    return data || {
      total_users: 0,
      active_users: 0,
      inactive_users: 0,
      total_roles: 0,
      total_settings: 0,
      total_admin_operations: 0,
      recent_operations: [],
    };
  }

  // ── Users ──────────────────────────────────────────────
  async listUsers(params?: {
    tenant_id?: string;
    status?: string;
    limit?: number;
    offset?: number;
  }): Promise<{ users: User[]; count: number }> {
    let query = supabase
      .from("admin_users")
      .select("*", { count: "exact" });

    if (params?.tenant_id) query = query.eq("tenant_id", params.tenant_id);
    if (params?.status) query = query.eq("status", params.status);
    if (params?.limit) query = query.limit(params.limit);
    if (params?.offset) query = query.range(params.offset, (params.offset + (params.limit || 50)) - 1);

    const { data, error, count } = await query;
    if (error) throw error;

    return { users: data || [], count: count || 0 };
  }

  async getUser(userId: string): Promise<User> {
    const { data, error } = await supabase
      .from("admin_users")
      .select("*")
      .eq("user_id", userId)
      .single();

    if (error) throw error;
    return data;
  }

  async createUser(payload: {
    email: string;
    full_name: string;
    role_ids?: string[];
    tenant_id?: string;
    department?: string;
  }): Promise<User> {
    const { data, error } = await supabase
      .from("admin_users")
      .insert([{
        user_id: `user-${Date.now()}`,
        email: payload.email,
        full_name: payload.full_name,
        status: "active",
        tenant_id: payload.tenant_id,
        department: payload.department,
        role_ids: payload.role_ids || [],
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        failed_login_attempts: 0,
        must_change_password: true,
      }])
      .select()
      .single();

    if (error) throw error;
    return data;
  }

  async updateUser(userId: string, updates: Partial<User>): Promise<User> {
    const { data, error } = await supabase
      .from("admin_users")
      .update({ ...updates, updated_at: new Date().toISOString() })
      .eq("user_id", userId)
      .select()
      .single();

    if (error) throw error;
    return data;
  }

  async suspendUser(userId: string): Promise<void> {
    const { error } = await supabase
      .from("admin_users")
      .update({ status: "suspended", updated_at: new Date().toISOString() })
      .eq("user_id", userId);

    if (error) throw error;
  }

  async deleteUser(userId: string): Promise<void> {
    const { error } = await supabase
      .from("admin_users")
      .delete()
      .eq("user_id", userId);

    if (error) throw error;
  }

  // ── Roles ───────────────────────────────────────────────
  async listRoles(tenantId?: string): Promise<{ roles: Role[]; count: number }> {
    let query = supabase
      .from("admin_roles")
      .select("*", { count: "exact" });

    if (tenantId) query = query.eq("tenant_id", tenantId);

    const { data, error, count } = await query;
    if (error) throw error;

    return { roles: data || [], count: count || 0 };
  }

  async createRole(payload: {
    name: string;
    role_type: string;
    description?: string;
    permissions?: Permission[];
    tenant_id?: string;
  }): Promise<Role> {
    const { data, error } = await supabase
      .from("admin_roles")
      .insert([{
        role_id: `role-${Date.now()}`,
        name: payload.name,
        role_type: payload.role_type,
        description: payload.description || "",
        permissions: payload.permissions || [],
        tenant_id: payload.tenant_id,
        is_system: !payload.tenant_id,
        created_at: new Date().toISOString(),
      }])
      .select()
      .single();

    if (error) throw error;
    return data;
  }

  async assignRole(userId: string, roleId: string): Promise<void> {
    // Obtener usuario actual
    const user = await this.getUser(userId);
    if (!user.role_ids.includes(roleId)) {
      await this.updateUser(userId, {
        role_ids: [...user.role_ids, roleId],
      });
    }
  }

  async removeRole(userId: string, roleId: string): Promise<void> {
    const user = await this.getUser(userId);
    await this.updateUser(userId, {
      role_ids: user.role_ids.filter(id => id !== roleId),
    });
  }

  // ── System Settings ────────────────────────────────────
  async getSettings(category?: string): Promise<SystemSetting[]> {
    let query = supabase.from("admin_settings").select("*");
    if (category) query = query.eq("category", category);

    const { data, error } = await query;
    if (error) throw error;
    return data || [];
  }

  async updateSetting(key: string, value: string): Promise<SystemSetting> {
    const { data, error } = await supabase
      .from("admin_settings")
      .update({
        value,
        updated_by: "admin",
        updated_at: new Date().toISOString(),
      })
      .eq("key", key)
      .select()
      .single();

    if (error) throw error;
    return data;
  }

  // ── Tenants ─────────────────────────────────────────────
  async listTenants(params?: {
    status?: string;
    limit?: number;
    offset?: number;
  }): Promise<{ tenants: Tenant[]; count: number }> {
    let query = supabase
      .from("tenants")
      .select("*", { count: "exact" });

    if (params?.status) query = query.eq("status", params.status);
    if (params?.limit) query = query.limit(params.limit);

    const { data, error, count } = await query;
    if (error) throw error;

    return { tenants: data || [], count: count || 0 };
  }
}

export const adminService = new AdminService();
