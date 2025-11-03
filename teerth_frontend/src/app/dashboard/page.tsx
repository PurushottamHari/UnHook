import { NewspaperService } from '@/lib/services/newspaper-service';
import TeerthLogo from '@/components/TeerthLogo';
import WaitlistSection from '@/components/WaitlistSection';
import ExpandableArticleCard from '@/components/ExpandableArticleCard';
import { Metadata } from 'next';
import { CachedNewspaper } from '@/models/newspaper.model';

export const metadata: Metadata = {
  title: 'Teerth - Dashboard',
  description: 'Your daily curated digest of mindful articles and insights.',
};

async function getNewspaperForToday(): Promise<CachedNewspaper | null> {
  // Always use today's date
  const today = new Date().toISOString().split('T')[0]; // YYYY-MM-DD format
  
  const newspaperService = new NewspaperService();
  const todayNewspaper = await newspaperService.getNewspaperByDate(today);
  return todayNewspaper;
}

export default async function Dashboard() {
  const newspaper = await getNewspaperForToday();

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
            {/* Desktop: Date in top right corner */}
            {formattedDate && (
              <div className='hidden md:block absolute top-0 right-0 text-sm font-light text-amber-600 dark:text-amber-700'>
                {formattedDate}
              </div>
            )}

            <div className='text-center'>
              {/* Teerth Logo */}
              <div className='flex justify-center mb-6'>
                <TeerthLogo alt='Teerth Logo' size={200} />
              </div>

              {/* Mobile: Date below logo */}
              {formattedDate && (
                <div className='md:hidden text-center text-sm font-light text-amber-600 dark:text-amber-700 mb-4'>
                  {formattedDate}
                </div>
              )}

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
              <div className='grid grid-cols-1 lg:grid-cols-2 gap-6 items-start'>
                {newspaper.articles.map(article => (
                  <ExpandableArticleCard key={article.id} article={article} />
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