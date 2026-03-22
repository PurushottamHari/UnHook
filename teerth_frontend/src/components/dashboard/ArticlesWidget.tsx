'use client';

import { useState, useMemo, useEffect } from 'react';
import { useInfiniteQuery, useQueryClient } from '@tanstack/react-query';
import ExpandableArticleCard from '@/components/ExpandableArticleCard';
import LoadingSpinner from '@/components/LoadingSpinner';
import NoArticlesMessage from '@/components/dashboard/NoArticlesMessage';
import ArticleSkeleton from '@/components/dashboard/ArticleSkeleton';
import ArticlesError from '@/components/dashboard/ArticlesError';
import NoDigestMessage from '@/components/dashboard/NoDigestMessage';
import ArticleSection from '@/components/ArticleSection';
import { CachedNewspaper, CachedNewspaperArticle } from '@/models/newspaper.model';
import { articleInteractionService } from '@/lib/services/article-interaction-service';
import { articleCache } from '@/lib/services/cache/article/article-cache';
import { Article } from '@/models/article.model';
import { GeneratedContentInteraction } from '@/types';

/**
 * Transform paginated articles to CachedNewspaperArticle format
 */
function transformArticles(contentWithInteractions: any[]): CachedNewspaperArticle[] {
  return contentWithInteractions.map((item: { generated_content: any; active_user_interactions?: GeneratedContentInteraction[] }) => {
    const article = item.generated_content;
    const generated = article.generated || {};

    let title = '';
    if (generated.VERY_SHORT && generated.VERY_SHORT.string) {
      title = generated.VERY_SHORT.string;
    }

    let summary = '';
    if (generated.SHORT && generated.SHORT.string) {
      summary = generated.SHORT.string;
    }

    const category = article.category?.category || 'Uncategorized';
    const readingTimeSeconds = article.reading_time_seconds || 0;
    const timeToRead =
      readingTimeSeconds > 0
        ? `${Math.ceil(readingTimeSeconds / 60)}m read`
        : '5 min read';

    const articleId = article.id;
    const interactions = item.active_user_interactions || [];

    return {
      id: articleId,
      title: title || 'Untitled Article',
      category: category,
      time_to_read: timeToRead,
      summary: summary || '',
      cached_at: new Date().toISOString(),
      interactions: interactions,
    };
  });
}

/**
 * Transform article to full Article object for caching
 */
