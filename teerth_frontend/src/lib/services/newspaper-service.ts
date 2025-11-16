import { getDatabase } from '@/lib/db/connection';
import { CachedNewspaper, CachedNewspaperArticle } from '@/models/newspaper.model';

export class NewspaperService {
  /**
   * Fetch a newspaper by date and user ID
   * @param date - Date in YYYY-MM-DD format
   * @param userId - User ID to filter newspapers
   * @returns CachedNewspaper model or null if not found
   */
  async getNewspaperByDate(date: string, userId: string): Promise<CachedNewspaper | null> {
    try {
      const db = await getDatabase();
      const newspapersCollection = db.collection('newspapers');

      // Convert date to epoch timestamp range
      const dateObj = new Date(date);
      const startOfDay = new Date(
        dateObj.getFullYear(),
        dateObj.getMonth(),
        dateObj.getDate(),
        0, 0, 0
      );
      const endOfDay = new Date(
        dateObj.getFullYear(),
        dateObj.getMonth(),
        dateObj.getDate(),
        23, 59, 59
      );

      const startOfDayTimestamp = Math.floor(startOfDay.getTime() / 1000);
      const endOfDayTimestamp = Math.floor(endOfDay.getTime() / 1000);

      const newspaper = await newspapersCollection.findOne({
        user_id: userId,
        created_at: {
          $gte: startOfDayTimestamp,
          $lte: endOfDayTimestamp,
        },
      });

      if (!newspaper) {
        return null;
      }

      const consideredContentList = newspaper.considered_content_list || [];
      const consideredContentIds = consideredContentList
        .map((item: { user_collected_content_id?: string }) => item.user_collected_content_id)
        .filter((id: string | undefined): id is string => Boolean(id));

      if (consideredContentIds.length === 0) {
        return {
          date: date,
          topics: [],
          total_time_to_read: '0m read',
          articles: [],
          cached_at: new Date().toISOString(),
        };
      }

      // Get external_ids from collected_content collection
      const collectedContentCollection = db.collection('collected_content');
      const externalIds = [];

      for (const contentId of consideredContentIds) {
        const collectedDoc = await collectedContentCollection.findOne({
          _id: contentId,
        });
        if (collectedDoc && collectedDoc.external_id) {
          externalIds.push(collectedDoc.external_id);
        }
      }

      if (externalIds.length === 0) {
        return {
          date: date,
          topics: [],
          total_time_to_read: '0m read',
          articles: [],
          cached_at: new Date().toISOString(),
        };
      }

      // Fetch generated articles
      const generatedContentCollection = db.collection('generated_content');
      const articles = await generatedContentCollection
        .find({
          status: 'ARTICLE_GENERATED',
          external_id: { $in: externalIds },
        })
        .toArray();

      const cachedArticles: CachedNewspaperArticle[] = articles.map(article => {
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
        const timeToRead = readingTimeSeconds > 0
          ? `${Math.ceil(readingTimeSeconds / 60)}m read`
          : '5 min read';

        return {
          id: article._id.toString(),
          title: title || 'Untitled Article',
          category: category,
          time_to_read: timeToRead,
          summary: summary || '', // Return empty string if no SHORT content
          cached_at: new Date().toISOString(),
        };
      });

      // Calculate total time to read
      const totalMinutes = cachedArticles.reduce((total, article) => {
        const timeMatch = article.time_to_read.match(/(\d+)/);
        return total + (timeMatch ? parseInt(timeMatch[1]) : 5);
      }, 0);

      const totalTimeToRead = totalMinutes > 60
        ? `${Math.floor(totalMinutes / 60)}h ${totalMinutes % 60}m read`
        : `${totalMinutes}m read`;

      const topics = [...new Set(cachedArticles.map(article => article.category))];

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
