/**
 * Article cache configuration
 * Controls client-side caching behavior for articles
 */
export interface ArticleCacheConfig {
  /**
   * Maximum number of articles to cache
   * When limit is reached, oldest articles are removed (FIFO)
   */
  maxCacheSize: number;

  /**
   * Cache storage key in localStorage
   */
  storageKey: string;

  /**
   * Enable or disable caching
   */
  enabled: boolean;
}

export const articleCacheConfig: ArticleCacheConfig = {
  maxCacheSize: 69,
  storageKey: 'teerth_article_cache',
  enabled: true,
};

