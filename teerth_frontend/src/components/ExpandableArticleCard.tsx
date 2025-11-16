'use client';

import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import Link from 'next/link';
import { CachedNewspaperArticle } from '@/models/newspaper.model';
import { Article } from '@/models/article.model';
import ArticleCardSkeleton from '@/components/article/ArticleCardSkeleton';
import { useAuthStore } from '@/store/auth-store';
import {
  articleInteractionService,
  ArticleInteractionState,
} from '@/lib/services/article-interaction-service';
import DislikeModal from './DislikeModal';
import ReportModal from './ReportModal';
import CategoryTag from './CategoryTag';

interface ExpandableArticleCardProps {
  /**
   * Article metadata from newspaper (used as placeholder for instant display)
   * This contains basic info: id, title, category, time_to_read, summary
   */
  article: CachedNewspaperArticle;
}

/**
 * Fetch full article data from API
 * Converts Article to CachedNewspaperArticle format for display
 * Preserves the SHORT summary from placeholder data (newspaper metadata)
 */
async function fetchFullArticle(
  articleId: string,
  existingSummary?: string
): Promise<CachedNewspaperArticle> {
  const response = await fetch(`/api/articles/${articleId}`);
  const data = await response.json();
  
  if (!data.success) {
    // Handle 404 errors gracefully - preserve error message
    throw new Error(data.error || 'Failed to fetch article');
  }
  
  const article: Article = data.article;
  
  // Use existing summary from newspaper metadata (SHORT version) if available
  // This is the correct summary, not extracted from content
  // Only extract from content as fallback if no summary provided
  let summary = existingSummary || '';
  
  if (!summary && article.content) {
    // Fallback: Extract summary from content if no SHORT version available
    const cleanContent = article.content
      .replace(/#{1,6}\s+/g, '') // Remove headers
      .replace(/\*\*([^*]+)\*\*/g, '$1') // Remove bold
      .replace(/\*([^*]+)\*/g, '$1') // Remove italic
      .replace(/\[([^\]]+)\]\([^\)]+\)/g, '$1') // Remove links
      .trim();
    
    const firstParagraph = cleanContent.split('\n\n')[0] || cleanContent.split('\n')[0] || cleanContent;
    summary = firstParagraph.length > 300 
      ? firstParagraph.substring(0, 300) + '...'
      : firstParagraph;
  }
  
  return {
    id: article.id,
    title: article.title,
    category: article.category,
    time_to_read: article.time_to_read,
    summary: summary || 'No summary available',
    cached_at: article.cached_at || new Date().toISOString(),
  };
}

/**
 * ExpandableArticleCard component with independent loading state
 * Each card manages its own data fetching and displays loading state internally
 */
