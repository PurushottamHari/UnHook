import { createPageMetadata } from '@/lib/metadata';

export const metadata = createPageMetadata(
  'Teerth - Dashboard',
  'Daily reads that sharpen focus instead of scatter it.'
);

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}


