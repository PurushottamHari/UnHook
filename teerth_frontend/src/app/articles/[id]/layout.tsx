import { Metadata } from 'next';
import { ArticleService } from '@/lib/services/article-service';
import { createPageMetadata } from '@/lib/metadata';

type Props = {
  params: Promise<{ id: string }>;
};

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { id } = await params;
  const articleService = new ArticleService();
  const article = await articleService.getArticleById(id);

  if (!article) {
    return createPageMetadata(
      'Article Not Found - Teerth',
      'The article you are looking for could not be found.'
    );
  }

  return createPageMetadata(
    `${article.title} - Teerth`,
    `Read ${article.title} on Teerth. ${article.time_to_read}.`
  );
}

export default function ArticleLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}

