# EPIC 5: Analytics & Reports

*Versión: 1.0.0*
*Fecha: 2026-07-24*

---

## Objetivo

**Transformar datos en insights actionable mediante visualización y reportes.**

EPIC 5 es responsable de:
- Crear dashboards analíticos interactivos
- Motor de generación de reportes
- Exportación de datos en múltiples formatos
- Métricas KPIs avanzados
- Consumir datos de PHASE 1
- Generar insights con PHASE 3

---

## Dependencias

```
FASE 5 (Cognitive Multi-Agent System)
        │
        └── PHASE 3 (Clinical Intelligence)
                │
                ├── Reasoning Engine
                ├── Evidence Retrieval
                ├── Confidence Engine
                └── Decision Engine
                        │
                        ▼
                   PHASE 6 (Hospital Platform)
                        │
                        ▼
                   EPIC 0 (Platform Foundation)
                        │
                        ▼
                   EPIC 1 (Dashboard)
                        │
                        ▼
                   EPIC 2 (Operations)
                        │
                        ▼
                   EPIC 4 (Knowledge)
                        │
                        ▼
                   EPIC 5 (Analytics & Reports)
                        │
                        ▼
                   EPIC 6 (Notifications)
```

---

## Arquitectura

```
┌─────────────────────────────────────────────────────────────────────────┐
│                   EPIC 5: Analytics & Reports                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    ANALYTICS MODULE                                │   │
│  │  ├── components/ ──────────── DashboardGrid, MetricCard, Charts │   │
│  │  ├── pages/ ─────────────── page.tsx (Analytics)               │   │
│  │  ├── hooks/ ─────────────── useAnalytics, useMetrics           │   │
│  │  ├── services/ ──────────── AnalyticsService, MetricService     │   │
│  │  ├── stores/ ───────────── analytics.store                      │   │
│  │  ├── types/ ────────────── analytics.types                      │   │
│  │  └── utils/ ────────────── chart-config                         │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    REPORTS MODULE                                 │   │
│  │  ├── components/ ────────── ReportBuilder, ReportList, Export   │   │
│  │  ├── services/ ─────────── ReportService, ExportService         │   │
│  │  ├── types/ ────────────── report.types                         │   │
│  │  └── utils/ ────────────── template-engine                      │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    INTEGRATION LAYER                               │   │
│  │  ├── PHASE 1 Data ──────────── Business Domain                  │   │
│  │  ├── PHASE 3 Intelligence ─── Clinical Intelligence             │   │
│  │  └── Chart Library ──────────── Visualization                    │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Estructura de Archivos

```
apps/web/src/modules/
├── analytics/                        # Módulo Analytics
│   ├── components/
│   │   ├── AnalyticsDashboard.tsx
│   │   ├── MetricCard.tsx
│   │   ├── MetricGrid.tsx
│   │   ├── ChartContainer.tsx
│   │   ├── LineChart.tsx
│   │   ├── BarChart.tsx
│   │   ├── PieChart.tsx
│   │   ├── TableChart.tsx
│   │   └── DateRangePicker.tsx
│   ├── hooks/
│   │   ├── useAnalytics.ts
│   │   └── useMetrics.ts
│   ├── services/
│   │   ├── analytics.service.ts
│   │   └── metric.service.ts
│   ├── stores/
│   │   └── analytics.store.ts
│   ├── types/
│   │   └── analytics.types.ts
│   └── pages/
│       └── page.tsx

├── reports/                         # Módulo Reports
│   ├── components/
│   │   ├── ReportBuilder.tsx
│   │   ├── ReportList.tsx
│   │   ├── ReportCard.tsx
│   │   ├── ReportViewer.tsx
│   │   └── ExportOptions.tsx
│   ├── services/
│   │   ├── report.service.ts
│   │   └── export.service.ts
│   ├── types/
│   │   └── report.types.ts
│   └── pages/
│       └── page.tsx
```

---

## Componentes

### 1. AnalyticsDashboard

Dashboard principal de analytics.

```typescript
// modules/analytics/components/AnalyticsDashboard.tsx
export interface AnalyticsDashboardProps {
  metrics: Metric[];
  charts: ChartConfig[];
  dateRange: DateRange;
  onDateRangeChange: (range: DateRange) => void;
}
```

### 2. MetricCard / MetricGrid

Tarjetas de métricas con tendencias.

```typescript
// modules/analytics/components/MetricCard.tsx
export interface MetricCardProps {
  metric: Metric;
  onClick?: () => void;
}

export interface Metric {
  id: string;
  label: string;
  value: number;
  previousValue?: number;
  unit?: string;
  format?: 'number' | 'percentage' | 'currency' | 'time';
  trend?: 'up' | 'down' | 'stable';
  trendValue?: number;
  status?: 'success' | 'warning' | 'danger' | 'info';
}
```

### 3. Chart Components

Componentes de visualización.

```typescript
// modules/analytics/components/ChartContainer.tsx
export interface ChartContainerProps {
  title: string;
  chart: ChartConfig;
  loading?: boolean;
}

export interface ChartConfig {
  id: string;
  type: 'line' | 'bar' | 'pie' | 'area' | 'scatter' | 'table';
  data: ChartData;
  options?: ChartOptions;
}

export interface ChartData {
  labels: string[];
  datasets: Dataset[];
}
```

### 4. DateRangePicker

Selector de rango de fechas.

```typescript
// modules/analytics/components/DateRangePicker.tsx
export interface DateRangePickerProps {
  value: DateRange;
  onChange: (range: DateRange) => void;
  presets?: DateRangePreset[];
}

