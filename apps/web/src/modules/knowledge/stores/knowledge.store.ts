'use client';

import { create } from 'zustand';
import type {
  KnowledgeArticle,
  Category,
  Tag,
  SearchResult,
  SearchFilters,
  KnowledgeState,
} from '../types/knowledge.types';

interface KnowledgeStore extends KnowledgeState {
  // Actions - Articles
  setArticles: (articles: KnowledgeArticle[]) => void;
  addArticle: (article: KnowledgeArticle) => void;
  updateArticle: (id: string, article: Partial<KnowledgeArticle>) => void;
  removeArticle: (id: string) => void;
  setSelectedArticle: (article: KnowledgeArticle | null) => void;
  
  // Actions - Categories & Tags
  setCategories: (categories: Category[]) => void;
  setTags: (tags: Tag[]) => void;
  
  // Actions - Search
  setSearchResults: (results: SearchResult[]) => void;
  setSearching: (searching: boolean) => void;
  clearSearchResults: () => void;
  
  // Actions - Filters
  setFilters: (filters: Partial<SearchFilters>) => void;
  clearFilters: () => void;
  
  // Actions - State
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  
  // Actions - Reset
  reset: () => void;
}

const initialState: KnowledgeState = {
  articles: [],
  categories: [],
  tags: [],
  searchResults: [],
  selectedArticle: null,
  loading: false,
  searching: false,
  error: null,
  filters: {},
};

export const useKnowledgeStore = create<KnowledgeStore>((set) => ({
  ...initialState,

  // Articles
  setArticles: (articles) => set({ articles }),
  addArticle: (article) => set((state) => ({ articles: [article, ...state.articles] })),
  updateArticle: (id, update) => set((state) => ({
    articles: state.articles.map((a) => (a.id === id ? { ...a, ...update } : a)),
  })),
  removeArticle: (id) => set((state) => ({
    articles: state.articles.filter((a) => a.id !== id),
    selectedArticle: state.selectedArticle?.id === id ? null : state.selectedArticle,
  })),
  setSelectedArticle: (article) => set({ selectedArticle: article }),

  // Categories & Tags
  setCategories: (categories) => set({ categories }),
  setTags: (tags) => set({ tags }),

  // Search
  setSearchResults: (results) => set({ searchResults: results }),
  setSearching: (searching) => set({ searching }),
  clearSearchResults: () => set({ searchResults: [] }),

  // Filters
  setFilters: (filters) => set((state) => ({
    filters: { ...state.filters, ...filters },
  })),
  clearFilters: () => set({ filters: {} }),

  // State
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),

  // Reset
  reset: () => set(initialState),
}));
