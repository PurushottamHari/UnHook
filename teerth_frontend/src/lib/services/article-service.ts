import { Article } from '@/models/article.model';
import { articleCache } from '@/lib/services/cache/article/article-cache';
import { ArticleAdaptor } from '../adaptors/article-adaptor';

const NEWSPAPER_SERVICE_URL = process.env.NEWSPAPER_SERVICE_URL;

export class ArticleService {
  /**
   * Check if running on client-side
   */
  private isClient(): boolean {
    return typeof window !== 'undefined';
  }

  /**
   * Fetch an article by its ID
   * On client: uses API + caching
   * On server: uses direct DB access
   * 
   * @param articleId - The article identifier
   * @param userId - Optional User ID for personalized data (interactions)
   * @returns Article model or null if not found
   */
  async getArticleById(articleId: string, userId?: string): Promise<Article | null> {
    if (this.isClient()) {
      return this.getArticleByIdClient(articleId);
    } else {
      return this.getArticleByIdServer(articleId, userId);
    }
  }

  /**
   * Client-side article fetching with caching
   * @private
   */
  private async getArticleByIdClient(articleId: string): Promise<Article | null> {
    // Check cache first for instant return
    const cachedArticle = articleCache.get(articleId);
    if (cachedArticle) {
      return cachedArticle;
    }

    // Not in cache, fetch from API
    return this.fetchAndCacheArticle(articleId);
  }

  /**
   * Fetch article from API and cache it (client-side only)
   * @private
   */
  private async fetchAndCacheArticle(articleId: string): Promise<Article | null> {
    try {
      const response = await fetch(`/api/articles/${articleId}`);
      const data = await response.json();

      if (!data.success) {
        throw new Error(data.error || 'Failed to fetch article');
      }

      // Store in cache for future use
      articleCache.set(data.article);

      return data.article;
    } catch (error) {
      console.error('Error fetching article:', error);
      return null;
    }
  }

  /**
   * Server-side article fetching (REST API)
   * @private
   */
  private async getArticleByIdServer(articleId: string, userId?: string): Promise<Article | null> {
    try {
      // The backend endpoint expects MongoDB _id (generated_content_id)
      const articleUrl = `${NEWSPAPER_SERVICE_URL}/generated_content/${articleId}`;
      
      // Backend REQUIRES X-User-ID header now
      const headers: Record<string, string> = {
        'X-User-ID': userId || process.env.NEXT_PUBLIC_DEFAULT_GUEST_USER_ID || '607d95f0-47ef-444c-89d2-d05f257d1265'
      };

      console.log(`[DEBUG] Fetching article from ${articleUrl} with headers:`, headers);

      const response = await fetch(articleUrl, { 
        headers,
        cache: 'no-store' // Ensure we don't get a cached error response
      });

      console.log(`[DEBUG] Fetch article response: ${response.status} ${response.statusText}`);

      if (!response.ok) {
        if (response.status === 404) {
          return null;
        }
        // For 400 Bad Request, log the error but return null
        if (response.status === 400) {
          console.error(`Article fetch failed: articleId ${articleId} may not be a valid MongoDB _id`);
          return null;
        }
        throw new Error(`Failed to fetch article: ${response.statusText}`);
      }

      const articleData = await response.json();
      return ArticleAdaptor.toArticle(articleData);
    } catch (error) {
      console.error('Error fetching article:', error);
      return null;
    }
  }

  /**
   * Get cached article without fetching (client-side only)
   * Useful for instant display while data is being fetched
   * 
   * @param articleId - The article identifier
   * @returns Article from cache or null if not cached
   */
  async getCachedArticle(articleId: string): Promise<Article | null> {
    if (!this.isClient()) {
      return null; // No cache on server
    }

    return articleCache.get(articleId);
  }

  /**
   * Clear the article cache (client-side only)
   */
  async clearCache(): Promise<void> {
    if (!this.isClient()) {
      return;
    }

    articleCache.clear();
  }

  /**
   * Remove a specific article from cache (client-side only)
   */
  async removeFromCache(articleId: string): Promise<void> {
    if (!this.isClient()) {
      return;
    }

    articleCache.remove(articleId);
  }
}
