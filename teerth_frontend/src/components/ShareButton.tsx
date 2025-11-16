interface ShareButtonProps {
  /** Click handler for the share button */
  onClick: () => void;
  /** Size variant of the button */
  size?: 'sm' | 'md' | 'lg';
  /** Custom aria-label for accessibility */
  ariaLabel?: string;
  /** Custom title/tooltip text */
  title?: string;
  /** Additional CSS classes */
  className?: string;
  /** Whether to show the icon */
  showIcon?: boolean;
  /** Custom icon component (overrides default icon) */
  icon?: React.ReactNode;
}

/**
 * Reusable share button component with customizable size and styling.
 * 
 * @example
 * ```tsx
 * <ShareButton onClick={handleShare} size="md" />
 * ```
 */
export default function ShareButton({
  onClick,
  size = 'md',
  ariaLabel = 'Share',
  title = 'Share',
  className = '',
  showIcon = true,
  icon,
}: ShareButtonProps) {
  const sizeClasses = {
    sm: 'p-1.5',
    md: 'p-2',
    lg: 'p-3',
  };

  const iconSizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-5 h-5',
    lg: 'w-6 h-6',
  };

  const defaultIcon = (
    <svg
      className={`${iconSizeClasses[size]} text-amber-700 dark:text-amber-800`}
      fill="none"
      stroke="currentColor"
      viewBox="0 0 24 24"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z"
      />
    </svg>
  );

  return (
    <button
      onClick={onClick}
      className={`${sizeClasses[size]} rounded-full bg-white/80 dark:bg-amber-100/80 backdrop-blur-sm border border-amber-200/50 dark:border-amber-300/50 hover:bg-amber-50 dark:hover:bg-amber-200/80 transition-all duration-200 shadow-md hover:shadow-lg ${className}`}
      aria-label={ariaLabel}
      title={title}
    >
      {showIcon && (icon || defaultIcon)}
    </button>
  );
}