export interface DateRange {
  start: Date;
  end: Date;
}
```

### 5. ReportBuilder

Constructor de reportes.

```typescript
// modules/analytics/components/ReportBuilder.tsx
export interface ReportBuilderProps {
  onGenerate: (config: ReportConfig) => void;
}
```

### 6. ReportList / ReportCard

Lista de reportes guardados.

```typescript
// modules/analytics/components/ReportCard.tsx
export interface ReportCardProps {
  report: AnalyticReport;
  onClick?: () => void;
  onExport?: (format: ExportFormat) => void;
  onDelete?: () => void;
}
```

### 7. ExportOptions

Opciones de exportación.

```typescript
// modules/analytics/components/ExportOptions.tsx
export interface ExportOptionsProps {
  formats: ExportFormat[];
  onExport: (format: ExportFormat) => void;
}

export type ExportFormat = 'pdf' | 'excel' | 'csv' | 'json';
```

---

## Implementaciones

### AnalyticsService

```typescript
// modules/analytics/services/analytics.service.ts
export class AnalyticsService {
  async getDashboardMetrics(dateRange: DateRange): Promise<Metric[]>;
  async getChartData(chartId: string, dateRange: DateRange): Promise<ChartData>;
  async getKPIs(dateRange: DateRange): Promise<KPI[]>;
  async getTrends(dateRange: DateRange): Promise<Trend[]>;
  async getComparisons(dateRange: DateRange): Promise<Comparison[]>;
}
```

### ReportService

```typescript
// modules/analytics/services/report.service.ts
export class ReportService {
  async getReports(): Promise<AnalyticReport[]>;
  async getReport(id: string): Promise<AnalyticReport | null>;
  async createReport(config: ReportConfig): Promise<AnalyticReport>;
  async updateReport(id: string, config: ReportConfig): Promise<AnalyticReport>;
  async deleteReport(id: string): Promise<void>;
  async generateReport(id: string): Promise<ReportData>;
}
```

### ExportService

```typescript
// modules/analytics/services/export.service.ts
export class ExportService {
  async exportPDF(report: AnalyticReport): Promise<Blob>;
  async exportExcel(data: any): Promise<Blob>;
  async exportCSV(data: any): Promise<Blob>;
  async exportJSON(data: any): Promise<Blob>;
}
```

### MetricCalculator

```typescript
// modules/analytics/services/metric.service.ts
export class MetricCalculator {
  calculateTrend(current: number, previous: number): Trend;
  calculatePercentageChange(current: number, previous: number): number;
  aggregateMetrics(metrics: Metric[], period: Period): AggregatedMetric[];
}
```

---

## Domain Objects

### AnalyticReport

```typescript
// modules/analytics/types/report.types.ts
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
  status: 'draft' | 'scheduled' | 'generated';
  schedule?: ReportSchedule;
}

export type ReportType = 'operational' | 'financial' | 'clinical' | 'maintenance' | 'custom';

export interface ReportConfig {
  metrics: string[];
  charts: ChartConfig[];
  dateRange: DateRange;
  filters?: ReportFilters;
  grouping?: 'day' | 'week' | 'month';
}

export interface ReportSchedule {
  frequency: 'daily' | 'weekly' | 'monthly';
  time: string;
  recipients: string[];
}
```

### ChartConfig

```typescript
export interface ChartConfig {
  id: string;
  title: string;
  type: ChartType;
  dataSource: DataSource;
  metrics: string[];
  dimensions?: string[];
  options?: ChartOptions;
}

export type ChartType = 'line' | 'bar' | 'pie' | 'area' | 'scatter' | 'table' | 'gauge';
```

### MetricDefinition

```typescript
export interface MetricDefinition {
  id: string;
  name: string;
  description: string;
  unit: string;
  format: MetricFormat;
  aggregation: 'sum' | 'avg' | 'count' | 'min' | 'max';
  dataSource: DataSource;
  calculation?: string;
  thresholds?: MetricThreshold[];
}

export interface MetricThreshold {
  min?: number;
  max?: number;
  status: 'success' | 'warning' | 'danger';
}
```

### ExportConfig

```typescript
export interface ExportConfig {
  format: ExportFormat;
  includeCharts: boolean;
  includeRawData: boolean;
  dateRange: DateRange;
  title?: string;
  metadata?: Record<string, string>;
}

export type ExportFormat = 'pdf' | 'excel' | 'csv' | 'json' | 'png';
```

---

## Integración con PHASE 1 y PHASE 3

```
PHASE 1 (Business Domain)
        │
        ├── Device Context ────→ Device Metrics
        ├── Incident Context ──→ Incident Analytics
        ├── WorkOrder Context ──→ Maintenance KPIs
        └── Capacity Context ───→ Resource Utilization
                │
                ▼
PHASE 3 (Clinical Intelligence)
        │
        ├── Reasoning Engine ────→ Trend Analysis
        ├── Evidence ───────────→ Clinical Insights
        └── Decision Engine ────→ Recommendations
                │
                ▼
           EPIC 5 (Analytics)
                │
                ├── AnalyticsDashboard → Visualización
                ├── ReportService ────→ Reportes
                └── ExportService ────→ Exportación
```

---

## Estado

**🚧 EN PROGRESO**

EPIC 5 está en desarrollo.

---

## Tareas

- [x] Crear documentación EPIC 5
- [x] Crear tipos para analytics
- [x] Crear servicios del módulo
- [x] Crear store Zustand
- [x] Crear hooks
- [x] Crear componentes de charts
- [x] Crear componentes de reportes
- [x] Crear página de Analytics
- [ ] Crear tests unitarios
- [ ] Integrar con PHASE 1 y PHASE 3

---

## Próximos Pasos

- EPIC 6: Notifications & Workspace
- EPIC 7: Administration & Connectors

---

*EREN PHASE 6 - EPIC 5*
*Architecture Board - 2026-07-24*
