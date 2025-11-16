'use client';

import { useState, useEffect } from 'react';
import { useAuthStore } from '@/store/auth-store';
import {
  articleInteractionService,
  ArticleInteractionState,
} from '@/lib/services/article-interaction-service';
import DislikeModal from '@/components/DislikeModal';
import ReportModal from '@/components/ReportModal';

interface ArticleActionBarProps {
  articleId: string;
}

export default function ArticleActionBar({ articleId }: ArticleActionBarProps) {
  const [interactionState, setInteractionState] = useState<ArticleInteractionState>({
    isRead: false,
    isSaved: false,
    isLiked: false,
    isDisliked: false,
    isReported: false,
  });
  const [isDislikeModalOpen, setIsDislikeModalOpen] = useState(false);
  const [isReportModalOpen, setIsReportModalOpen] = useState(false);
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const { user } = useAuthStore();
  const userId = user?.id || '607d95f0-47ef-444c-89d2-d05f257d1265';

  // Load interaction state
  useEffect(() => {
    if (articleId) {
      const state = articleInteractionService.getArticleState(userId, articleId);
      setInteractionState(state);
    }
  }, [articleId, userId]);

  // Close menu when clicking outside
  useEffect(() => {
    if (!isMenuOpen) return;

    const handleClickOutside = (e: MouseEvent) => {
      const target = e.target as HTMLElement;
      if (!target.closest('[data-action-menu]')) {
        setIsMenuOpen(false);
      }
    };

    document.addEventListener('click', handleClickOutside);
    return () => document.removeEventListener('click', handleClickOutside);
  }, [isMenuOpen]);

  // Action handlers
  const handleToggleRead = () => {
    const newState = articleInteractionService.toggleRead(userId, articleId);
    setInteractionState(newState);
  };

  const handleToggleSave = () => {
    const newState = articleInteractionService.toggleSaveForLater(userId, articleId);
    setInteractionState(newState);
  };

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

  const handleReportClick = () => {
    if (interactionState.isReported) {
      // Toggle off - ask for confirmation
      if (window.confirm('Remove report from this article?')) {
        const newState = articleInteractionService.reportArticle(userId, articleId);
        setInteractionState(newState);
      }
    } else {
      setIsReportModalOpen(true);
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

  const handleReportConfirm = (reasons: string[], otherReason?: string) => {
    const newState = articleInteractionService.reportArticle(
      userId,
      articleId,
      reasons,
      otherReason
    );
    setInteractionState(newState);
    setIsReportModalOpen(false);
  };


  return (
    <>
      {/* Floating 3-Dot Menu - Always Collapsed */}
      <div className="fixed bottom-6 right-6 z-[100] pointer-events-auto" data-action-menu>
        <div className="relative">
          <button
            onClick={(e) => {
              e.stopPropagation();
              setIsMenuOpen(!isMenuOpen);
            }}
            className="p-2 md:p-2 hover:opacity-90 active:opacity-100 transition-opacity md:opacity-75 md:hover:opacity-100"
            aria-label="Article actions"
            title="Article actions"
          >
            <svg
              className="w-4 h-4 md:w-4 md:h-4 text-amber-600 dark:text-amber-700 md:text-amber-600/70 md:dark:text-amber-700/70"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z"
              />
            </svg>
          </button>

          {isMenuOpen && (
            <>
              <div className="fixed inset-0 z-40 bg-black/20" onClick={() => setIsMenuOpen(false)} />
              <div className="absolute right-0 bottom-full mb-2 w-56 bg-white dark:bg-amber-100 rounded-lg shadow-2xl border border-amber-200/50 dark:border-amber-300/50 z-50 overflow-hidden">
                <div className="py-2">
                  {/* Mark as Read */}
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleToggleRead();
                      setIsMenuOpen(false);
                    }}
                    className="w-full px-4 py-3 text-left hover:bg-amber-50 dark:hover:bg-amber-200/50 active:bg-amber-100 dark:active:bg-amber-200 transition-colors flex items-center gap-3 border-b border-amber-200/30 dark:border-amber-300/30"
                  >
                    {interactionState.isRead ? (
                      <svg className="w-5 h-5 text-amber-600 dark:text-amber-700" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z" />
                      </svg>
                    ) : (
                      <svg className="w-5 h-5 text-amber-600 dark:text-amber-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    )}
                    <span className="text-amber-900 dark:text-amber-900 font-medium text-sm">{interactionState.isRead ? 'Mark as Unread' : 'Mark as Read'}</span>
                  </button>
                  {/* Save for Later */}
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleToggleSave();
                      setIsMenuOpen(false);
                    }}
                    className="w-full px-4 py-3 text-left hover:bg-amber-50 dark:hover:bg-amber-200/50 active:bg-amber-100 dark:active:bg-amber-200 transition-colors flex items-center gap-3 border-b border-amber-200/30 dark:border-amber-300/30"
                  >
                    {interactionState.isSaved ? (
                      <svg className="w-5 h-5 text-amber-600 dark:text-amber-700" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M17 3H7c-1.1 0-2 .9-2 2v16l7-3 7 3V5c0-1.1-.9-2-2-2z" />
                      </svg>
                    ) : (
                      <svg className="w-5 h-5 text-amber-600 dark:text-amber-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
                      </svg>
                    )}
                    <span className="text-amber-900 dark:text-amber-900 font-medium text-sm">{interactionState.isSaved ? 'Remove from Saved' : 'Save for Later'}</span>
                  </button>
                  {/* Like */}
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleToggleLike();
                      setIsMenuOpen(false);
                    }}
                    className="w-full px-4 py-3 text-left hover:bg-amber-50 dark:hover:bg-amber-200/50 active:bg-amber-100 dark:active:bg-amber-200 transition-colors flex items-center gap-3 border-b border-amber-200/30 dark:border-amber-300/30"
                  >
                    {interactionState.isLiked ? (
                      <svg className="w-5 h-5 text-amber-600 dark:text-amber-700" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z" />
                      </svg>
                    ) : (
                      <svg className="w-5 h-5 text-amber-600 dark:text-amber-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                      </svg>
                    )}
                    <span className="text-amber-900 dark:text-amber-900 font-medium text-sm">{interactionState.isLiked ? 'Unlike' : 'Like'}</span>
                  </button>
                  {/* Dislike */}
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDislikeClick();
                      setIsMenuOpen(false);
                    }}
                    className="w-full px-4 py-3 text-left hover:bg-amber-50 dark:hover:bg-amber-200/50 active:bg-amber-100 dark:active:bg-amber-200 transition-colors flex items-center gap-3 border-b border-amber-200/30 dark:border-amber-300/30"
                  >
                    {interactionState.isDisliked ? (
                      <svg className="w-5 h-5 text-amber-600 dark:text-amber-700" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M15 3H6c-.83 0-1.54.5-1.85 1.22l-3.02 7.05c-.09.23-.13.47-.13.73v2c0 1.1.9 2 2 2h6.31l-.95 4.57-.03.32c0 .41.17.79.44 1.06L9.83 23l6.59-6.59c.36-.36.58-.86.58-1.41V5c0-1.1-.9-2-2-2zm4 0v12h4V3h-4z" />
                      </svg>
                    ) : (
                      <svg className="w-5 h-5 text-amber-600 dark:text-amber-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 14H5.236a2 2 0 01-1.789-2.894l3.5-7A2 2 0 018.736 3h4.018a2 2 0 01.485.06l3.76.94m-7 10v5a2 2 0 002 2h.096c.5 0 .905-.405.905-.904 0-.715.211-1.413.608-2.008L17.293 13m-7 10h2M14 14h4.764a2 2 0 001.789-2.894l-3.5-7A2 2 0 0013.264 3H9.246a2 2 0 00-1.789 1.106l-3.5 7A2 2 0 005.236 14H10" />
                      </svg>
                    )}
                    <span className="text-amber-900 dark:text-amber-900 font-medium text-sm">{interactionState.isDisliked ? 'Remove Dislike' : 'Dislike'}</span>
                  </button>
                  {/* Report */}
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleReportClick();
                      setIsMenuOpen(false);
                    }}
                    className="w-full px-4 py-3 text-left hover:bg-amber-50 dark:hover:bg-amber-200/50 active:bg-amber-100 dark:active:bg-amber-200 transition-colors flex items-center gap-3"
                  >
                    {interactionState.isReported ? (
                      <svg className="w-5 h-5 text-amber-600 dark:text-amber-700" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" />
                      </svg>
                    ) : (
                      <svg className="w-5 h-5 text-amber-600 dark:text-amber-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 21v-4m0 0V5a2 2 0 012-2h6.5l1 1H21l-3 6 3 6h-8.5l-1-1H5a2 2 0 00-2 2zm9-13.5V9" />
                      </svg>
                    )}
                    <span className="text-amber-900 dark:text-amber-900 font-medium text-sm">{interactionState.isReported ? 'Remove Report' : 'Report'}</span>
                  </button>
                </div>
              </div>
            </>
          )}
        </div>
      </div>

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
    </>
  );
}

