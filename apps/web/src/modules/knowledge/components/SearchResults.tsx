'use client';

import type { SearchResult } from '../types/knowledge.types';

interface SearchResultsProps {
  results: SearchResult[];
  loading?: boolean;
  onResultClick?: (result: SearchResult) => void;
}

export function SearchResults({ results, loading = false, onResultClick }: SearchResultsProps) {
  if (loading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="card p-4 animate-pulse">
            <div className="h-5 bg-gray-200 rounded w-3/4 mb-2" />
            <div className="h-4 bg-gray-100 rounded w-full mb-2" />
            <div className="h-4 bg-gray-100 rounded w-2/3" />
          </div>
        ))}
      </div>
    );
  }

  if (results.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-[var(--background)] flex items-center justify-center">
          <svg className="w-8 h-8 text-muted" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <p className="text-muted">No se encontraron resultados</p>
        <p className="text-sm text-muted mt-1">Intenta con otros términos de búsqueda</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <p className="text-sm text-muted mb-4">
        {results.length} resultado{results.length !== 1 ? 's' : ''} encontrado{results.length !== 1 ? 's' : ''}
      </p>
      {results.map((result) => (
        <SearchResultCard
          key={result.id}
          result={result}
          onClick={() => onResultClick?.(result)}
        />
      ))}
    </div>
  );
}

interface SearchResultCardProps {
  result: SearchResult;
  onClick?: () => void;
}

function SearchResultCard({ result, onClick }: SearchResultCardProps) {
  const typeConfig = {
    procedure: { label: 'Procedimiento', color: 'bg-blue-100 text-blue-800' },
    protocol: { label: 'Protocolo', color: 'bg-purple-100 text-purple-800' },
    guideline: { label: 'Guía', color: 'bg-green-100 text-green-800' },
    manual: { label: 'Manual', color: 'bg-gray-100 text-gray-800' },
    article: { label: 'Artículo', color: 'bg-teal-100 text-teal-800' },
    faq: { label: 'FAQ', color: 'bg-yellow-100 text-yellow-800' },
    other: { label: 'Otro', color: 'bg-slate-100 text-slate-800' },
  };

  const type = typeConfig[result.type] || typeConfig.other;

  return (
    <div
      className="card p-4 hover:shadow-md transition-shadow cursor-pointer"
      onClick={onClick}
    >
      <div className="flex items-start justify-between mb-2">
        <h3 className="font-medium flex-1">{result.title}</h3>
        <span className={`badge ${type.color} ml-2`}>{type.label}</span>
      </div>

      <p className="text-sm text-muted line-clamp-2 mb-3">{result.snippet}</p>

      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          {result.category && (
            <span className="text-xs text-muted">{result.category}</span>
          )}
          {result.tags?.slice(0, 2).map((tag) => (
            <span key={tag} className="text-xs px-2 py-0.5 bg-[var(--background)] rounded">
              {tag}
            </span>
          ))}
        </div>

        <div className="flex items-center gap-2">
          {result.citations && result.citations.length > 0 && (
            <span className="text-xs text-muted flex items-center gap-1">
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              {result.citations.length}
            </span>
          )}
          <span className="text-xs text-[var(--primary)] font-medium">
            {(result.relevance * 100).toFixed(0)}% relevante
          </span>
        </div>
      </div>
    </div>
  );
}

export default SearchResults;
