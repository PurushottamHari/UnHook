'use client';

/**
 * Skeleton loader for category tags section
 * Shows animated placeholders while categories are loading
 */
export default function CategoryTagsSkeleton() {
  return (
    <div className="text-center text-amber-700 dark:text-amber-800 mb-8">
      <div className="h-6 bg-amber-200/50 dark:bg-amber-300/50 rounded w-32 mx-auto mb-3 animate-pulse" />
      <div className="flex flex-wrap items-center justify-center gap-2 mb-3">
        {[1, 2, 3, 4].map((i) => (
          <div
            key={i}
            className="h-6 bg-amber-200/50 dark:bg-amber-300/50 rounded-md w-20 animate-pulse"
            style={{ animationDelay: `${i * 100}ms` }}
          />
        ))}
      </div>
      <div className="h-4 bg-amber-200/50 dark:bg-amber-300/50 rounded w-24 mx-auto animate-pulse" />
    </div>
  );
}





