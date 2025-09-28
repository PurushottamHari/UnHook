import Link from 'next/link';

interface InfoIconProps {
  className?: string;
}

export default function InfoIcon({ className = '' }: InfoIconProps) {
  return (
    <Link
      href='/about'
      className={`inline-flex items-center justify-center w-8 h-8 rounded-full bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors ${className}`}
      aria-label='Learn more about Teerth'
    >
      <svg
        className='w-4 h-4 text-gray-600 dark:text-gray-400'
        fill='none'
        stroke='currentColor'
        viewBox='0 0 24 24'
      >
        <path
          strokeLinecap='round'
          strokeLinejoin='round'
          strokeWidth={2}
          d='M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z'
        />
      </svg>
    </Link>
  );
}
