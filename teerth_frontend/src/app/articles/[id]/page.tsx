import { Metadata } from 'next';
import { ArticleService } from '@/lib/services/article-service';
import ArticleClientWrapper from './ArticleClientWrapper';
import { createPageMetadata } from '@/lib/metadata';

interface ArticlePageProps {
  params: Promise<{ id: string }>;
}

export async function generateMetadata({ params }: ArticlePageProps): Promise<Metadata> {
  const { id } = await params;
  const articleService = new ArticleService();
  const article = await articleService.getArticleById(id);

  if (!article) {
    return createPageMetadata('Article Not Found | Teerth', 'The requested article could not be found.');
  }

  const title = article.title;
  const description = article.summary ?? "";
  const canonicalUrl = `https://www.teerth.xyz/articles/${id}`;
  const oEmbedUrl = `https://www.teerth.xyz/api/oembed?url=${encodeURIComponent(canonicalUrl)}`;

  return createPageMetadata(
    `${title} | Teerth`,
    description,
    {
      alternates: {
        canonical: canonicalUrl,
        types: {
          'application/json+oEmbed': oEmbedUrl,
        },
      },
      openGraph: {
        title: title,
        description: description,
        url: canonicalUrl,
        siteName: 'Teerth',
        type: 'article',
        images: [
          {
            url: `/articles/${id}/opengraph-image`,
            width: 1200,
            height: 630,
            alt: title,
          },
        ],
      },
      twitter: {
        card: 'summary_large_image',
        title: title,
        description: description,
        images: [`/articles/${id}/twitter-image`],
      },
    }
  );
}

export default async function ArticlePage({ params }: ArticlePageProps) {
  const { id } = await params;
  return <ArticleClientWrapper articleId={id} />;
}
