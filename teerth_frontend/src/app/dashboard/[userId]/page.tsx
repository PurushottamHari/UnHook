'use client';

import { use } from 'react';
import { useAuthStore } from '@/store/auth-store';
import AdminView from '@/app/dashboard/admin-view';
import UserView from '@/app/dashboard/user-view';
import GuestView from '@/app/dashboard/guest-view';

export default function UserDashboardPage({ params }: { params: Promise<{ userId: string }> }) {
  const { userId: spectatedUserId } = use(params);
  const { user, isAuthenticated } = useAuthStore();
  
  // If not authenticated, or if the user is visiting someone else's space
  if (!isAuthenticated || user?.id !== spectatedUserId) {
    return <GuestView userId={spectatedUserId} />;
  }

  // At this point, the user is authenticated and navigating to their own space
  if (user?.role === 'admin') {
    return <AdminView userId={user.id} />;
  }

  // Default behavior for standard logged in users visiting their own space
  return <UserView userId={user.id} />;
}
