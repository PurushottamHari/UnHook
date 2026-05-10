import { CachedNewspaper, CachedNewspaperArticle } from '@/models/newspaper.model';
import { Article } from '@/models/article.model';
import { articleCache } from '@/lib/services/cache/article/article-cache';
import { ArticleAdaptor } from '../adaptors/article-adaptor';

const NEWSPAPER_SERVICE_URL = process.env.NEWSPAPER_SERVICE_URL;

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
   * Fetch a single page of articles for a newspaper using V2 API
   * @param date - Date in YYYY-MM-DD format
   * @param userId - User ID
   * @param startingAfter - Optional cursor for pagination (nextCursor from previous response)
   * @returns Object with articles and hasNext flag
   */
  async getNewspaperArticlesPage(
    date: string,
    userId: string,
    startingAfter?: string | null
  ): Promise<{ articles: any[], hasNext: boolean, nextCursor: string | null, newspaperId: string }> {
    const convertedDate = this.convertDateFormat(date);
    const articlesUrl = new URL(`${NEWSPAPER_SERVICE_URL}/v2/newspapers/by-date`);
    
    articlesUrl.searchParams.set('date', convertedDate);
    if (startingAfter) {
      articlesUrl.searchParams.set('starting_after', startingAfter);
    }

    const response = await fetch(articlesUrl.toString(), {
      headers: {
        'X-User-ID': userId,
      },
    });

    if (!response.ok) {
      if (response.status === 404) {
        return { articles: [], hasNext: false, nextCursor: null, newspaperId: '' };
      }
      throw new Error(`Failed to fetch articles page: ${response.statusText}`);
    }

    const v2Data = await response.json();
    const articles = v2Data.articles?.data || [];
    const hasNext = v2Data.articles?.hasNext || false;
    const nextCursor = v2Data.articles?.nextCursor || null;

    return {
      articles,
      hasNext,
      nextCursor,
      newspaperId: v2Data.id,
    };
  }

  async getNewspaperIdByDate(date: string, userId: string): Promise<string | null> {
    try {
      const convertedDate = this.convertDateFormat(date);
      const url = `${NEWSPAPER_SERVICE_URL}/v2/newspapers/by-date?date=${encodeURIComponent(convertedDate)}`;
      
      const response = await fetch(url, {
        headers: {
          'X-User-ID': userId,
        },
      });

      if (!response.ok) {
        return null;
      }

      const data = await response.json();
      return data.id || null;
    } catch (error) {
      console.error('Error fetching newspaper ID:', error);
      return null;
    }
  }

  async getNewspaperByDate(date: string, userId: string): Promise<CachedNewspaper | null> {
    try {
      const convertedDate = this.convertDateFormat(date);
      const url = `${NEWSPAPER_SERVICE_URL}/v2/newspapers/by-date?date=${encodeURIComponent(convertedDate)}`;
      
      const response = await fetch(url, {
        headers: {
          'X-User-ID': userId,
        },
      });

      if (!response.ok) {
        if (response.status === 404) return null;
        throw new Error(`Failed to fetch newspaper V2: ${response.statusText}`);
      }

      const v2Data = await response.json();
      const rawArticles = v2Data.articles?.data || [];

      // Single-pass mapping and hydration
      const cachedArticles: CachedNewspaperArticle[] = rawArticles.map((article: any) => {
        // A. Transform to FULL Article and hydrate cache
        const fullArticle = ArticleAdaptor.toArticle(article);
        articleCache.set(fullArticle);

        // B. Return lightweight summary for the dashboard
        return {
          id: fullArticle.id,
          title: fullArticle.title,
          category: fullArticle.category,
          time_to_read: fullArticle.time_to_read,
          summary: fullArticle.summary || '',
          youtube_channel: fullArticle.youtube_channel,
          published_at: fullArticle.published_at,
          interactions: article.interactions || [],
          cached_at: new Date().toISOString(),
        };
      });

      // Calculate total reading time from newspaper level (V2 provides this)
      const totalReadingTimeSeconds = v2Data.reading_time_in_seconds || 0;
      const totalMinutes = Math.ceil(totalReadingTimeSeconds / 60);
      const totalTimeToRead =
        totalMinutes > 60
          ? `${Math.floor(totalMinutes / 60)}h ${totalMinutes % 60}m read`
          : `${totalMinutes}m read`;

      // Extract unique topics
      const topics = [...new Set(cachedArticles.map((article) => article.category))];

      return {
        date: date,
        articles: cachedArticles,
        total_time_to_read: totalTimeToRead,
        topics: topics,
        cached_at: new Date().toISOString(),
      };
    } catch (error) {
      console.error('Error fetching newspaper V2:', error);
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
