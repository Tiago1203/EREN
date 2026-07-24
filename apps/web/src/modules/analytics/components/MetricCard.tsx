'use client';

import type { Metric, Trend } from '../types/analytics.types';

interface MetricCardProps {
  metric: Metric;
  onClick?: () => void;
}

export function MetricCard({ metric, onClick }: MetricCardProps) {
  const trendIcons: Record<Trend, string> = {
    up: '↑',
    down: '↓',
    stable: '→',
  };

  const trendColors: Record<Trend, string> = {
    up: 'text-green-600',
    down: 'text-red-600',
    stable: 'text-gray-500',
  };

  const statusColors: Record<string, string> = {
    success: 'border-l-green-500',
    warning: 'border-l-yellow-500',
    danger: 'border-l-red-500',
    info: 'border-l-blue-500',
  };

  const formatValue = (value: number, format: string, unit?: string): string => {
    let formatted: string;
    switch (format) {
      case 'percentage':
        formatted = `${value.toFixed(1)}%`;
        break;
      case 'currency':
        formatted = `$${value.toLocaleString()}`;
        break;
      case 'time':
        formatted = `${value.toFixed(1)}`;
        break;
      default:
        formatted = value.toLocaleString();
    }
    return unit ? `${formatted} ${unit}` : formatted;
  };

  return (
    <div
      className={`card p-4 border-l-4 ${statusColors[metric.status || 'info']} hover:shadow-md transition-shadow cursor-pointer`}
      onClick={onClick}
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-muted">{metric.label}</p>
          <p className="text-2xl font-bold mt-1">
            {formatValue(metric.value, metric.format, metric.unit)}
          </p>
        </div>
        
        {metric.trend && (
          <div className={`flex flex-col items-end ${trendColors[metric.trend]}`}>
            <span className="text-lg">{trendIcons[metric.trend]}</span>
            {metric.trendValue !== undefined && (
              <span className="text-sm font-medium">
                {metric.trend > 0 ? '+' : ''}{metric.trendValue.toFixed(1)}%
              </span>
            )}
          </div>
        )}
      </div>

      {metric.previousValue !== undefined && (
        <div className="mt-3 pt-3 border-t border-[var(--border)]">
          <p className="text-xs text-muted">
            Anterior: {formatValue(metric.previousValue, metric.format, metric.unit)}
          </p>
        </div>
      )}
    </div>
  );
}

export default MetricCard;
