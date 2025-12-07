import { CachedNewspaper, CachedNewspaperArticle } from '@/models/newspaper.model';
import { Article } from '@/models/article.model';
import { articleCache } from '@/lib/services/cache/article/article-cache';

const NEWSPAPER_SERVICE_URL = 'https://unhook-production-b172.up.railway.app';

export class NewspaperService {
  /**
   * Convert date from YYYY-MM-DD to DD/MM/YYYY format
   * @private
   */
  private convertDateFormat(date: string): string {
    const parts = date.split('-');
    if (parts.length !== 3) {
      throw new Error(`Invalid date format: ${date}. Expected YYYY-MM-DD`);
    }
    return `${parts[2]}/${parts[1]}/${parts[0]}`;
  }

  /**
   * Transform GeneratedContent object to full Article object
   * Used to populate ArticleCache when fetching newspapers
   * @private
   */
  private transformToArticle(article: any): Article {
    const generated = article.generated || {};

    // Title should ONLY come from VERY_SHORT, never extracted from SHORT
    let title = '';
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
    let youtube_channel = '';
    if (article.youtube_channel) {
      youtube_channel = article.youtube_channel;
    }

    // Use MongoDB _id as the Article ID (backend endpoint expects MongoDB _id)
    const articleId = article.id;

    // Set article source and link
    const article_source = 'Teerth';
    const article_link = `https://unhook-production.up.railway.app/article/${articleId}`;

    return {
      id: articleId,
      title: title || 'Untitled Article',
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
  }

  /**
   * Fetch a newspaper by date and user ID
   * @param date - Date in YYYY-MM-DD format
   * @param userId - User ID to filter newspapers
   * @returns CachedNewspaper model or null if not found
   */
  async getNewspaperByDate(date: string, userId: string): Promise<CachedNewspaper | null> {
    try {
      // Convert date format from YYYY-MM-DD to DD/MM/YYYY
      const convertedDate = this.convertDateFormat(date);

      // Step 1: Fetch newspapers for the date
      const newspapersUrl = `${NEWSPAPER_SERVICE_URL}/newspapers?date=${encodeURIComponent(convertedDate)}`;
      const newspapersResponse = await fetch(newspapersUrl, {
        headers: {
          'X-User-ID': userId,
        },
      });

      if (!newspapersResponse.ok) {
        if (newspapersResponse.status === 404) {
          return null;
        }
        throw new Error(`Failed to fetch newspapers: ${newspapersResponse.statusText}`);
      }

      const newspapersData = await newspapersResponse.json();
      const newspapers = newspapersData?.data?.list_response || [];

      // Step 2: Find the newspaper matching the date
      // The backend filters by date, so we should get the first one (or none)
      if (newspapers.length === 0) {
        return null;
      }

      // Use the first newspaper (assuming backend filters correctly by date)
      const newspaper = newspapers[0];
      const newspaperId = newspaper.id;

      // Step 3: Fetch articles for this newspaper
      const articlesUrl = `${NEWSPAPER_SERVICE_URL}/newspapers/${newspaperId}/generated_content`;
      const articlesResponse = await fetch(articlesUrl, {
        headers: {
          'X-User-ID': userId,
        },
      });

      if (!articlesResponse.ok) {
        if (articlesResponse.status === 404) {
          // Newspaper exists but has no articles
          return {
            date: date,
            topics: [],
            total_time_to_read: '0m read',
            articles: [],
            cached_at: new Date().toISOString(),
          };
        }
        throw new Error(`Failed to fetch articles: ${articlesResponse.statusText}`);
      }

      const articlesData = await articlesResponse.json();
      const contentWithInteractions = articlesData?.data?.list_response || [];

      // Step 4: Transform articles to CachedNewspaperArticle format
      const cachedArticles: CachedNewspaperArticle[] = contentWithInteractions.map(
        (item: { generated_content: any }) => {
          const article = item.generated_content;
          const generated = article.generated || {};

          // Title should ONLY come from VERY_SHORT, never extracted from SHORT
          let title = '';
          if (generated.VERY_SHORT && generated.VERY_SHORT.string) {
            title = generated.VERY_SHORT.string;
          }

          // Summary should be the full SHORT content (for expandable card)
          // SHORT is the summary shown in the dashboard cards
          let summary = '';
          if (generated.SHORT && generated.SHORT.string) {
            summary = generated.SHORT.string;
          }

          const category = article.category?.category || 'Uncategorized';
          const readingTimeSeconds = article.reading_time_seconds || 0;
          const timeToRead =
            readingTimeSeconds > 0
              ? `${Math.ceil(readingTimeSeconds / 60)}m read`
              : '5 min read';

          // Use MongoDB _id as the article ID (backend endpoint expects MongoDB _id)
          const articleId = article.id;

          return {
            id: articleId,
            title: title || 'Untitled Article',
            category: category,
            time_to_read: timeToRead,
            summary: summary || '', // Return empty string if no SHORT content
            cached_at: new Date().toISOString(),
          };
        }
      );

      // Step 4.5: Transform articles to full Article objects and populate cache
      // This allows other pages (like article detail pages) to use cached data
      // Cache uses MongoDB _id as key (matching CachedNewspaperArticle.id)
      contentWithInteractions.forEach((item: { generated_content: any }) => {
        const article = item.generated_content;
        if (!article.id) {
          return; // Skip articles without MongoDB _id
        }
        try {
          const fullArticle = this.transformToArticle(article);
          articleCache.set(fullArticle);
        } catch (error) {
          console.warn('Failed to cache article:', error);
        }
      });

      // Step 5: Calculate total time to read
      const totalMinutes = cachedArticles.reduce((total, article) => {
        const timeMatch = article.time_to_read.match(/(\d+)/);
        return total + (timeMatch ? parseInt(timeMatch[1]) : 5);
      }, 0);

      const totalTimeToRead =
        totalMinutes > 60
          ? `${Math.floor(totalMinutes / 60)}h ${totalMinutes % 60}m read`
          : `${totalMinutes}m read`;

      // Step 6: Extract unique topics from article categories
      const topics = [...new Set(cachedArticles.map((article) => article.category))];

      return {
        date: date,
        articles: cachedArticles,
        total_time_to_read: totalTimeToRead,
        topics: topics,
        cached_at: new Date().toISOString(),
      };
    } catch (error) {
      console.error('Error fetching newspaper:', error);
      return null;
    }
  }

  /**
   * Fetch today's newspaper
   * @param userId - User ID to filter newspapers
   * @returns CachedNewspaper model or null if not found
   */
  async getTodayNewspaper(userId: string): Promise<CachedNewspaper | null> {
    const today = new Date().toISOString().split('T')[0];
    return this.getNewspaperByDate(today, userId);
  }
}
