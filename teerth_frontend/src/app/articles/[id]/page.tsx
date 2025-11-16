'use client';

import { useQuery } from '@tanstack/react-query';
import { useParams } from 'next/navigation';
import { useEffect, useMemo, useState } from 'react';
import { Article } from '@/models/article.model';
import TeerthLogoIcon from '@/components/TeerthLogoIcon';
import WaitlistSection from '@/components/WaitlistSection';
import LoadingSpinner from '@/components/LoadingSpinner';
import ArticleContentSkeleton from '@/components/ArticleContentSkeleton';
import ShareModal from '@/components/ShareModal';
import Toast from '@/components/Toast';
import ArticleActionBar from '@/components/article/ArticleActionBar';
import ArticleContent from '@/components/article/ArticleContent';
import MobileMetadataDropdown from '@/components/MobileMetadataDropdown';
import CategoryTag from '@/components/CategoryTag';
import ArticleTitle from '@/components/article/ArticleTitle';
import Breadcrumb from '@/components/navigation/Breadcrumb';
import ShareButton from '@/components/ShareButton';
import { copyToClipboard, isWebShareAvailable } from '@/lib/share';

/**
 * Get placeholder data from sessionStorage
 * This allows showing article metadata immediately while fetching full content
 */
function getPlaceholderData(articleId: string): Partial<Article> | undefined {
  if (typeof window === 'undefined') return undefined;

  try {
    const stored = sessionStorage.getItem(`article_placeholder_${articleId}`);
    if (!stored) return undefined;

    const placeholder = JSON.parse(stored);
    
    // Convert placeholder to partial Article format
    // Use current date as published_at fallback, will be replaced with real data
    return {
      id: placeholder.id,
      title: placeholder.title,
      category: placeholder.category,
      time_to_read: placeholder.time_to_read,
      content: '', // Content will be loaded from API
      article_link: '',
      article_source: 'Teerth',
      external_id: '',
      youtube_channel: '',
      published_at: new Date().toISOString(), // Will be replaced with real data
      cached_at: placeholder.cached_at || new Date().toISOString(),
    };
  } catch (error) {
    console.warn('Failed to load placeholder data:', error);
    return undefined;
  }
}

/**
 * Clean up placeholder data from sessionStorage after use
 */
function clearPlaceholderData(articleId: string) {
  if (typeof window === 'undefined') return;
  try {
    sessionStorage.removeItem(`article_placeholder_${articleId}`);
  } catch (error) {
    // Silently fail
  }
}

