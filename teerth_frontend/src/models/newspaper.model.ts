/**
 * Newspaper domain models
 * Represents a curated collection of articles for a specific date
 */

import { GeneratedContentInteraction } from '@/types';

export interface CachedNewspaperArticle {
  id: string;
  title: string;
  category: string;
  time_to_read: string;
  summary?: string;
  cached_at: string;
  interactions?: GeneratedContentInteraction[];
}

export interface CachedNewspaper {
  date: string;
  articles: CachedNewspaperArticle[];
  total_time_to_read: string;
  topics: string[];
  cached_at: string;
}
