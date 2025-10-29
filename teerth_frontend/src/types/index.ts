export interface User {
  id: string;
  username: string;
  role: 'admin' | 'customer';
  createdAt: string;
}

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

export interface UserInteraction {
  articleId: string;
  userId: string;
  type: 'like' | 'dislike' | 'read_later';
  reason?: string;
  createdAt: string;
}
