'use client';

import type { OperationsStats } from '../types/operations.types';

interface StatsCardsProps {
  stats: OperationsStats;
}

export function StatsCards({ stats }: StatsCardsProps) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {/* Work Orders */}
      <div className="card p-4">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-muted">Órdenes de Trabajo</p>
            <p className="text-2xl font-bold">{stats.totalWorkOrders}</p>
          </div>
          <div className="w-10 h-10 rounded-lg bg-blue-500/10 flex items-center justify-center">
            <svg className="w-5 h-5 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
          </div>
        </div>
        <div className="mt-2 text-xs text-muted">
          <span className="text-yellow-500">{stats.pendingWorkOrders} pendientes</span>
          {' • '}
          <span className="text-green-500">{stats.completedWorkOrders} completadas</span>
        </div>
      </div>

      {/* Incidents */}
      <div className="card p-4">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-muted">Incidentes</p>
            <p className="text-2xl font-bold">{stats.totalIncidents}</p>
          </div>
          <div className="w-10 h-10 rounded-lg bg-red-500/10 flex items-center justify-center">
            <svg className="w-5 h-5 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
        </div>
        <div className="mt-2 text-xs text-muted">
          <span className="text-red-500">{stats.criticalIncidents} críticos</span>
          {' • '}
          <span className="text-orange-500">{stats.openIncidents} abiertos</span>
        </div>
      </div>

      {/* Alerts */}
      <div className="card p-4">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-muted">Alertas</p>
            <p className="text-2xl font-bold">{stats.totalAlerts}</p>
          </div>
          <div className="w-10 h-10 rounded-lg bg-orange-500/10 flex items-center justify-center">
            <svg className="w-5 h-5 text-orange-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
            </svg>
          </div>
        </div>
        <div className="mt-2 text-xs text-muted">
          <span className="text-red-500">{stats.criticalAlerts} críticas</span>
        </div>
      </div>

      {/* Devices */}
      <div className="card p-4">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-muted">Dispositivos</p>
            <p className="text-2xl font-bold">
              {stats.devicesOnline + stats.devicesOffline + stats.devicesWarning}
            </p>
          </div>
          <div className="w-10 h-10 rounded-lg bg-green-500/10 flex items-center justify-center">
            <svg className="w-5 h-5 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
          </div>
        </div>
        <div className="mt-2 text-xs text-muted">
          <span className="text-green-500">{stats.devicesOnline} en línea</span>
          {stats.devicesWarning > 0 && (
            <>
              {' • '}
              <span className="text-yellow-500">{stats.devicesWarning} advertencia</span>
            </>
          )}
          {stats.devicesOffline > 0 && (
            <>
              {' • '}
              <span className="text-red-500">{stats.devicesOffline} desconectados</span>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export default StatsCards;
