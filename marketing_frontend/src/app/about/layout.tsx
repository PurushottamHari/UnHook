import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Teerth - About',
  description:
    "Learn about Teerth's mission to help you reclaim your attention and build better digital habits through curated, mindful content.",
};

export default function AboutLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return children;
}
