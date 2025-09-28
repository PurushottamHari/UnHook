import { notFound } from 'next/navigation';
import Link from 'next/link';
import TeerthLogoIcon from '@/components/TeerthLogoIcon';
import WaitlistSection from '@/components/WaitlistSection';
import { getCachedArticle, CachedArticle } from '@/lib/cache/article-cache';
import ReactMarkdown from 'react-markdown';
import { Metadata } from 'next';

interface ArticlePageProps {
  params: {
    id: string;
  };
}

async function getArticle(id: string): Promise<CachedArticle | null> {
  // Try to get article from cache first
  const cachedArticle = getCachedArticle(id);

  if (cachedArticle) {
    return cachedArticle;
  }

  // If not in cache, return null (article not found)
  return null;
}

async function getArticleDateForNavigation(
  article: CachedArticle
): Promise<string | null> {
  try {
    // Use the article's published date to determine which newspaper date to navigate to
    const publishedDate = new Date(article.published_at);
    const articleDate = publishedDate.toISOString().split('T')[0]; // YYYY-MM-DD format

    return articleDate;
  } catch (error) {
    console.error('Error getting article date for navigation:', error);
    return null;
  }
}

export async function generateMetadata({
  params,
}: ArticlePageProps): Promise<Metadata> {
  const { id } = await params;
  const article = await getArticle(id);

  if (!article) {
    return {
      title: 'Teerth - Article Not Found',
      description: 'The requested article could not be found.',
    };
  }

  return {
    title: `Teerth - ${article.title}`,
    description: `Read "${article.title}" - ${article.category} article from Teerth's curated collection.`,
    openGraph: {
      title: `Teerth - ${article.title}`,
      description: `Read "${article.title}" - ${article.category} article from Teerth's curated collection.`,
      type: 'article',
      publishedTime: article.published_at,
    },
  };
}

export default async function ArticlePage({ params }: ArticlePageProps) {
  const { id } = await params;
  const article = await getArticle(id);

  if (!article) {
    notFound();
  }

  // Get the date for navigation based on article's published date
  const navigationDate = await getArticleDateForNavigation(article);

  return (
    <div className='min-h-screen bg-yellow-50 dark:bg-amber-50'>
      <div className='w-full px-4 sm:px-6 lg:px-8 py-8'>
        {/* Breadcrumb */}
        <nav className='mb-8'>
          <Link
            href={
              navigationDate
                ? `/dashboard?date=${navigationDate}`
                : '/dashboard'
            }
            className='inline-flex items-center text-sm text-amber-700 dark:text-amber-800 hover:text-amber-900 dark:hover:text-amber-900 transition-colors'
          >
            <svg
              className='w-4 h-4 mr-2'
              fill='none'
              stroke='currentColor'
              viewBox='0 0 24 24'
            >
              <path
                strokeLinecap='round'
                strokeLinejoin='round'
                strokeWidth={2}
                d='M15 19l-7-7 7-7'
              />
            </svg>
            Back to Puru&apos;s Newspaper
          </Link>
        </nav>

        {/* Article Header */}
        <header className='mb-8 text-center'>
          {/* Teerth Logo */}
          <div className='flex justify-center mb-8'>
            <TeerthLogoIcon alt='Teerth Logo' size={200} />
          </div>

          <h1 className='text-3xl md:text-4xl lg:text-5xl font-bold text-amber-900 dark:text-amber-900 mb-6 leading-tight'>
            {article.title}
          </h1>

          <div className='flex items-center justify-center gap-6 text-sm text-amber-700 dark:text-amber-800 mb-4 flex-wrap'>
            <div className='flex items-center gap-2'>
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
                  d='M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z'
                />
              </svg>
              <span className='inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-amber-100 text-amber-800 dark:bg-amber-200 dark:text-amber-900'>
                {article.category}
              </span>
            </div>

            <div className='flex items-center gap-2'>
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
              <time dateTime={article.published_at}>
                {new Date(article.published_at).toLocaleDateString('en-US', {
                  weekday: 'long',
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric',
                })}
              </time>
            </div>

            <div className='flex items-center gap-2'>
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
                  d='M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253'
                />
              </svg>
              <span>{article.time_to_read}</span>
            </div>
          </div>
        </header>

        {/* Article Content */}
        <article className='prose prose-lg max-w-none dark:prose-invert mb-12'>
          <div className='bg-white/80 dark:bg-amber-100/80 backdrop-blur-sm rounded-xl shadow-lg border border-amber-200/50 dark:border-amber-300/50 p-8 md:p-12'>
            <div className='prose prose-gray dark:prose-invert max-w-none'>
              <ReactMarkdown
                components={{
                  h1: ({ children }) => (
                    <h1 className='text-2xl font-bold text-amber-900 dark:text-amber-900 mb-4'>
                      {children}
                    </h1>
                  ),
                  h2: ({ children }) => (
                    <h2 className='text-xl font-semibold text-amber-900 dark:text-amber-900 mb-3 mt-6'>
                      {children}
                    </h2>
                  ),
                  h3: ({ children }) => (
                    <h3 className='text-lg font-semibold text-amber-900 dark:text-amber-900 mb-2 mt-4'>
                      {children}
                    </h3>
                  ),
                  p: ({ children }) => (
                    <p className='text-amber-800 dark:text-amber-900 mb-4 leading-relaxed'>
                      {children}
                    </p>
                  ),
                  strong: ({ children }) => (
                    <strong className='font-semibold text-amber-900 dark:text-amber-900'>
                      {children}
                    </strong>
                  ),
                  em: ({ children }) => (
                    <em className='italic text-amber-800 dark:text-amber-900'>
                      {children}
                    </em>
                  ),
                  blockquote: ({ children }) => (
                    <blockquote className='border-l-4 border-amber-400 pl-4 italic text-amber-700 dark:text-amber-800 my-4'>
                      {children}
                    </blockquote>
                  ),
                  ul: ({ children }) => (
                    <ul className='list-disc list-inside mb-4 text-amber-800 dark:text-amber-900'>
                      {children}
                    </ul>
                  ),
                  ol: ({ children }) => (
                    <ol className='list-decimal list-inside mb-4 text-amber-800 dark:text-amber-900'>
                      {children}
                    </ol>
                  ),
                  li: ({ children }) => <li className='mb-1'>{children}</li>,
                }}
              >
                {article.content}
              </ReactMarkdown>
            </div>
          </div>
        </article>

        {/* Waitlist Section */}
        <WaitlistSection variant='detailed' />
      </div>
    </div>
  );
}
