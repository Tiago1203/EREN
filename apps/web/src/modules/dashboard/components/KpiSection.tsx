'use client';

import { KpiGrid } from '@/components/ui/KpiGrid';
import type { Kpi } from '../types/dashboard.types';

interface KpiSectionProps {
  kpis: Kpi[];
  isAdmin: boolean;
}

/**
 * KpiSection - Sección de KPIs
 */
export function KpiSection({ kpis, isAdmin }: KpiSectionProps) {
  return (
    <div>
      <h2 className="text-lg font-semibold mb-4">
        {isAdmin ? 'KPIs del Sistema' : 'KPIs de su Establecimiento'}
      </h2>
      <KpiGrid kpis={kpis} />
    </div>
  );
}

export default KpiSection;
