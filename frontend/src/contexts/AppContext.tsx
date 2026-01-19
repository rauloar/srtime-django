import { createContext, useState, useCallback, type ReactNode, useEffect } from 'react';

export type Theme = 'dark' | 'light';

interface AppContextType {
  sidebarOpen: boolean;
  toggleSidebar: () => void;
  theme: Theme;
  setTheme: (theme: Theme) => void;
  isLoading: boolean;
  setIsLoading: (loading: boolean) => void;
}

export const AppContext = createContext<AppContextType | undefined>(undefined);

const THEME_STORAGE_KEY = 'app-theme';

export const AppProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [theme, setThemeState] = useState<Theme>(() => {
    if (typeof window === 'undefined') return 'light';
    const stored = localStorage.getItem(THEME_STORAGE_KEY);
    if (stored === 'dark' || stored === 'light') return stored;

    // Fall back to system preference when no stored theme exists
    const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    return prefersDark ? 'dark' : 'light';
  });
  const [hasStoredPreference] = useState<boolean>(() => {
    if (typeof window === 'undefined') return false;
    return localStorage.getItem(THEME_STORAGE_KEY) === 'dark' || localStorage.getItem(THEME_STORAGE_KEY) === 'light';
  });
  const [isLoading, setIsLoadingState] = useState(false);

  const toggleSidebar = useCallback(() => {
    setSidebarOpen(prev => !prev);
  }, []);

  const setTheme = useCallback((newTheme: Theme) => {
    setThemeState(newTheme);
  }, []);

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem(THEME_STORAGE_KEY, theme);
  }, [theme]);

  useEffect(() => {
    if (hasStoredPreference || typeof window === 'undefined' || !window.matchMedia) return;

    const media = window.matchMedia('(prefers-color-scheme: dark)');
    const handleChange = (event: MediaQueryListEvent) => {
      // Only auto-switch when user has not explicitly chosen a theme
      if (!localStorage.getItem(THEME_STORAGE_KEY)) {
        setThemeState(event.matches ? 'dark' : 'light');
      }
    };

    media.addEventListener('change', handleChange);
    return () => media.removeEventListener('change', handleChange);
  }, [hasStoredPreference]);

  const setIsLoading = useCallback((loading: boolean) => {
    setIsLoadingState(loading);
  }, []);

  const value: AppContextType = {
    sidebarOpen,
    toggleSidebar,
    theme,
    setTheme,
    isLoading,
    setIsLoading,
  };

  return (
    <AppContext.Provider value={value}>
      {children}
    </AppContext.Provider>
  );
};
