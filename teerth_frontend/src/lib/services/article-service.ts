import { Article } from '@/models/article.model';
import { articleCache } from '@/lib/services/cache/article/article-cache';

const NEWSPAPER_SERVICE_URL = 'https://unhook-production-b172.up.railway.app';

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
   * @returns Article model or null if not found
   */
  async getArticleById(articleId: string): Promise<Article | null> {
    if (this.isClient()) {
      return this.getArticleByIdClient(articleId);
    } else {
      return this.getArticleByIdServer(articleId);
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
  private async getArticleByIdServer(articleId: string): Promise<Article | null> {
    try {
      // The backend endpoint expects MongoDB _id (generated_content_id)
      const articleUrl = `${NEWSPAPER_SERVICE_URL}/generated_content/${articleId}`;
      const response = await fetch(articleUrl);

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

      const article = await response.json();

      // Title should ONLY come from VERY_SHORT, never extracted from SHORT
      let title = '';
      const generated = article.generated || {};
      if (generated.VERY_SHORT && generated.VERY_SHORT.string) {
        title = generated.VERY_SHORT.string;
      }

      // Get content - prefer LONG, then MEDIUM, then SHORT
      let content = '';
      if (generated.LONG && generated.LONG.markdown_string) {
        content = generated.LONG.markdown_string;
      } else if (generated.LONG && generated.LONG.string) {
        content = generated.LONG.string;
      } else if (generated.MEDIUM && generated.MEDIUM.markdown_string) {
        content = generated.MEDIUM.markdown_string;
      } else if (generated.MEDIUM && generated.MEDIUM.string) {
        content = generated.MEDIUM.string;
      } else if (generated.SHORT && generated.SHORT.string) {
        content = generated.SHORT.string;
      }

      // Get category
      const category = article.category?.category || 'TECHNOLOGY';

      // Get reading time
      const readingTimeSeconds = article.reading_time_seconds || 0;
      const minutes = Math.ceil(readingTimeSeconds / 60);
      const time_to_read =
        minutes < 1 ? 'Less than 1 min read' : `${minutes} min read`;

      // Get published date
      let published_at = new Date().toISOString();
      if (article.content_generated_at) {
        published_at = new Date(article.content_generated_at * 1000).toISOString();
      } else if (article.created_at) {
        published_at = new Date(article.created_at * 1000).toISOString();
      }

      // Get external_id (YouTube video ID)
      const external_id = article.external_id || '';

      // Note: youtube_channel may not be included in the GeneratedContent response
      // If needed, this would require an additional API call or the backend to include it
      // For now, we'll leave it empty if not in the response
      let youtube_channel = '';
      // Check if youtube_channel is included in the response
      if (article.youtube_channel) {
        youtube_channel = article.youtube_channel;
      }

      // Set article source and link
      const article_source = 'Teerth';
      const article_link = `https://unhook-production.up.railway.app/article/${articleId}`;

      // Use MongoDB _id if available, otherwise use external_id or the provided articleId
      const articleIdToUse = article.id || article.external_id || articleId;

      return {
        id: articleIdToUse,
        title: title || 'Article Not Found',
        content: content || '',
        category,
        time_to_read,
        article_link,
        article_source,
        external_id,
        youtube_channel,
        published_at,
        cached_at: new Date().toISOString(),
      };
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
