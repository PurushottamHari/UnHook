import { User } from '@/types';

// Hardcoded users for now
const HARDCODED_USERS: User[] = [
  {
    id: '1',
    username: 'admin',
    role: 'admin',
    createdAt: new Date().toISOString(),
  },
  {
    id: '2',
    username: 'customer',
    role: 'customer',
    createdAt: new Date().toISOString(),
  },
];

const HARDCODED_PASSWORDS: Record<string, string> = {
  admin: 'admin123',
  customer: 'customer123',
};

export function validateCredentials(username: string, password: string): User | null {
  const user = HARDCODED_USERS.find(u => u.username === username);
  
  if (!user || HARDCODED_PASSWORDS[username] !== password) {
    return null;
  }
  
  return user;
}

export function getUserById(id: string): User | null {
  return HARDCODED_USERS.find(u => u.id === id) || null;
}

export function getUserByUsername(username: string): User | null {
  return HARDCODED_USERS.find(u => u.username === username) || null;
}
