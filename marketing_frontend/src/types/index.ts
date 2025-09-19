export interface Article {
  id: string;
  title: string;
  body: string;
  imageUrl?: string;
  publishedAt: string;
  newspaperId: string;
}

export interface UnHookArticle {
  id: string;
  title: string;
  content: string;
  imageUrl?: string;
  publishedAt: string;
  category?: string;
  readTime?: string;
  videoId?: string;
  creator?: string;
  articleId?: string;
}

export interface Newspaper {
  id: string;
  name: string;
  articles: Article[];
}

export type Theme = 'default' | 'vipassana';
