'use client';

import { useAuthStore } from '@/store/auth-store';

export default function Header() {
  const { user } = useAuthStore();
  // Always show header - user is always signed in
  // Logout removed - user stays signed in

  return (
    <header className="bg-white shadow-sm border-b">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center">
            <h1 className="text-xl font-semibold text-gray-900">Teerth</h1>
          </div>
          
          <div className="flex items-center space-x-4">
            <span className="text-sm text-gray-700">
              Welcome, {user?.username} ({user?.role})
            </span>
          </div>
        </div>
      </div>
    </header>
  );
}
