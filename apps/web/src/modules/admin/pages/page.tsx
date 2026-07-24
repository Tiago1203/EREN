'use client';

import { useState } from 'react';
import { useAdmin } from '../hooks/useAdmin';
import { UserList } from '../components/UserList';
import { SettingsPanel } from '../components/SettingsPanel';
import { AuditLogViewer } from '../components/AuditLogViewer';

type AdminTab = 'users' | 'roles' | 'settings' | 'connectors' | 'audit';

export default function AdminPage() {
  const {
    users,
    roles,
    settings,
    auditLogs,
    loading,
    error,
    updateSetting,
  } = useAdmin();

  const [activeTab, setActiveTab] = useState<AdminTab>('users');

  const tabs: { id: AdminTab; label: string; icon: JSX.Element }[] = [
    {
      id: 'users',
      label: 'Usuarios',
      icon: <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" /></svg>,
    },
    {
      id: 'roles',
      label: 'Roles',
      icon: <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" /></svg>,
    },
    {
      id: 'settings',
      label: 'Configuración',
      icon: <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" /></svg>,
    },
    {
      id: 'connectors',
      label: 'Conectores',
      icon: <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" /></svg>,
    },
    {
      id: 'audit',
      label: 'Auditoría',
      icon: <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" /></svg>,
    },
  ];

  const renderContent = () => {
    switch (activeTab) {
      case 'users':
        return (
          <div>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold">Usuarios del Sistema</h2>
              <button className="btn-primary">
                <svg className="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
                Agregar Usuario
              </button>
            </div>
            <UserList users={users} />
          </div>
        );

      case 'roles':
        return (
          <div>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold">Roles y Permisos</h2>
              <button className="btn-primary">
                <svg className="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
                Crear Rol
              </button>
            </div>
            <div className="space-y-4">
              {roles.map((role) => (
                <div key={role.id} className="card p-4">
                  <div className="flex items-center justify-between mb-3">
                    <div>
                      <h3 className="font-medium">{role.name}</h3>
                      <p className="text-sm text-muted">{role.description}</p>
                    </div>
                    <span className="badge bg-gray-100">{role.userCount} usuarios</span>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {role.permissions.map((perm) => (
                      <span key={perm.id} className="px-2 py-1 text-xs bg-[var(--background)] rounded">
                        {perm.resource}.{perm.action}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        );

      case 'settings':
        return (
          <div>
            <h2 className="text-lg font-semibold mb-4">Configuración del Sistema</h2>
            <SettingsPanel settings={settings} onSettingChange={updateSetting} />
          </div>
        );

      case 'connectors':
        return (
          <div>
            <h2 className="text-lg font-semibold mb-4">Conectores</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <ConnectorCard
                name="FHIR R4"
                type="fhir"
                description="Integración con servidores FHIR R4"
              />
              <ConnectorCard
                name="HL7 v2"
                type="hl7"
                description="Mensajería HL7 v2.x"
              />
              <ConnectorCard
                name="DICOM"
                type="dicom"
                description="Comunicación DICOM"
              />
            </div>
            <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
              <p className="text-sm text-yellow-800">
                ⚠️ Los conectores están preparados pero no implementados aún. 
                Se activarán en FASE 7 (Enterprise).
              </p>
            </div>
          </div>
        );

      case 'audit':
        return (
          <div>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold">Registro de Auditoría</h2>
              <button className="btn-secondary">
                <svg className="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                </svg>
                Exportar
              </button>
            </div>
            <AuditLogViewer logs={auditLogs} loading={loading} />
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="h-[calc(100vh-4rem)] flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-[var(--border)]">
        <h1 className="text-xl font-bold">Administración</h1>
        <p className="text-sm text-muted mt-1">
          Gestiona usuarios, roles, configuraciones y conectores
        </p>
      </div>

      {/* Error */}
      {error && (
        <div className="mx-4 mt-4 p-4 bg-red-100 border border-red-300 rounded-lg text-red-700">
          {error}
        </div>
      )}

      {/* Tabs */}
      <div className="px-4 border-b border-[var(--border)]">
        <nav className="flex gap-1">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
                activeTab === tab.id
                  ? 'border-[var(--primary)] text-[var(--primary)]'
                  : 'border-transparent text-muted hover:text-foreground'
              }`}
            >
              {tab.icon}
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4">
        {renderContent()}
      </div>
    </div>
  );
}

interface ConnectorCardProps {
  name: string;
  type: string;
  description: string;
}

function ConnectorCard({ name, type, description }: ConnectorCardProps) {
  const icons: Record<string, JSX.Element> = {
    fhir: <svg className="w-8 h-8 text-teal-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" /></svg>,
    hl7: <svg className="w-8 h-8 text-purple-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>,
    dicom: <svg className="w-8 h-8 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>,
  };

  return (
    <div className="card p-6 text-center opacity-60">
      <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-[var(--background)] flex items-center justify-center">
        {icons[type] || icons.fhir}
      </div>
      <h3 className="font-semibold mb-2">{name}</h3>
      <p className="text-sm text-muted">{description}</p>
      <span className="badge bg-gray-100 mt-4">Preparado</span>
    </div>
  );
}
