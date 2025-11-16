'use client';

import ArticleCardSkeleton from '@/components/article/ArticleCardSkeleton';

export default function ArticleSkeleton() {
  return (
    <div className='bg-white/50 dark:bg-amber-100/50 backdrop-blur-sm rounded-3xl p-8 md:p-12 border border-amber-200/50 dark:border-amber-300/50 shadow-lg'>
      <div className='grid grid-cols-1 lg:grid-cols-2 gap-6 items-start'>
        {[1, 2, 3, 4].map((i) => (
          <ArticleCardSkeleton key={i} />
        ))}
      </div>
    </div>
  );
}

