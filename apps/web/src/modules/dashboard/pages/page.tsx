'use client';

import { useMemo } from 'react';
import { ReadOnlyBanner } from '@/components/ui/ReadOnlyBanner';
import { WelcomeHeader } from '../components/WelcomeHeader';
import { DashboardGrid } from '../components/DashboardGrid';
import { KpiSection } from '../components/KpiSection';
import { EstablishmentInfo } from '../components/EstablishmentInfo';
import { useDashboardData } from '../hooks/useDashboardData';
import type { StatCard } from '../types/dashboard.types';

/**
 * DashboardPage - Página principal del dashboard
 * Migrada al esquema modular
 */
export default function DashboardPage() {
  const { stats, kpis, establishment, loading, isAdmin, profile } = useDashboardData();

  const cards = useMemo<StatCard[]>(() => [
    {
      id: 'equipos',
      title: 'Equipos',
      value: stats.equipos,
      subtitle: 'Registrados',
      href: '/equipos',
      color: 'bg-teal-500',
      show: true,
      icon: 'server',
    },
    {
      id: 'mantenimientos',
      title: 'Mantenimientos',
      value: stats.mantenimientos,
      subtitle: 'Eventos',
      href: '/mantenimientos',
      color: 'bg-emerald-500',
      show: true,
      icon: 'wrench',
    },
    {
      id: 'establecimientos',
      title: 'Establecimientos',
      value: stats.establecimientos,
      subtitle: 'Centros',
      href: '/establecimientos',
      color: 'bg-violet-500',
      show: isAdmin,
      icon: 'building',
    },
  ], [stats, isAdmin]);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="w-6 h-6 border-2 border-[var(--primary)] border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {!isAdmin && <ReadOnlyBanner />}

      <WelcomeHeader
        userName={profile?.nombre}
        isAdmin={isAdmin}
        establishmentName={establishment?.nombre_comercial}
      />

      <DashboardGrid cards={cards} />

      <KpiSection kpis={kpis} isAdmin={isAdmin} />

      {establishment && !isAdmin && (
        <EstablishmentInfo establishment={establishment} />
      )}
    </div>
  );
}
