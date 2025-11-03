'use client';

import { useState } from 'react';
import Link from 'next/link';
import { CachedNewspaperArticle } from '@/models/newspaper.model';

interface ExpandableArticleCardProps {
  article: CachedNewspaperArticle;
}

export default function ExpandableArticleCard({ article }: ExpandableArticleCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <Link
      href={`/articles/${article.id}`}
      className='block'
      onClick={(e) => {
        // Prevent navigation when clicking "Read more"
        if ((e.target as HTMLElement).closest('.read-more-button')) {
          e.preventDefault();
        }
      }}
    >
      <div className='group relative bg-white/80 dark:bg-amber-100/80 backdrop-blur-sm rounded-xl shadow-lg border border-amber-200/50 dark:border-amber-300/50 overflow-hidden transition-all duration-300 hover:shadow-xl hover:scale-[1.01] flex flex-col'>
        {/* Subtle Pattern Overlay */}
        <div className='absolute inset-0 opacity-5'>
          <div
            className='absolute inset-0'
            style={{
              backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23d97706' fill-opacity='0.1'%3E%3Ccircle cx='30' cy='30' r='2'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
            }}
          />
        </div>

        {/* Article Title and Metadata */}
        <div className='relative z-20 p-6 flex-1 flex flex-col'>
          <h3 className='text-xl font-bold text-amber-900 dark:text-amber-900 mb-3 leading-tight'>
            {article.title}
          </h3>

          <div className='flex items-center gap-4 text-sm text-amber-700 dark:text-amber-800 mb-4'>
            <span className='inline-flex items-center px-3 py-1.5 rounded-full text-xs font-medium bg-amber-200/50 text-amber-800 dark:bg-amber-300/50 dark:text-amber-900 border border-amber-300/30'>
              {article.category}
            </span>
            <span className='flex items-center gap-2 text-amber-600 dark:text-amber-700'>
              <svg
                className='w-4 h-4'
                fill='none'
                stroke='currentColor'
                viewBox='0 0 24 24'
              >
                <path
                  strokeLinecap='round'
                  strokeLinejoin='round'
                  strokeWidth={2}
                  d='M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z'
                />
              </svg>
              {article.time_to_read}
            </span>
          </div>

          {/* Article Summary */}
          {article.summary && (
            <div className='flex-1 flex flex-col'>
              <p
                className={`text-sm text-amber-700 dark:text-amber-800 leading-relaxed ${
                  !isExpanded ? 'line-clamp-3' : ''
                }`}
              >
                {article.summary}
              </p>
              {article.summary.length > 150 && (
                <button
                  className='read-more-button mt-2 inline-flex items-center gap-1 text-xs font-medium text-amber-600 dark:text-amber-700 hover:text-amber-800 dark:hover:text-amber-900 transition-colors self-start'
                  onClick={(e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    setIsExpanded(!isExpanded);
                  }}
                >
                  {isExpanded ? (
                    <>
                      <span>Read less</span>
                      <svg
                        className='w-4 h-4'
                        fill='none'
                        stroke='currentColor'
                        viewBox='0 0 24 24'
                      >
                        <path
                          strokeLinecap='round'
                          strokeLinejoin='round'
                          strokeWidth={2}
                          d='M5 15l7-7 7 7'
                        />
                      </svg>
                    </>
                  ) : (
                    <>
                      <span>Read more</span>
                      <svg
                        className='w-4 h-4'
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
                    </>
                  )}
                </button>
              )}
            </div>
          )}
        </div>

        {/* Subtle Border Glow */}
        <div className='absolute inset-0 rounded-2xl border-2 border-transparent bg-gradient-to-br from-amber-300/20 to-amber-400/20 opacity-0 group-hover:opacity-100 transition-opacity duration-300' />
      </div>
    </Link>
  );
}

