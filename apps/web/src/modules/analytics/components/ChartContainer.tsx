'use client';

import type { ChartConfig, ChartData } from '../types/analytics.types';

interface ChartContainerProps {
  title: string;
  chartId: string;
  type: 'line' | 'bar' | 'pie';
  data?: ChartData;
  loading?: boolean;
}

export function ChartContainer({ title, chartId, type, data, loading }: ChartContainerProps) {
  return (
    <div className="card p-4">
      <h3 className="font-semibold mb-4">{title}</h3>
      
      {loading ? (
        <div className="h-64 flex items-center justify-center">
          <div className="w-8 h-8 border-2 border-[var(--primary)] border-t-transparent rounded-full animate-spin" />
        </div>
      ) : data ? (
        <ChartVisualization type={type} data={data} />
      ) : (
        <div className="h-64 flex items-center justify-center text-muted">
          No hay datos disponibles
        </div>
      )}
    </div>
  );
}

interface ChartVisualizationProps {
  type: 'line' | 'bar' | 'pie';
  data: ChartData;
}

function ChartVisualization({ type, data }: ChartVisualizationProps) {
  if (type === 'pie') {
    return <PieChartVisualization data={data} />;
  }

  if (type === 'bar') {
    return <BarChartVisualization data={data} />;
  }

  return <LineChartVisualization data={data} />;
}

