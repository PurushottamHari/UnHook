'use client';

interface ArticlesErrorProps {
  title?: string;
  message?: string;
}

export default function ArticlesError({
  title = 'Unable to Load Articles',
  message = "There was an error loading today's articles. Please try refreshing the page.",
}: ArticlesErrorProps) {
  return (
    <div className='text-center py-12'>
      <div className='bg-white/80 dark:bg-amber-100/80 backdrop-blur-sm rounded-xl shadow-lg border border-amber-200/50 dark:border-amber-300/50 p-8'>
        <h3 className='text-xl font-semibold text-amber-900 dark:text-amber-900 mb-4'>
          {title}
        </h3>
        <p className='text-amber-800 dark:text-amber-900'>
          {message}
        </p>
      </div>
    </div>
  );
}

