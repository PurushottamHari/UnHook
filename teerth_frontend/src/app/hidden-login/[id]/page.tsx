'use client';

import { useEffect, useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { useAuthStore } from '@/store/auth-store';
import LoadingSpinner from '@/components/LoadingSpinner';

export default function HiddenLogin() {
  const params = useParams();
  const router = useRouter();
  const { login } = useAuthStore();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const authenticate = async () => {
      const userId = params.id;
      
      if (!userId || typeof userId !== 'string') {
        setError('Invalid User ID');
        return;
      }

      try {
        const response = await fetch(`/api/users/${userId}`);
        const data = await response.json();

        if (response.ok && data.success) {
          login({
            id: data.user.id,
            name: data.user.name,
            username: data.user.username,
            role: data.user.role,
            createdAt: data.user.createdAt
          });

          // Small delay to ensure state is persisted before redirecting
          setTimeout(() => {
            router.push('/dashboard');
          }, 500);
        } else {
          setError('Login Failed: User not found');
        }
      } catch (err) {
        console.error('Authentication error:', err);
        setError('Login Failed: Internal server error');
      }
    };

    authenticate();
  }, [params.id, router, login]);

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-yellow-50 dark:bg-amber-50">
        <div className="text-center p-8 bg-white dark:bg-amber-100 rounded-2xl shadow-xl border border-red-200">
          <div className="text-red-600 text-5xl mb-4">⚠️</div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-amber-900 mb-2">{error}</h1>
          <p className="text-gray-600 dark:text-amber-800 mb-6">We couldn't find a user with that ID.</p>
          <button 
            onClick={() => router.push('/dashboard')}
            className="px-6 py-2 bg-amber-600 text-white rounded-lg hover:bg-amber-700 transition-colors"
          >
            Go to Dashboard
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-yellow-50 dark:bg-amber-50">
      <div className="text-center">
        <LoadingSpinner size="lg" text="Authenticating..." />
      </div>
    </div>
  );
}
