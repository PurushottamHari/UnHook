import { Article } from '@/models/article.model';
import { articleCacheConfig } from './article-cache.config';

interface CachedArticle extends Article {
  cachedAt: number; // timestamp when cached
}

interface ArticleCacheData {
  articles: Map<string, CachedArticle>;
  order: string[]; // FIFO order - article IDs in insertion order
}

/**
 * Client-side article cache with FIFO eviction
 * Uses localStorage for persistence across page refreshes
 */
export class ArticleCache {
  private config = articleCacheConfig;
  private cache: ArticleCacheData;

  constructor() {
    this.cache = this.loadFromStorage();
  }

  /**
   * Load cache from localStorage
   */
  private loadFromStorage(): ArticleCacheData {
    if (typeof window === 'undefined' || !this.config.enabled) {
      return { articles: new Map(), order: [] };
    }

    try {
      const stored = localStorage.getItem(this.config.storageKey);
      if (!stored) {
        return { articles: new Map(), order: [] };
      }

      const parsed = JSON.parse(stored);
      // Convert array of [key, value] pairs back to Map
      const articles = new Map<string, CachedArticle>(parsed.articles || []);

      return {
        articles,
        order: parsed.order || [],
      };
    } catch (error) {
      console.error('Error loading article cache from localStorage:', error);
      return { articles: new Map(), order: [] };
    }
  }

  /**
   * Save cache to localStorage
   */
  private saveToStorage(): void {
    if (typeof window === 'undefined' || !this.config.enabled) {
      return;
    }

    try {
      // Convert Map to array for JSON serialization
      const articlesArray = Array.from(this.cache.articles.entries());
      const data = {
        articles: articlesArray,
        order: this.cache.order,
      };
      localStorage.setItem(this.config.storageKey, JSON.stringify(data));
    } catch (error) {
      console.error('Error saving article cache to localStorage:', error);
    }
  }

  /**
   * Get an article from cache
   */
  get(articleId: string): Article | null {
    if (!this.config.enabled) {
      return null;
    }

    const cached = this.cache.articles.get(articleId);
    if (!cached) {
      return null;
    }

    // Return article without the cachedAt timestamp
    const { cachedAt, ...article } = cached;
    return article;
  }

  /**
   * Store an article in cache with FIFO eviction
   */
  set(article: Article): void {
    if (!this.config.enabled) {
      return;
    }

    const articleId = article.id;

    // If article already exists, update it and move to end (most recent)
    if (this.cache.articles.has(articleId)) {
      // Remove from current position
      this.cache.order = this.cache.order.filter(id => id !== articleId);
    }

    // Add/update article
    this.cache.articles.set(articleId, {
      ...article,
      cachedAt: Date.now(),
    });

    // Add to end of order (most recent)
    this.cache.order.push(articleId);

    // Apply FIFO eviction if limit exceeded
    while (this.cache.order.length > this.config.maxCacheSize) {
      const oldestId = this.cache.order.shift(); // Remove from front (oldest)
      if (oldestId) {
        this.cache.articles.delete(oldestId);
      }
    }

    this.saveToStorage();
  }

  /**
   * Remove an article from cache
   */
  remove(articleId: string): void {
    this.cache.articles.delete(articleId);
    this.cache.order = this.cache.order.filter(id => id !== articleId);
    this.saveToStorage();
  }

  /**
   * Clear all cached articles
   */
  clear(): void {
    this.cache = { articles: new Map(), order: [] };
    this.saveToStorage();
  }

  /**
   * Get cache statistics
   */
  getStats() {
    return {
      size: this.cache.articles.size,
      maxSize: this.config.maxCacheSize,
      enabled: this.config.enabled,
    };
  }
}

// Singleton instance
export const articleCache = new ArticleCache();

