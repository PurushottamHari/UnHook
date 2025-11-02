/**
 * Newspaper domain models
 * Represents a curated collection of articles for a specific date
 */

export interface CachedNewspaperArticle {
  id: string;
  title: string;
  category: string;
  time_to_read: string;
  cached_at: string;
}

export interface CachedNewspaper {
  date: string;
  articles: CachedNewspaperArticle[];
  total_time_to_read: string;
  topics: string[];
  cached_at: string;
}
