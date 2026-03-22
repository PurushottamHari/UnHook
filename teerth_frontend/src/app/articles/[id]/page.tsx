'use client';

import { useParams } from 'next/navigation';
import { useAuthStore } from '@/store/auth-store';
import UserView from './user-view';
import AdminView from './admin-view';
import GuestView from './guest-view';

export default function ArticlePage() {
  const params = useParams();
  const articleId = params.id as string;
  const { user, isAuthenticated } = useAuthStore();

  if (!isAuthenticated || !user || user.role === 'guest') {
    return <GuestView articleId={articleId} />;
  }

  if (user.role === 'admin') {
    return <AdminView articleId={articleId} />;
  }

  return <UserView articleId={articleId} />;
}
