import fs from 'fs';
import path from 'path';

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

const CACHE_DIR = path.join(process.cwd(), 'src', 'lib', 'cache', 'newspapers');

// Ensure cache directory exists
if (!fs.existsSync(CACHE_DIR)) {
  fs.mkdirSync(CACHE_DIR, { recursive: true });
}

export function getCachedNewspaper(date: string): CachedNewspaper | null {
  try {
    const filePath = path.join(CACHE_DIR, `${date}.json`);

    if (!fs.existsSync(filePath)) {
      return null;
    }

    const fileContent = fs.readFileSync(filePath, 'utf-8');
    return JSON.parse(fileContent);
  } catch (error) {
    console.error('Error reading cached newspaper:', error);
    return null;
  }
}

export function cacheNewspaper(newspaper: CachedNewspaper): void {
  try {
    const filePath = path.join(CACHE_DIR, `${newspaper.date}.json`);
    fs.writeFileSync(filePath, JSON.stringify(newspaper, null, 2));
  } catch (error) {
    console.error('Error caching newspaper:', error);
  }
}

export function isNewspaperCached(date: string): boolean {
  const filePath = path.join(CACHE_DIR, `${date}.json`);
  return fs.existsSync(filePath);
}

export function getMostRecentCachedNewspaper(): CachedNewspaper | null {
  try {
    if (!fs.existsSync(CACHE_DIR)) {
      return null;
    }

    const files = fs.readdirSync(CACHE_DIR);
    const jsonFiles = files.filter(file => file.endsWith('.json'));

    if (jsonFiles.length === 0) {
      return null;
    }

    // Sort files by date (newest first)
    const sortedFiles = jsonFiles.sort((a, b) => {
      const dateA = a.replace('.json', '');
      const dateB = b.replace('.json', '');
      return dateB.localeCompare(dateA);
    });

    // Try to get the most recent newspaper
    for (const file of sortedFiles) {
      const filePath = path.join(CACHE_DIR, file);
      try {
        const fileContent = fs.readFileSync(filePath, 'utf-8');
        const newspaper = JSON.parse(fileContent);
        return newspaper;
      } catch (error) {
        console.error(`Error reading cached newspaper file ${file}:`, error);
        continue;
      }
    }

    return null;
  } catch (error) {
    console.error('Error getting most recent cached newspaper:', error);
    return null;
  }
}
