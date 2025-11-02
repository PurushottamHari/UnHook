import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { User } from '@/types';

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  login: (user: User) => void;
  logout: () => void;
}

// Hardcoded user - always signed in
const HARDCODED_USER: User = {
  id: '607d95f0-47ef-444c-89d2-d05f257d1265',
  username: 'user',
  role: 'customer',
  createdAt: new Date().toISOString(),
};

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: HARDCODED_USER,
      isAuthenticated: true,
      login: (user: User) => set({ user, isAuthenticated: true }),
      logout: () => set({ user: HARDCODED_USER, isAuthenticated: true }), // Keep user signed in even on logout
    }),
    {
      name: 'auth-storage',
    }
  )
);
