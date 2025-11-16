'use client';

interface NoDigestMessageProps {
  message?: string;
}

export default function NoDigestMessage({
  message = 'No digest available for this date',
}: NoDigestMessageProps) {
  return (
    <div className='bg-white/50 dark:bg-amber-100/50 backdrop-blur-sm rounded-3xl p-8 md:p-12 border border-amber-200/50 dark:border-amber-300/50 shadow-lg'>
      <div className='text-center py-12'>
        <p className='text-amber-800 dark:text-amber-900 text-lg font-light'>
          {message}
        </p>
      </div>
    </div>
  );
}

