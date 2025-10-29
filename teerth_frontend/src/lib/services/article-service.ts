import { getDatabase } from '@/lib/db/connection';
import { Article } from '@/types';
import { ObjectId } from 'mongodb';

export class ArticleService {
  async fetchArticleFromMongoDB(articleId: string): Promise<Article | null> {
    try {
      const db = await getDatabase();
      const generatedContentCollection = db.collection('generated_content');

      // Try different query approaches
      let doc = null;
      
      // First try as string ID
      doc = await generatedContentCollection.findOne({ _id: articleId });

      // If not found, try as ObjectId
      if (!doc && /^[0-9a-fA-F]{24}$/.test(articleId)) {
        try {
          doc = await generatedContentCollection.findOne({
            _id: new ObjectId(articleId),
          });
        } catch {
          // ObjectId conversion failed
        }
      }

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
      console.error('Error fetching article from MongoDB:', error);
      return null;
    }
  }
}
