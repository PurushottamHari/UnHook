import ReactMarkdown from 'react-markdown';
import ArticleLikeDislike from '@/components/article/ArticleLikeDislike';
import CTAButton from '@/components/CTAButton';

interface ArticleContentProps {
  /** The markdown content of the article */
  content: string;
  /** The article ID for like/dislike functionality */
  articleId: string;
  /** Handler function for share button click */
  onShare: () => void;
  /** Optional additional CSS classes */
  className?: string;
}

/**
 * Article content component that displays markdown content along with
 * like/dislike buttons, AI enhanced section, and share CTA.
 * 
 * @example
 * ```tsx
 * <ArticleContent
 *   content="# Article Title\n\nArticle content..."
 *   articleId="123"
 *   onShare={handleShare}
 * />
 * ```
 */
export default function ArticleContent({
  content,
  articleId,
  onShare,
  className = '',
}: ArticleContentProps) {

  return (
    <article className={`prose prose-lg max-w-none dark:prose-invert mb-12 pb-24 ${className}`}>
      <div className="relative bg-white/80 dark:bg-amber-100/80 backdrop-blur-sm rounded-xl shadow-lg border border-amber-200/50 dark:border-amber-300/50 p-6 md:p-8 lg:p-10">
        <div className="relative prose dark:prose-invert max-w-3xl md:max-w-4xl lg:max-w-5xl xl:max-w-6xl mx-auto">
          <ReactMarkdown
            components={{
              h1: ({ children }) => (
                <h1 className="text-2xl font-bold text-amber-900 dark:text-amber-900 mb-4">
                  {children}
                </h1>
              ),
              h2: ({ children }) => (
                <h2 className="text-xl font-semibold text-amber-900 dark:text-amber-900 mb-3 mt-6">
                  {children}
                </h2>
              ),
              h3: ({ children }) => (
                <h3 className="text-lg font-semibold text-amber-900 dark:text-amber-900 mb-2 mt-4">
                  {children}
                </h3>
              ),
              h4: ({ children }) => (
                <h4 className="text-base font-semibold text-amber-900 dark:text-amber-900 mb-2 mt-4">
                  {children}
                </h4>
              ),
              h5: ({ children }) => (
                <h5 className="text-sm font-semibold text-amber-900 dark:text-amber-900 mb-2 mt-3">
                  {children}
                </h5>
              ),
              h6: ({ children }) => (
                <h6 className="text-sm font-semibold text-amber-900 dark:text-amber-900 mb-2 mt-3">
                  {children}
                </h6>
              ),
              p: ({ children }) => (
                <p className="text-amber-800 dark:text-amber-900 mb-4 leading-relaxed">
                  {children}
                </p>
              ),
              strong: ({ children }) => (
                <strong className="font-semibold text-amber-900 dark:text-amber-900">
                  {children}
                </strong>
              ),
              em: ({ children }) => (
                <em className="italic text-amber-800 dark:text-amber-900">
                  {children}
                </em>
              ),
              blockquote: ({ children }) => (
                <blockquote className="border-l-4 border-amber-400 pl-4 italic text-amber-700 dark:text-amber-800 my-4">
                  {children}
                </blockquote>
              ),
              ul: ({ children }) => (
                <ul className="list-disc list-outside mb-4 text-amber-800 dark:text-amber-900 pl-6 space-y-2">
                  {children}
                </ul>
              ),
              ol: ({ children }) => (
                <ol className="list-decimal list-outside mb-4 text-amber-800 dark:text-amber-900 pl-6 space-y-2">
                  {children}
                </ol>
              ),
              li: ({ children }) => <li className="mb-2 leading-relaxed">{children}</li>,
            }}
          >
            {content}
          </ReactMarkdown>
        </div>

        {/* Section 1: Like/Dislike CTAs */}
        <section className="mt-4 pt-2">
          <div className="max-w-3xl md:max-w-4xl lg:max-w-5xl xl:max-w-6xl mx-auto">
            <ArticleLikeDislike
              articleId={articleId}
              position="inline"
              showOnMobile={true}
              mobilePosition="bottom-right"
            />
          </div>
        </section>

        {/* Section 2: AI Enhanced */}
        <section
          className="mt-8 pt-6 pb-6 border-t border-b border-amber-200 dark:border-amber-300 flex justify-center"
          data-ai-enhanced-section
        >
          <div className="relative group">
            <div className="flex items-center gap-2 text-xs text-amber-600 dark:text-amber-700 cursor-help">
              <svg
                className="w-4 h-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
                />
              </svg>
              <span className="italic">AI Enhanced</span>
            </div>

            {/* Tooltip */}
            <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 w-72 sm:w-80 max-w-[calc(100vw-2rem)] p-3 bg-amber-900 dark:bg-amber-800 text-amber-50 text-xs rounded-lg shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-10 pointer-events-none">
              <p className="leading-relaxed">
                Artificial intelligence (AI) has been used solely to structure and present the content in a clear and non-sensationalized manner. No new information has been generated beyond what is available in the original source material.
              </p>
              {/* Tooltip arrow */}
              <div className="absolute top-full left-1/2 transform -translate-x-1/2 -mt-1">
                <div className="w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-amber-900 dark:border-t-amber-800"></div>
              </div>
            </div>
          </div>
        </section>

        {/* Section 3: Share CTA */}
        <section className="mt-8 pt-6 flex justify-center">
          <div className="max-w-md text-center">
            <h3 className="text-xl md:text-2xl font-semibold text-amber-900 dark:text-amber-900 mb-4">
              Found this useful?<br />
              Share it with someone who might too.
            </h3>
            <CTAButton onClick={onShare} variant="primary" size="md">
              <svg
                className="w-5 h-5 mr-2"
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
              Share Article
            </CTAButton>
          </div>
        </section>
      </div>
    </article>
  );
}

