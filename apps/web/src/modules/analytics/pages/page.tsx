'use client';

import { useState } from 'react';
import { useAnalytics } from '../hooks/useAnalytics';
import { MetricGrid } from '../components/MetricGrid';
import { ChartContainer } from '../components/ChartContainer';
import type { DateRange } from '../types/analytics.types';

export default function AnalyticsPage() {
  const {
    metrics,
    chartData,
    dateRange,
    loading,
    error,
    loadMetrics,
    loadChartData,
    setDateRange,
  } = useAnalytics();

  const [selectedPreset, setSelectedPreset] = useState('30d');

  const datePresets = [
    { label: 'Últimos 7 días', value: '7d', days: 7 },
    { label: 'Últimos 30 días', value: '30d', days: 30 },
    { label: 'Últimos 90 días', value: '90d', days: 90 },
    { label: 'Este año', value: 'year', days: 365 },
  ];

  const handlePresetChange = (preset: string) => {
    setSelectedPreset(preset);
    const config = datePresets.find(p => p.value === preset);
    if (config) {
      const range: DateRange = {
        start: new Date(Date.now() - config.days * 24 * 60 * 60 * 1000),
        end: new Date(),
      };
      setDateRange(range);
      loadMetrics(range);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">Analytics</h1>
          <p className="text-sm text-muted mt-1">
            Métricas y análisis de operaciones
          </p>
        </div>

        {/* Date Range Selector */}
        <div className="flex gap-2">
          {datePresets.map((preset) => (
            <button
              key={preset.value}
              onClick={() => handlePresetChange(preset.value)}
              className={`px-3 py-1.5 text-sm rounded-lg transition-colors ${
                selectedPreset === preset.value
                  ? 'bg-[var(--primary)] text-white'
                  : 'bg-[var(--card)] border border-[var(--border)] hover:bg-[var(--background)]'
              }`}
            >
              {preset.label}
            </button>
          ))}
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="p-4 bg-red-100 border border-red-300 rounded-lg text-red-700">
          {error}
        </div>
      )}

      {/* Metrics Grid */}
      <section>
        <h2 className="text-lg font-semibold mb-4">Métricas Clave</h2>
        <MetricGrid metrics={metrics} loading={loading} />
      </section>

      {/* Charts */}
      <section className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div>
          <ChartContainer
            title="Mantenimientos por Tipo"
            chartId="mantenimientos"
            type="bar"
            data={chartData.mantenimientos}
            loading={loading}
          />
        </div>
        <div>
          <ChartContainer
            title="Incidentes"
            chartId="incidentes"
            type="line"
            data={chartData.incidentes}
            loading={loading}
          />
        </div>
        <div>
          <ChartContainer
            title="Disponibilidad"
            chartId="disponibilidad"
            type="line"
            data={chartData.disponibilidad}
            loading={loading}
          />
        </div>
        <div>
          <ChartContainer
            title="Costos de Mantenimiento"
            chartId="costos"
            type="bar"
            data={chartData.costos}
            loading={loading}
          />
        </div>
      </section>

      {/* Summary */}
      <section className="card p-6">
        <h2 className="text-lg font-semibold mb-4">Resumen del Período</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="p-4 bg-[var(--background)] rounded-lg">
            <p className="text-sm text-muted">Período</p>
            <p className="text-lg font-medium">
              {datePresets.find(p => p.value === selectedPreset)?.label}
            </p>
          </div>
          <div className="p-4 bg-[var(--background)] rounded-lg">
            <p className="text-sm text-muted">Total Equipos</p>
            <p className="text-lg font-medium">
              {metrics.find(m => m.id === 'total-equipos')?.value || 0}
            </p>
          </div>
          <div className="p-4 bg-[var(--background)] rounded-lg">
            <p className="text-sm text-muted">Disponibilidad</p>
            <p className="text-lg font-medium text-green-600">
              {metrics.find(m => m.id === 'disponibilidad')?.value.toFixed(1) || 0}%
            </p>
          </div>
          <div className="p-4 bg-[var(--background)] rounded-lg">
            <p className="text-sm text-muted">Cumplimiento PM</p>
            <p className="text-lg font-medium text-blue-600">
              {metrics.find(m => m.id === 'cumplimiento')?.value.toFixed(1) || 0}%
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}