function LineChartVisualization({ data }: { data: ChartData }) {
  const maxValue = Math.max(...data.datasets.flatMap(d => d.data), 1);
  
  return (
    <div className="h-64">
      <div className="flex h-full">
        {/* Y-axis labels */}
        <div className="flex flex-col justify-between text-xs text-muted pr-2">
          <span>{maxValue}</span>
          <span>{maxValue * 0.75}</span>
          <span>{maxValue * 0.5}</span>
          <span>{maxValue * 0.25}</span>
          <span>0</span>
        </div>
        
        {/* Chart area */}
        <div className="flex-1 border-l border-b border-[var(--border)] relative">
          {data.datasets.map((dataset, datasetIndex) => (
            <svg
              key={datasetIndex}
              className="absolute inset-0 w-full h-full"
              style={{ overflow: 'visible' }}
            >
              {/* Grid lines */}
              {[0.25, 0.5, 0.75].map((ratio) => (
                <line
                  key={ratio}
                  x1="0"
                  y1={`${(1 - ratio) * 100}%`}
                  x2="100%"
                  y2={`${(1 - ratio) * 100}%`}
                  stroke="var(--border)"
                  strokeDasharray="4"
                />
              ))}
              
              {/* Line */}
              <polyline
                fill="none"
                stroke={dataset.color || '#3b82f6'}
                strokeWidth="2"
                points={dataset.data.map((value, index) => {
                  const x = `${(index / (dataset.data.length - 1)) * 100}%`;
                  const y = `${(1 - value / maxValue) * 100}%`;
                  return `${x},${y}`;
                }).join(' ')}
              />
              
              {/* Points */}
              {dataset.data.map((value, index) => (
                <circle
                  key={index}
                  cx={`${(index / (dataset.data.length - 1)) * 100}%`}
                  cy={`${(1 - value / maxValue) * 100}%`}
                  r="4"
                  fill={dataset.color || '#3b82f6'}
                />
              ))}
            </svg>
          ))}
        </div>
      </div>
      
      {/* X-axis labels */}
      <div className="flex justify-between mt-2 text-xs text-muted">
        {data.labels.map((label, index) => (
          <span key={index}>{label}</span>
        ))}
      </div>
      
      {/* Legend */}
      <div className="flex flex-wrap gap-4 mt-4">
        {data.datasets.map((dataset, index) => (
          <div key={index} className="flex items-center gap-2">
            <div
              className="w-3 h-3 rounded-full"
              style={{ backgroundColor: dataset.color || '#3b82f6' }}
            />
            <span className="text-xs">{dataset.name}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function BarChartVisualization({ data }: { data: ChartData }) {
  const maxValue = Math.max(...data.datasets.flatMap(d => d.data), 1);
  const barWidth = 100 / (data.labels.length * (data.datasets.length + 1));
  
  return (
    <div className="h-64">
      <div className="flex h-full">
        {/* Y-axis labels */}
        <div className="flex flex-col justify-between text-xs text-muted pr-2">
          <span>{maxValue}</span>
          <span>{maxValue * 0.5}</span>
          <span>0</span>
        </div>
        
        {/* Chart area */}
        <div className="flex-1 border-l border-b border-[var(--border)] relative flex items-end">
          {data.labels.map((_, labelIndex) => (
            <div
              key={labelIndex}
              className="flex-1 flex items-end justify-center gap-1"
              style={{ height: '100%' }}
            >
              {data.datasets.map((dataset, datasetIndex) => {
                const height = (dataset.data[labelIndex] / maxValue) * 100;
                return (
                  <div
                    key={datasetIndex}
                    className="w-full rounded-t"
                    style={{
                      height: `${height}%`,
                      backgroundColor: dataset.color || '#3b82f6',
                      opacity: 0.8 + (datasetIndex * 0.1),
                    }}
                    title={`${dataset.name}: ${dataset.data[labelIndex]}`}
                  />
                );
              })}
            </div>
          ))}
        </div>
      </div>
      
      {/* X-axis labels */}
      <div className="flex justify-between mt-2 text-xs text-muted">
        {data.labels.map((label, index) => (
          <span key={index} className="flex-1 text-center">{label}</span>
        ))}
      </div>
      
      {/* Legend */}
      <div className="flex flex-wrap gap-4 mt-4">
        {data.datasets.map((dataset, index) => (
          <div key={index} className="flex items-center gap-2">
            <div
              className="w-3 h-3 rounded"
              style={{ backgroundColor: dataset.color || '#3b82f6' }}
            />
            <span className="text-xs">{dataset.name}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function PieChartVisualization({ data }: { data: ChartData }) {
  const total = data.datasets[0]?.data.reduce((a, b) => a + b, 0) || 1;
  let currentAngle = 0;
  
  const slices = data.datasets[0]?.data.map((value, index) => {
    const angle = (value / total) * 360;
    const slice = {
      ...data.datasets[0],
      value,
      label: data.labels[index],
      startAngle: currentAngle,
      endAngle: currentAngle + angle,
    };
    currentAngle += angle;
    return slice;
  }) || [];

  const describeArc = (startAngle: number, endAngle: number, radius: number) => {
    const start = polarToCartesian(50, 50, radius, endAngle);
    const end = polarToCartesian(50, 50, radius, startAngle);
    const largeArcFlag = endAngle - startAngle <= 180 ? 0 : 1;
    return [
      'M', 50, 50,
      'L', start.x, start.y,
      'A', radius, radius, 0, largeArcFlag, 0, end.x, end.y,
      'Z',
    ].join(' ');
  };

  const polarToCartesian = (cx: number, cy: number, r: number, angle: number) => {
    const rad = ((angle - 90) * Math.PI) / 180;
    return {
      x: cx + r * Math.cos(rad),
      y: cy + r * Math.sin(rad),
    };
  };

  return (
    <div className="h-64 flex items-center justify-center">
      <svg viewBox="0 0 100 100" className="w-full h-full max-w-xs">
        {slices.map((slice, index) => (
          <path
            key={index}
            d={describeArc(slice.startAngle, slice.endAngle, 40)}
            fill={slice.color || `hsl(${index * 60}, 70%, 50%)`}
            stroke="white"
            strokeWidth="0.5"
          />
        ))}
        <circle cx="50" cy="50" r="15" fill="white" />
      </svg>
      
      {/* Legend */}
      <div className="ml-4 space-y-2">
        {slices.map((slice, index) => (
          <div key={index} className="flex items-center gap-2">
            <div
              className="w-3 h-3 rounded"
              style={{ backgroundColor: slice.color || `hsl(${index * 60}, 70%, 50%)` }}
            />
            <span className="text-xs">{slice.label}: {slice.value}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

export default ChartContainer;
