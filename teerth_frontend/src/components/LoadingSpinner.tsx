'use client';

interface LoadingSpinnerProps {
  /**
   * Size of the spinner
   * @default 'md'
   */
  size?: 'sm' | 'md' | 'lg';
  /**
   * Additional CSS classes
   */
  className?: string;
  /**
   * Text to display below the spinner
   */
  text?: string;
}

/**
 * Theme-aware loading spinner component
 * Uses amber colors to match the Teerth design system
 * Supports both light and dark modes
 */
export default function LoadingSpinner({ 
  size = 'md', 
  className = '',
  text 
}: LoadingSpinnerProps) {
  // Size mappings for spinner dimensions
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
  };

  // Border width based on size
  const borderWidth = {
    sm: 'border-2',
    md: 'border-[3px]',
    lg: 'border-4',
  };

  return (
    <div className={`flex flex-col items-center justify-center ${className}`}>
      <div
        className={`
          ${sizeClasses[size]}
          ${borderWidth[size]}
          border-amber-200 dark:border-amber-300
          border-t-amber-600 dark:border-t-amber-700
          rounded-full
          animate-spin
        `}
        role="status"
        aria-label="Loading"
      >
        <span className="sr-only">Loading...</span>
      </div>
      {text && (
        <p className="mt-3 text-sm text-amber-700 dark:text-amber-800">
          {text}
        </p>
      )}
    </div>
  );
}

