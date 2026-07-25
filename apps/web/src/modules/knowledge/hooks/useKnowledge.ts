'use client';

import { useCallback, useEffect, useState } from 'react';
import { useKnowledgeStore } from '../stores/knowledge.store';
import { knowledgeService } from '../services/knowledge.service';
import { searchService } from '../services/search.service';
import type { SearchFilters, KnowledgeArticle } from '../types/knowledge.types';

export interface UseKnowledgeReturn {
  // Data
  articles: KnowledgeArticle[];
  categories: ReturnType<typeof useKnowledgeStore>['categories'];
  tags: ReturnType<typeof useKnowledgeStore>['tags'];
  searchResults: ReturnType<typeof useKnowledgeStore>['searchResults'];
  selectedArticle: KnowledgeArticle | null;
  
  // State
  loading: boolean;
  searching: boolean;
  error: string | null;
  
  // Actions
  loadArticles: (filters?: SearchFilters) => Promise<void>;
  loadCategories: () => Promise<void>;
  loadTags: () => Promise<void>;
  search: (query: string, filters?: SearchFilters) => Promise<void>;
  selectArticle: (article: KnowledgeArticle | null) => void;
  clearSearch: () => void;
}

export function useKnowledge(): UseKnowledgeReturn {
  const {
    articles,
    categories,
    tags,
    searchResults,
    selectedArticle,
    loading,
    searching,
    error,
    setArticles,
    setCategories,
    setTags,
    setSearchResults,
    setSelectedArticle,
    clearSearchResults,
    setLoading,
    setSearching,
    setError,
  } = useKnowledgeStore();

  const loadArticles = useCallback(async (filters?: SearchFilters) => {
    try {
      setLoading(true);
      setError(null);
      const data = await knowledgeService.getArticles(filters);
      setArticles(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error loading articles');
    } finally {
      setLoading(false);
    }
  }, [setArticles, setLoading, setError]);

  const loadCategories = useCallback(async () => {
    try {
      const data = await knowledgeService.getCategories();
      setCategories(data);
    } catch (err) {
      console.error('Error loading categories:', err);
    }
  }, [setCategories]);

  const loadTags = useCallback(async () => {
    try {
      const data = await knowledgeService.getTags();
      setTags(data);
    } catch (err) {
      console.error('Error loading tags:', err);
    }
  }, [setTags]);

  const search = useCallback(async (query: string, filters?: SearchFilters) => {
    try {
      setSearching(true);
      const results = await searchService.search(query, filters);
      setSearchResults(results);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error searching');
    } finally {
      setSearching(false);
    }
  }, [setSearchResults, setSearching, setError]);

  const selectArticle = useCallback((article: KnowledgeArticle | null) => {
    setSelectedArticle(article);
  }, [setSelectedArticle]);

  const clearSearch = useCallback(() => {
    clearSearchResults();
  }, [clearSearchResults]);

  useEffect(() => {
    loadArticles();
    loadCategories();
    loadTags();
  }, []);

  return {
    articles,
    categories,
    tags,
    searchResults,
    selectedArticle,
    loading,
    searching,
    error,
    loadArticles,
    loadCategories,
    loadTags,
    search,
    selectArticle,
    clearSearch,
  };
}