export default function ExpandableArticleCard({ article }: ExpandableArticleCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isDislikeModalOpen, setIsDislikeModalOpen] = useState(false);
  const [isReportModalOpen, setIsReportModalOpen] = useState(false);
  const [interactionState, setInteractionState] = useState<ArticleInteractionState>({
    isRead: false,
    isSaved: false,
    isLiked: false,
    isDisliked: false,
    isReported: false,
  });

  const { user } = useAuthStore();
  const userId = user?.id || '607d95f0-47ef-444c-89d2-d05f257d1265';

  // Load interaction state
  useEffect(() => {
    if (article.id) {
      const state = articleInteractionService.getArticleState(userId, article.id);
      setInteractionState(state);
    }
  }, [article.id, userId]);

  // Each card fetches its own full article data independently
  // Uses article metadata as placeholderData for instant display
  const {
    data: fullArticle,
    isLoading,
    isFetching,
  } = useQuery<CachedNewspaperArticle>({
    queryKey: ['article', 'dashboard', article.id],
    // Pass existing summary from newspaper metadata to preserve SHORT version
    queryFn: () => fetchFullArticle(article.id, article.summary),
    enabled: !!article.id,
    // Use metadata from newspaper as placeholder for instant display
    placeholderData: article,
    // Persist to cache for future visits
    meta: {
      persist: true,
    },
    // Data is fresh for 5 minutes
    staleTime: 5 * 60 * 1000,
    // Retry once on failure
    retry: 1,
  });

  // Use full article data if available, otherwise use metadata placeholder
  const displayArticle = fullArticle || article;

  /**
   * Store article metadata in sessionStorage before navigation
   * This allows the article page to show initial data immediately
   */
  const handleArticleClick = (e: React.MouseEvent<HTMLAnchorElement>) => {
    // Prevent navigation when clicking action buttons or "Read more"
    if (
      (e.target as HTMLElement).closest('.read-more-button') ||
      (e.target as HTMLElement).closest('.article-action-button') ||
      (e.target as HTMLElement).closest('.article-action-menu')
    ) {
      e.preventDefault();
      return;
    }

    // Store article data for progressive loading on article page
    if (typeof window !== 'undefined') {
      try {
        sessionStorage.setItem(
          `article_placeholder_${article.id}`,
          JSON.stringify({
            id: displayArticle.id,
            title: displayArticle.title,
            category: displayArticle.category,
            time_to_read: displayArticle.time_to_read,
            summary: displayArticle.summary,
            cached_at: displayArticle.cached_at,
          })
        );
      } catch (error) {
        // Silently fail if sessionStorage is not available
        console.warn('Failed to store article placeholder data:', error);
      }
    }
  };

  // Action handlers
  const handleToggleRead = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    const newState = articleInteractionService.toggleRead(userId, article.id);
    setInteractionState(newState);
  };

  const handleToggleSave = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    const newState = articleInteractionService.toggleSaveForLater(userId, article.id);
    setInteractionState(newState);
  };

  const handleToggleLike = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsMenuOpen(false);
    const newState = articleInteractionService.toggleLike(userId, article.id);
    setInteractionState(newState);
  };

  const handleDislikeClick = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsMenuOpen(false);
    if (interactionState.isDisliked) {
      // Toggle off - ask for confirmation
      if (window.confirm('Remove dislike from this article?')) {
        const newState = articleInteractionService.dislikeArticle(userId, article.id);
        setInteractionState(newState);
      }
    } else {
      setIsDislikeModalOpen(true);
    }
  };

  const handleReportClick = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsMenuOpen(false);
    if (interactionState.isReported) {
      // Toggle off - ask for confirmation
      if (window.confirm('Remove report from this article?')) {
        const newState = articleInteractionService.reportArticle(userId, article.id);
        setInteractionState(newState);
      }
    } else {
      setIsReportModalOpen(true);
    }
  };

  const handleDislikeConfirm = (reason: string, otherReason?: string) => {
    const newState = articleInteractionService.dislikeArticle(
      userId,
      article.id,
      reason,
      otherReason
    );
    setInteractionState(newState);
    setIsDislikeModalOpen(false);
  };

  const handleReportConfirm = (reasons: string[], otherReason?: string) => {
    const newState = articleInteractionService.reportArticle(
      userId,
      article.id,
      reasons,
      otherReason
    );
    setInteractionState(newState);
    setIsReportModalOpen(false);
  };

  // Show skeleton while loading (only if no cache exists)
  // If we have placeholder data (metadata), show the card immediately
  if (isLoading && !fullArticle && !article.summary) {
    return <ArticleCardSkeleton />;
  }

  return (
    <div className='relative'>
      {/* Show subtle loading indicator when refetching in background */}
      {isFetching && fullArticle && (
        <div className='absolute -top-2 -right-2 z-30'>
          <div className='w-3 h-3 bg-amber-500 rounded-full animate-pulse border-2 border-white dark:border-amber-100' />
        </div>
      )}
      
      <Link
        href={`/articles/${displayArticle.id}`}
        className='block'
        onClick={handleArticleClick}
      >
        <div className='group relative bg-white/80 dark:bg-amber-100/80 backdrop-blur-sm rounded-xl shadow-lg border border-amber-200/50 dark:border-amber-300/50 overflow-hidden transition-all duration-300 hover:shadow-xl hover:scale-[1.01] flex flex-col'>
          {/* Action Buttons - Bottom Right */}
          <div className='absolute bottom-4 right-4 z-30 flex items-center gap-2'>
            {/* Save for Later - Desktop Only */}
            <button
              onClick={handleToggleSave}
              className='article-action-button hidden md:block opacity-75 hover:opacity-100 transition-opacity'
              aria-label={interactionState.isSaved ? 'Remove from saved' : 'Save for later'}
              title={interactionState.isSaved ? 'Remove from saved' : 'Save for later'}
            >
              {interactionState.isSaved ? (
                <svg
                  className='w-5 h-5 text-amber-600 dark:text-amber-700'
                  fill='currentColor'
                  viewBox='0 0 24 24'
                >
                  <path d='M17 3H7c-1.1 0-2 .9-2 2v16l7-3 7 3V5c0-1.1-.9-2-2-2z' />
                </svg>
              ) : (
                <svg
                  className='w-5 h-5 text-amber-600 dark:text-amber-700'
                  fill='none'
                  stroke='currentColor'
                  viewBox='0 0 24 24'
                  strokeWidth={2}
                >
                  <path
                    strokeLinecap='round'
                    strokeLinejoin='round'
                    d='M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z'
                  />
                </svg>
              )}
            </button>

            {/* Dropdown Menu - Always visible */}
            <div className='article-action-menu relative'>
              <button
                onClick={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  setIsMenuOpen(!isMenuOpen);
                }}
                className='md:opacity-75 md:hover:opacity-100 transition-opacity p-2 hover:opacity-90 active:opacity-100 md:p-0'
                aria-label='More options'
                title='More options'
              >
                <svg
                  className='w-4 h-4 md:w-4 md:h-4 text-amber-600 dark:text-amber-700 md:text-amber-600 md:dark:text-amber-700'
                  fill='none'
                  stroke='currentColor'
                  viewBox='0 0 24 24'
                  strokeWidth={2}
                >
                  <path
                    strokeLinecap='round'
                    strokeLinejoin='round'
                    d='M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z'
                  />
                </svg>
              </button>

              {/* Dropdown Menu Content */}
              {isMenuOpen && (
                <>
                  <div
                    className='fixed inset-0 z-40 bg-black/20'
                    onClick={() => setIsMenuOpen(false)}
                  />
                  {/* Mobile: Compact Popover, Desktop: Dropdown */}
                  <div className='absolute right-0 bottom-full mb-2 w-56 md:w-48 bg-white dark:bg-amber-100 rounded-lg shadow-2xl border border-amber-200/50 dark:border-amber-300/50 z-50 overflow-hidden max-h-[70vh] overflow-y-auto'>
                    {/* Mark as Read */}
                    <button
                      onClick={(e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        handleToggleRead(e);
                        setIsMenuOpen(false);
                      }}
                      className='w-full px-4 md:px-4 py-3 md:py-3 text-left hover:bg-amber-50 dark:hover:bg-amber-200/50 active:bg-amber-100 dark:active:bg-amber-200 transition-colors flex items-center gap-3 border-b border-amber-200/30 dark:border-amber-300/30'
                    >
                      {interactionState.isRead ? (
                        <svg
                          className='w-5 h-5 text-amber-600 dark:text-amber-700'
                          fill='currentColor'
                          viewBox='0 0 24 24'
                        >
                          <path d='M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z' />
                        </svg>
                      ) : (
                        <svg
                          className='w-5 h-5 text-amber-600 dark:text-amber-700'
                          fill='none'
                          stroke='currentColor'
                          viewBox='0 0 24 24'
                        >
                          <path
                            strokeLinecap='round'
                            strokeLinejoin='round'
                            strokeWidth={2}
                            d='M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z'
                          />
                        </svg>
                      )}
                      <span className='text-amber-900 dark:text-amber-900 font-medium text-sm'>
                        {interactionState.isRead ? 'Mark as Unread' : 'Mark as Read'}
                      </span>
                    </button>
                    {/* Save for Later */}
                    <button
                      onClick={(e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        handleToggleSave(e);
                        setIsMenuOpen(false);
                      }}
                      className='w-full px-4 py-3 text-left hover:bg-amber-50 dark:hover:bg-amber-200/50 active:bg-amber-100 dark:active:bg-amber-200 transition-colors flex items-center gap-3 border-b border-amber-200/30 dark:border-amber-300/30'
                    >
                      {interactionState.isSaved ? (
                        <svg
                          className='w-5 h-5 text-amber-600 dark:text-amber-700'
                          fill='currentColor'
                          viewBox='0 0 24 24'
                        >
                          <path d='M17 3H7c-1.1 0-2 .9-2 2v16l7-3 7 3V5c0-1.1-.9-2-2-2z' />
                        </svg>
                      ) : (
                        <svg
                          className='w-5 h-5 text-amber-600 dark:text-amber-700'
                          fill='none'
                          stroke='currentColor'
                          viewBox='0 0 24 24'
                        >
                          <path
                            strokeLinecap='round'
                            strokeLinejoin='round'
                            strokeWidth={2}
                            d='M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z'
                          />
                        </svg>
                      )}
                      <span className='text-amber-900 dark:text-amber-900 font-medium text-sm'>
                        {interactionState.isSaved ? 'Remove from Saved' : 'Save for Later'}
                      </span>
                    </button>
                    <button
                      onClick={(e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        handleToggleLike(e);
                        setIsMenuOpen(false);
                      }}
                      className='w-full px-4 py-3 text-left hover:bg-amber-50 dark:hover:bg-amber-200/50 active:bg-amber-100 dark:active:bg-amber-200 transition-colors flex items-center gap-3 border-b border-amber-200/30 dark:border-amber-300/30'
                    >
                      {interactionState.isLiked ? (
                        <svg
                          className='w-5 h-5 text-amber-600 dark:text-amber-700'
                          fill='currentColor'
                          viewBox='0 0 24 24'
                        >
                          <path d='M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z' />
                        </svg>
                      ) : (
                        <svg
                          className='w-5 h-5 text-amber-600 dark:text-amber-700'
                          fill='none'
                          stroke='currentColor'
                          viewBox='0 0 24 24'
                        >
                          <path
                            strokeLinecap='round'
                            strokeLinejoin='round'
                            strokeWidth={2}
                            d='M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z'
                          />
                        </svg>
                      )}
                      <span className='text-amber-900 dark:text-amber-900 font-medium text-sm'>
                        {interactionState.isLiked ? 'Unlike' : 'Like'}
                      </span>
                    </button>
                    <button
                      onClick={(e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        handleDislikeClick(e);
                      }}
                      className='w-full px-4 py-3 text-left hover:bg-amber-50 dark:hover:bg-amber-200/50 active:bg-amber-100 dark:active:bg-amber-200 transition-colors flex items-center gap-3 border-b border-amber-200/30 dark:border-amber-300/30'
                    >
                      {interactionState.isDisliked ? (
                        <svg
                          className='w-5 h-5 text-amber-600 dark:text-amber-700'
                          fill='currentColor'
                          viewBox='0 0 24 24'
                        >
                          <path d='M15 3H6c-.83 0-1.54.5-1.85 1.22l-3.02 7.05c-.09.23-.13.47-.13.73v2c0 1.1.9 2 2 2h6.31l-.95 4.57-.03.32c0 .41.17.79.44 1.06L9.83 23l6.59-6.59c.36-.36.58-.86.58-1.41V5c0-1.1-.9-2-2-2zm4 0v12h4V3h-4z' />
                        </svg>
                      ) : (
                        <svg
                          className='w-5 h-5 text-amber-600 dark:text-amber-700'
                          fill='none'
                          stroke='currentColor'
                          viewBox='0 0 24 24'
                        >
                          <path
                            strokeLinecap='round'
                            strokeLinejoin='round'
                            strokeWidth={2}
                            d='M10 14H5.236a2 2 0 01-1.789-2.894l3.5-7A2 2 0 018.736 3h4.018a2 2 0 01.485.06l3.76.94m-7 10v5a2 2 0 002 2h.096c.5 0 .905-.405.905-.904 0-.715.211-1.413.608-2.008L17.293 13m-7 10h2M14 14h4.764a2 2 0 001.789-2.894l-3.5-7A2 2 0 0013.264 3H9.246a2 2 0 00-1.789 1.106l-3.5 7A2 2 0 005.236 14H10'
                          />
                        </svg>
                      )}
                      <span className='text-amber-900 dark:text-amber-900 font-medium text-sm'>
                        {interactionState.isDisliked ? 'Remove Dislike' : 'Dislike'}
                      </span>
                    </button>
                    <button
                      onClick={(e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        handleReportClick(e);
                      }}
                      className='w-full px-4 py-3 text-left hover:bg-amber-50 dark:hover:bg-amber-200/50 active:bg-amber-100 dark:active:bg-amber-200 transition-colors flex items-center gap-3'
                    >
                      {interactionState.isReported ? (
                        <svg
                          className='w-5 h-5 text-amber-600 dark:text-amber-700'
                          fill='currentColor'
                          viewBox='0 0 24 24'
                        >
                          <path d='M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z' />
                        </svg>
                      ) : (
                        <svg
                          className='w-5 h-5 text-amber-600 dark:text-amber-700'
                          fill='none'
                          stroke='currentColor'
                          viewBox='0 0 24 24'
                        >
                          <path
                            strokeLinecap='round'
                            strokeLinejoin='round'
                            strokeWidth={2}
                            d='M3 21v-4m0 0V5a2 2 0 012-2h6.5l1 1H21l-3 6 3 6h-8.5l-1-1H5a2 2 0 00-2 2zm9-13.5V9'
                          />
                        </svg>
                      )}
                      <span className='text-amber-900 dark:text-amber-900 font-medium text-sm'>
                        {interactionState.isReported ? 'Remove Report' : 'Report'}
                      </span>
                    </button>
                  </div>
                </>
              )}
            </div>
          </div>
          {/* Subtle Pattern Overlay */}
          <div className='absolute inset-0 opacity-5'>
            <div
              className='absolute inset-0'
              style={{
                backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23d97706' fill-opacity='0.1'%3E%3Ccircle cx='30' cy='30' r='2'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
              }}
            />
          </div>

          {/* Article Title and Metadata */}
          <div className='relative z-20 p-6 flex-1 flex flex-col pb-16'>
            <h3 className='text-xl font-bold text-amber-900 dark:text-amber-900 mb-3 leading-tight'>
              {displayArticle.title}
            </h3>

            <div className='flex items-center gap-4 mb-4 flex-wrap'>
              <CategoryTag category={displayArticle.category} variant="compact" />
              <span className='flex items-center gap-1.5 text-xs text-amber-600 dark:text-amber-700'>
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
                {displayArticle.time_to_read}
              </span>
            </div>

            {/* Article Summary */}
            {displayArticle.summary && (
              <div className='flex-1 flex flex-col min-h-[180px] md:min-h-[140px]'>
                <p
                  className={
                    !isExpanded
                      ? 'text-sm text-amber-700 dark:text-amber-800 leading-relaxed line-clamp-8 md:line-clamp-3'
                      : 'text-sm text-amber-700 dark:text-amber-800 leading-relaxed'
                  }
                >
                  {displayArticle.summary}
                </p>
                {displayArticle.summary.length > 150 && (
                  <button
                    className='read-more-button mt-2 mb-2 inline-flex items-center gap-1 text-xs font-medium text-amber-600 dark:text-amber-700 hover:text-amber-800 dark:hover:text-amber-900 transition-colors self-start'
                    onClick={(e) => {
                      e.preventDefault();
                      e.stopPropagation();
                      setIsExpanded(!isExpanded);
                    }}
                  >
                    {isExpanded ? (
                      <>
                        <span>Read less</span>
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
                            d='M5 15l7-7 7 7'
                          />
                        </svg>
                      </>
                    ) : (
                      <>
                        <span>Read more</span>
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
                            d='M19 9l-7 7-7-7'
                          />
                        </svg>
                      </>
                    )}
                  </button>
                )}
              </div>
            )}
          </div>

          {/* Subtle Border Glow */}
          <div className='absolute inset-0 rounded-2xl border-2 border-transparent bg-gradient-to-br from-amber-300/20 to-amber-400/20 opacity-0 group-hover:opacity-100 transition-opacity duration-300' />
        </div>
      </Link>

      {/* Modals */}
      <DislikeModal
        isOpen={isDislikeModalOpen}
        onClose={() => setIsDislikeModalOpen(false)}
        onConfirm={handleDislikeConfirm}
        currentReason={interactionState.dislikedReason}
        currentOtherReason={interactionState.dislikedOtherReason}
      />
      <ReportModal
        isOpen={isReportModalOpen}
        onClose={() => setIsReportModalOpen(false)}
        onConfirm={handleReportConfirm}
        currentReasons={interactionState.reportedReasons}
        currentOtherReason={interactionState.reportedOtherReason}
      />
    </div>
  );
}
