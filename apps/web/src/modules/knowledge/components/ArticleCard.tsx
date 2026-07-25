'use client';

import type { KnowledgeArticle } from '../types/knowledge.types';

interface ArticleCardProps {
  article: KnowledgeArticle;
  onClick?: () => void;
  compact?: boolean;
}

export function ArticleCard({ article, onClick, compact = false }: ArticleCardProps) {
  const typeConfig = {
    procedure: { label: 'Procedimiento', color: 'bg-blue-100 text-blue-800', icon: '📋' },
    protocol: { label: 'Protocolo', color: 'bg-purple-100 text-purple-800', icon: '📜' },
    guideline: { label: 'Guía', color: 'bg-green-100 text-green-800', icon: '📖' },
    manual: { label: 'Manual', color: 'bg-gray-100 text-gray-800', icon: '📚' },
    article: { label: 'Artículo', color: 'bg-teal-100 text-teal-800', icon: '📄' },
    faq: { label: 'FAQ', color: 'bg-yellow-100 text-yellow-800', icon: '❓' },
    other: { label: 'Otro', color: 'bg-slate-100 text-slate-800', icon: '📎' },
  };

  const type = typeConfig[article.type] || typeConfig.other;

  return (
    <div
      className={`card p-4 hover:shadow-md transition-shadow cursor-pointer ${
        compact ? 'border-l-4 border-l-[var(--primary)]' : ''
      }`}
      onClick={onClick}
    >
      <div className="flex items-start justify-between mb-2">
        <div className="flex items-center gap-2">
          <span className="text-lg">{type.icon}</span>
          <span className={`badge ${type.color}`}>{type.label}</span>
        </div>
        {article.metadata.estimatedReadTime && (
          <span className="text-xs text-muted">
            {article.metadata.estimatedReadTime} min
          </span>
        )}
      </div>

      <h3 className="font-medium mb-2 line-clamp-2">{article.title}</h3>
      
      {article.summary && (
        <p className="text-sm text-muted line-clamp-2 mb-3">{article.summary}</p>
      )}

      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-xs text-muted">{article.category.name}</span>
          {article.tags.slice(0, 2).map((tag) => (
            <span key={tag.id} className="text-xs px-2 py-0.5 bg-[var(--background)] rounded">
              {tag.name}
            </span>
          ))}
        </div>
        
        {article.author && (
          <span className="text-xs text-muted">{article.author.name}</span>
        )}
      </div>

      <div className="flex items-center gap-4 mt-3 pt-3 border-t border-[var(--border)] text-xs text-muted">
        <span>Actualizado: {new Date(article.updatedAt).toLocaleDateString()}</span>
        {article.metadata.difficulty && (
          <span className="capitalize">{article.metadata.difficulty}</span>
        )}
      </div>
    </div>
  );
}

export default ArticleCard;
