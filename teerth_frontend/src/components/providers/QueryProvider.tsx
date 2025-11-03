'use client';

import { QueryClient } from '@tanstack/react-query';
import { PersistQueryClientProvider } from '@tanstack/react-query-persist-client';
import { createSyncStoragePersister } from '@tanstack/query-sync-storage-persister';
import { useState } from 'react';

export function QueryProvider({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            // How long data is considered "fresh" (not stale)
            // During this time, React Query won't refetch even if component remounts
            staleTime: 60 * 1000, // 1 minute - data stays fresh for 1 min

            // How long unused/inactive data stays in cache before garbage collection
            // After this time, cache is cleared if not being used
            gcTime: 5 * 60 * 1000, // 5 minutes (was cacheTime in v4)

            // Retry failed requests
            retry: 1, // Retry once on failure (default: 3)

            // Retry delay (exponential backoff)
            retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),

            // Refetch on window focus
            refetchOnWindowFocus: true,

            // Refetch on reconnect
            refetchOnReconnect: true,

            // Refetch on mount
            refetchOnMount: true, // Always refetch when component mounts

            // Background refetching when data becomes stale
            // refetchInterval: false, // Disable automatic polling (default)
            // refetchInterval: 30000, // Poll every 30 seconds if you want
          },
        },
      })
  );

  // Create localStorage persister
  const persister = createSyncStoragePersister({
    storage: typeof window !== 'undefined' ? window.localStorage : undefined,
    key: 'REACT_QUERY_CACHE', // Storage key in localStorage
  });

  return (
    <PersistQueryClientProvider
      client={queryClient}
      persistOptions={{
        persister,
        // Only persist queries that have meta.persist === true
        // This allows page-level control: add meta: { persist: true } to opt-in
        dehydrateOptions: {
          shouldDehydrateQuery: (query) => {
            // Check if query has meta.persist flag set to true
            return query.meta?.persist === true;
          },
        },
      }}
    >
      {children}
    </PersistQueryClientProvider>
  );
}
