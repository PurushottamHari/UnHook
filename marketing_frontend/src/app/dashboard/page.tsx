import { getCachedNewspaper, CachedNewspaper } from '@/lib/cache/newspaper-cache';
import { getCachedArticle, CachedArticle } from '@/lib/cache/article-cache';
import TeerthLogo from '@/components/TeerthLogo';
import TeerthLogoIcon from '@/components/TeerthLogoIcon';
import CTAButton from '@/components/CTAButton';

interface DashboardPageProps {
  searchParams: { date?: string };
}

async function getNewspaperForDate(date?: string): Promise<CachedNewspaper | null> {
  // If no date provided, use today's date
  // If date provided, use that specific date
  const targetDate = date || new Date().toISOString().split('T')[0]; // YYYY-MM-DD format
  return getCachedNewspaper(targetDate);
}

async function getArticlesWithMetadata(articleIds: string[]): Promise<(CachedArticle | null)[]> {
  return Promise.all(articleIds.map(id => getCachedArticle(id)));
}

export default async function Dashboard({ searchParams }: DashboardPageProps) {
  const newspaper = await getNewspaperForDate(searchParams.date);
  
  // Only format date if newspaper exists
  const formattedDate = newspaper ? new Date(newspaper.date).toLocaleDateString('en-US', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  }) : null;

  // Get full article data with metadata
  const articlesWithMetadata = newspaper ? await getArticlesWithMetadata(newspaper.articles.map(a => a.id)) : [];

  return (
    <div className="min-h-screen bg-yellow-50 dark:bg-amber-50">
      <div className="w-full px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        {/* Main Content Container */}
        <div className="max-w-6xl mx-auto">
          {/* Header Section */}
          <div className="relative mb-12">
            {/* Date in top right corner - only show if newspaper exists */}
            {formattedDate && (
              <div className="absolute top-0 right-0 text-sm font-light text-amber-600 dark:text-amber-700">
                {formattedDate}
              </div>
            )}
            
            <div className="text-center">
              {/* Teerth Logo */}
              <div className="flex justify-center mb-8">
                <TeerthLogo alt="Teerth Logo" width={200} height={50} />
              </div>
              
              <h1 className="text-4xl md:text-5xl lg:text-6xl font-light text-amber-900 dark:text-amber-900 mb-8 leading-tight tracking-tight">
                Puru's Digest
              </h1>
              
              {newspaper && (
                <div className="text-center text-amber-700 dark:text-amber-800 mb-8">
                  <p className="text-lg font-medium leading-relaxed mb-2">
                    {newspaper.topics.join(' • ')}
                  </p>
                  <p className="text-sm font-light text-amber-600 dark:text-amber-700">
                    {newspaper.total_time_to_read}
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Articles Section */}
          {newspaper ? (
            <div className="bg-gradient-to-br from-amber-50/30 to-amber-100/30 dark:from-amber-100/30 dark:to-amber-200/30 rounded-3xl p-8 md:p-12 border border-amber-200/20 dark:border-amber-300/20 backdrop-blur-sm shadow-lg">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {newspaper.articles.map((article, index) => {
                const fullArticle = articlesWithMetadata[index];
                return (
                <div
                  key={article.id}
                  className="group relative bg-gradient-to-br from-amber-50 to-amber-100 dark:from-amber-100 dark:to-amber-200 rounded-xl shadow-lg border border-amber-200/50 dark:border-amber-300/50 overflow-hidden transition-all duration-300 hover:shadow-xl hover:scale-[1.01]"
                >
                  {/* Subtle Pattern Overlay */}
                  <div className="absolute inset-0 opacity-5">
                    <div className="absolute inset-0" style={{
                      backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23d97706' fill-opacity='0.1'%3E%3Ccircle cx='30' cy='30' r='2'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
                    }} />
                  </div>

                  {/* Article Title and Metadata - Always Visible */}
                  <div className="relative z-20 p-6 pb-3">
                    <h3 className="text-xl font-bold text-amber-900 dark:text-amber-900 mb-3 leading-tight">
                      {article.title}
                    </h3>
                    
                    
                    <div className="flex items-center gap-4 text-sm text-amber-700 dark:text-amber-800">
                      <span className="inline-flex items-center px-3 py-1.5 rounded-full text-xs font-medium bg-amber-200/50 text-amber-800 dark:bg-amber-300/50 dark:text-amber-900 border border-amber-300/30">
                        {article.category}
                      </span>
                      <span className="flex items-center gap-2 text-amber-600 dark:text-amber-700">
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        {article.time_to_read}
                      </span>
                    </div>
                  </div>

                  {/* Lock Overlay - Only on Content */}
                  <div className="absolute inset-0 bg-gradient-to-br from-amber-100/90 to-amber-200/90 dark:from-amber-200/90 dark:to-amber-300/90 backdrop-blur-sm flex items-center justify-center z-10 transition-all duration-300 group-hover:from-amber-200/95 group-hover:to-amber-300/95" style={{top: '120px'}}>
                    <div className="text-center p-4 w-full">
                      <div className="w-12 h-12 mx-auto mb-3 bg-gradient-to-br from-amber-200 to-amber-300 dark:from-amber-300 dark:to-amber-400 rounded-full flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform duration-300">
                        <svg className="w-6 h-6 text-amber-700 dark:text-amber-800" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                        </svg>
                      </div>
                      <h4 className="text-base font-semibold text-amber-800 dark:text-amber-900 mb-1">Subscribe to Unlock</h4>
                      <p className="text-xs text-amber-700 dark:text-amber-800 leading-relaxed">Read the full article</p>
                    </div>
                  </div>

                  {/* Article Content (Blurred) */}
                  <div className="opacity-25 p-6 pt-0">
                    <div className="text-amber-800 dark:text-amber-900 space-y-2">
                      <p className="text-base leading-relaxed">This is a preview of the article content...</p>
                      <p className="text-sm leading-relaxed">Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.</p>
                      <p className="text-sm leading-relaxed">Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p>
                    </div>
                  </div>

                  {/* Subtle Border Glow */}
                  <div className="absolute inset-0 rounded-2xl border-2 border-transparent bg-gradient-to-br from-amber-300/20 to-amber-400/20 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                </div>
                );
              })}
              </div>
            </div>
          ) : (
          <div className="text-center py-12">
            <div className="bg-amber-100 dark:bg-amber-200 rounded-xl shadow-lg border border-amber-300 dark:border-amber-400 p-8">
              <h3 className="text-xl font-semibold text-amber-900 dark:text-amber-900 mb-4">
                Your Digest is Being Prepared
              </h3>
              <p className="text-amber-800 dark:text-amber-900">
                We're curating today's most relevant articles for you. Check back later for your personalized digest.
              </p>
            </div>
          </div>
          )}

          {/* Waitlist Section */}
          <div className="mt-16 bg-gradient-to-br from-amber-100/80 to-amber-200/80 dark:from-amber-200/80 dark:to-amber-300/80 rounded-3xl shadow-2xl border border-amber-200/50 dark:border-amber-300/50 p-8 md:p-12 backdrop-blur-sm">
            <div className="flex flex-col lg:flex-row gap-8 lg:gap-16">
            {/* Left side - Text content */}
            <div className="w-full lg:w-[35%]">
              <h3 className="text-3xl md:text-4xl font-light text-amber-900 dark:text-amber-900 mb-6 leading-tight">
                Want Full Access?
              </h3>
              <p className="text-lg text-amber-800 dark:text-amber-900 mb-8 font-light leading-relaxed">
                Get your personalized daily digest with full article access:
              </p>
              <ul className="space-y-3">
                <li className="flex items-start gap-3">
                  <div className="flex-shrink-0 w-6 h-6 mt-0.5">
                    <svg className="w-6 h-6 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <span className="text-amber-800 dark:text-amber-900">No clickbait, no noise</span>
                </li>
                <li className="flex items-start gap-3">
                  <div className="flex-shrink-0 w-6 h-6 mt-0.5">
                    <svg className="w-6 h-6 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                  </div>
                  <span className="text-amber-800 dark:text-amber-900">Focused, meaningful articles</span>
                </li>
                <li className="flex items-start gap-3">
                  <div className="flex-shrink-0 w-6 h-6 mt-0.5">
                    <svg className="w-6 h-6 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                  </div>
                  <span className="text-amber-800 dark:text-amber-900">Hyper personalized</span>
                </li>
                <li className="flex items-start gap-3">
                  <div className="flex-shrink-0 w-6 h-6 mt-0.5">
                    <svg className="w-6 h-6 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <span className="text-amber-800 dark:text-amber-900">Enhance your time and attention</span>
                </li>
              </ul>
              
              {/* Teerth Logo Icon under features */}
              <div className="flex justify-center mt-6">
                <TeerthLogoIcon alt="Teerth Logo Icon" width={75} height={50} />
              </div>
            </div>

            {/* Divider */}
            <div className="hidden lg:block w-px bg-amber-300 dark:bg-amber-400"></div>

            {/* Right side - Form */}
            <div className="w-full lg:w-[60%]">
              <form className="max-w-md mx-auto lg:mx-0">
                <div className="mb-6">
                  <input
                    type="email"
                    placeholder="Enter your email address"
                    className="w-full px-6 py-4 border border-amber-300/50 dark:border-amber-400/50 rounded-2xl focus:ring-2 focus:ring-amber-500/50 focus:border-transparent dark:bg-amber-200/50 dark:text-amber-900 placeholder-amber-600/70 bg-white/50 backdrop-blur-sm text-lg font-light transition-all duration-300 hover:border-amber-400/70"
                    required
                  />
                </div>
                <div className="mb-6">
                  <textarea
                    placeholder="Would love to hear your thoughts, feedback, or questions…"
                    rows={4}
                    className="w-full px-6 py-4 border border-amber-300/50 dark:border-amber-400/50 rounded-2xl focus:ring-2 focus:ring-amber-500/50 focus:border-transparent dark:bg-amber-200/50 dark:text-amber-900 placeholder-amber-600/70 bg-white/50 backdrop-blur-sm text-lg font-light resize-none transition-all duration-300 hover:border-amber-400/70"
                  />
                </div>
                <button
                  type="submit"
                  className="w-full bg-gradient-to-r from-amber-600 to-amber-700 hover:from-amber-700 hover:to-amber-800 text-white font-light py-4 px-8 rounded-2xl transition-all duration-300 text-lg shadow-lg hover:shadow-xl transform hover:scale-[1.02] mb-4"
                >
                  Join Waitlist
                </button>
                <CTAButton 
                  href="/about" 
                  variant="secondary" 
                  size="lg"
                  className="w-full bg-amber-100 hover:bg-amber-200 text-amber-800 hover:text-amber-900 border border-amber-300 hover:border-amber-400"
                >
                  Learn More
                </CTAButton>
              </form>
            </div>
          </div>
        </div>
        </div>      </div>
    </div>
  );
}