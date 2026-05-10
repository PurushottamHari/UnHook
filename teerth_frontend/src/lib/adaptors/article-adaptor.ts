import { Article } from '@/models/article.model';

/**
 * Adaptor for converting raw API article data to standardized frontend formats.
 */

export interface ExtractedSourceInfo {
  external_id: string;
  youtube_channel: string;
  article_source: string;
}

export class ArticleAdaptor {
  /**
   * Extracts source metadata (external_id, youtube_channel, article_source)
   * from a raw article object, handling different backend structures.
   */
  static extractSourceInfo(article: any): ExtractedSourceInfo {
    let external_id = article.external_id || '';
    let youtube_channel = '';
    let article_source = 'Teerth';

    const sourceType = article.source_details?.type;

    if (sourceType === 'YOUTUBE_VIDEO') {
      article_source = 'YouTube';
      youtube_channel = article.source_details?.metadata?.channel_name || '';
      external_id = article.source_details?.external_id || external_id;
    } else if (sourceType) {
      console.error(`Unknown source type: ${sourceType}. Falling back to Teerth.`);
    }

    return { 
      external_id, 
      youtube_channel, 
      article_source 
    };
  }

  /**
   * Standardizes the published_at date from different backend formats.
   */
  static extractPublishedAt(article: any): string {
    if (article.content_generated_at) {
      return new Date(article.content_generated_at * 1000).toISOString();
    }
    if (article.created_at) {
      return new Date(article.created_at * 1000).toISOString();
    }
    return new Date().toISOString();
  }

  /**
   * Formats the reading time string.
   */
  static formatTimeToRead(readingTimeSeconds: number): string {
    const minutes = Math.ceil((readingTimeSeconds || 0) / 60);
    return minutes < 1 ? 'Less than 1 min read' : `${minutes} min read`;
  }

  /**
   * Transforms a raw ArticleResponse from the backend to a standardized Article model.
   * This logic is shared between single article fetching and newspaper aggregation.
   */
  static toArticle(article: any): Article {
    const generated = article.generated || {};

    // Title should ONLY come from VERY_SHORT, never extracted from SHORT
    let title = '';
    if (generated.VERY_SHORT && generated.VERY_SHORT.string) {
      title = generated.VERY_SHORT.string;
    }

    // Get content - prefer LONG, then MEDIUM, then SHORT
    let content = '';
    if (generated.LONG && (generated.LONG.markdown_string || generated.LONG.string)) {
      content = generated.LONG.markdown_string || generated.LONG.string;
    } else if (generated.MEDIUM && (generated.MEDIUM.markdown_string || generated.MEDIUM.string)) {
      content = generated.MEDIUM.markdown_string || generated.MEDIUM.string;
    } else if (generated.SHORT && generated.SHORT.string) {
      content = generated.SHORT.string;
    }

    // Get category
    const category = article.category?.category || 'TECHNOLOGY';

    const { external_id, youtube_channel, article_source } = ArticleAdaptor.extractSourceInfo(article);
    const published_at = ArticleAdaptor.extractPublishedAt(article);
    const time_to_read = ArticleAdaptor.formatTimeToRead(article.reading_time_seconds);

    // Use MongoDB _id as the primary ID (backend endpoints expect this)
    const articleId = article.id || article.external_id;

    // Set article link (canonical production URL)
    const article_link = `https://unhook-production.up.railway.app/article/${articleId}`;

    return {
      id: articleId,
      title: title || 'Untitled Article',
      content: content || '',
      summary: generated.SHORT?.string || '',
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
}
