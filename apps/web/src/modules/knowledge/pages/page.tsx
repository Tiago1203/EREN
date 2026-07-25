'use client';

import { useState } from 'react';
import { useKnowledge } from '../hooks/useKnowledge';
import { SearchBar } from '../components/SearchBar';
import { SearchResults } from '../components/SearchResults';
import { ArticleCard } from '../components/ArticleCard';
import { CategoryNav } from '../components/CategoryNav';
import type { Category } from '../types/knowledge.types';

export default function KnowledgePage() {
  const {
    articles,
    categories,
    tags,
    searchResults,
    loading,
    searching,
    error,
    search,
    selectArticle,
    clearSearch,
  } = useKnowledge();

  const [selectedCategory, setSelectedCategory] = useState<Category | null>(null);
  const [showSidebar, setShowSidebar] = useState(true);

  const handleCategorySelect = (category: Category) => {
    setSelectedCategory(category);
    clearSearch();
  };

  const handleSearch = (query: string) => {
    if (query.trim()) {
      search(query);
    } else {
      clearSearch();
    }
  };

  const filteredArticles = selectedCategory
    ? articles.filter((a) => a.category.id === selectedCategory.id)
    : articles;

  const hasSearchQuery = searchResults.length > 0 || searching;

  return (
    <div className="flex h-[calc(100vh-4rem)]">
      {/* Sidebar - Categories */}
      <div className={`w-64 border-r border-[var(--border)] bg-[var(--card)] overflow-y-auto ${showSidebar ? 'block' : 'hidden'}`}>
        <div className="p-4 border-b border-[var(--border)]">
          <h2 className="font-semibold">Categorías</h2>
        </div>
        <div className="p-2">
          <CategoryNav
            categories={categories}
            selectedId={selectedCategory?.id}
            onSelect={handleCategorySelect}
          />
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <div className="p-4 border-b border-[var(--border)]">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-xl font-bold">Centro de Conocimiento</h1>
              <p className="text-sm text-muted">
                {selectedCategory ? selectedCategory.name : 'Todos los artículos'}
              </p>
            </div>
            <button
              onClick={() => setShowSidebar(!showSidebar)}
              className="btn-secondary"
            >
              {showSidebar ? 'Ocultar' : 'Mostrar'} categorías
            </button>
          </div>

          <SearchBar
            onSearch={handleSearch}
            loading={searching}
            placeholder="Buscar artículos, procedimientos, guías..."
          />
        </div>

        {/* Error */}
        {error && (
          <div className="mx-4 mt-4 p-4 bg-red-100 border border-red-300 rounded-lg text-red-700">
            {error}
          </div>
        )}

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-4">
          {hasSearchQuery ? (
            // Search Results
            <SearchResults
              results={searchResults}
              loading={searching}
              onResultClick={(result) => {
                const article = articles.find((a) => a.id === result.id);
                if (article) selectArticle(article);
              }}
            />
          ) : (
            // Articles Grid
            <div>
              {/* Tags */}
              {tags.length > 0 && (
                <div className="mb-6">
                  <h3 className="text-sm font-medium mb-2">Tags populares</h3>
                  <div className="flex flex-wrap gap-2">
                    {tags.slice(0, 8).map((tag) => (
                      <button
                        key={tag.id}
                        onClick={() => handleSearch(tag.name)}
                        className="px-3 py-1 text-sm rounded-full border border-[var(--border)] hover:bg-[var(--background)] transition-colors"
                      >
                        {tag.name} ({tag.articleCount})
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Articles */}
              {loading ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {[1, 2, 3, 4, 5, 6].map((i) => (
                    <div key={i} className="card p-4 animate-pulse">
                      <div className="h-5 bg-gray-200 rounded w-3/4 mb-2" />
                      <div className="h-4 bg-gray-100 rounded w-full mb-2" />
                      <div className="h-4 bg-gray-100 rounded w-2/3" />
                    </div>
                  ))}
                </div>
              ) : filteredArticles.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {filteredArticles.map((article) => (
                    <ArticleCard
                      key={article.id}
                      article={article}
                      onClick={() => selectArticle(article)}
                    />
                  ))}
                </div>
              ) : (
                <div className="text-center py-12">
                  <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-[var(--background)] flex items-center justify-center">
                    <svg className="w-8 h-8 text-muted" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                    </svg>
                  </div>
                  <p className="text-muted">No hay artículos en esta categoría</p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
