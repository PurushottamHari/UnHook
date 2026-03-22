import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { User } from '@/types';

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  login: (user: User) => void;
  logout: () => void;
}

// Default guest user
const GUEST_USER: User = {
  id: 'guest',
  username: 'Guest',
  role: 'guest',
  createdAt: new Date().toISOString(),
};

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: GUEST_USER,
      isAuthenticated: false,
      login: (user: User) => set({ user, isAuthenticated: true }),
      logout: () => set({ user: GUEST_USER, isAuthenticated: false }),
    }),
    {
      name: 'auth-storage',
    }
  )
);
