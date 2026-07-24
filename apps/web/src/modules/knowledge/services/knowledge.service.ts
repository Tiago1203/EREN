/**
 * Knowledge Service
 * Consumes PHASE 4 Knowledge Platform
 */

import type {
  KnowledgeArticle,
  Category,
  Tag,
  SearchResult,
  SearchFilters,
  Citation,
  ArticleType,
} from '../types/knowledge.types';

export class KnowledgeService {
  private baseUrl: string;

  constructor(baseUrl: string = '/api/knowledge') {
    this.baseUrl = baseUrl;
  }

  /**
   * Obtiene todos los artículos
   */
  async getArticles(filters?: SearchFilters): Promise<KnowledgeArticle[]> {
    // TODO: Integrar con PHASE 4
    return this.getMockArticles();
  }

  /**
   * Obtiene un artículo por ID
   */
  async getArticle(id: string): Promise<KnowledgeArticle | null> {
    // TODO: Integrar con PHASE 4
    const articles = this.getMockArticles();
    return articles.find((a) => a.id === id) || null;
  }

  /**
   * Obtiene categorías
   */
  async getCategories(): Promise<Category[]> {
    return this.getMockCategories();
  }

  /**
   * Obtiene tags
   */
  async getTags(): Promise<Tag[]> {
    return this.getMockTags();
  }

  /**
   * Obtiene artículos populares
   */
  async getPopularArticles(limit: number = 10): Promise<KnowledgeArticle[]> {
    return this.getMockArticles().slice(0, limit);
  }

  /**
   * Obtiene artículos relacionados
   */
  async getRelatedArticles(articleId: string): Promise<KnowledgeArticle[]> {
    // TODO: Integrar con PHASE 4 embeddings
    return this.getMockArticles().filter((a) => a.id !== articleId).slice(0, 5);
  }

  // ============== MOCK DATA ==============

  private getMockArticles(): KnowledgeArticle[] {
    return [
      {
        id: 'art-1',
        title: 'Protocolo de Mantenimiento Preventivo - Bombas de Infusión',
        content: 'Este protocolo describe los procedimientos de mantenimiento preventivo para bombas de infusión...',
        summary: 'Guía completa para el mantenimiento preventivo de bombas de infusión.',
        type: 'protocol',
        category: this.getMockCategories()[0],
        tags: [this.getMockTags()[0], this.getMockTags()[2]],
        author: { id: 'user-1', name: 'Dr. García', role: 'Ingeniero Biomédico' },
        createdAt: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000),
        updatedAt: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000),
        publishedAt: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000),
        status: 'published',
        citations: [],
        metadata: {
          language: 'es',
          version: '2.0',
          difficulty: 'intermediate',
          estimatedReadTime: 15,
        },
      },
      {
        id: 'art-2',
        title: 'Manual de Operación - Monitor de Signos Vitales',
        content: 'Manual de operación para monitores de signos vitales de la serie VS...',
        summary: 'Manual de operación detallado para monitores de signos vitales.',
        type: 'manual',
        category: this.getMockCategories()[1],
        tags: [this.getMockTags()[1]],
        author: { id: 'user-2', name: 'Ing. Martínez', role: 'Técnico Biomédico' },
        createdAt: new Date(Date.now() - 60 * 24 * 60 * 60 * 1000),
        updatedAt: new Date(Date.now() - 14 * 24 * 60 * 60 * 1000),
        publishedAt: new Date(Date.now() - 14 * 24 * 60 * 60 * 1000),
        status: 'published',
        citations: [],
        metadata: {
          language: 'es',
          version: '3.1',
          difficulty: 'basic',
          estimatedReadTime: 20,
        },
      },
      {
        id: 'art-3',
        title: 'Guía Clínica - Calibración de Equipos de Diagnóstico',
        content: 'Esta guía describe los procedimientos de calibración para equipos de diagnóstico...',
        summary: 'Procedimientos de calibración según normativas internacionales.',
        type: 'guideline',
        category: this.getMockCategories()[2],
        tags: [this.getMockTags()[3], this.getMockTags()[4]],
        author: { id: 'user-3', name: 'Dra. López', role: 'Coordinadora Clínica' },
        createdAt: new Date(Date.now() - 90 * 24 * 60 * 60 * 1000),
        updatedAt: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000),
        publishedAt: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000),
        status: 'published',
        citations: [
          {
            id: 'cit-1',
            title: 'IEC 60601-1:2020',
            type: 'guideline',
            relevance: 0.95,
          },
        ],
        metadata: {
          language: 'es',
          version: '1.0',
          difficulty: 'advanced',
          estimatedReadTime: 30,
        },
      },
      {
        id: 'art-4',
        title: 'Procedimiento de Emergencia - Fallo de Respirador',
        content: 'Pasos a seguir en caso de fallo de un respirador mecánico...',
        summary: 'Protocolo de emergencia para fallo de equipos de ventilación.',
        type: 'procedure',
        category: this.getMockCategories()[3],
        tags: [this.getMockTags()[5], this.getMockTags()[0]],
        author: { id: 'user-1', name: 'Dr. García', role: 'Ingeniero Biomédico' },
        createdAt: new Date(Date.now() - 15 * 24 * 60 * 60 * 1000),
        updatedAt: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000),
        publishedAt: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000),
        status: 'published',
        citations: [],
        metadata: {
          language: 'es',
          version: '1.2',
          difficulty: 'basic',
          estimatedReadTime: 10,
        },
      },
    ];
  }

  private getMockCategories(): Category[] {
    return [
      {
        id: 'cat-1',
        name: 'Bombas de Infusión',
        description: 'Artículos sobre bombas de infusión y perfusión',
        articleCount: 12,
        icon: 'Wrench',
        children: [
          { id: 'cat-1-1', name: 'Infusión Volumétrica', articleCount: 5 },
          { id: 'cat-1-2', name: 'Bombas de Jeringa', articleCount: 7 },
        ],
      },
      {
        id: 'cat-2',
        name: 'Monitores',
        description: 'Monitores de signos vitales y parametros',
        articleCount: 18,
        icon: 'Monitor',
        children: [
          { id: 'cat-2-1', name: 'Signos Vitales', articleCount: 10 },
          { id: 'cat-2-2', name: 'Cardiacos', articleCount: 8 },
        ],
      },
      {
        id: 'cat-3',
        name: 'Diagnóstico',
        description: 'Equipos de diagnóstico y laboratorio',
        articleCount: 25,
        icon: 'Search',
      },
      {
        id: 'cat-4',
        name: 'Emergencia',
        description: 'Procedimientos de emergencia y UCI',
        articleCount: 8,
        icon: 'AlertTriangle',
      },
      {
        id: 'cat-5',
        name: 'Ventilación',
        description: 'Respiradores y equipos de ventilación',
        articleCount: 15,
        icon: 'Activity',
      },
    ];
  }

  private getMockTags(): Tag[] {
    return [
      { id: 'tag-1', name: 'Mantenimiento', color: 'blue', articleCount: 45 },
      { id: 'tag-2', name: 'Operación', color: 'green', articleCount: 32 },
      { id: 'tag-3', name: 'Preventivo', color: 'purple', articleCount: 28 },
      { id: 'tag-4', name: 'Calibración', color: 'orange', articleCount: 15 },
      { id: 'tag-5', name: 'Seguridad', color: 'red', articleCount: 22 },
      { id: 'tag-6', name: 'Emergencia', color: 'yellow', articleCount: 10 },
    ];
  }
}

export const knowledgeService = new KnowledgeService();
