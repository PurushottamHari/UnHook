import Link from 'next/link';

interface BreadcrumbProps {
  /** The URL to navigate to when the breadcrumb is clicked */
  href: string;
  /** The text label to display in the breadcrumb */
  label: string;
  /** Optional additional CSS classes */
  className?: string;
}

/**
 * Breadcrumb navigation component for navigating back to a parent page.
 * 
 * @example
 * ```tsx
 * <Breadcrumb href="/dashboard" label="Puru's Digest" />
 * ```
 */
export default function Breadcrumb({
  href,
  label,
  className = '',
}: BreadcrumbProps) {
  return (
    <nav className={`mb-8 ${className}`}>
      <Link
        href={href}
        className="inline-flex items-center text-sm text-amber-700 dark:text-amber-800 hover:text-amber-900 dark:hover:text-amber-900 transition-colors"
      >
        <svg
          className="w-4 h-4 mr-2"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M15 19l-7-7 7-7"
          />
        </svg>
        {label}
      </Link>
    </nav>
  );
}

