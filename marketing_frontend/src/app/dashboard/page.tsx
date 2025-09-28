import {
  getCachedNewspaper,
  CachedNewspaper,
} from '@/lib/cache/newspaper-cache';
import TeerthLogo from '@/components/TeerthLogo';
import WaitlistSection from '@/components/WaitlistSection';
import { Metadata } from 'next';

interface DashboardPageProps {
  searchParams: { date?: string };
}

export const metadata: Metadata = {
  title: 'Teerth - Dashboard',
  description: 'Your daily curated digest of mindful articles and insights.',
};

async function getNewspaperForDate(
  date?: string
): Promise<CachedNewspaper | null> {
  // If no date provided, use today's date
  // If date provided, use that specific date
  const targetDate = date || new Date().toISOString().split('T')[0]; // YYYY-MM-DD format
  return getCachedNewspaper(targetDate);
}

export default async function Dashboard({ searchParams }: DashboardPageProps) {
  const resolvedSearchParams = await searchParams;
  const newspaper = await getNewspaperForDate(resolvedSearchParams.date);

  // Only format date if newspaper exists
  const formattedDate = newspaper
    ? new Date(newspaper.date).toLocaleDateString('en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      })
    : null;

  return (
    <div className='min-h-screen bg-yellow-50 dark:bg-amber-50'>
      <div className='w-full px-4 sm:px-6 lg:px-8 py-8'>
        {/* Header */}
        {/* Main Content Container */}
        <div className='max-w-6xl mx-auto'>
          {/* Header Section */}
          <div className='relative mb-12'>
            {/* Date in top right corner - only show if newspaper exists */}
            {formattedDate && (
              <div className='absolute top-0 right-0 text-sm font-light text-amber-600 dark:text-amber-700'>
                {formattedDate}
              </div>
            )}

            <div className='text-center'>
              {/* Teerth Logo */}
              <div className='flex justify-center mb-6'>
                <TeerthLogo alt='Teerth Logo' size={200} />
              </div>

              <h1 className='text-4xl md:text-5xl lg:text-6xl font-light text-amber-900 dark:text-amber-900 mb-8 leading-tight tracking-tight'>
                Puru&apos;s Digest
              </h1>

              {newspaper && (
                <div className='text-center text-amber-700 dark:text-amber-800 mb-8'>
                  <p className='text-lg font-medium leading-relaxed mb-2'>
                    {newspaper.topics.join(' • ')}
                  </p>
                  <p className='text-sm font-light text-amber-600 dark:text-amber-700'>
                    {newspaper.total_time_to_read}
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Articles Section */}
          {newspaper ? (
            <div className='bg-white/50 dark:bg-amber-100/50 backdrop-blur-sm rounded-3xl p-8 md:p-12 border border-amber-200/50 dark:border-amber-300/50 shadow-lg'>
              <div className='grid grid-cols-1 lg:grid-cols-2 gap-6'>
                {newspaper.articles.map(article => (
                  <div
                    key={article.id}
                    className='group relative bg-white/80 dark:bg-amber-100/80 backdrop-blur-sm rounded-xl shadow-lg border border-amber-200/50 dark:border-amber-300/50 overflow-hidden transition-all duration-300 hover:shadow-xl hover:scale-[1.01]'
                  >
                    {/* Subtle Pattern Overlay */}
                    <div className='absolute inset-0 opacity-5'>
                      <div
                        className='absolute inset-0'
                        style={{
                          backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23d97706' fill-opacity='0.1'%3E%3Ccircle cx='30' cy='30' r='2'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
                        }}
                      />
                    </div>

                    {/* Article Title and Metadata - Always Visible */}
                    <div className='relative z-20 p-6 pb-3'>
                      <h3 className='text-xl font-bold text-amber-900 dark:text-amber-900 mb-3 leading-tight'>
                        {article.title}
                      </h3>

                      <div className='flex items-center gap-4 text-sm text-amber-700 dark:text-amber-800'>
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
                    </div>

                    {/* Lock Overlay - Only on Content */}
                    <div
                      className='absolute inset-0 bg-gradient-to-br from-amber-100/90 to-amber-200/90 dark:from-amber-200/90 dark:to-amber-300/90 backdrop-blur-sm flex items-center justify-center z-10 transition-all duration-300 group-hover:from-amber-200/95 group-hover:to-amber-300/95'
                      style={{ top: '120px' }}
                    >
                      <div className='text-center p-4 w-full'>
                        <div className='w-12 h-12 mx-auto mb-3 bg-gradient-to-br from-amber-200 to-amber-300 dark:from-amber-300 dark:to-amber-400 rounded-full flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform duration-300'>
                          <svg
                            className='w-6 h-6 text-amber-700 dark:text-amber-800'
                            fill='none'
                            stroke='currentColor'
                            viewBox='0 0 24 24'
                          >
                            <path
                              strokeLinecap='round'
                              strokeLinejoin='round'
                              strokeWidth={2}
                              d='M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z'
                            />
                          </svg>
                        </div>
                        <h4 className='text-base font-semibold text-amber-800 dark:text-amber-900 mb-1'>
                          Subscribe to Unlock
                        </h4>
                        <p className='text-xs text-amber-700 dark:text-amber-800 leading-relaxed'>
                          Read the full article
                        </p>
                      </div>
                    </div>

                    {/* Article Content (Blurred) */}
                    <div className='opacity-25 p-6 pt-0'>
                      <div className='text-amber-800 dark:text-amber-900 space-y-2'>
                        <p className='text-base leading-relaxed'>
                          This is a preview of the article content...
                        </p>
                        <p className='text-sm leading-relaxed'>
                          Lorem ipsum dolor sit amet, consectetur adipiscing
                          elit. Sed do eiusmod tempor incididunt ut labore et
                          dolore magna aliqua.
                        </p>
                        <p className='text-sm leading-relaxed'>
                          Ut enim ad minim veniam, quis nostrud exercitation
                          ullamco laboris nisi ut aliquip ex ea commodo
                          consequat.
                        </p>
                      </div>
                    </div>

                    {/* Subtle Border Glow */}
                    <div className='absolute inset-0 rounded-2xl border-2 border-transparent bg-gradient-to-br from-amber-300/20 to-amber-400/20 opacity-0 group-hover:opacity-100 transition-opacity duration-300' />
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className='text-center py-12'>
              <div className='bg-white/80 dark:bg-amber-100/80 backdrop-blur-sm rounded-xl shadow-lg border border-amber-200/50 dark:border-amber-300/50 p-8'>
                <h3 className='text-xl font-semibold text-amber-900 dark:text-amber-900 mb-4'>
                  Your Digest is Being Prepared
                </h3>
                <p className='text-amber-800 dark:text-amber-900'>
                  We&apos;re curating today&apos;s most relevant articles for
                  you. Check back later for your personalized digest.
                </p>
              </div>
            </div>
          )}

          {/* Waitlist Section */}
          <WaitlistSection variant='detailed' />
        </div>
      </div>
    </div>
  );
}
