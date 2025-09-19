import Link from 'next/link';
import CTAButton from '@/components/CTAButton';

export default function NotFound() {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
      <div className="max-w-md mx-auto px-4 text-center">
        <div className="mb-8">
          <div className="w-24 h-24 bg-gray-100 dark:bg-gray-800 rounded-full flex items-center justify-center mx-auto mb-6">
            <svg className="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
            Article Not Found
          </h1>
          <p className="text-lg text-gray-600 dark:text-gray-300 mb-8">
            This article hasn't been cached yet. Use the addArticle endpoint to cache it first, 
            or browse other available articles.
          </p>
        </div>
        
        <div className="space-y-4">
          <CTAButton href="/dashboard" size="lg">
            Back to Dashboard
          </CTAButton>
          <CTAButton href="/about" variant="secondary" size="lg">
            Learn More
          </CTAButton>
        </div>
      </div>
    </div>
  );
}

