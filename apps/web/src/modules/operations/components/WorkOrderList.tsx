'use client';

import type { WorkOrder } from '../types/operations.types';

interface WorkOrderListProps {
  workOrders: WorkOrder[];
  onWorkOrderClick?: (id: string) => void;
}

export function WorkOrderList({ workOrders, onWorkOrderClick }: WorkOrderListProps) {
  if (workOrders.length === 0) {
    return (
      <div className="text-center py-8 text-muted">
        No hay órdenes de trabajo
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {workOrders.map((wo) => (
        <WorkOrderCard
          key={wo.id}
          workOrder={wo}
          onClick={() => onWorkOrderClick?.(wo.id)}
        />
      ))}
    </div>
  );
}

interface WorkOrderCardProps {
  workOrder: WorkOrder;
  onClick?: () => void;
}

function WorkOrderCard({ workOrder, onClick }: WorkOrderCardProps) {
  const statusConfig = {
    pending: { label: 'Pendiente', color: 'bg-yellow-100 text-yellow-800' },
    assigned: { label: 'Asignada', color: 'bg-blue-100 text-blue-800' },
    in_progress: { label: 'En Progreso', color: 'bg-purple-100 text-purple-800' },
    completed: { label: 'Completada', color: 'bg-green-100 text-green-800' },
    cancelled: { label: 'Cancelada', color: 'bg-gray-100 text-gray-800' },
  };

  const priorityConfig = {
    low: { label: 'Baja', color: 'text-green-600' },
    medium: { label: 'Media', color: 'text-yellow-600' },
    high: { label: 'Alta', color: 'text-orange-600' },
    critical: { label: 'Crítica', color: 'text-red-600' },
  };

  const typeConfig = {
    preventive: 'Preventivo',
    corrective: 'Correctivo',
    predictive: 'Predictivo',
    inspection: 'Inspección',
  };

  const status = statusConfig[workOrder.status];
  const priority = priorityConfig[workOrder.priority];

  return (
    <div
      className="card p-4 hover:shadow-md transition-shadow cursor-pointer"
      onClick={onClick}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <h4 className="font-medium">{workOrder.title}</h4>
            <span className={`badge ${priority.color}`}>{priority.label}</span>
          </div>
          
          <p className="text-sm text-muted line-clamp-2">{workOrder.description}</p>
          
          <div className="flex items-center gap-4 mt-3 text-xs text-muted">
            {workOrder.deviceName && (
              <span className="flex items-center gap-1">
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
                {workOrder.deviceName}
              </span>
            )}
            <span>{typeConfig[workOrder.type]}</span>
            {workOrder.assignedToName && (
              <span className="flex items-center gap-1">
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
                {workOrder.assignedToName}
              </span>
            )}
          </div>
        </div>
        
        <div className="flex flex-col items-end gap-2">
          <span className={`badge ${status.color}`}>{status.label}</span>
          <span className="text-xs text-muted">
            {new Date(workOrder.createdAt).toLocaleDateString()}
          </span>
        </div>
      </div>
    </div>
  );
}

export default WorkOrderList;
