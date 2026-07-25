'use client';

import type { Category } from '../types/knowledge.types';

interface CategoryNavProps {
  categories: Category[];
  selectedId?: string;
  onSelect: (category: Category) => void;
}

export function CategoryNav({ categories, selectedId, onSelect }: CategoryNavProps) {
  return (
    <nav className="space-y-1">
      <button
        onClick={() => onSelect({ id: '', name: 'Todos', articleCount: 0 } as Category)}
        className={`w-full text-left px-4 py-2 rounded-lg text-sm transition-colors ${
          !selectedId
            ? 'bg-[var(--primary)] text-white'
            : 'text-muted hover:bg-[var(--background)]'
        }`}
      >
        Todos los artículos
      </button>

      {categories.map((category) => (
        <CategoryItem
          key={category.id}
          category={category}
          selectedId={selectedId}
          onSelect={onSelect}
          level={0}
        />
      ))}
    </nav>
  );
}

interface CategoryItemProps {
  category: Category;
  selectedId?: string;
  onSelect: (category: Category) => void;
  level: number;
}

function CategoryItem({ category, selectedId, onSelect, level }: CategoryItemProps) {
  const hasChildren = category.children && category.children.length > 0;
  const isSelected = selectedId === category.id;

  return (
    <div>
      <button
        onClick={() => onSelect(category)}
        className={`w-full text-left px-4 py-2 rounded-lg text-sm transition-colors flex items-center justify-between ${
          isSelected
            ? 'bg-[var(--primary)] text-white'
            : 'text-muted hover:bg-[var(--background)]'
        }`}
        style={{ paddingLeft: `${16 + level * 16}px` }}
      >
        <div className="flex items-center gap-2">
          {category.icon && <CategoryIcon name={category.icon} />}
          <span className="truncate">{category.name}</span>
        </div>
        <span className={`text-xs ${isSelected ? 'text-white/70' : 'text-muted'}`}>
          {category.articleCount}
        </span>
      </button>

      {hasChildren && (
        <div>
          {category.children!.map((child) => (
            <CategoryItem
              key={child.id}
              category={child}
              selectedId={selectedId}
              onSelect={onSelect}
              level={level + 1}
            />
          ))}
        </div>
      )}
    </div>
  );
}

function CategoryIcon({ name }: { name: string }) {
  const icons: Record<string, JSX.Element> = {
    Wrench: (
      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
      </svg>
    ),
    Monitor: (
      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
      </svg>
    ),
    Search: (
      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
      </svg>
    ),
    AlertTriangle: (
      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
      </svg>
    ),
    Activity: (
      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
      </svg>
    ),
  };

  return icons[name] || (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
    </svg>
  );
}

export default CategoryNav;
