'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { moduleRegistry } from '@/modules/shared/lib/module-registry';

export interface BreadcrumbItem {
  label: string;
  path?: string;
}

interface BreadcrumbNavProps {
  customItems?: BreadcrumbItem[];
}

/**
 * BreadcrumbNav - Componente de breadcrumbs
 */
export function BreadcrumbNav({ customItems }: BreadcrumbNavProps) {
  const pathname = usePathname();

  const items = customItems || getBreadcrumbsFromPath(pathname);

  if (items.length <= 1) return null;

  return (
    <nav className="flex items-center space-x-2 text-sm mb-4">
      {items.map((item, index) => (
        <span key={index} className="flex items-center">
          {index > 0 && (
            <svg className="w-4 h-4 mx-2 text-muted-foreground" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          )}
          {item.path ? (
            <Link
              href={item.path}
              className="text-muted-foreground hover:text-foreground transition-colors"
            >
              {item.label}
            </Link>
          ) : (
            <span className="text-foreground font-medium">{item.label}</span>
          )}
        </span>
      ))}
    </nav>
  );
}

/**
 * Genera breadcrumbs basado en el pathname
 */
function getBreadcrumbsFromPath(pathname: string): BreadcrumbItem[] {
  const segments = pathname.split('/').filter(Boolean);
  const breadcrumbs: BreadcrumbItem[] = [{ label: 'Inicio', path: '/dashboard' }];

  let currentPath = '';
  for (const segment of segments) {
    currentPath += `/${segment}`;
    
    // Intentar encontrar el módulo
    const module = moduleRegistry.getEnabledModules().find(m => m.path === currentPath);
    
    if (module) {
      breadcrumbs.push({ label: module.name, path: module.path });
    } else {
      // Para rutas anidadas, usar el segmento como label
      const label = segment
        .split('-')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
      breadcrumbs.push({ label });
    }
  }

  return breadcrumbs;
}

export default BreadcrumbNav;