function transformToArticle(article: any): Article {
  const generated = article.generated || {};

  let title = '';
  if (generated.VERY_SHORT && generated.VERY_SHORT.string) {
    title = generated.VERY_SHORT.string;
  }

  let content = '';
  if (generated.LONG && generated.LONG.markdown_string) {
    content = generated.LONG.markdown_string;
  } else if (generated.LONG && generated.LONG.string) {
    content = generated.LONG.string;
  } else if (generated.MEDIUM && generated.MEDIUM.markdown_string) {
    content = generated.MEDIUM.markdown_string;
  } else if (generated.MEDIUM && generated.MEDIUM.string) {
    content = generated.MEDIUM.string;
  } else if (generated.SHORT && generated.SHORT.string) {
    content = generated.SHORT.string;
  }

  const category = article.category?.category || 'TECHNOLOGY';
  const readingTimeSeconds = article.reading_time_seconds || 0;
  const minutes = Math.ceil(readingTimeSeconds / 60);
  const time_to_read =
    minutes < 1 ? 'Less than 1 min read' : `${minutes} min read`;

  let published_at = new Date().toISOString();
  if (article.content_generated_at) {
    published_at = new Date(article.content_generated_at * 1000).toISOString();
  } else if (article.created_at) {
    published_at = new Date(article.created_at * 1000).toISOString();
  }

  const external_id = article.external_id || '';
  let youtube_channel = '';
  if (article.youtube_channel) {
    youtube_channel = article.youtube_channel;
  }

  const articleId = article.id;
  const article_source = 'Teerth';
  const article_link = `https://unhook-production.up.railway.app/article/${articleId}`;

  return {
    id: articleId,
    title: title || 'Untitled Article',
    content: content || '',
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

/**
 * Fetch a page of articles from API
 */
async function fetchNewspaperPage(
  userId: string,
  date: string,
  pageParam: string | null,
  pageLimit?: number
): Promise<{ articles: any[], hasNext: boolean, lastExternalId: string | null }> {
  try {
    const url = new URL('/api/newspapers/today/page', window.location.origin);
    url.searchParams.set('userId', userId);
    url.searchParams.set('date', date);
    if (pageParam) {
      url.searchParams.set('startingAfter', pageParam);
    }
    if (pageLimit) {
      url.searchParams.set('pageLimit', pageLimit.toString());
    }

    const response = await fetch(url.toString());

    if (!response.ok) {
      if (response.status === 404) {
        return { articles: [], hasNext: false, lastExternalId: null };
      }
      throw new Error(`Failed to fetch newspaper page: ${response.statusText}`);
    }

    const data = await response.json();

    if (!data.success) {
      if (response.status === 404) {
        return { articles: [], hasNext: false, lastExternalId: null };
      }
      throw new Error(data.error || 'Failed to fetch newspaper page');
    }

    return {
      articles: Array.isArray(data.articles) ? data.articles : [],
      hasNext: Boolean(data.hasNext),
      lastExternalId: data.lastExternalId || null,
    };
  } catch (error) {
    console.error('Error fetching newspaper page:', error);
    return { articles: [], hasNext: false, lastExternalId: null };
  }
}

interface ArticlesWidgetProps {
  userId: string;
  selectedDate: string;
  isGuestMode?: boolean;
}

export default function ArticlesWidget({ userId, selectedDate, isGuestMode }: ArticlesWidgetProps) {
  const queryClient = useQueryClient();
  const [interactionUpdateKey, setInteractionUpdateKey] = useState(0);

  useEffect(() => {
    if (typeof window === 'undefined') return;

    const handleCustomStorageChange = () => {
      setInteractionUpdateKey((prev) => prev + 1);
    };

    const handleInteractionUpdate = () => {
      queryClient.invalidateQueries({ queryKey: ['newspaper-paginated', selectedDate, userId] });
      setInteractionUpdateKey((prev) => prev + 1);
    };

    const handleStorageChange = (e: StorageEvent) => {
      if (e.key?.startsWith('user_')) {
        setInteractionUpdateKey((prev) => prev + 1);
      }
    };

    window.addEventListener('storage', handleStorageChange);
    window.addEventListener('articleInteractionChange', handleCustomStorageChange);
    window.addEventListener('articleInteractionUpdated', handleInteractionUpdate);

    return () => {
      window.removeEventListener('storage', handleStorageChange);
      window.removeEventListener('articleInteractionChange', handleCustomStorageChange);
      window.removeEventListener('articleInteractionUpdated', handleInteractionUpdate);
    };
  }, [selectedDate, userId, queryClient]);

  const {
    data: newspaperPages,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
    isLoading: isLoadingNewspaper,
    isFetching: isFetchingNewspaper,
    error: newspaperError,
  } = useInfiniteQuery({
    queryKey: ['newspaper-paginated', selectedDate, userId],
    queryFn: ({ pageParam }) => fetchNewspaperPage(userId, selectedDate, pageParam as string | null, pageParam ? undefined : 5),
    getNextPageParam: (lastPage) => {
      if (!lastPage || typeof lastPage !== 'object' || !('hasNext' in lastPage)) {
        return undefined;
      }
      return lastPage.hasNext ? lastPage.lastExternalId : undefined;
    },
    initialPageParam: null as string | null,
    enabled: !!userId && !!selectedDate,
    staleTime: 5 * 60 * 1000, 
  });

  const newspaper = useMemo<CachedNewspaper | null>(() => {
    if (!newspaperPages || !newspaperPages.pages || !Array.isArray(newspaperPages.pages) || newspaperPages.pages.length === 0) {
      return null;
    }

    const allContentWithInteractions = newspaperPages.pages
      .filter(page => page && Array.isArray(page.articles))
      .flatMap(page => page.articles);

    if (allContentWithInteractions.length === 0) {
      return null;
    }

    const cachedArticles = transformArticles(allContentWithInteractions);

    allContentWithInteractions.forEach((item: { generated_content: any }) => {
      const article = item.generated_content;
      if (!article.id) {
        return; 
      }
      try {
        const fullArticle = transformToArticle(article);
        articleCache.set(fullArticle);
      } catch (error) {
        console.warn('Failed to cache article:', error);
      }
    });

    const totalMinutes = cachedArticles.reduce((total, article) => {
      const timeMatch = article.time_to_read.match(/(\d+)/);
      return total + (timeMatch ? parseInt(timeMatch[1]) : 5);
    }, 0);

    const totalTimeToRead =
      totalMinutes > 60
        ? `${Math.floor(totalMinutes / 60)}h ${totalMinutes % 60}m read`
        : `${totalMinutes}m read`;

    const topics = [...new Set(cachedArticles.map((article) => article.category))];

    return {
      date: selectedDate,
      articles: cachedArticles,
      total_time_to_read: totalTimeToRead,
      topics: topics,
      cached_at: new Date().toISOString(),
    };
  }, [newspaperPages, selectedDate]);

  useEffect(() => {
    if (hasNextPage && !isFetchingNextPage && newspaper) {
      fetchNextPage();
    }
  }, [hasNextPage, isFetchingNextPage, newspaper, fetchNextPage]);

  const { mainArticles, readArticles, dislikedArticles, reportedArticles } = useMemo(() => {
    if (!newspaper || !newspaper.articles) {
      return {
        mainArticles: [],
        readArticles: [],
        dislikedArticles: [],
        reportedArticles: [],
      };
    }

    const readArticleIds = new Set(
      articleInteractionService.getArticlesByState(userId, 'read')
    );

    const articlesWithInteractions = newspaper.articles.map(article => ({
      id: article.id,
      interactions: article.interactions || [],
    }));

    const dislikedArticleIds = new Set(
      articleInteractionService.getArticlesByState(userId, 'disliked', articlesWithInteractions)
    );
    const reportedArticleIds = new Set(
      articleInteractionService.getArticlesByState(userId, 'reported', articlesWithInteractions)
    );

    const main: typeof newspaper.articles = [];
    const read: typeof newspaper.articles = [];
    const disliked: typeof newspaper.articles = [];
    const reported: typeof newspaper.articles = [];

    newspaper.articles.forEach((article) => {
      const isRead = readArticleIds.has(article.id);
      const isDisliked = dislikedArticleIds.has(article.id);
      const isReported = reportedArticleIds.has(article.id);

      if (isDisliked) {
        disliked.push(article);
      } else if (isReported) {
        reported.push(article);
      } else if (isRead) {
        read.push(article);
      } else {
        main.push(article);
      }
    });

    return {
      mainArticles: main,
      readArticles: read,
      dislikedArticles: disliked,
      reportedArticles: reported,
    };
  }, [newspaper, userId, interactionUpdateKey]);

  return (
    <div className="w-full">
      {/* Time to Read - Pulled from earlier in page.tsx */}
      {newspaper && (
        <div className='flex items-center justify-center gap-1.5 text-sm font-light text-amber-600 dark:text-amber-700 mb-8'>
          <svg className='w-4 h-4' fill='none' stroke='currentColor' viewBox='0 0 24 24'>
            <path strokeLinecap='round' strokeLinejoin='round' strokeWidth={2} d='M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253' />
          </svg>
          <div className='flex items-center gap-1.5'>
            <span>{newspaper.articles.length} {newspaper.articles.length === 1 ? 'article' : 'articles'}</span>
            <span className='opacity-40 font-thin'>|</span>
            <span>{newspaper.total_time_to_read}</span>
          </div>
        </div>
      )}

      {(isLoadingNewspaper || isFetchingNewspaper) && !newspaper ? (
        <ArticleSkeleton />
      ) : newspaperError ? (
        <ArticlesError />
      ) : !newspaper ? (
        <NoDigestMessage />
      ) : newspaper && newspaper.articles.length > 0 ? (
        <>
          {mainArticles.length > 0 && (
            <div className='bg-white/50 dark:bg-amber-100/50 backdrop-blur-sm rounded-3xl p-8 md:p-12 border border-amber-200/50 dark:border-amber-300/50 shadow-lg mb-6'>
              {isFetchingNewspaper && newspaper && !isFetchingNextPage && (
                <div className='flex justify-center mb-4'>
                  <LoadingSpinner size='sm' text='Refreshing articles...' />
                </div>
              )}

              {isFetchingNextPage && (
                <div className='flex justify-center mb-4'>
                  <LoadingSpinner size='sm' text='Loading more articles...' />
                </div>
              )}

              <div className='grid grid-cols-1 lg:grid-cols-2 gap-6 items-start'>
                {mainArticles.map(article => (
                  <ExpandableArticleCard key={article.id} article={article} isGuestMode={isGuestMode} />
                ))}
              </div>
            </div>
          )}

          <ArticleSection
            title='Read Articles'
            articles={readArticles}
            defaultCollapsed={true}
            isGuestMode={isGuestMode}
            icon={
              <svg className='w-6 h-6' fill='currentColor' viewBox='0 0 24 24'>
                <path d='M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z' />
              </svg>
            }
          />

          <ArticleSection
            title='Disliked Articles'
            articles={dislikedArticles}
            defaultCollapsed={true}
            isGuestMode={isGuestMode}
            icon={
              <svg className='w-6 h-6' fill='currentColor' viewBox='0 0 24 24'>
                <path d='M15 3H6c-.83 0-1.54.5-1.85 1.22l-3.02 7.05c-.09.23-.13.47-.13.73v2c0 1.1.9 2 2 2h6.31l-.95 4.57-.03.32c0 .41.17.79.44 1.06L9.83 23l6.59-6.59c.36-.36.58-.86.58-1.41V5c0-1.1-.9-2-2-2zm4 0v12h4V3h-4z' />
              </svg>
            }
          />
        </>
      ) : (
        <NoArticlesMessage />
      )}
    </div>
  );
}
