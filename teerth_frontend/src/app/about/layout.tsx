import { createPageMetadata } from '@/lib/metadata';

export const metadata = createPageMetadata(
  'Teerth - About',
  "Learn about Teerth's mission to help you reclaim your attention and build better digital habits through curated, mindful content."
);

export default function AboutLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return children;
}

