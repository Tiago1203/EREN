/**
 * Search Service
 * Búsqueda semántica usando PHASE 4
 */

import type { SearchResult, SearchFilters, KnowledgeArticle } from '../types/knowledge.types';
import { knowledgeService } from './knowledge.service';

export class SearchService {
  /**
   * Búsqueda semántica
   */
  async search(query: string, filters?: SearchFilters): Promise<SearchResult[]> {
    if (!query.trim()) {
      return [];
    }

    // TODO: Integrar con PHASE 4 Embeddings + Qdrant
    // Por ahora buscar en artículos mock
    
    const articles = await knowledgeService.getArticles();
    const queryLower = query.toLowerCase();
    
    return articles
      .filter((article) => {
        // Text match
        const textMatch =
          article.title.toLowerCase().includes(queryLower) ||
          article.content.toLowerCase().includes(queryLower) ||
          article.summary?.toLowerCase().includes(queryLower);
        
        if (!textMatch) return false;
        
        // Apply filters
        if (filters?.types?.length && !filters.types.includes(article.type)) {
          return false;
        }
        
        if (filters?.categoryIds?.length && article.category.id !== filters.categoryIds[0]) {
          return false;
        }
        
        return true;
      })
      .map((article) => this.articleToSearchResult(article, query));
  }

  /**
   * Sugerencias de búsqueda
   */
  async suggest(query: string): Promise<string[]> {
    if (!query.trim()) return [];
    
    const articles = await knowledgeService.getArticles();
    const queryLower = query.toLowerCase();
    
    // Get unique titles that match
    const suggestions = articles
      .filter((a) => a.title.toLowerCase().includes(queryLower))
      .map((a) => a.title)
      .slice(0, 5);
    
    return suggestions;
  }

  /**
   * Convierte artículo a resultado de búsqueda
   */
  private articleToSearchResult(article: KnowledgeArticle, query: string): SearchResult {
    // Extract snippet around match
    const queryLower = query.toLowerCase();
    const contentLower = article.content.toLowerCase();
    const index = contentLower.indexOf(queryLower);
    
    let snippet = article.summary || article.content;
    if (index !== -1) {
      const start = Math.max(0, index - 50);
      const end = Math.min(article.content.length, index + query.length + 100);
      snippet = '...' + article.content.substring(start, end) + '...';
    }
    
    // Calculate relevance (simplified)
    const relevance = article.title.toLowerCase().includes(queryLower) ? 0.9 : 0.7;
    
    return {
      id: article.id,
      title: article.title,
      snippet,
      relevance,
      type: article.type,
      category: article.category.name,
      tags: article.tags.map((t) => t.name),
      citations: article.citations,
    };
  }
}

export const searchService = new SearchService();
