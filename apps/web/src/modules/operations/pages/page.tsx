'use client';

import { useOperations } from '../hooks/useOperations';
import { StatsCards } from '../components/StatsCards';
import { WorkOrderList } from '../components/WorkOrderList';
import { IncidentList } from '../components/IncidentList';
import { AlertList } from '../components/AlertList';

export default function OperationsPage() {
  const {
    workOrders,
    incidents,
    alerts,
    stats,
    loading,
    error,
    activeTab,
    setActiveTab,
    acknowledgeAlert,
    dismissAlert,
  } = useOperations();

  const tabs = [
    { id: 'overview', label: 'Resumen' },
    { id: 'workorders', label: 'Órdenes de Trabajo' },
    { id: 'incidents', label: 'Incidentes' },
    { id: 'alerts', label: 'Alertas' },
  ] as const;

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="w-6 h-6 border-2 border-[var(--primary)] border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold">Centro de Operaciones</h1>
        <p className="text-sm text-muted mt-1">
          Gestiona órdenes de trabajo, incidentes y alertas
        </p>
      </div>

      {error && (
        <div className="alert-error">
          {error}
        </div>
      )}

      {/* Tabs */}
      <div className="border-b border-border">
        <nav className="flex gap-4">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
                activeTab === tab.id
                  ? 'border-primary text-primary'
                  : 'border-transparent text-muted hover:text-foreground'
              }`}
            >
              {tab.label}
              {tab.id === 'alerts' && alerts.filter(a => !a.acknowledged).length > 0 && (
                <span className="ml-2 px-2 py-0.5 text-xs bg-red-500 text-white rounded-full">
                  {alerts.filter(a => !a.acknowledged).length}
                </span>
              )}
            </button>
          ))}
        </nav>
      </div>

      {/* Content */}
      <div className="space-y-6">
        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="space-y-6">
            <StatsCards stats={stats} />
            
            {/* Recent Alerts */}
            <div>
              <h2 className="text-lg font-semibold mb-4">Alertas Activas</h2>
              <AlertList
                alerts={alerts.filter(a => !a.acknowledged).slice(0, 5)}
                onAcknowledge={acknowledgeAlert}
                onDismiss={dismissAlert}
              />
            </div>
            
            {/* Recent Work Orders */}
            <div>
              <h2 className="text-lg font-semibold mb-4">Órdenes Recientes</h2>
              <WorkOrderList workOrders={workOrders.slice(0, 5)} />
            </div>
          </div>
        )}

        {/* Work Orders Tab */}
        {activeTab === 'workorders' && (
          <div>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold">Órdenes de Trabajo</h2>
              <button className="btn-primary">
                Nueva Orden
              </button>
            </div>
            <WorkOrderList workOrders={workOrders} />
          </div>
        )}

        {/* Incidents Tab */}
        {activeTab === 'incidents' && (
          <div>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold">Incidentes</h2>
              <button className="btn-primary">
                Reportar Incidente
              </button>
            </div>
            <IncidentList incidents={incidents} />
          </div>
        )}

        {/* Alerts Tab */}
        {activeTab === 'alerts' && (
          <div>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold">Alertas</h2>
            </div>
            <AlertList
              alerts={alerts}
              onAcknowledge={acknowledgeAlert}
              onDismiss={dismissAlert}
            />
          </div>
        )}
      </div>
    </div>
  );
}
