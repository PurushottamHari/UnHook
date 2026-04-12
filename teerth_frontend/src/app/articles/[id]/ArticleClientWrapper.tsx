'use client';

import { useAuthStore } from '@/store/auth-store';
import UserView from './user-view';
import AdminView from './admin-view';
import GuestView from './guest-view';

interface ArticleClientWrapperProps {
  articleId: string;
}

export default function ArticleClientWrapper({ articleId }: ArticleClientWrapperProps) {
  const { user, isAuthenticated } = useAuthStore();

  if (!isAuthenticated || !user || user.role === 'guest') {
    return <GuestView articleId={articleId} />;
  }

  if (user.role === 'admin') {
    return <AdminView articleId={articleId} />;
  }

  return <UserView articleId={articleId} />;
}
