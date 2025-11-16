'use client';

import { useState, useEffect } from 'react';
import { useAuthStore } from '@/store/auth-store';
import {
  articleInteractionService,
  ArticleInteractionState,
} from '@/lib/services/article-interaction-service';
import DislikeModal from '@/components/DislikeModal';

interface ArticleLikeDislikeProps {
  articleId: string;
  position?: 'top-right' | 'bottom-right' | 'bottom-left' | 'inline';
  showOnMobile?: boolean;
  mobilePosition?: 'bottom-right' | 'bottom-left';
}

export default function ArticleLikeDislike({ 
  articleId, 
  position = 'inline',
  showOnMobile = false,
  mobilePosition = 'bottom-right'
}: ArticleLikeDislikeProps) {
  const [interactionState, setInteractionState] = useState<ArticleInteractionState>({
    isRead: false,
    isSaved: false,
    isLiked: false,
    isDisliked: false,
    isReported: false,
  });
  const [isDislikeModalOpen, setIsDislikeModalOpen] = useState(false);

  const { user } = useAuthStore();
  const userId = user?.id || '607d95f0-47ef-444c-89d2-d05f257d1265';

  // Load interaction state
  useEffect(() => {
    if (articleId) {
      const state = articleInteractionService.getArticleState(userId, articleId);
      setInteractionState(state);
    }
  }, [articleId, userId]);

  // Listen for interaction changes
  useEffect(() => {
    if (typeof window === 'undefined') return;
    const handleInteractionChange = () => {
      if (articleId) {
        const state = articleInteractionService.getArticleState(userId, articleId);
        setInteractionState(state);
      }
    };
    window.addEventListener('articleInteractionChange', handleInteractionChange);
    return () => window.removeEventListener('articleInteractionChange', handleInteractionChange);
  }, [articleId, userId]);

  const handleToggleLike = () => {
    const newState = articleInteractionService.toggleLike(userId, articleId);
    setInteractionState(newState);
  };

  const handleDislikeClick = () => {
    if (interactionState.isDisliked) {
      // Toggle off - ask for confirmation
      if (window.confirm('Remove dislike from this article?')) {
        const newState = articleInteractionService.dislikeArticle(userId, articleId);
        setInteractionState(newState);
      }
    } else {
      setIsDislikeModalOpen(true);
    }
  };

  const handleDislikeConfirm = (reason: string, otherReason?: string) => {
    const newState = articleInteractionService.dislikeArticle(
      userId,
      articleId,
      reason,
      otherReason
    );
    setInteractionState(newState);
    setIsDislikeModalOpen(false);
  };

  // Inline mode - flows with content
  if (position === 'inline') {
    return (
      <>
        {/* Inline in content flow - Desktop and Mobile */}
        <div className="flex flex-row items-center justify-start gap-6 py-2">
          {/* Like Button */}
          <div className="flex flex-col items-center gap-1">
            <button
              onClick={handleToggleLike}
              className={`p-2.5 rounded-full transition-all duration-200 ${
                interactionState.isLiked
                  ? 'bg-amber-100 dark:bg-amber-200 text-amber-700 dark:text-amber-900 shadow-md'
                  : 'bg-white dark:bg-amber-100 backdrop-blur-sm text-amber-600 dark:text-amber-700 hover:text-amber-600 dark:hover:text-amber-700 hover:bg-amber-50 dark:hover:bg-amber-200/50 border border-amber-200 dark:border-amber-300 shadow-sm'
              }`}
              aria-label={interactionState.isLiked ? 'Unlike' : 'Like'}
              title={interactionState.isLiked ? 'Unlike' : 'Like'}
            >
              {interactionState.isLiked ? (
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z" />
                </svg>
              ) : (
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                </svg>
              )}
            </button>
            <span className="text-xs text-amber-700 dark:text-amber-800 font-medium">Like</span>
          </div>

          {/* Dislike Button */}
          <div className="flex flex-col items-center gap-1">
            <button
              onClick={handleDislikeClick}
              className={`p-2.5 rounded-full transition-all duration-200 ${
                interactionState.isDisliked
                  ? 'bg-amber-100 dark:bg-amber-200 text-amber-700 dark:text-amber-900 shadow-md'
                  : 'bg-white dark:bg-amber-100 backdrop-blur-sm text-amber-600 dark:text-amber-700 hover:text-amber-600 dark:hover:text-amber-700 hover:bg-amber-50 dark:hover:bg-amber-200/50 border border-amber-200 dark:border-amber-300 shadow-sm'
              }`}
              aria-label={interactionState.isDisliked ? 'Remove dislike' : 'Dislike'}
              title={interactionState.isDisliked ? 'Remove dislike' : 'Dislike'}
            >
              {interactionState.isDisliked ? (
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M15 3H6c-.83 0-1.54.5-1.85 1.22l-3.02 7.05c-.09.23-.13.47-.13.73v2c0 1.1.9 2 2 2h6.31l-.95 4.57-.03.32c0 .41.17.79.44 1.06L9.83 23l6.59-6.59c.36-.36.58-.86.58-1.41V5c0-1.1-.9-2-2-2zm4 0v12h4V3h-4z" />
                </svg>
              ) : (
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 14H5.236a2 2 0 01-1.789-2.894l3.5-7A2 2 0 018.736 3h4.018a2 2 0 01.485.06l3.76.94m-7 10v5a2 2 0 002 2h.096c.5 0 .905-.405.905-.904 0-.715.211-1.413.608-2.008L17.293 13m-7 10h2M14 14h4.764a2 2 0 001.789-2.894l-3.5-7A2 2 0 0013.264 3H9.246a2 2 0 00-1.789 1.106l-3.5 7A2 2 0 005.236 14H10" />
                </svg>
              )}
            </button>
            <span className="text-xs text-amber-700 dark:text-amber-800 font-medium">Dislike</span>
          </div>
        </div>

        {/* Dislike Modal */}
        <DislikeModal
          isOpen={isDislikeModalOpen}
          onClose={() => setIsDislikeModalOpen(false)}
          onConfirm={handleDislikeConfirm}
          currentReason={interactionState.dislikedReason}
          currentOtherReason={interactionState.dislikedOtherReason}
        />
      </>
    );
  }

  // Absolute positioning modes (for backward compatibility)
  const desktopPositionClasses = 
    position === 'top-right' 
      ? 'md:absolute md:top-6 md:right-6' 
      : position === 'bottom-right'
      ? 'md:absolute md:bottom-0 md:right-6'
      : 'md:absolute md:bottom-0 md:left-6';

  // Mobile positioning - position above the 3-dot menu to avoid overlap
  const mobilePositionClasses = showOnMobile
    ? mobilePosition === 'bottom-right'
      ? 'fixed bottom-24 right-6 md:hidden'
      : 'fixed bottom-24 left-6 md:hidden'
    : 'hidden md:flex';

  const containerClasses = `${desktopPositionClasses} ${mobilePositionClasses} flex-col items-center gap-3 z-10`;

  return (
    <>
      <div className={containerClasses}>
        {/* Like Button */}
        <div className="flex flex-col items-center gap-1">
          <button
            onClick={handleToggleLike}
            className={`rounded-full transition-all duration-200 ${
              interactionState.isLiked
                ? 'bg-amber-100 dark:bg-amber-200 text-amber-700 dark:text-amber-900 shadow-md'
                : 'bg-white/90 dark:bg-amber-100/90 backdrop-blur-sm text-amber-600/70 dark:text-amber-700/70 hover:text-amber-600 dark:hover:text-amber-700 hover:bg-amber-50 dark:hover:bg-amber-200/50 border border-amber-200/60 dark:border-amber-300/60'
            } ${showOnMobile ? 'p-3' : 'p-2.5'}`}
            aria-label={interactionState.isLiked ? 'Unlike' : 'Like'}
            title={interactionState.isLiked ? 'Unlike' : 'Like'}
          >
            {interactionState.isLiked ? (
              <svg className={`${showOnMobile ? 'w-6 h-6' : 'w-5 h-5'}`} fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z" />
              </svg>
            ) : (
              <svg
                className={`${showOnMobile ? 'w-6 h-6' : 'w-5 h-5'}`}
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"
                />
              </svg>
            )}
          </button>
          <span className="text-xs text-amber-700 dark:text-amber-800 font-medium">Like</span>
        </div>

        {/* Dislike Button */}
        <div className="flex flex-col items-center gap-1">
          <button
            onClick={handleDislikeClick}
            className={`rounded-full transition-all duration-200 ${
              interactionState.isDisliked
                ? 'bg-amber-100 dark:bg-amber-200 text-amber-700 dark:text-amber-900 shadow-md'
                : 'bg-white/90 dark:bg-amber-100/90 backdrop-blur-sm text-amber-600/70 dark:text-amber-700/70 hover:text-amber-600 dark:hover:text-amber-700 hover:bg-amber-50 dark:hover:bg-amber-200/50 border border-amber-200/60 dark:border-amber-300/60'
            } ${showOnMobile ? 'p-3' : 'p-2.5'}`}
            aria-label={interactionState.isDisliked ? 'Remove dislike' : 'Dislike'}
            title={interactionState.isDisliked ? 'Remove dislike' : 'Dislike'}
          >
            {interactionState.isDisliked ? (
              <svg className={`${showOnMobile ? 'w-6 h-6' : 'w-5 h-5'}`} fill="currentColor" viewBox="0 0 24 24">
                <path d="M15 3H6c-.83 0-1.54.5-1.85 1.22l-3.02 7.05c-.09.23-.13.47-.13.73v2c0 1.1.9 2 2 2h6.31l-.95 4.57-.03.32c0 .41.17.79.44 1.06L9.83 23l6.59-6.59c.36-.36.58-.86.58-1.41V5c0-1.1-.9-2-2-2zm4 0v12h4V3h-4z" />
              </svg>
            ) : (
              <svg
                className={`${showOnMobile ? 'w-6 h-6' : 'w-5 h-5'}`}
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M10 14H5.236a2 2 0 01-1.789-2.894l3.5-7A2 2 0 018.736 3h4.018a2 2 0 01.485.06l3.76.94m-7 10v5a2 2 0 002 2h.096c.5 0 .905-.405.905-.904 0-.715.211-1.413.608-2.008L17.293 13m-7 10h2M14 14h4.764a2 2 0 001.789-2.894l-3.5-7A2 2 0 0013.264 3H9.246a2 2 0 00-1.789 1.106l-3.5 7A2 2 0 005.236 14H10"
                />
              </svg>
            )}
          </button>
          <span className="text-xs text-amber-700 dark:text-amber-800 font-medium">Dislike</span>
        </div>
      </div>

      {/* Dislike Modal */}
      <DislikeModal
        isOpen={isDislikeModalOpen}
        onClose={() => setIsDislikeModalOpen(false)}
        onConfirm={handleDislikeConfirm}
        currentReason={interactionState.dislikedReason}
        currentOtherReason={interactionState.dislikedOtherReason}
      />
    </>
  );
}

