'use client';

export function AuthProvider({ children }: { children: React.ReactNode }) {
  // Auth checks removed - user is always signed in
  return <>{children}</>;
}
