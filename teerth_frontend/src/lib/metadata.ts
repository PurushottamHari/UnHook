import { Metadata } from 'next';

/**
 * Shared icon configuration for all pages
 */
const sharedIcons = {
  icon: [
    { url: '/icon.png', sizes: '32x32', type: 'image/png' },
    { url: '/favicon.ico', sizes: 'any' },
  ],
  apple: '/icon.png',
};

/**
 * Creates metadata with shared icons configuration
 * 
 * @param title - The page title
 * @param description - The page description
 * @param additionalMetadata - Optional additional metadata to merge
 * @returns Metadata object with icons included
 * 
 * @example
 * ```tsx
 * export const metadata = createPageMetadata(
 *   'Teerth - About',
 *   'Learn about Teerth...'
 * );
 * ```
 */
export function createPageMetadata(
  title: string,
  description: string,
  additionalMetadata?: Partial<Metadata>
): Metadata {
  return {
    title,
    description,
    icons: sharedIcons,
    ...additionalMetadata,
  };
}

