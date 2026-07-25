/**
 * Tipos para el módulo Knowledge
 */

// ============== ARTICLES ==============

export type ArticleType = 'procedure' | 'protocol' | 'guideline' | 'manual' | 'article' | 'faq' | 'other';
export type ArticleStatus = 'draft' | 'review' | 'published' | 'archived';

export interface KnowledgeArticle {
  id: string;
  title: string;
  content: string;
  summary?: string;
  type: ArticleType;
  category: Category;
  tags: Tag[];
  author?: Author;
  createdAt: Date;
  updatedAt: Date;
  publishedAt?: Date;
  status: ArticleStatus;
  citations: Citation[];
  relatedArticles?: KnowledgeArticle[];
  metadata: ArticleMetadata;
}

export interface ArticleMetadata {
  language: string;
  version: string;
  lastReviewed?: Date;
  nextReview?: Date;
  difficulty?: 'basic' | 'intermediate' | 'advanced';
  estimatedReadTime?: number;
}

export interface Author {
  id: string;
  name: string;
  email?: string;
  role?: string;
}

// ============== CATEGORIES ==============

export interface Category {
  id: string;
  name: string;
  description?: string;
  parentId?: string;
  children?: Category[];
  articleCount: number;
  icon?: string;
  color?: string;
}

export interface CategoryTree {
  root: Category[];
  flat: Map<string, Category>;
}

// ============== TAGS ==============

export interface Tag {
  id: string;
  name: string;
  color?: string;
  articleCount: number;
}

// ============== SEARCH ==============

export interface SearchResult {
  id: string;
  title: string;
  snippet: string;
  relevance: number;
  type: ArticleType;
  category?: string;
  tags?: string[];
  citations?: Citation[];
}

export interface SearchFilters {
  query?: string;
  types?: ArticleType[];
  categoryIds?: string[];
  tagIds?: string[];
  authorId?: string;
  dateFrom?: Date;
  dateTo?: Date;
  status?: ArticleStatus[];
}

export interface SearchQuery {
  id: string;
  query: string;
  timestamp: Date;
  resultCount: number;
}

// ============== CITATIONS ==============

export type CitationType = 'article' | 'book' | 'guideline' | 'protocol' | 'web' | 'other';

export interface Citation {
  id: string;
  title: string;
  authors?: string[];
  journal?: string;
  year?: number;
  doi?: string;
  url?: string;
  type: CitationType;
  relevance: number;
  pages?: string;
  volume?: string;
  issue?: string;
}

export type CitationStyle = 'apa' | 'mla' | 'chicago' | 'vancouver';

// ============== STATE ==============

export interface KnowledgeState {
  articles: KnowledgeArticle[];
  categories: Category[];
  tags: Tag[];
  searchResults: SearchResult[];
  selectedArticle: KnowledgeArticle | null;
  loading: boolean;
  searching: boolean;
  error: string | null;
  filters: SearchFilters;
}

export interface KnowledgeFilters {
  categories: string[];
  tags: string[];
  types: ArticleType[];
  status: ArticleStatus[];
}
