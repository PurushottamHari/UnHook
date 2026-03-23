import Link from 'next/link';

import { useNavigation } from './NavigationProvider';

interface BreadcrumbProps {
  /** The URL to navigate to when the breadcrumb is clicked (optional if onClick is provided) */
  href?: string;
  /** Function to execute when clicked */
  onClick?: () => void;
  /** The text label to display in the breadcrumb */
  label: string;
  /** Optional additional CSS classes */
  className?: string;
  /** Whether to hide the label on mobile (defaults to false) */
  hideLabelOnMobile?: boolean;
  /** Whether the current page is the main dashboard */
  isDashboard?: boolean;
}

/**
 * Breadcrumb navigation component for navigating back to a parent page.
 */
export default function Breadcrumb({
  href,
  onClick,
  label,
  className = '',
  hideLabelOnMobile = false,
  isDashboard = false,
}: BreadcrumbProps) {
  const { hasPreviousTeerthPage } = useNavigation();

  // Don't show breadcrumb on the main dashboard,
  // or if the user didn't land from a previously visited teerth page
  if (isDashboard || !hasPreviousTeerthPage) {
    return null;
  }

  const content = (
    <>
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
      <span className={hideLabelOnMobile ? 'hidden sm:inline' : ''}>{label}</span>
    </>
  );

  const buttonClass = "inline-flex items-center text-sm text-amber-700 dark:text-amber-800 hover:text-amber-900 dark:hover:text-amber-900 transition-colors bg-transparent border-none p-0 cursor-pointer";

  if (href) {
    return (
      <nav className={`mb-8 ${className}`}>
        <Link href={href} className={buttonClass}>
          {content}
        </Link>
      </nav>
    );
  }

  return (
    <nav className={`mb-8 ${className}`}>
      <button onClick={onClick} className={buttonClass}>
        {content}
      </button>
    </nav>
  );
}
