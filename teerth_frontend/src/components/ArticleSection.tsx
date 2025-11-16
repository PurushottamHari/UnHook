'use client';

import { useState } from 'react';
import { CachedNewspaperArticle } from '@/models/newspaper.model';
import ExpandableArticleCard from './ExpandableArticleCard';

interface ArticleSectionProps {
  title: string;
  articles: CachedNewspaperArticle[];
  defaultCollapsed?: boolean;
  icon?: React.ReactNode;
}

export default function ArticleSection({
  title,
  articles,
  defaultCollapsed = true,
  icon,
}: ArticleSectionProps) {
  const [isCollapsed, setIsCollapsed] = useState(defaultCollapsed);

  if (articles.length === 0) {
    return null;
  }

  return (
    <div className='bg-white/50 dark:bg-amber-100/50 backdrop-blur-sm rounded-3xl p-8 md:p-12 border border-amber-200/50 dark:border-amber-300/50 shadow-lg mb-6'>
      <button
        onClick={() => setIsCollapsed(!isCollapsed)}
        className='w-full flex items-center justify-between mb-6 text-left'
      >
        <div className='flex items-center gap-3'>
          {icon && <div className='text-amber-700 dark:text-amber-800'>{icon}</div>}
          <h2 className='text-2xl md:text-3xl font-semibold text-amber-900 dark:text-amber-900'>
            {title}
          </h2>
          <span className='text-sm font-normal text-amber-600 dark:text-amber-700'>
            ({articles.length})
          </span>
        </div>
        <svg
          className={`w-6 h-6 text-amber-700 dark:text-amber-800 transition-transform duration-200 ${
            isCollapsed ? '' : 'rotate-180'
          }`}
          fill='none'
          stroke='currentColor'
          viewBox='0 0 24 24'
        >
          <path
            strokeLinecap='round'
            strokeLinejoin='round'
            strokeWidth={2}
            d='M19 9l-7 7-7-7'
          />
        </svg>
      </button>

      {!isCollapsed && (
        <div className='grid grid-cols-1 lg:grid-cols-2 gap-6 items-start'>
          {articles.map(article => (
            <ExpandableArticleCard key={article.id} article={article} />
          ))}
        </div>
      )}
    </div>
  );
}

