'use client';

import { useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { useAuthStore } from '@/store/auth-store';
import LoadingSpinner from '@/components/LoadingSpinner';

export default function HiddenLogin() {
  const params = useParams();
  const router = useRouter();
  const { login } = useAuthStore();

  useEffect(() => {
    if (params.id && typeof params.id === 'string') {
      login({
        id: params.id,
        username: 'Admin User',
        role: 'admin',
        createdAt: new Date().toISOString()
      });
      // Small delay to ensure state is persisted before redirecting
      setTimeout(() => {
        router.push('/dashboard');
      }, 500);
    } else {
      router.push('/dashboard');
    }
  }, [params.id, router, login]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-yellow-50 dark:bg-amber-50">
      <div className="text-center">
        <LoadingSpinner size="lg" text="Authenticating..." />
      </div>
    </div>
  );
}
