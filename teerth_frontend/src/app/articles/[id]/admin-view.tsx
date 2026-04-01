'use client';

import { useQuery } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';
import { useEffect, useMemo, useState } from 'react';
import { Article } from '@/models/article.model';
import TeerthLogoIcon from '@/components/TeerthLogoIcon';
import LoadingSpinner from '@/components/LoadingSpinner';
import ArticleContentSkeleton from '@/components/ArticleContentSkeleton';
import ShareModal from '@/components/ShareModal';
import Toast from '@/components/Toast';
import ArticleActionBar from '@/components/article/ArticleActionBar';
import ArticleContent from '@/components/article/ArticleContent';
import CategoryTag from '@/components/CategoryTag';
import YoutubeBadge from '@/components/YoutubeBadge';
import SourceBadge from '@/components/SourceBadge';
import ReadTimeBadge from '@/components/ReadTimeBadge';
import ArticleTitle from '@/components/article/ArticleTitle';
import Breadcrumb from '@/components/navigation/Breadcrumb';
import ShareButton from '@/components/ShareButton';
import ModeBanner from '@/components/ModeBanner';
import { copyToClipboard, isWebShareAvailable } from '@/lib/share';

function getPlaceholderData(articleId: string): Partial<Article> | undefined {
  if (typeof window === 'undefined') return undefined;

  try {
    const stored = sessionStorage.getItem(`article_placeholder_${articleId}`);
    if (!stored) return undefined;

    const placeholder = JSON.parse(stored);
    
    return {
      id: placeholder.id,
      title: placeholder.title,
      category: placeholder.category,
      time_to_read: placeholder.time_to_read,
      content: '', 
      summary: placeholder.summary,
      article_link: '',
      article_source: 'Teerth',
      external_id: '',
      youtube_channel: placeholder.youtube_channel || '',
      published_at: placeholder.published_at || new Date().toISOString(), 
      cached_at: placeholder.cached_at || new Date().toISOString(),
    };
  } catch (error) {
    console.warn('Failed to load placeholder data:', error);
    return undefined;
  }
}

function clearPlaceholderData(articleId: string) {
  if (typeof window === 'undefined') return;
  try {
    sessionStorage.removeItem(`article_placeholder_${articleId}`);
  } catch (error) {
    // Silently fail
  }
}

export default function AdminView({ articleId }: { articleId: string }) {
  const router = useRouter();
  const [isShareModalOpen, setIsShareModalOpen] = useState(false);
  const [showToast, setShowToast] = useState(false);

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
      
      if (response.status === 404) {
        return null;
      }
      
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
    placeholderData: placeholderData as Article | undefined,
    meta: {
      persist: true,
    },
    retry: (failureCount, error) => {
      if (error?.message?.includes('No article found')) {
        return false;
      }
      return failureCount < 1; 
    },
  });

  useEffect(() => {
    if (article && !isFetching) {
      clearPlaceholderData(articleId);
    }
  }, [article, isFetching, articleId]);

  const displayArticle = article || placeholderData;

  const handleShare = () => {
    setIsShareModalOpen(true);
  };

  const shareData = useMemo(() => {
    const url = typeof window !== 'undefined' ? window.location.href : '';
    const title = displayArticle?.title || 'Check out this article on Teerth';
    return {
      url,
      title,
      text: `Check out this article: ${title}`,
    };
  }, [displayArticle]);

  if (error && !displayArticle) {
    return (
      <div className="min-h-screen bg-yellow-50 dark:bg-amber-50">
        <ModeBanner mode="admin" />
        <div className="w-full px-4 sm:px-6 lg:px-8 py-8 pt-12">
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

  if (isLoading && !displayArticle) {
    return (
      <div className="min-h-screen bg-yellow-50 dark:bg-amber-50">
        <ModeBanner mode="admin" />
        <div className="w-full px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex items-center justify-center h-64">
            <LoadingSpinner size="lg" text="Loading article..." />
          </div>
        </div>
      </div>
    );
  }

  if (!displayArticle) {
    return null;
  }

  return (
    <div className="min-h-screen bg-yellow-50 dark:bg-amber-50 relative">
      <ModeBanner mode="admin" />
      <div className="w-full px-4 sm:px-6 lg:px-8 py-8 pt-12">
        <header className="mb-8 text-center relative">
          <div className="absolute top-0 left-0 z-10">
            <Breadcrumb onClick={() => router.back()} label="Back to Dashboard" hideLabelOnMobile={true} />
          </div>

          <div className="absolute top-0 right-0 z-10">
            <ShareButton
              onClick={handleShare}
              size="md"
              ariaLabel="Share article"
              title="Share article"
            />
          </div>

          <div className="flex justify-center mb-8">
            <TeerthLogoIcon alt="Teerth Logo" size={200} />
          </div>

          {isFetching && article && (
            <div className="flex justify-center mb-4">
              <LoadingSpinner size="sm" />
            </div>
          )}

          <ArticleTitle title={displayArticle.title || ''} />

          <div className="flex flex-col items-center gap-4 mb-4">
            <div className="flex md:hidden items-center justify-center gap-4 text-[13px] text-amber-700 dark:text-amber-800 flex-wrap">
              <div className="flex items-center gap-1.5">
                <svg
                  className="w-3.5 h-3.5"
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
                {displayArticle?.published_at ? (
                  <time dateTime={displayArticle.published_at}>
                    {(() => {
                      const date = new Date(displayArticle.published_at);
                      const day = String(date.getDate()).padStart(2, '0');
                      const month = String(date.getMonth() + 1).padStart(2, '0');
                      const year = date.getFullYear();
                      return `${day}/${month}/${year}`;
                    })()}
                  </time>
                ) : (
                  <span>Loading date...</span>
                )}
              </div>

              {displayArticle?.youtube_channel ? (
                <YoutubeBadge
                  channelName={displayArticle.youtube_channel}
                  className="flex items-center gap-1.5"
                  iconClassName="w-3.5 h-3.5"
                />
              ) : (
                <SourceBadge
                  sourceName={displayArticle?.article_source || 'Teerth'}
                  className="flex items-center gap-1.5"
                  iconClassName="w-3.5 h-3.5"
                />
              )}
            </div>

            <div className="hidden md:flex items-center justify-center gap-6 text-[13px] text-amber-700 dark:text-amber-800 flex-wrap">
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
                {displayArticle?.published_at ? (
                  <time dateTime={displayArticle.published_at}>
                    {new Date(displayArticle.published_at).toLocaleDateString('en-US', {
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

              {displayArticle?.youtube_channel && (
                <YoutubeBadge
                  channelName={displayArticle.youtube_channel}
                  className="flex items-center gap-1.5"
                  iconClassName="w-3 h-3 md:w-4 md:h-4"
                />
              )}
            </div>

            <ReadTimeBadge
              timeToRead={displayArticle.time_to_read || ''}
              className="flex items-center justify-center gap-1.5 text-[13px] text-amber-600 dark:text-amber-700"
              iconClassName="w-4 h-4"
            />
          </div>
        </header>

        {article?.content ? (
          <ArticleContent
            content={article.content}
            articleId={article.id}
            onShare={handleShare}
          />
        ) : (
          <ArticleContentSkeleton />
        )}
      </div>

      <ShareModal
        isOpen={isShareModalOpen}
        onClose={() => setIsShareModalOpen(false)}
        shareData={shareData}
        article={displayArticle as Article}
      />

      <Toast
        message="Link copied to clipboard!"
        isVisible={showToast}
        onClose={() => setShowToast(false)}
      />

      {article && <ArticleActionBar articleId={article.id} />}
    </div>
  );
}
