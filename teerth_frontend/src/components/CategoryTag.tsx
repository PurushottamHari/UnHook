'use client';

interface CategoryTagProps {
  /** The category name to display */
  category: string;
  /** Visual variant of the tag */
  variant?: 'default' | 'compact' | 'article';
  /** Additional CSS classes */
  className?: string;
}

/**
 * Reusable CategoryTag component with proper responsive sizing
 * 
 * Variants:
 * - default: Standard size for category lists (dashboard)
 * - compact: Smaller size for article cards (ExpandableArticleCard)
 * - article: Medium size for article detail pages
 * 
 * @example
 * ```tsx
 * <CategoryTag category="Technology" variant="compact" />
 * <CategoryTag category="Science" variant="default" />
 * ```
 */
export default function CategoryTag({
  category,
  variant = 'default',
  className = '',
}: CategoryTagProps) {
  // Base classes common to all variants
  const baseClasses = 'inline-flex items-center';

  // Variant-specific classes with all styling included
  const variantClasses = {
    default: 'px-2 py-1 rounded-md text-xs font-medium bg-amber-100 text-amber-800 dark:bg-amber-200 dark:text-amber-900',
    compact: 'px-1.5 py-0.5 md:px-2 rounded-full text-[8px] md:text-[10px] leading-tight font-normal bg-amber-200/50 text-amber-800 dark:bg-amber-300/50 dark:text-amber-900 border border-amber-300/30',
    article: 'px-2 py-1 rounded-md text-xs md:text-[13px] font-medium bg-amber-100 text-amber-800 dark:bg-amber-200 dark:text-amber-900',
  };

  return (
    <span className={`${baseClasses} ${variantClasses[variant]} ${className}`}>
      {category}
    </span>
  );
}

