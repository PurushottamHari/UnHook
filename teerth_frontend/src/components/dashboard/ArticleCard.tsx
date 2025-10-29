import Link from 'next/link';
import { CachedNewspaperArticle } from '@/types';

interface ArticleCardProps {
  article: CachedNewspaperArticle;
}

export default function ArticleCard({ article }: ArticleCardProps) {
  return (
    <Link href={`/articles/${article.id}`} className="block">
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow duration-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-2 line-clamp-2">
          {article.title}
        </h3>
        <div className="flex items-center justify-between text-sm text-gray-500">
          <span className="bg-gray-100 px-2 py-1 rounded-full">
            {article.category}
          </span>
          <span>{article.time_to_read}</span>
        </div>
      </div>
    </Link>
  );
}
