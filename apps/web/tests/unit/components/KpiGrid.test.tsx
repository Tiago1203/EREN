import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { KpiGrid } from '@/components/ui/KpiGrid';
import type { KpiResult } from '@/lib/kpis';

describe('KpiGrid', () => {
  it('renders empty state when no kpis provided', () => {
    render(<KpiGrid kpis={[]} />);
    expect(screen.queryByRole('article')).toBeNull();
  });

  it('renders kpi items', () => {
    const kpis: KpiResult[] = [
      { label: 'Test KPI 1', value: '10', status: 'ok' },
      { label: 'Test KPI 2', value: '20', status: 'warning' },
    ];
    render(<KpiGrid kpis={kpis} />);
    expect(screen.getByText('Test KPI 1')).toBeDefined();
    expect(screen.getByText('Test KPI 2')).toBeDefined();
  });
});
