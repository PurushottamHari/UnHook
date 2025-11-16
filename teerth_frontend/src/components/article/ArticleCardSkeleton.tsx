'use client';

/**
 * Skeleton loader for article cards in the dashboard
 * Matches the layout and styling of ExpandableArticleCard
 */
export default function ArticleCardSkeleton() {
  return (
    <div className="group relative bg-white/80 dark:bg-amber-100/80 backdrop-blur-sm rounded-xl shadow-lg border border-amber-200/50 dark:border-amber-300/50 overflow-hidden flex flex-col animate-pulse">
      {/* Subtle Pattern Overlay */}
      <div className="absolute inset-0 opacity-5">
        <div
          className="absolute inset-0"
          style={{
            backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23d97706' fill-opacity='0.1'%3E%3Ccircle cx='30' cy='30' r='2'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
          }}
        />
      </div>

      {/* Article Content Skeleton */}
      <div className="relative z-20 p-6 flex-1 flex flex-col">
        {/* Title Skeleton */}
        <div className="h-6 bg-amber-200/50 dark:bg-amber-300/50 rounded mb-3 w-4/5" />

        {/* Metadata Skeleton */}
        <div className="flex items-center gap-4 mb-4">
          <div className="h-6 w-20 bg-amber-200/50 dark:bg-amber-300/50 rounded-full" />
          <div className="h-4 w-16 bg-amber-200/50 dark:bg-amber-300/50 rounded" />
        </div>

        {/* Summary Skeleton */}
        <div className="flex-1 space-y-2">
          <div className="h-4 bg-amber-200/50 dark:bg-amber-300/50 rounded" />
          <div className="h-4 bg-amber-200/50 dark:bg-amber-300/50 rounded w-5/6" />
          <div className="h-4 bg-amber-200/50 dark:bg-amber-300/50 rounded w-4/6" />
        </div>
      </div>

      {/* Subtle Border Glow */}
      <div className="absolute inset-0 rounded-2xl border-2 border-transparent bg-gradient-to-br from-amber-300/20 to-amber-400/20 opacity-0" />
    </div>
  );
}





