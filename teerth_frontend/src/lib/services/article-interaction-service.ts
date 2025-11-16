/**
 * Mock Article Interaction Service
 * 
 * This service handles user interactions with articles:
 * - Mark as Read/Unread
 * - Save for Later / Remove from Saved
 * - Like/Unlike
 * - Dislike (with reason)
 * - Report (with reasons)
 * 
 * Currently uses localStorage for state management.
 * Backend implementation will replace this later.
 */

export interface ArticleInteractionState {
  isRead: boolean;
  isSaved: boolean;
  isLiked: boolean;
  isDisliked: boolean;
  dislikedReason?: string;
  dislikedOtherReason?: string;
  isReported: boolean;
  reportedReasons?: string[];
  reportedOtherReason?: string;
}

export interface DislikeReason {
  value: string;
  label: string;
}

export interface ReportReason {
  value: string;
  label: string;
}

export const DISLIKE_REASONS: DislikeReason[] = [
  { value: 'not_relevant', label: 'Not relevant' },
  { value: 'misleading_headline', label: 'Misleading headline' },
  { value: 'too_long', label: 'Too long' },
  { value: 'poor_writing', label: 'Poor writing' },
  { value: 'off_topic', label: 'Off-topic' },
  { value: 'other', label: 'Other' },
];

export const REPORT_REASONS: ReportReason[] = [
  { value: 'wrong_information', label: 'Wrong information' },
  { value: 'clickbaity', label: 'Clickbaity' },
  { value: 'misleading', label: 'Misleading' },
  { value: 'inappropriate', label: 'Inappropriate content' },
  { value: 'spam', label: 'Spam' },
  { value: 'other', label: 'Other' },
];

class ArticleInteractionService {
  private readonly STORAGE_KEY = 'article_interactions';
  private readonly USER_PREFIX = 'user_';

  /**
   * Get storage key for a specific user
   */
  private getUserStorageKey(userId: string): string {
    return `${this.USER_PREFIX}${userId}`;
  }

  /**
   * Get all interactions for a user
   */
  private getUserInteractions(userId: string): Record<string, ArticleInteractionState> {
    if (typeof window === 'undefined') {
      return {};
    }

    try {
      const storageKey = this.getUserStorageKey(userId);
      const stored = localStorage.getItem(storageKey);
      return stored ? JSON.parse(stored) : {};
    } catch (error) {
      console.error('Error reading article interactions:', error);
      return {};
    }
  }

  /**
   * Save interactions for a user
   */
  private saveUserInteractions(
    userId: string,
    interactions: Record<string, ArticleInteractionState>
  ): void {
    if (typeof window === 'undefined') {
      return;
    }

    try {
      const storageKey = this.getUserStorageKey(userId);
      localStorage.setItem(storageKey, JSON.stringify(interactions));
    } catch (error) {
      console.error('Error saving article interactions:', error);
    }
  }

  /**
   * Get interaction state for a specific article
   */
  getArticleState(userId: string, articleId: string): ArticleInteractionState {
    const interactions = this.getUserInteractions(userId);
    return interactions[articleId] || {
      isRead: false,
      isSaved: false,
      isLiked: false,
      isDisliked: false,
      isReported: false,
    };
  }

  /**
   * Update interaction state for a specific article
   */
  private updateArticleState(
    userId: string,
    articleId: string,
    updates: Partial<ArticleInteractionState>
  ): ArticleInteractionState {
    const interactions = this.getUserInteractions(userId);
    const currentState = interactions[articleId] || {
      isRead: false,
      isSaved: false,
      isLiked: false,
      isDisliked: false,
      isReported: false,
    };

    const newState: ArticleInteractionState = {
      ...currentState,
      ...updates,
    };

    interactions[articleId] = newState;
    this.saveUserInteractions(userId, interactions);

    // Dispatch custom event to notify components of changes (same tab)
    if (typeof window !== 'undefined') {
      window.dispatchEvent(new Event('articleInteractionChange'));
    }

    // Log for debugging (will be replaced with API call)
    console.log(`[ArticleInteraction] ${articleId}:`, newState);

    return newState;
  }

  /**
   * Toggle read state
   */
  toggleRead(userId: string, articleId: string): ArticleInteractionState {
    const currentState = this.getArticleState(userId, articleId);
    return this.updateArticleState(userId, articleId, {
      isRead: !currentState.isRead,
    });
  }

  /**
   * Toggle save for later
   */
  toggleSaveForLater(userId: string, articleId: string): ArticleInteractionState {
    const currentState = this.getArticleState(userId, articleId);
    return this.updateArticleState(userId, articleId, {
      isSaved: !currentState.isSaved,
    });
  }

  /**
   * Toggle like
   */
  toggleLike(userId: string, articleId: string): ArticleInteractionState {
    const currentState = this.getArticleState(userId, articleId);
    return this.updateArticleState(userId, articleId, {
      isLiked: !currentState.isLiked,
      // If liking, remove dislike
      isDisliked: currentState.isLiked ? currentState.isDisliked : false,
      dislikedReason: currentState.isLiked ? currentState.dislikedReason : undefined,
      dislikedOtherReason: currentState.isLiked ? currentState.dislikedOtherReason : undefined,
    });
  }

  /**
   * Set dislike with reason
   */
  dislikeArticle(
    userId: string,
    articleId: string,
    reason?: string,
    otherReason?: string
  ): ArticleInteractionState {
    const currentState = this.getArticleState(userId, articleId);
    
    // If already disliked and toggling off, remove dislike
    if (currentState.isDisliked && !reason) {
      return this.updateArticleState(userId, articleId, {
        isDisliked: false,
        dislikedReason: undefined,
        dislikedOtherReason: undefined,
      });
    }

    // Set dislike
    return this.updateArticleState(userId, articleId, {
      isDisliked: true,
      dislikedReason: reason,
      dislikedOtherReason: otherReason,
      // If disliking, remove like
      isLiked: false,
    });
  }

  /**
   * Set report with reasons
   */
  reportArticle(
    userId: string,
    articleId: string,
    reasons?: string[],
    otherReason?: string
  ): ArticleInteractionState {
    const currentState = this.getArticleState(userId, articleId);
    
    // If already reported and toggling off, remove report
    if (currentState.isReported && !reasons) {
      return this.updateArticleState(userId, articleId, {
        isReported: false,
        reportedReasons: undefined,
        reportedOtherReason: undefined,
      });
    }

    // Set report
    return this.updateArticleState(userId, articleId, {
      isReported: true,
      reportedReasons: reasons,
      reportedOtherReason: otherReason,
    });
  }

  /**
   * Get all articles by state (for dashboard sections)
   */
  getArticlesByState(
    userId: string,
    state: 'read' | 'saved' | 'liked' | 'disliked' | 'reported'
  ): string[] {
    const interactions = this.getUserInteractions(userId);
    const articleIds: string[] = [];

    for (const [articleId, interactionState] of Object.entries(interactions)) {
      switch (state) {
        case 'read':
          if (interactionState.isRead) articleIds.push(articleId);
          break;
        case 'saved':
          if (interactionState.isSaved) articleIds.push(articleId);
          break;
        case 'liked':
          if (interactionState.isLiked) articleIds.push(articleId);
          break;
        case 'disliked':
          if (interactionState.isDisliked) articleIds.push(articleId);
          break;
        case 'reported':
          if (interactionState.isReported) articleIds.push(articleId);
          break;
      }
    }

    return articleIds;
  }
}

// Export singleton instance
export const articleInteractionService = new ArticleInteractionService();

