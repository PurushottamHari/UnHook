import { useMemo, useCallback, useRef } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { useAuthStore } from '@/store/auth-store';
import { articleInteractionService } from '@/lib/services/article-interaction-service';
import { GeneratedContentInteraction } from '@/types';
import { ArticleInteractionState } from '@/lib/services/article-interaction-service';

/**
 * Shared hook for managing article interactions
 * Fetches interactions once and shares state across all components
 * Updates state optimistically after POST calls without refetching
 */
export function useArticleInteractions(
  articleId: string,
  initialInteractions?: GeneratedContentInteraction[]
) {
  const { user } = useAuthStore();
  const userId = user?.id || '607d95f0-47ef-444c-89d2-d05f257d1265';
  const queryClient = useQueryClient();
  const queryKey = ['article-interactions', articleId, userId];
  
  // Fetch interactions only if not provided
  const {
    data: fetchedInteractions,
    isLoading,
  } = useQuery<GeneratedContentInteraction[]>({
    queryKey,
    queryFn: () => articleInteractionService.fetchInteractions(articleId, userId),
    enabled: !!articleId && !!userId && !initialInteractions,
    staleTime: 5 * 60 * 1000, // 5 minutes - don't refetch too often
    initialData: initialInteractions,
  });

  // Get interactions from cache (which includes optimistic updates) or fetched/initial data
  const interactions = useMemo(() => {
    // First check React Query cache (includes optimistic updates)
    const cached = queryClient.getQueryData<GeneratedContentInteraction[]>(queryKey);
    if (cached) return cached;
    
    // Fall back to initial or fetched data
    const result = initialInteractions || fetchedInteractions || [];
    return result.length === 0 ? [] : result;
  }, [queryKey, queryClient, initialInteractions, fetchedInteractions]);

  // Get interaction state from current interactions - reads from cache
  const getInteractionState = useCallback((): ArticleInteractionState => {
    // Always read from cache to get latest optimistic updates
    const cached = queryClient.getQueryData<GeneratedContentInteraction[]>(queryKey);
    const currentInteractions = cached || initialInteractions || fetchedInteractions || [];
    return articleInteractionService.getArticleState(
      userId,
      articleId,
      currentInteractions
    );
  }, [articleId, userId, queryKey, queryClient, initialInteractions, fetchedInteractions]);

  // Update interactions in cache optimistically
  const updateInteractionsOptimistically = useCallback((
    updater: (interactions: GeneratedContentInteraction[]) => GeneratedContentInteraction[]
  ) => {
    queryClient.setQueryData<GeneratedContentInteraction[]>(queryKey, (old) => {
      const current = old || initialInteractions || fetchedInteractions || [];
      return updater(current);
    });
  }, [queryKey, queryClient, initialInteractions, fetchedInteractions]);

  // Listen for interaction updates from other components
  const handleInteractionUpdate = useCallback((e?: CustomEvent) => {
    if (e?.detail?.articleId === articleId) {
      if (e.detail?.source === 'local') {
        // Local update - interaction data is in the event, update cache directly
        if (e.detail?.interaction) {
          const interaction = e.detail.interaction;
          queryClient.setQueryData<GeneratedContentInteraction[]>(queryKey, (old) => {
            const current = old || initialInteractions || fetchedInteractions || [];
            // Remove old interactions of same type for this user, add new one
            const filtered = current.filter(i => 
              !(i.user_id === userId && i.interaction_type === interaction.interaction_type)
            );
            // Only add if ACTIVE
            if (interaction.status === 'ACTIVE') {
              return [...filtered, interaction];
            }
            return filtered;
          });
        }
      } else {
        // Update from another component/page - refetch to get latest state
        queryClient.invalidateQueries({ queryKey });
      }
    }
  }, [articleId, userId, queryKey, queryClient, initialInteractions, fetchedInteractions]);

  return {
    interactions,
    getInteractionState,
    updateInteractionsOptimistically,
    isLoading,
    handleInteractionUpdate,
  };
}
