import Image from 'next/image';
import Link from 'next/link';
import { Article } from '@/types';

interface ArticleCardProps {
  article: Article;
  variant?: 'featured' | 'preview';
  className?: string;
}

export default function ArticleCard({
  article,
  variant = 'featured',
  className = '',
}: ArticleCardProps) {
  if (variant === 'preview') {
    return (
      <Link href={`/article/${article.id}`} className='block'>
        <div
          className={`bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-4 hover:shadow-md hover:scale-105 transition-all duration-200 ${className}`}
        >
          <h3 className='text-lg font-semibold text-gray-900 dark:text-white mb-2 line-clamp-2'>
            {article.title}
          </h3>
          <p className='text-sm text-gray-500 dark:text-gray-400'>
            {new Date(article.publishedAt).toLocaleDateString()}
          </p>
        </div>
      </Link>
    );
  }

  return (
    <Link href={`/article/${article.id}`} className='block'>
      <article
        className={`bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 overflow-hidden hover:shadow-xl transition-shadow duration-200 ${className}`}
      >
        {article.imageUrl && (
          <div className='relative h-64 md:h-80'>
            <Image
              src={article.imageUrl}
              alt={article.title}
              fill
              className='object-cover'
              priority
            />
          </div>
        )}
        <div className='p-6 md:p-8'>
          <h1 className='text-2xl md:text-3xl font-bold text-gray-900 dark:text-white mb-4 leading-tight'>
            {article.title}
          </h1>
          <div className='prose prose-gray dark:prose-invert max-w-none'>
            <p className='text-gray-700 dark:text-gray-300 leading-relaxed'>
              {article.body}
            </p>
          </div>
          <div className='mt-6 pt-4 border-t border-gray-200 dark:border-gray-700'>
            <p className='text-sm text-gray-500 dark:text-gray-400'>
              Published on{' '}
              {new Date(article.publishedAt).toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
              })}
            </p>
          </div>
        </div>
      </article>
    </Link>
  );
}
