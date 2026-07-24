'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { moduleRegistry } from '@/modules/shared/lib/module-registry';
import { useAuth } from '@/hooks/useAuth';
import { NotificationBell } from '@/components/ui/Notifications';

interface SidebarProps {
  collapsed?: boolean;
  onToggle?: () => void;
}

/**
 * Sidebar - Navegación principal usando ModuleRegistry
 */
export function Sidebar({ collapsed = false, onToggle }: SidebarProps) {
  const pathname = usePathname();
  const { isAdmin, profile } = useAuth();
  const modules = moduleRegistry.getEnabledModules();

  return (
    <aside className={`hidden md:flex flex-col bg-[var(--sidebar)] text-[var(--sidebar-text)] ${collapsed ? 'w-20' : 'w-64'}`}>
      {/* Logo */}
      <div className="px-6 py-5 border-b border-slate-700">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-[var(--primary)] flex items-center justify-center">
              <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
              </svg>
            </div>
            {!collapsed && (
              <div>
                <h1 className="text-sm font-semibold text-white leading-tight">BioMédico</h1>
                <p className="text-xs text-slate-400">Mantenimiento</p>
              </div>
            )}
          </div>
          <NotificationBell />
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {modules
          .filter((m) => !m.permissions.includes('admin') || isAdmin)
          .map((module) => {
            const active = pathname.startsWith(module.path);
            return (
              <NavItem
                key={module.id}
                module={module}
                active={active}
                collapsed={collapsed}
              />
            );
          })}
      </nav>

      {/* User Section */}
      <div className="px-4 py-4 border-t border-slate-700">
        <UserSection collapsed={collapsed} />
      </div>
    </aside>
  );
}

interface NavItemProps {
  module: { id: string; name: string; path: string; icon: string };
  active: boolean;
  collapsed: boolean;
}

function NavItem({ module, active, collapsed }: NavItemProps) {
  return (
    <Link
      href={module.path}
      className={`
        flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors
        ${active
          ? 'bg-[var(--primary)] text-white'
          : 'text-slate-300 hover:bg-slate-800 hover:text-white'
        }
        ${collapsed ? 'justify-center' : ''}
      `}
      title={collapsed ? module.name : undefined}
    >
      <ModuleIcon name={module.icon} />
      {!collapsed && <span>{module.name}</span>}
    </Link>
  );
}

function ModuleIcon({ name }: { name: string }) {
  const icons: Record<string, string> = {
    LayoutDashboard: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6',
    Monitor: 'M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z',
    Wrench: 'M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z',
    Building: 'M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4',
    BarChart3: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z',
    Bot: 'M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z',
    LineChart: 'M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z',
    FileText: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z',
    Bell: 'M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9',
    Activity: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01',
    Settings: 'M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z',
    Plug: 'M13 10V3L4 14h7v7l9-11h-7z',
    BookOpen: 'M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253',
    Briefcase: 'M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4',
  };

  return (
    <svg className="w-5 h-5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.75}>
      <path strokeLinecap="round" strokeLinejoin="round" d={icons[name] || icons.LayoutDashboard} />
    </svg>
  );
}

interface UserSectionProps {
  collapsed: boolean;
}

function UserSection({ collapsed }: UserSectionProps) {
  const { profile, isAdmin, signOut } = useAuth();

  if (collapsed) {
    return (
      <button
        onClick={signOut}
        className="w-10 h-10 rounded-full bg-slate-600 flex items-center justify-center text-sm font-medium text-white mx-auto"
        title="Cerrar sesión"
      >
        {(profile?.nombre || profile?.email || 'U').charAt(0).toUpperCase()}
      </button>
    );
  }

  return (
    <>
      <div className="flex items-center gap-3 mb-3">
        <div className="w-8 h-8 rounded-full bg-slate-600 flex items-center justify-center text-xs font-medium text-white">
          {(profile?.nombre || profile?.email || 'U').charAt(0).toUpperCase()}
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-white truncate">
            {profile?.nombre || profile?.email}
          </p>
          <span className={`badge ${isAdmin ? 'badge-admin' : 'badge-establecimiento'} mt-0.5`}>
            {isAdmin ? 'Admin' : 'Establecimiento'}
          </span>
        </div>
      </div>
      <button
        onClick={signOut}
        className="w-full text-left text-xs text-slate-400 hover:text-white transition-colors px-1"
      >
        Cerrar sesión
      </button>
    </>
  );
}

export default Sidebar;
