'use client';

import type { Incident } from '../types/operations.types';

interface IncidentListProps {
  incidents: Incident[];
  onIncidentClick?: (id: string) => void;
}

export function IncidentList({ incidents, onIncidentClick }: IncidentListProps) {
  if (incidents.length === 0) {
    return (
      <div className="text-center py-8 text-muted">
        No hay incidentes
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {incidents.map((incident) => (
        <IncidentCard
          key={incident.id}
          incident={incident}
          onClick={() => onIncidentClick?.(incident.id)}
        />
      ))}
    </div>
  );
}

interface IncidentCardProps {
  incident: Incident;
  onClick?: () => void;
}

function IncidentCard({ incident, onClick }: IncidentCardProps) {
  const severityConfig = {
    low: { label: 'Baja', color: 'border-l-blue-500', badge: 'badge-info' },
    medium: { label: 'Media', color: 'border-l-yellow-500', badge: 'badge-warning' },
    high: { label: 'Alta', color: 'border-l-orange-500', badge: 'badge-warning' },
    critical: { label: 'Crítica', color: 'border-l-red-500', badge: 'badge-error' },
  };

  const statusConfig = {
    open: { label: 'Abierto', color: 'bg-red-100 text-red-800' },
    investigating: { label: 'Investigando', color: 'bg-yellow-100 text-yellow-800' },
    resolved: { label: 'Resuelto', color: 'bg-green-100 text-green-800' },
    closed: { label: 'Cerrado', color: 'bg-gray-100 text-gray-800' },
  };

  const severity = severityConfig[incident.severity];
  const status = statusConfig[incident.status];

  return (
    <div
      className={`card p-4 border-l-4 ${severity.color} hover:shadow-md transition-shadow cursor-pointer`}
      onClick={onClick}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <h4 className="font-medium">{incident.title}</h4>
            <span className={`badge ${severity.badge}`}>{severity.label}</span>
          </div>
          
          <p className="text-sm text-muted line-clamp-2">{incident.description}</p>
          
          <div className="flex items-center gap-4 mt-3 text-xs text-muted">
            {incident.location && (
              <span className="flex items-center gap-1">
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
                {incident.location}
              </span>
            )}
            {incident.deviceName && (
              <span className="flex items-center gap-1">
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
                {incident.deviceName}
              </span>
            )}
            {incident.reportedByName && (
              <span className="flex items-center gap-1">
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
                {incident.reportedByName}
              </span>
            )}
          </div>
        </div>
        
        <div className="flex flex-col items-end gap-2">
          <span className={`badge ${status.color}`}>{status.label}</span>
          <span className="text-xs text-muted">
            {new Date(incident.createdAt).toLocaleString()}
          </span>
        </div>
      </div>
    </div>
  );
}

export default IncidentList;
