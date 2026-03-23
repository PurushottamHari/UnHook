'use client';

import { createContext, useContext, useEffect, useState } from 'react';
import { usePathname } from 'next/navigation';

interface NavigationContextType {
  /** Whether the user has visited at least one other teerth page before the current one in this session */
  hasPreviousTeerthPage: boolean;
  /** The stack of paths visited in this session */
  history: string[];
}

const NavigationContext = createContext<NavigationContextType>({
  hasPreviousTeerthPage: false,
  history: [],
});

export const useNavigation = () => useContext(NavigationContext);

/**
 * NavigationProvider tracks internal page transitions to determine if a "Back" button should be shown.
 * This ensures the back button only appears if there's actually a previous within-app page to return to.
 */
export function NavigationProvider({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const [history, setHistory] = useState<string[]>([]);

  useEffect(() => {
    setHistory((prev) => {
      // Don't add if it's the same as the last path (e.g. hash changes or just re-renders)
      if (prev.length > 0 && prev[prev.length - 1] === pathname) {
        return prev;
      }
      return [...prev, pathname];
    });
  }, [pathname]);

  const hasPreviousTeerthPage = history.length > 1;

  return (
    <NavigationContext.Provider value={{ hasPreviousTeerthPage, history }}>
      {children}
    </NavigationContext.Provider>
  );
}
