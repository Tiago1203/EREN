/**
 * Tipos para el módulo Reports
 */

// ============== REPORT ==============

export type ReportType = 'operational' | 'financial' | 'clinical' | 'maintenance' | 'custom';
export type ReportStatus = 'draft' | 'scheduled' | 'generated';
export type ExportFormat = 'pdf' | 'excel' | 'csv' | 'json' | 'png';

export interface AnalyticReport {
  id: string;
  title: string;
  description?: string;
  type: ReportType;
  config: ReportConfig;
  createdBy: string;
  createdAt: Date;
  updatedAt: Date;
  lastGenerated?: Date;
  status: ReportStatus;
  schedule?: ReportSchedule;
}

export interface ReportConfig {
  metrics: string[];
  charts: string[];
  dateRange: {
    start: Date;
    end: Date;
  };
  filters?: ReportFilters;
  grouping?: 'day' | 'week' | 'month';
  title?: string;
}

export interface ReportFilters {
  establishmentId?: string;
  departmentId?: string;
  deviceType?: string;
  status?: string[];
}

export interface ReportSchedule {
  frequency: 'daily' | 'weekly' | 'monthly';
  time: string;
  recipients: string[];
}

// ============== REPORT TEMPLATE ==============

export interface ReportTemplate {
  id: string;
  name: string;
  description: string;
  type: ReportType;
  config: Partial<ReportConfig>;
  thumbnail?: string;
}

// ============== EXPORT ==============

export interface ExportConfig {
  format: ExportFormat;
  includeCharts: boolean;
  includeRawData: boolean;
  dateRange: {
    start: Date;
    end: Date;
  };
  title?: string;
  metadata?: Record<string, string>;
}

export interface ExportJob {
  id: string;
  reportId: string;
  format: ExportFormat;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  downloadUrl?: string;
  expiresAt?: Date;
}

// ============== REPORTS STATE ==============

export interface ReportsState {
  reports: AnalyticReport[];
  templates: ReportTemplate[];
  selectedReport: AnalyticReport | null;
  loading: boolean;
  generating: boolean;
  error: string | null;
}
