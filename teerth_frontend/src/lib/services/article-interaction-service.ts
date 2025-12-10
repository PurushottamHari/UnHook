/**
 * Article Interaction Service
 * 
 * This service handles user interactions with articles:
 * - Mark as Read/Unread (frontend-only)
 * - Save for Later / Remove from Saved
 * - Like/Unlike
 * - Dislike (with reason)
 * - Report (with reasons)
 * 
 * Uses API endpoints for backend interactions.
 */

import { GeneratedContentInteraction } from '@/types';

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

/**
 * Parse active_user_interactions array into ArticleInteractionState
 */
export function parseInteractionsToState(
  interactions: GeneratedContentInteraction[],
  userId: string
): ArticleInteractionState {
  const state: ArticleInteractionState = {
    isRead: false, // Frontend-only, not in backend
    isSaved: false,
    isLiked: false,
    isDisliked: false,
    isReported: false,
  };

  if (!interactions || interactions.length === 0) {
    return state;
  }

  // Filter interactions for this user and ACTIVE status
  const activeInteractions = interactions.filter(
    (interaction) =>
      interaction.user_id === userId && interaction.status === 'ACTIVE'
  );

  for (const interaction of activeInteractions) {
    switch (interaction.interaction_type) {
      case 'LIKE':
        state.isLiked = true;
        break;
      case 'DISLIKE':
        state.isDisliked = true;
        if (interaction.metadata) {
          state.dislikedReason = interaction.metadata.reason || interaction.metadata.dislike_reason;
          state.dislikedOtherReason = interaction.metadata.other_reason || interaction.metadata.otherReason;
        }
        break;
      case 'SAVED':
        state.isSaved = true;
        break;
      case 'REPORT':
        state.isReported = true;
        if (interaction.metadata) {
          const reasonsStr = interaction.metadata.reasons || interaction.metadata.report_reasons;
          if (reasonsStr) {
            // Parse comma-separated reasons or JSON array
            try {
              state.reportedReasons = JSON.parse(reasonsStr);
            } catch {
              state.reportedReasons = reasonsStr.split(',').map((r) => r.trim());
            }
          }
          state.reportedOtherReason = interaction.metadata.other_reason || interaction.metadata.otherReason;
        }
        break;
    }
  }

  return state;
}

class ArticleInteractionService {
  private readonly STORAGE_KEY = 'article_read_state'; // Only for read state (frontend-only)
  private readonly USER_PREFIX = 'user_';

  /**
   * Get storage key for a specific user (read state only)
   */
  private getUserStorageKey(userId: string): string {
    return `${this.USER_PREFIX}${userId}`;
  }

  /**
   * Get read state for a user (frontend-only, uses localStorage)
   */
  private getUserReadStates(userId: string): Record<string, boolean> {
    if (typeof window === 'undefined') {
      return {};
    }

    try {
      const storageKey = this.getUserStorageKey(userId);
      const stored = localStorage.getItem(storageKey);
      return stored ? JSON.parse(stored) : {};
    } catch (error) {
      console.error('Error reading read states:', error);
      return {};
    }
  }

  /**
   * Save read state for a user (frontend-only)
   */
  private saveUserReadStates(
    userId: string,
    readStates: Record<string, boolean>
  ): void {
    if (typeof window === 'undefined') {
      return;
    }

    try {
      const storageKey = this.getUserStorageKey(userId);
      localStorage.setItem(storageKey, JSON.stringify(readStates));
    } catch (error) {
      console.error('Error saving read states:', error);
    }
  }

  /**
   * Get interaction state for a specific article
   * Combines API interactions with frontend read state
   */
  getArticleState(
    userId: string,
    articleId: string,
    interactions?: GeneratedContentInteraction[]
  ): ArticleInteractionState {
    // Parse API interactions
    const apiState = interactions
      ? parseInteractionsToState(interactions, userId)
      : {
          isSaved: false,
          isLiked: false,
          isDisliked: false,
          isReported: false,
        };

    // Get read state from localStorage (frontend-only)
    const readStates = this.getUserReadStates(userId);
    const isRead = readStates[articleId] || false;

    return {
      ...apiState,
      isRead,
    };
  }

