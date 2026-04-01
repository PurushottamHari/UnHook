import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { QueryProvider } from '@/components/providers/QueryProvider';
import { AuthProvider } from '@/components/providers/AuthProvider';
import { ThemeProvider } from '@/lib/theme-context';
import { createPageMetadata } from '@/lib/metadata';
import { NavigationProvider } from '@/components/navigation/NavigationProvider';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = createPageMetadata(
  'Teerth',
  ''
);

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className={inter.className}>
        <ThemeProvider>
        <QueryProvider>
          <AuthProvider>
            <NavigationProvider>
              <main className="min-h-screen bg-gray-50">
                {children}
              </main>
            </NavigationProvider>
          </AuthProvider>
        </QueryProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}