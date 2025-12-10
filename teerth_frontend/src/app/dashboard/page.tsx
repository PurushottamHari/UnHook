'use client';

import { useState, useMemo, useEffect } from 'react';
import { useInfiniteQuery, useQuery, useQueryClient } from '@tanstack/react-query';
import { useAuthStore } from '@/store/auth-store';
import TeerthLogo from '@/components/TeerthLogo';
import WaitlistSection from '@/components/WaitlistSection';
import ExpandableArticleCard from '@/components/ExpandableArticleCard';
import LoadingSpinner from '@/components/LoadingSpinner';
import CategoryTagsSkeleton from '@/components/CategoryTagsSkeleton';
import DashboardDatePicker from '@/components/dashboard/DashboardDatePicker';
import DashboardTitle from '@/components/dashboard/DashboardTitle';
import CategoriesError from '@/components/dashboard/CategoriesError';
import MobileMetadataDropdown from '@/components/MobileMetadataDropdown';
import CategoryTag from '@/components/CategoryTag';
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

    // Title should ONLY come from VERY_SHORT, never extracted from SHORT
    let title = '';
    if (generated.VERY_SHORT && generated.VERY_SHORT.string) {
      title = generated.VERY_SHORT.string;
    }

    // Summary should be the full SHORT content (for expandable card)
    // SHORT is the summary shown in the dashboard cards
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

    // Use MongoDB _id as the article ID (backend endpoint expects MongoDB _id)
    const articleId = article.id;

    // Extract interactions from API response
    const interactions = item.active_user_interactions || [];

    return {
      id: articleId,
      title: title || 'Untitled Article',
      category: category,
      time_to_read: timeToRead,
      summary: summary || '', // Return empty string if no SHORT content
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

  // Title should ONLY come from VERY_SHORT, never extracted from SHORT
  let title = '';
  if (generated.VERY_SHORT && generated.VERY_SHORT.string) {
    title = generated.VERY_SHORT.string;
  }

  // Get content - prefer LONG, then MEDIUM, then SHORT
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

  // Get category
  const category = article.category?.category || 'TECHNOLOGY';

  // Get reading time
  const readingTimeSeconds = article.reading_time_seconds || 0;
  const minutes = Math.ceil(readingTimeSeconds / 60);
  const time_to_read =
    minutes < 1 ? 'Less than 1 min read' : `${minutes} min read`;

  // Get published date
  let published_at = new Date().toISOString();
  if (article.content_generated_at) {
    published_at = new Date(article.content_generated_at * 1000).toISOString();
  } else if (article.created_at) {
    published_at = new Date(article.created_at * 1000).toISOString();
  }

  // Get external_id (YouTube video ID)
  const external_id = article.external_id || '';

  // Note: youtube_channel may not be included in the GeneratedContent response
  let youtube_channel = '';
  if (article.youtube_channel) {
    youtube_channel = article.youtube_channel;
  }

  // Use MongoDB _id as the Article ID (backend endpoint expects MongoDB _id)
  const articleId = article.id;

  // Set article source and link
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
  pageParam: string | null
): Promise<{ articles: any[], hasNext: boolean, lastExternalId: string | null }> {
  try {
    const url = new URL('/api/newspapers/today/page', window.location.origin);
    url.searchParams.set('userId', userId);
    url.searchParams.set('date', date);
    if (pageParam) {
      url.searchParams.set('startingAfter', pageParam);
    }

    const response = await fetch(url.toString());
    
    if (!response.ok) {
      // Handle 404 errors gracefully - return empty page
      if (response.status === 404) {
        return { articles: [], hasNext: false, lastExternalId: null };
      }
      throw new Error(`Failed to fetch newspaper page: ${response.statusText}`);
    }
    
    const data = await response.json();
    
    if (!data.success) {
      // Handle 404 errors gracefully - return empty page
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
    // Return empty page on error to prevent breaking the query
    return { articles: [], hasNext: false, lastExternalId: null };
  }
}

/**
 * Fetch user categories from API for a specific date
 */
async function fetchUserCategories(userId: string, date: string): Promise<string[]> {
  const response = await fetch(`/api/users/categories/today?userId=${userId}&date=${date}`);
  const data = await response.json();
  
  if (!data.success) {
    throw new Error(data.error || 'Failed to fetch user categories');
  }
  
  return data.categories || [];
}

export default function Dashboard() {
  const { user } = useAuthStore();
  const userId = user?.id || '607d95f0-47ef-444c-89d2-d05f257d1265';
  const queryClient = useQueryClient();

  // State for selected date, default to today
  const [selectedDate, setSelectedDate] = useState<string>(() => {
    return new Date().toISOString().split('T')[0];
  });

  // State to force re-render when interactions change
  const [interactionUpdateKey, setInteractionUpdateKey] = useState(0);

  // Listen for interaction updates and refetch newspaper data
  useEffect(() => {
    if (typeof window === 'undefined') return;

    // Custom event for same-tab updates (since storage event only fires in other tabs)
    const handleCustomStorageChange = () => {
      setInteractionUpdateKey((prev) => prev + 1);
    };

    // Handle API interaction updates - refetch newspaper to get updated interactions
    const handleInteractionUpdate = () => {
      // Invalidate newspaper query to refetch with updated interactions
      queryClient.invalidateQueries({ queryKey: ['newspaper-paginated', selectedDate, userId] });
      setInteractionUpdateKey((prev) => prev + 1);
    };

    // Listen for storage events (from other tabs) - for read state
    const handleStorageChange = (e: StorageEvent) => {
      // Check if it's an article interaction change (all user interactions use 'user_' prefix)
      if (e.key?.startsWith('user_')) {
        setInteractionUpdateKey((prev) => prev + 1);
      }
    };

    window.addEventListener('storage', handleStorageChange);
    // Listen for custom events (same tab) - for read state
    window.addEventListener('articleInteractionChange', handleCustomStorageChange);
    // Listen for API interaction updates
    window.addEventListener('articleInteractionUpdated', handleInteractionUpdate);

    return () => {
      window.removeEventListener('storage', handleStorageChange);
      window.removeEventListener('articleInteractionChange', handleCustomStorageChange);
      window.removeEventListener('articleInteractionUpdated', handleInteractionUpdate);
    };
  }, [selectedDate, userId, queryClient]);

  // Independent infinite query for newspaper articles with pagination
  // This will show cached data immediately and fetch pages progressively
  // Using 'newspaper-paginated' key to avoid conflicts with old cached data
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
    queryFn: ({ pageParam }) => fetchNewspaperPage(userId, selectedDate, pageParam as string | null),
    getNextPageParam: (lastPage) => {
      if (!lastPage || typeof lastPage !== 'object' || !('hasNext' in lastPage)) {
        return undefined;
      }
      return lastPage.hasNext ? lastPage.lastExternalId : undefined;
    },
    initialPageParam: null as string | null,
    enabled: !!userId && !!selectedDate,
    // Temporarily disable persist to avoid conflicts with old cache structure
    // Can re-enable after confirming the new structure works
    // meta: {
    //   persist: true,
    // },
    // Data is fresh for 5 minutes, then will refetch in background
    staleTime: 5 * 60 * 1000, // 5 minutes
    // Provide safe default structure
    placeholderData: (previousData) => {
      // If previous data exists and is valid, use it
      if (previousData && previousData.pages && Array.isArray(previousData.pages)) {
        return previousData;
      }
      // Otherwise return empty structure
      return { pages: [], pageParams: [] };
    },
  });

  // Transform paginated data into CachedNewspaper format
  const newspaper = useMemo<CachedNewspaper | null>(() => {
    if (!newspaperPages || !newspaperPages.pages || !Array.isArray(newspaperPages.pages) || newspaperPages.pages.length === 0) {
      return null;
    }

    // Flatten all pages into single articles array
    const allContentWithInteractions = newspaperPages.pages
      .filter(page => page && Array.isArray(page.articles))
      .flatMap(page => page.articles);

    if (allContentWithInteractions.length === 0) {
      return null;
    }

    // Transform articles to CachedNewspaperArticle format
    const cachedArticles = transformArticles(allContentWithInteractions);

    // Cache full article objects for article detail pages
    allContentWithInteractions.forEach((item: { generated_content: any }) => {
      const article = item.generated_content;
      if (!article.id) {
        return; // Skip articles without MongoDB _id
      }
      try {
        const fullArticle = transformToArticle(article);
        articleCache.set(fullArticle);
      } catch (error) {
        console.warn('Failed to cache article:', error);
      }
    });

    // Calculate total time to read
    const totalMinutes = cachedArticles.reduce((total, article) => {
      const timeMatch = article.time_to_read.match(/(\d+)/);
      return total + (timeMatch ? parseInt(timeMatch[1]) : 5);
    }, 0);

    const totalTimeToRead =
      totalMinutes > 60
        ? `${Math.floor(totalMinutes / 60)}h ${totalMinutes % 60}m read`
        : `${totalMinutes}m read`;

    // Extract unique topics from article categories
    const topics = [...new Set(cachedArticles.map((article) => article.category))];

    return {
      date: selectedDate,
      articles: cachedArticles,
      total_time_to_read: totalTimeToRead,
      topics: topics,
      cached_at: new Date().toISOString(),
    };
  }, [newspaperPages, selectedDate]);

  // Auto-fetch next page when hasNextPage is true
  useEffect(() => {
    if (hasNextPage && !isFetchingNextPage && newspaper) {
      fetchNextPage();
    }
  }, [hasNextPage, isFetchingNextPage, newspaper, fetchNextPage]);

  // Independent query for user categories
  // This will show cached data immediately and refetch in background if stale
  const {
    data: userCategories,
    isLoading: isLoadingCategories,
    isFetching: isFetchingCategories,
    error: categoriesError,
  } = useQuery<string[]>({
    queryKey: ['userCategories', selectedDate, userId],
    queryFn: () => fetchUserCategories(userId, selectedDate),
    enabled: !!userId && !!selectedDate,
    // Persist to localStorage for instant load on page refresh
    meta: {
      persist: true,
    },
    // Data is fresh for 5 minutes, then will refetch in background
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  // Filter articles by interaction state
  const { mainArticles, readArticles, dislikedArticles, reportedArticles } = useMemo(() => {
    if (!newspaper || !newspaper.articles) {
      return {
        mainArticles: [],
        readArticles: [],
        dislikedArticles: [],
        reportedArticles: [],
      };
    }

    // Get read article IDs (frontend-only, uses localStorage)
    const readArticleIds = new Set(
      articleInteractionService.getArticlesByState(userId, 'read')
    );
    
    // Get disliked and reported article IDs from API interactions
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
    <div className='min-h-screen bg-yellow-50 dark:bg-amber-50'>
      <div className='w-full px-4 sm:px-6 lg:px-8 py-8'>
        {/* Main Content Container */}
        <div className='max-w-6xl mx-auto'>
          {/* Header Section */}
          <div className='relative mb-12'>
            {/* Desktop: Date picker in top right corner */}
            <DashboardDatePicker
              selectedDate={selectedDate}
              onDateChange={setSelectedDate}
              variant='desktop'
            />

            <div className='text-center'>
              {/* Teerth Logo */}
              <div className='flex justify-center mb-6'>
                <TeerthLogo alt='Teerth Logo' size={200} />
              </div>

              <DashboardTitle title="Puru's Digest" />

              {/* Mobile: Date picker below title */}
              <DashboardDatePicker
                selectedDate={selectedDate}
                onDateChange={setSelectedDate}
                variant='mobile'
              />

              {/* User Categories Section */}
              {/* Show cached categories immediately, skeleton only if no cache */}
              {isLoadingCategories && !userCategories ? (
                <CategoryTagsSkeleton />
              ) : categoriesError ? (
                <CategoriesError />
              ) : userCategories && userCategories.length > 0 ? (
                <div className='text-center text-amber-700 dark:text-amber-800 mb-8'>
                  {/* Show loading indicator when refetching in background */}
                  {isFetchingCategories && userCategories && (
                    <div className='flex justify-center mb-2'>
                      <LoadingSpinner size='sm' />
                    </div>
                  )}
                  
                  {/* Mobile: Dropdown for categories */}
                  <MobileMetadataDropdown
                    label="In Focus Today:"
                    items={userCategories.map((category: string, index: number) => (
                      <CategoryTag key={index} category={category} variant="default" />
                    ))}
                  />
                  
                  {/* Desktop: Inline display */}
                  <div className="hidden md:flex flex-col items-center mb-3">
                    <p className="text-lg font-medium leading-relaxed mb-3">
                      In Focus Today:
                    </p>
                    <div className="flex flex-wrap gap-2 justify-center">
                      {userCategories.map((category: string, index: number) => (
                        <CategoryTag key={index} category={category} variant="default" />
                      ))}
                    </div>
                  </div>

                  {/* Time to read - kept separate */}
                  {newspaper && (
                    <div className='flex items-center justify-center gap-1.5 text-sm font-light text-amber-600 dark:text-amber-700'>
                      <svg
                        className='w-4 h-4'
                        fill='none'
                        stroke='currentColor'
                        viewBox='0 0 24 24'
                      >
                        <path
                          strokeLinecap='round'
                          strokeLinejoin='round'
                          strokeWidth={2}
                          d='M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253'
                        />
                      </svg>
                      <span>{newspaper.total_time_to_read}</span>
                    </div>
                  )}
                </div>
              ) : null}
            </div>
          </div>

          {/* Articles Section */}
          {/* Once newspaper metadata is loaded, render all article cards */}
          {/* Each card manages its own loading/fetched state */}
          {isLoadingNewspaper && !newspaper ? (
            // Show skeleton grid while loading newspaper metadata (no cache)
            <ArticleSkeleton />
          ) : newspaperError ? (
            // Error state for articles (non-404 errors)
            <ArticlesError />
          ) : !newspaper ? (
            // No newspaper found state (404 handled gracefully)
            <NoDigestMessage />
          ) : newspaper && newspaper.articles.length > 0 ? (
            <>
              {/* Main Articles Section */}
              {mainArticles.length > 0 && (
                <div className='bg-white/50 dark:bg-amber-100/50 backdrop-blur-sm rounded-3xl p-8 md:p-12 border border-amber-200/50 dark:border-amber-300/50 shadow-lg mb-6'>
                  {/* Show loading indicator when refetching newspaper metadata in background */}
                  {isFetchingNewspaper && newspaper && !isFetchingNextPage && (
                    <div className='flex justify-center mb-4'>
                      <LoadingSpinner size='sm' text='Refreshing articles...' />
                    </div>
                  )}
                  
                  {/* Show loading indicator when fetching next page */}
                  {isFetchingNextPage && (
                    <div className='flex justify-center mb-4'>
                      <LoadingSpinner size='sm' text='Loading more articles...' />
                    </div>
                  )}
                  
                  <div className='grid grid-cols-1 lg:grid-cols-2 gap-6 items-start'>
                    {mainArticles.map(article => (
                      <ExpandableArticleCard key={article.id} article={article} />
                    ))}
                  </div>
                </div>
              )}

              {/* Read Articles Section */}
              <ArticleSection
                title='Read Articles'
                articles={readArticles}
                defaultCollapsed={true}
                icon={
                  <svg
                    className='w-6 h-6'
                    fill='currentColor'
                    viewBox='0 0 24 24'
                  >
                    <path d='M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z' />
                  </svg>
                }
              />

              {/* Disliked Articles Section */}
              <ArticleSection
                title='Disliked Articles'
                articles={dislikedArticles}
                defaultCollapsed={true}
                icon={
                  <svg
                    className='w-6 h-6'
                    fill='currentColor'
                    viewBox='0 0 24 24'
                  >
                    <path d='M15 3H6c-.83 0-1.54.5-1.85 1.22l-3.02 7.05c-.09.23-.13.47-.13.73v2c0 1.1.9 2 2 2h6.31l-.95 4.57-.03.32c0 .41.17.79.44 1.06L9.83 23l6.59-6.59c.36-.36.58-.86.58-1.41V5c0-1.1-.9-2-2-2zm4 0v12h4V3h-4z' />
                  </svg>
                }
              />
            </>
          ) : (
            // No articles in newspaper state (newspaper exists but has no articles)
            <NoArticlesMessage />
          )}

          {/* Waitlist Section */}
          <WaitlistSection variant='detailed' />
        </div>
      </div>
    </div>
  );
}
