'use client';

/**
 * Skeleton loader for article content area
 * Shows animated placeholders while article content is loading
 */
export default function ArticleContentSkeleton() {
  return (
    <div className="prose prose-lg max-w-none dark:prose-invert mb-12">
      <div className="bg-white/80 dark:bg-amber-100/80 backdrop-blur-sm rounded-xl shadow-lg border border-amber-200/50 dark:border-amber-300/50 p-6 md:p-8 lg:p-10">
        <div className="max-w-3xl md:max-w-4xl lg:max-w-5xl xl:max-w-6xl mx-auto space-y-6">
          {/* Paragraph skeletons */}
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="space-y-3">
              <div className="h-4 bg-amber-200/50 dark:bg-amber-300/50 rounded animate-pulse" />
              <div className="h-4 bg-amber-200/50 dark:bg-amber-300/50 rounded animate-pulse w-5/6" />
              <div className="h-4 bg-amber-200/50 dark:bg-amber-300/50 rounded animate-pulse w-4/6" />
            </div>
          ))}
          
          {/* Heading skeleton */}
          <div className="pt-4 space-y-3">
            <div className="h-6 bg-amber-300/50 dark:bg-amber-400/50 rounded animate-pulse w-3/4" />
            <div className="h-4 bg-amber-200/50 dark:bg-amber-300/50 rounded animate-pulse" />
            <div className="h-4 bg-amber-200/50 dark:bg-amber-300/50 rounded animate-pulse w-5/6" />
          </div>

          {/* More paragraph skeletons */}
          {[1, 2].map((i) => (
            <div key={i} className="space-y-3">
              <div className="h-4 bg-amber-200/50 dark:bg-amber-300/50 rounded animate-pulse" />
              <div className="h-4 bg-amber-200/50 dark:bg-amber-300/50 rounded animate-pulse w-5/6" />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}





