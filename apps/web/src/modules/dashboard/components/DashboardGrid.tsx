'use client';

import { StatCard } from './StatCard';
import type { StatCard as StatCardType } from '../types/dashboard.types';

interface DashboardGridProps {
  cards: StatCardType[];
}

/**
 * DashboardGrid - Grid de tarjetas de estadísticas
 */
export function DashboardGrid({ cards }: DashboardGridProps) {
  const visibleCards = cards.filter((card) => card.show);

  if (visibleCards.length === 0) {
    return null;
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
      {visibleCards.map((card) => (
        <StatCard key={card.id} card={card} />
      ))}
    </div>
  );
}

export default DashboardGrid;
