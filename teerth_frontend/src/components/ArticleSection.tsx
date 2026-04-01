"use client";

import { useState } from "react";
import { CachedNewspaperArticle } from "@/models/newspaper.model";
import ExpandableArticleCard from "./ExpandableArticleCard";

interface ArticleSectionProps {
  title: string;
  articles: CachedNewspaperArticle[];
  defaultCollapsed?: boolean;
  icon?: React.ReactNode;
  isGuestMode?: boolean;
}

export default function ArticleSection({
  title,
  articles,
  defaultCollapsed = true,
  icon,
  isGuestMode,
}: ArticleSectionProps) {
  const [isCollapsed, setIsCollapsed] = useState(defaultCollapsed);

  if (articles.length === 0) {
    return null;
  }

  return (
    <div className="bg-transparent md:bg-white/50 md:dark:bg-amber-100/50 backdrop-blur-none md:backdrop-blur-sm rounded-none md:rounded-3xl p-0 md:p-12 border-none md:border border-amber-200/50 md:dark:border-amber-300/50 shadow-none md:shadow-lg mb-6 -mx-4 sm:mx-0 snap-start snap-mt-8">
      <button
        onClick={() => setIsCollapsed(!isCollapsed)}
        className="w-full flex items-center justify-between mb-4 md:mb-6 px-4 md:px-0 text-left"
      >
        <div className="flex items-center gap-3">
          {icon && (
            <div className="text-amber-700 dark:text-amber-800">{icon}</div>
          )}
          <h2 className="text-2xl md:text-3xl font-semibold text-amber-900 dark:text-amber-900">
            {title}
          </h2>
          <span className="text-sm font-normal text-amber-600 dark:text-amber-700">
            ({articles.length})
          </span>
        </div>
        <svg
          className={`w-6 h-6 text-amber-700 dark:text-amber-800 transition-transform duration-200 ${
            isCollapsed ? "" : "rotate-180"
          }`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M19 9l-7 7-7-7"
          />
        </svg>
      </button>

      {!isCollapsed && (
        <div className="flex flex-col md:grid md:grid-cols-2 gap-4 md:gap-6 items-start h-auto overflow-visible pb-12 md:pb-0 scroll-smooth px-4 md:px-0">
          {articles.map((article) => (
            <div key={article.id} className="w-full h-full min-h-0 shrink-0 flex flex-col md:block py-2 md:py-0 snap-start snap-mt-4">
              <ExpandableArticleCard article={article} isGuestMode={isGuestMode} />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
