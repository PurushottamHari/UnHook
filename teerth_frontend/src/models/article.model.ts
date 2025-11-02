/**
 * Article domain model
 * Represents a published article with all its metadata
 */
export interface Article {
  id: string;
  title: string;
  content: string;
  category: string;
  time_to_read: string;
  article_link: string;
  article_source: string;
  external_id: string;
  youtube_channel: string;
  published_at: string;
  cached_at: string;
}