  /**
   * Fetch interactions for an article from API
   */
  async fetchInteractions(
    articleId: string,
    userId: string
  ): Promise<GeneratedContentInteraction[]> {
    try {
      const response = await fetch(`/api/articles/${articleId}/interactions?userId=${userId}`, {
        method: 'GET',
      });

      if (!response.ok) {
        // If 404, return empty array (no interactions yet)
        if (response.status === 404) {
          return [];
        }
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || 'Failed to fetch interactions');
      }

      const data = await response.json();
      return data.interactions || [];
    } catch (error) {
      console.error('Error fetching interactions:', error);
      return [];
    }
  }

  /**
   * Create or update an interaction via API
   */
  async createInteraction(
    articleId: string,
    userId: string,
    interactionType: 'LIKE' | 'DISLIKE' | 'REPORT' | 'SAVED',
    metadata?: Record<string, string>
  ): Promise<GeneratedContentInteraction> {
    try {
      const response = await fetch(`/api/articles/${articleId}/interactions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          userId,
          interactionType,
          metadata: metadata || {},
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || 'Failed to create interaction');
      }

      const data = await response.json();
      const interaction = data.interaction;

      // Dispatch custom event to notify components of changes
      // Mark as local update so components don't refetch unnecessarily
      if (typeof window !== 'undefined') {
        window.dispatchEvent(new CustomEvent('articleInteractionChange', {
          detail: { articleId, interactionType },
        }));
        // Dispatch with interaction data so components can update optimistically
        window.dispatchEvent(new CustomEvent('articleInteractionUpdated', {
          detail: { articleId, interaction, source: 'local' },
        }));
      }

      return interaction;
    } catch (error) {
      console.error('Error creating interaction:', error);
      throw error;
    }
  }

  /**
   * Toggle read state (frontend-only, no API call)
   */
  toggleRead(userId: string, articleId: string): ArticleInteractionState {
    const readStates = this.getUserReadStates(userId);
    const currentRead = readStates[articleId] || false;
    readStates[articleId] = !currentRead;
    this.saveUserReadStates(userId, readStates);

    // Dispatch custom event
    if (typeof window !== 'undefined') {
      window.dispatchEvent(new Event('articleInteractionChange'));
    }

    // Return updated state (read state only, other states would need to be passed in)
    return {
      isRead: !currentRead,
      isSaved: false,
      isLiked: false,
      isDisliked: false,
      isReported: false,
    };
  }

  /**
   * Toggle save for later
   */
  async toggleSaveForLater(
    userId: string,
    articleId: string,
    currentInteractions: GeneratedContentInteraction[]
  ): Promise<GeneratedContentInteraction> {
    // Create interaction - backend handles toggle logic
    return await this.createInteraction(articleId, userId, 'SAVED');
  }

  /**
   * Toggle like
   */
  async toggleLike(
    userId: string,
    articleId: string,
    currentInteractions: GeneratedContentInteraction[]
  ): Promise<GeneratedContentInteraction> {
    // Backend handles toggle logic - creating LIKE will deactivate if already active
    return await this.createInteraction(articleId, userId, 'LIKE');
  }

  /**
   * Set dislike with reason
   */
  async dislikeArticle(
    userId: string,
    articleId: string,
    reason?: string,
    otherReason?: string,
    currentInteractions?: GeneratedContentInteraction[]
  ): Promise<GeneratedContentInteraction> {
    // If toggling off, reason will be undefined
    const metadata: Record<string, string> = {};
    if (reason) {
      metadata.reason = reason;
    }
    if (otherReason) {
      metadata.other_reason = otherReason;
    }

    return await this.createInteraction(
      articleId,
      userId,
      'DISLIKE',
      Object.keys(metadata).length > 0 ? metadata : undefined
    );
  }

  /**
   * Set report with reasons
   */
  async reportArticle(
    userId: string,
    articleId: string,
    reasons?: string[],
    otherReason?: string,
    currentInteractions?: GeneratedContentInteraction[]
  ): Promise<GeneratedContentInteraction | null> {
    // Report cannot be toggled off per backend logic
    const metadata: Record<string, string> = {};
    if (reasons && reasons.length > 0) {
      metadata.reasons = JSON.stringify(reasons);
    }
    if (otherReason) {
      metadata.other_reason = otherReason;
    }

    try {
      return await this.createInteraction(
        articleId,
        userId,
        'REPORT',
        Object.keys(metadata).length > 0 ? metadata : undefined
      );
    } catch (error) {
      // If already reported, backend will reject - that's expected behavior
      console.warn('Report interaction failed (may already be reported):', error);
      return null;
    }
  }

  /**
   * Get all articles by state (for dashboard sections)
   * Note: This now requires interactions to be passed in from API responses
   * For read state, still uses localStorage
   */
  getArticlesByState(
    userId: string,
    state: 'read' | 'saved' | 'liked' | 'disliked' | 'reported',
    articlesWithInteractions?: Array<{
      id: string;
      interactions?: GeneratedContentInteraction[];
    }>
  ): string[] {
    const articleIds: string[] = [];

    if (state === 'read') {
      // Read state is frontend-only, use localStorage
      const readStates = this.getUserReadStates(userId);
      for (const [articleId, isRead] of Object.entries(readStates)) {
        if (isRead) articleIds.push(articleId);
      }
      return articleIds;
    }

    // For other states, use API interactions
    if (!articlesWithInteractions) {
      return [];
    }

    for (const article of articlesWithInteractions) {
      if (!article.interactions || article.interactions.length === 0) {
        continue;
      }

      const stateFromInteractions = parseInteractionsToState(
        article.interactions,
        userId
      );

      switch (state) {
        case 'saved':
          if (stateFromInteractions.isSaved) articleIds.push(article.id);
          break;
        case 'liked':
          if (stateFromInteractions.isLiked) articleIds.push(article.id);
          break;
        case 'disliked':
          if (stateFromInteractions.isDisliked) articleIds.push(article.id);
          break;
        case 'reported':
          if (stateFromInteractions.isReported) articleIds.push(article.id);
          break;
      }
    }

    return articleIds;
  }
}

// Export singleton instance
export const articleInteractionService = new ArticleInteractionService();
