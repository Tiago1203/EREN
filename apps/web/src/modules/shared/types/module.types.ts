/**
 * Tipos para navegación
 */

export interface NavigationItem {
  id: string;
  label: string;
  icon: string;
  path: string;
  children?: NavigationItem[];
  permissions?: string[];
  badge?: string | number;
  enabled?: boolean;
}

export interface BreadcrumbItem {
  label: string;
  path?: string;
}

export interface RouteConfig {
  path: string;
  module: string;
  component?: string;
  permissions: string[];
  exact?: boolean;
  breadcrumb?: BreadcrumbItem[];
}
