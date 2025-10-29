'use client';

import { useQuery } from '@tanstack/react-query';
import { CachedNewspaper } from '@/types';
import ArticleCard from './ArticleCard';
import { useAuthStore } from '@/store/auth-store';

export default function DashboardContent() {
  const { user } = useAuthStore();

  const { data: newspaper, isLoading, error } = useQuery<CachedNewspaper>({
    queryKey: ['newspaper', 'today'],
    queryFn: async () => {
      const response = await fetch('/api/newspapers/today');
      const data = await response.json();
      if (!data.success) {
        throw new Error(data.error);
      }
      return data.newspaper;
    },
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-lg text-gray-600">Loading today's articles...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-lg text-red-600">Error loading articles</div>
      </div>
    );
  }

  if (!newspaper) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-lg text-gray-600">No articles available today</div>
      </div>
    );
  }

  const formattedDate = new Date(newspaper.date).toLocaleDateString('en-US', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          {user?.role === 'admin' ? 'Admin Dashboard' : 'Your Daily Digest'}
        </h1>
        <p className="text-gray-600">{formattedDate}</p>
        <div className="mt-4 flex items-center space-x-4 text-sm text-gray-500">
          <span>{newspaper.articles.length} articles</span>
          <span>•</span>
          <span>{newspaper.total_time_to_read}</span>
          {newspaper.topics.length > 0 && (
            <>
              <span>•</span>
              <span>{newspaper.topics.join(', ')}</span>
            </>
          )}
        </div>
      </div>

      {/* Articles Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {newspaper.articles.map((article) => (
          <ArticleCard key={article.id} article={article} />
        ))}
      </div>

      {newspaper.articles.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-500">No articles available for today.</p>
        </div>
      )}
    </div>
  );
}
