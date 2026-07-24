/**
 * Tipos para el módulo Analytics
 */

// ============== METRICS ==============

export type Trend = 'up' | 'down' | 'stable';
export type MetricFormat = 'number' | 'percentage' | 'currency' | 'time';
export type MetricStatus = 'success' | 'warning' | 'danger' | 'info';

export interface Metric {
  id: string;
  label: string;
  value: number;
  previousValue?: number;
  unit?: string;
  format: MetricFormat;
  trend?: Trend;
  trendValue?: number;
  status?: MetricStatus;
  description?: string;
}

export interface MetricDefinition {
  id: string;
  name: string;
  description: string;
  unit: string;
  format: MetricFormat;
  aggregation: 'sum' | 'avg' | 'count' | 'min' | 'max';
  dataSource: DataSource;
  thresholds?: MetricThreshold[];
}

export interface MetricThreshold {
  min?: number;
  max?: number;
  status: MetricStatus;
}

// ============== DATE RANGE ==============

export interface DateRange {
  start: Date;
  end: Date;
}

export interface DateRangePreset {
  label: string;
  value: string;
  getRange: () => DateRange;
}

// ============== CHARTS ==============

export type ChartType = 'line' | 'bar' | 'pie' | 'area' | 'scatter' | 'table' | 'gauge';

export interface ChartConfig {
  id: string;
  title: string;
  type: ChartType;
  dataSource: DataSource;
  metrics: string[];
  dimensions?: string[];
  options?: ChartOptions;
}

export interface ChartData {
  labels: string[];
  datasets: Dataset[];
}

export interface Dataset {
  name: string;
  data: number[];
  color?: string;
}

export interface ChartOptions {
  showLegend?: boolean;
  showGrid?: boolean;
  showLabels?: boolean;
  animated?: boolean;
}

// ============== DATA SOURCE ==============

export type DataSource = 'devices' | 'incidents' | 'workorders' | 'maintenance' | 'staffing';

// ============== ANALYTICS STATE ==============

export interface AnalyticsState {
  metrics: Metric[];
  charts: ChartConfig[];
  chartData: Record<string, ChartData>;
  dateRange: DateRange;
  loading: boolean;
  error: string | null;
}

// ============== KPI ==============

export interface KPI {
  id: string;
  name: string;
  value: number;
  target?: number;
  status: MetricStatus;
  trend: Trend;
  period: 'day' | 'week' | 'month' | 'year';
}

// ============== TREND ==============

export interface Trend {
  metricId: string;
  direction: 'up' | 'down' | 'stable';
  changePercent: number;
  changeValue: number;
  forecast?: number[];
}

// ============== COMPARISON ==============

export interface Comparison {
  metricId: string;
  current: number;
  previous: number;
  change: number;
  changePercent: number;
}
