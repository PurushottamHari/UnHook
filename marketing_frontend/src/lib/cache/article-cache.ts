import fs from 'fs';
import path from 'path';

export interface CachedArticle {
  id: string;
  title: string;
  content: string;
  category: string;
  time_to_read: string;
  article_link: string;
  article_source: string;
  external_id: string; // YouTube video ID
  youtube_channel: string;
  published_at: string;
  cached_at: string;
}

const CACHE_DIR = path.join(process.cwd(), 'src/lib/cache/articles');

// Ensure cache directory exists
function ensureCacheDir() {
  if (!fs.existsSync(CACHE_DIR)) {
    fs.mkdirSync(CACHE_DIR, { recursive: true });
  }
}

export function getCachedArticle(articleId: string): CachedArticle | null {
  try {
    ensureCacheDir();
    const filePath = path.join(CACHE_DIR, `${articleId}.json`);

    if (!fs.existsSync(filePath)) {
      return null;
    }

    const fileContent = fs.readFileSync(filePath, 'utf-8');
    return JSON.parse(fileContent);
  } catch (error) {
    console.error('Error reading cached article:', error);
    return null;
  }
}

export function cacheArticle(article: CachedArticle): void {
  try {
    ensureCacheDir();
    const filePath = path.join(CACHE_DIR, `${article.id}.json`);

    fs.writeFileSync(filePath, JSON.stringify(article, null, 2));
    console.log(`Article ${article.id} cached successfully`);
  } catch (error) {
    console.error('Error caching article:', error);
    throw error;
  }
}

export function isArticleCached(articleId: string): boolean {
  try {
    ensureCacheDir();
    const filePath = path.join(CACHE_DIR, `${articleId}.json`);
    return fs.existsSync(filePath);
  } catch (error) {
    console.error('Error checking if article is cached:', error);
    return false;
  }
}
