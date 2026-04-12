import { NextRequest, NextResponse } from 'next/server';
import { ArticleService } from '@/lib/services/article-service';

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const url = searchParams.get('url');

  if (!url) {
    return NextResponse.json({ error: 'Missing url parameter' }, { status: 400 });
  }

  // Extract article ID from URL (e.g., .../articles/123)
  const articleIdMatch = url.match(/\/articles\/([^\/\?]+)/);
  if (!articleIdMatch) {
    return NextResponse.json({ error: 'Invalid article URL' }, { status: 400 });
  }

  const articleId = articleIdMatch[1];
  const articleService = new ArticleService();
  const article = await articleService.getArticleById(articleId);

  if (!article) {
    return NextResponse.json({ error: 'Article not found' }, { status: 404 });
  }

  // Use the production domain for consistency with metadataBase
  const baseUrl = 'https://www.teerth.xyz';
  const thumbnail_url = `${baseUrl}/articles/${articleId}/opengraph-image`;

  return NextResponse.json({
    type: 'link',
    version: '1.0',
    title: article.title,
    author_name: article.youtube_channel || 'Teerth',
    author_url: baseUrl,
    provider_name: 'Teerth',
    provider_url: baseUrl,
    cache_age: 86400, // 24 hours
    thumbnail_url,
    thumbnail_width: 1200,
    thumbnail_height: 630,
    description: article.summary,
  });
}
