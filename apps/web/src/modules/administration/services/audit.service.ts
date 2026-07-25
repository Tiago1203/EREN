/**
 * PHASE 7 - EPIC 5: Audit Service
 * Consulta logs de auditoría para el panel admin
 * Integración: EPIC 1 (audit logs)
 */

import { supabase } from "@/lib/supabase";

export interface AuditLogEntry {
  entry_id: string;
  timestamp: string;
  user_id: string;
  user_email: string;
  action: string;
  category: string;
  resource_type: string;
  resource_id: string;
  details: Record<string, unknown>;
  ip_address: string;
  user_agent: string;
  session_id: string;
  tenant_id?: string;
}

export interface AuditFilters {
  start_date?: string;
  end_date?: string;
  user_id?: string;
  action?: string;
  category?: string;
  resource_type?: string;
  resource_id?: string;
  tenant_id?: string;
}

class AuditService {
  async queryLogs(
    filters: AuditFilters,
    limit: number = 100,
    offset: number = 0
  ): Promise<{ entries: AuditLogEntry[]; count: number }> {
    let query = supabase
      .from("audit_logs")
      .select("*", { count: "exact" })
      .order("timestamp", { ascending: false })
      .range(offset, offset + limit - 1);

    if (filters.start_date) {
      query = query.gte("timestamp", filters.start_date);
    }
    if (filters.end_date) {
      query = query.lte("timestamp", filters.end_date);
    }
    if (filters.user_id) {
      query = query.eq("user_id", filters.user_id);
    }
    if (filters.action) {
      query = query.eq("action", filters.action);
    }
    if (filters.category) {
      query = query.eq("category", filters.category);
    }
    if (filters.resource_type) {
      query = query.eq("resource_type", filters.resource_type);
    }
    if (filters.tenant_id) {
      query = query.eq("tenant_id", filters.tenant_id);
    }

    const { data, error, count } = await query;
    if (error) throw error;

    return { entries: data || [], count: count || 0 };
  }

  async getEntry(entryId: string): Promise<AuditLogEntry | null> {
    const { data, error } = await supabase
      .from("audit_logs")
      .select("*")
      .eq("entry_id", entryId)
      .single();

    if (error) return null;
    return data;
  }

  async exportLogs(
    filters: AuditFilters,
    format: "csv" | "json" | "pdf"
  ): Promise<Blob> {
    const { entries } = await this.queryLogs(filters, 10000, 0);

    if (format === "json") {
      return new Blob([JSON.stringify(entries, null, 2)], {
        type: "application/json",
      });
    }

    if (format === "csv") {
      const headers = [
        "ID", "Timestamp", "User", "Action", "Category",
        "Resource Type", "Resource ID", "Tenant ID", "IP Address",
      ];
      const rows = entries.map(e => [
        e.entry_id,
        e.timestamp,
        e.user_email,
        e.action,
        e.category,
        e.resource_type,
        e.resource_id,
        e.tenant_id || "",
        e.ip_address,
      ]);
      const csv = [headers, ...rows].map(r => r.join(",")).join("\n");
      return new Blob([csv], { type: "text/csv" });
    }

    // PDF: return JSON for now (real impl would use a PDF library)
    return new Blob([JSON.stringify(entries)], { type: "application/json" });
  }

  async getAuditSummary(tenantId?: string): Promise<{
    total_entries: number;
    by_category: Record<string, number>;
    by_action: Record<string, number>;
    recent_count: number;
  }> {
    const { entries, count } = await this.queryLogs(
      { tenant_id: tenantId },
      1000, 0
    );

    const since24h = entries.filter(e => {
      const diff = Date.now() - new Date(e.timestamp).getTime();
      return diff < 24 * 60 * 60 * 1000;
    }).length;

    const by_category: Record<string, number> = {};
    const by_action: Record<string, number> = {};

    for (const entry of entries) {
      by_category[entry.category] = (by_category[entry.category] || 0) + 1;
      by_action[entry.action] = (by_action[entry.action] || 0) + 1;
    }

    return {
      total_entries: count,
      by_category,
      by_action,
      recent_count: since24h,
    };
  }
}

export const auditService = new AuditService();
