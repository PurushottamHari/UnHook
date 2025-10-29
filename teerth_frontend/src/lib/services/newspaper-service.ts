import { getDatabase } from '@/lib/db/connection';
import { CachedNewspaper, CachedNewspaperArticle } from '@/types';

export class NewspaperService {
  async fetchNewspaperFromMongoDB(date: string): Promise<CachedNewspaper | null> {
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
        .map((item: any) => item.user_collected_content_id)
        .filter(Boolean);

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
        
        let title = '';
        if (generated.VERY_SHORT && generated.VERY_SHORT.string) {
          title = generated.VERY_SHORT.string;
        }

        if (!title && generated.SHORT && generated.SHORT.string) {
          const firstSentence = generated.SHORT.string.split('.')[0];
          title = firstSentence.length > 50
            ? firstSentence.substring(0, 50) + '...'
            : firstSentence;
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
      console.error('Error fetching newspaper from MongoDB:', error);
      return null;
    }
  }

  async getTodayNewspaper(): Promise<CachedNewspaper | null> {
    const today = new Date().toISOString().split('T')[0];
    return this.fetchNewspaperFromMongoDB(today);
  }
}
