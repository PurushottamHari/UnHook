import { Article } from '@/models/article.model';
import { getDatabase } from '@/lib/db/connection';
import { articleCache } from '@/lib/services/cache/article/article-cache';

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
   * Server-side article fetching (direct DB access)
   * @private
   */
  private async getArticleByIdServer(articleId: string): Promise<Article | null> {
    try {
      const db = await getDatabase();
      const generatedContentCollection = db.collection('generated_content');

      // Query by string ID (UUID format) - this is how articles are stored
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const query: any = { _id: articleId };
      const doc = await generatedContentCollection.findOne(query);

      if (!doc) {
        return null;
      }

      // Extract title from VERY_SHORT content
      let title = '';
      const generated = doc.generated || {};
      if (generated.VERY_SHORT && generated.VERY_SHORT.string) {
        title = generated.VERY_SHORT.string;
      }

      // If no title from VERY_SHORT, try to extract from SHORT
      if (!title && generated.SHORT && generated.SHORT.string) {
        const summary = generated.SHORT.string;
        title = summary.split('.')[0].length > 50
          ? summary.split('.')[0].substring(0, 50) + '...'
          : summary.split('.')[0];
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
      const category = doc.category?.category || 'TECHNOLOGY';

      // Get reading time
      const readingTimeSeconds = doc.reading_time_seconds || 0;
      const minutes = Math.ceil(readingTimeSeconds / 60);
      const time_to_read = minutes < 1 ? 'Less than 1 min read' : `${minutes} min read`;

      // Get published date
      let published_at = new Date().toISOString();
      if (doc.content_generated_at) {
        published_at = new Date(doc.content_generated_at * 1000).toISOString();
      } else if (doc.created_at) {
        published_at = new Date(doc.created_at * 1000).toISOString();
      }

      // Get external_id (YouTube video ID)
      const external_id = doc.external_id || '';

      // Fetch channel name from collected_content collection
      let youtube_channel = '';
      if (external_id) {
        const collectedContentCollection = db.collection('collected_content');
        const collectedDoc = await collectedContentCollection.findOne({
          external_id: external_id,
        });

        if (collectedDoc && collectedDoc.data && collectedDoc.data.YOUTUBE_VIDEO) {
          const videoDetails = collectedDoc.data.YOUTUBE_VIDEO;
          if (videoDetails.channel_name) {
            youtube_channel = videoDetails.channel_name;
          }
        }
      }

      // Set article source and link
      const article_source = 'Teerth';
      const article_link = `https://unhook-production.up.railway.app/article/${articleId}`;

      return {
        id: articleId,
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
