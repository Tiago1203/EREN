/**
 * BreadcrumbNav Component
 * 
 * Provides breadcrumb navigation for nested routes.
 */
'use client';

import Link from 'next/link';

interface BreadcrumbItem {
  label: string;
  href?: string;
}

interface BreadcrumbNavProps {
  items: BreadcrumbItem[];
}

export function BreadcrumbNav({ items }: BreadcrumbNavProps) {
  return (
    <nav className="flex items-center space-x-2 text-sm">
      {items.map((item, index) => (
        <div key={index} className="flex items-center">
          {index > 0 && <span className="mx-2 text-muted">/</span>}
          {item.href ? (
            <Link href={item.href} className="text-[var(--primary)] hover:underline">
              {item.label}
            </Link>
          ) : (
            <span className="text-muted">{item.label}</span>
          )}
        </div>
      ))}
    </nav>
  );
}
