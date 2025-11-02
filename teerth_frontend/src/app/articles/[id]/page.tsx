'use client';

import { useQuery } from '@tanstack/react-query';
import { useParams } from 'next/navigation';
import { Article } from '@/models/article.model';
import ReactMarkdown from 'react-markdown';
import { ArticleService } from '@/lib/services/article-service';

const articleService = new ArticleService();

export default function ArticlePage() {
  const params = useParams();
  const articleId = params.id as string;

  const { data: article, isLoading, error } = useQuery<Article>({
    queryKey: ['article', articleId],
    queryFn: async () => {
      const article = await articleService.getArticleById(articleId);
      if (!article) {
        throw new Error('Article not found');
      }
      return article;
    },
    enabled: !!articleId,
  });

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex items-center justify-center h-64">
          <div className="text-lg text-gray-600">Loading article...</div>
        </div>
      </div>
    );
  }

  if (error || !article) {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex items-center justify-center h-64">
          <div className="text-lg text-red-600">Article not found</div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <article className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
        <div className="p-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">
            {article.title}
          </h1>
          
          <div className="flex items-center space-x-4 text-sm text-gray-500 mb-6">
            <span className="bg-gray-100 px-3 py-1 rounded-full">
              {article.category}
            </span>
            <span>{article.time_to_read}</span>
            <span>•</span>
            <span>{article.youtube_channel}</span>
            <span>•</span>
            <span>
              {new Date(article.published_at).toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
              })}
            </span>
          </div>

          <div className="prose prose-lg max-w-none">
            <ReactMarkdown>{article.content}</ReactMarkdown>
          </div>

          <div className="mt-8 pt-6 border-t border-gray-200">
            <div className="flex items-center justify-between">
              <div className="text-sm text-gray-500">
                Source: {article.article_source}
              </div>
              {article.article_link && (
                <a
                  href={article.article_link}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-indigo-600 hover:text-indigo-800"
                >
                  View Original →
                </a>
              )}
            </div>
          </div>
        </div>
      </article>
    </div>
  );
}
