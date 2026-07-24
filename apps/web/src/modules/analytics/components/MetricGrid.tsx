'use client';

import { MetricCard } from './MetricCard';
import type { Metric } from '../types/analytics.types';

interface MetricGridProps {
  metrics: Metric[];
  loading?: boolean;
  onMetricClick?: (metric: Metric) => void;
}

export function MetricGrid({ metrics, loading, onMetricClick }: MetricGridProps) {
  if (loading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {[1, 2, 3, 4, 5, 6, 7, 8].map((i) => (
          <div key={i} className="card p-4 animate-pulse">
            <div className="h-4 bg-gray-200 rounded w-1/2 mb-2" />
            <div className="h-8 bg-gray-100 rounded w-3/4" />
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {metrics.map((metric) => (
        <MetricCard
          key={metric.id}
          metric={metric}
          onClick={() => onMetricClick?.(metric)}
        />
      ))}
    </div>
  );
}

export default MetricGrid;
