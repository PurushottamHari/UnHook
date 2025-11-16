interface ArticleTitleProps {
  /** The title text to display */
  title: string;
  /** Optional additional CSS classes */
  className?: string;
}

/**
 * Article title component for displaying article headings.
 * 
 * @example
 * ```tsx
 * <ArticleTitle title="My Article Title" />
 * ```
 */
export default function ArticleTitle({
  title,
  className = '',
}: ArticleTitleProps) {
  return (
    <h1
      className={`text-3xl md:text-4xl lg:text-5xl font-bold text-amber-900 dark:text-amber-900 mb-6 leading-tight ${className}`}
    >
      {title}
    </h1>
  );
}

