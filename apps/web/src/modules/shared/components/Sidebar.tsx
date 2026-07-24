'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { moduleRegistry, type ModuleConfig } from '../lib/module-registry';

/**
 * Sidebar - Navegación principal
 * Muestra módulos habilitados del ModuleRegistry
 */
export function Sidebar() {
  const pathname = usePathname();
  const modules = moduleRegistry.getEnabledModules();

  return (
    <aside className="w-64 bg-card border-r border-border h-screen flex flex-col">
      {/* Logo */}
      <div className="p-4 border-b border-border">
        <h1 className="text-xl font-bold text-primary">EREN</h1>
        <p className="text-xs text-muted">Hospital Platform</p>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto p-2">
        <ul className="space-y-1">
          {modules.map((module) => (
            <NavItem
              key={module.id}
              module={module}
              isActive={pathname.startsWith(module.path)}
            />
          ))}
        </ul>
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-border text-xs text-muted">
        EREN v1.0.0
      </div>
    </aside>
  );
}

interface NavItemProps {
  module: ModuleConfig;
  isActive: boolean;
}

function NavItem({ module, isActive }: NavItemProps) {
  return (
    <li>
      <Link
        href={module.path}
        className={`
          flex items-center gap-3 px-3 py-2 rounded-md text-sm
          transition-colors
          ${
            isActive
              ? 'bg-primary text-primary-foreground'
              : 'text-muted-foreground hover:bg-muted hover:text-foreground'
          }
        `}
      >
        <ModuleIcon name={module.icon} className="w-5 h-5" />
        <span>{module.name}</span>
        {module.badge && (
          <span className="ml-auto bg-primary/10 text-primary px-2 py-0.5 rounded-full text-xs">
            {module.badge}
          </span>
        )}
      </Link>
    </li>
  );
}

// Icon placeholder - En producción usar lucide-react o similar
function ModuleIcon({ name, className }: { name: string; className?: string }) {
  return (
    <svg
      className={className}
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      strokeWidth={2}
    >
      <rect x="3" y="3" width="18" height="18" rx="2" />
    </svg>
  );
}

export default Sidebar;
