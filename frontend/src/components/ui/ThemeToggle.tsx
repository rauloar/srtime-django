import React from 'react';
import { Moon, Sun } from 'lucide-react';
import type { Theme } from '../../contexts/AppContext';

interface ThemeToggleProps {
  theme: Theme;
  onToggle: () => void;
}

export const ThemeToggle: React.FC<ThemeToggleProps> = ({ theme, onToggle }) => {
  const isLight = theme === 'light';
  const label = isLight ? 'Activar modo oscuro' : 'Activar modo claro';

  return (
    <button
      type="button"
      className="theme-toggle-btn"
      onClick={onToggle}
      aria-label={label}
      title={label}
    >
      {isLight ? <Moon size={18} /> : <Sun size={18} />}
    </button>
  );
};