export default function ArticlePage() {
  const params = useParams();
  const articleId = params.id as string;
  const [isShareModalOpen, setIsShareModalOpen] = useState(false);
  const [showToast, setShowToast] = useState(false);

  // Get placeholder data from sessionStorage for instant display
  const placeholderData = useMemo(
    () => getPlaceholderData(articleId),
    [articleId]
  );

  const { 
    data: article, 
    isLoading, 
    isFetching,
    error 
  } = useQuery<Article | null>({
    queryKey: ['article', articleId],
    queryFn: async () => {
      const response = await fetch(`/api/articles/${articleId}`);
      
      // Handle 404 gracefully - return null instead of throwing
      if (response.status === 404) {
        return null;
      }
      
      // For other errors, check if response is ok
      if (!response.ok) {
        const data = await response.json().catch(() => ({}));
        throw new Error(data.error || 'Failed to fetch article');
      }
      
      const data = await response.json();
      if (!data.success) {
        throw new Error(data.error || 'Failed to fetch article');
      }
      return data.article;
    },
    enabled: !!articleId,
    // Use placeholder data for instant display while fetching
    placeholderData: placeholderData as Article | undefined,
    // Opt-in to localStorage persistence
    // This article will be cached and persist across page refreshes
    meta: {
      persist: true,
    },
    // Don't retry on 404s (they won't succeed on retry)
    retry: (failureCount, error) => {
      // Don't retry if we got a 404 or if error message indicates not found
      if (error?.message?.includes('No article found')) {
        return false;
      }
      return failureCount < 1; // Retry once for other errors
    },
  });

  // Clean up placeholder data once we have real data
  useEffect(() => {
    if (article && !isFetching) {
      clearPlaceholderData(articleId);
    }
  }, [article, isFetching, articleId]);

  // Use placeholder or actual article data for display
  const displayArticle = article || placeholderData;

  // Share function
  const handleShare = async () => {
    // Check if mobile and native share is available
    const isMobile = /iPhone|iPad|iPod|Android/i.test(
      typeof window !== 'undefined' ? navigator.userAgent : ''
    );
    
    if (isMobile && isWebShareAvailable()) {
      // Open modal with native share option
      setIsShareModalOpen(true);
    } else {
      // Just copy to clipboard and show toast
      const url = typeof window !== 'undefined' ? window.location.href : '';
      const success = await copyToClipboard(url);
      if (success) {
        setShowToast(true);
      }
    }
  };

  // Get share data
  const shareData = useMemo(() => {
    const url = typeof window !== 'undefined' ? window.location.href : '';
    const title = displayArticle?.title || 'Check out this article on Teerth';
    return {
      url,
      title,
      text: `Check out this article: ${title}`,
    };
  }, [displayArticle]);

  // Show error state for actual errors (not 404s - those return null)
  if (error && !displayArticle) {
    return (
      <div className="min-h-screen bg-yellow-50 dark:bg-amber-50">
        <div className="w-full px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex items-center justify-center min-h-[60vh]">
            <div className="bg-white/80 dark:bg-amber-100/80 backdrop-blur-sm rounded-xl shadow-lg border border-amber-200/50 dark:border-amber-300/50 p-8 text-center">
              <p className="text-lg text-amber-800 dark:text-amber-900 font-light">
                {error.message}
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Show "not found" state when article is explicitly null (404 case)
  // Only show if we've finished loading and have no placeholder data
  if (article === null && !isLoading && !isFetching && !placeholderData) {
    return (
      <div className="min-h-screen bg-yellow-50 dark:bg-amber-50 flex items-center justify-center">
        <div className="text-center">
          <div className="flex justify-center mb-8">
            <TeerthLogoIcon alt="Teerth Logo" size={200} />
          </div>
          <h1 className="text-4xl font-light text-amber-900 dark:text-amber-900 mb-4">
            Article Not Found
          </h1>
        </div>
      </div>
    );
  }

  // Show loading state only if we have no data at all (first load, no cache, no placeholder)
  if (isLoading && !displayArticle) {
    return (
      <div className="min-h-screen bg-yellow-50 dark:bg-amber-50">
        <div className="w-full px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex items-center justify-center h-64">
            <LoadingSpinner size="lg" text="Loading article..." />
          </div>
        </div>
      </div>
    );
  }

  // If we don't have article data yet, show nothing (shouldn't happen with placeholder)
  if (!displayArticle) {
    return null;
  }

  return (
    <div className="min-h-screen bg-yellow-50 dark:bg-amber-50">
      <div className="w-full px-4 sm:px-6 lg:px-8 py-8">
        <Breadcrumb href="/dashboard" label="Puru's Digest" />

        {/* Article Header */}
        <header className="mb-8 text-center relative">
          {/* Share Icon - Top Right */}
          <div className="absolute top-0 right-0">
            <ShareButton
              onClick={handleShare}
              size="md"
              ariaLabel="Share article"
              title="Share article"
            />
          </div>

          {/* Teerth Logo */}
          <div className="flex justify-center mb-8">
            <TeerthLogoIcon alt="Teerth Logo" size={200} />
          </div>

          {/* Loading indicator when fetching fresh data */}
          {isFetching && article && (
            <div className="flex justify-center mb-4">
              <LoadingSpinner size="sm" />
            </div>
          )}

          <ArticleTitle title={displayArticle.title || ''} />

          {/* Article Metadata */}
          <div className="flex flex-col items-center gap-4 mb-4">
            {/* Mobile: Dropdown for article info */}
            <MobileMetadataDropdown
              label="Article Info"
              items={[
                // Category
                <div key="category" className="flex items-center gap-1.5">
                  <svg
                    className="w-3 h-3 md:w-4 md:h-4"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"
                    />
                  </svg>
                  <CategoryTag category={displayArticle.category || ''} variant="article" />
                </div>,
                // Published Date
                <div key="date" className="flex items-center gap-1.5">
                  <svg
                    className="w-3 h-3 md:w-4 md:h-4"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                  </svg>
                  {article?.published_at ? (
                    <time dateTime={article.published_at}>
                      {(() => {
                        const date = new Date(article.published_at);
                        const day = String(date.getDate()).padStart(2, '0');
                        const month = String(date.getMonth() + 1).padStart(2, '0');
                        const year = date.getFullYear();
                        return `${day}/${month}/${year}`;
                      })()}
                    </time>
                  ) : (
                    <span>Loading date...</span>
                  )}
                </div>,
                // YouTube Channel (if present)
                ...(article?.youtube_channel
                  ? [
                      <div key="channel" className="flex items-center gap-1.5">
                        <svg
                          className="w-3 h-3 md:w-4 md:h-4"
                          fill="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z" />
                        </svg>
                        <span className="italic">{article.youtube_channel}</span>
                      </div>,
                    ]
                  : []),
              ]}
            />

            {/* Desktop: Inline display */}
            <div className="hidden md:flex items-center justify-center gap-6 text-[13px] text-amber-700 dark:text-amber-800 flex-wrap">
              {/* Category */}
              <div className="flex items-center gap-1.5">
                <svg
                  className="w-3 h-3 md:w-4 md:h-4"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"
                  />
                </svg>
                <CategoryTag category={displayArticle.category || ''} variant="article" />
              </div>

              {/* Published Date */}
              <div className="flex items-center gap-1.5">
                <svg
                  className="w-3 h-3 md:w-4 md:h-4"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
                {article?.published_at ? (
                  <time dateTime={article.published_at}>
                    {new Date(article.published_at).toLocaleDateString('en-US', {
                      weekday: 'long',
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric',
                    })}
                  </time>
                ) : (
                  <span className="text-amber-600 dark:text-amber-700">Loading date...</span>
                )}
              </div>

              {/* YouTube Channel (Creator) */}
              {article?.youtube_channel && (
                <div className="flex items-center gap-1.5">
                  <svg
                    className="w-3 h-3 md:w-4 md:h-4"
                    fill="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z" />
                  </svg>
                  <span className="italic">{article.youtube_channel}</span>
                </div>
              )}
            </div>

            {/* Time to read - always visible below */}
            <div className="flex items-center justify-center gap-1.5 text-[13px] text-amber-600 dark:text-amber-700">
              <svg
                className="w-4 h-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
                />
              </svg>
              <span>{displayArticle.time_to_read || ''}</span>
            </div>
          </div>
        </header>

        {/* Article Content */}
        {article?.content ? (
          <ArticleContent
            content={article.content}
            articleId={article.id}
            onShare={handleShare}
          />
        ) : (
          <ArticleContentSkeleton />
        )}

        {/* Waitlist Section */}
        <WaitlistSection variant="detailed" />
      </div>

      {/* Share Modal */}
      <ShareModal
        isOpen={isShareModalOpen}
        onClose={() => setIsShareModalOpen(false)}
        shareData={shareData}
      />

      {/* Toast */}
      <Toast
        message="Link copied to clipboard!"
        isVisible={showToast}
        onClose={() => setShowToast(false)}
      />

      {/* Floating Action Bar */}
      {article && <ArticleActionBar articleId={article.id} />}
    </div>
  );
}
