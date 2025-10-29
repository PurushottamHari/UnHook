'use client';

import { useAuthStore } from '@/store/auth-store';
import { useRouter, usePathname } from 'next/navigation';
import { useEffect } from 'react';

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuthStore();
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    const isProtectedRoute = pathname.startsWith('/dashboard') || 
                            pathname.startsWith('/articles');
    const isAuthRoute = pathname.startsWith('/login');

    if (isProtectedRoute && !isAuthenticated) {
      router.push('/login');
    } else if (isAuthRoute && isAuthenticated) {
      router.push('/dashboard');
    }
  }, [isAuthenticated, pathname, router]);

  return <>{children}</>;
}
