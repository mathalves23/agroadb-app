/**
 * Theme Context - Dark Mode e Temas Personalizáveis
 * 
 * Gerencia tema da aplicação com suporte a dark mode e temas customizados
 */
import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

// Tipos de tema
export type ThemeMode = 'light' | 'dark' | 'system';

export interface ThemeColors {
  primary: string;
  secondary: string;
  accent: string;
  success: string;
  warning: string;
  error: string;
  info: string;
}

export interface Theme {
  mode: ThemeMode;
  colors: ThemeColors;
}

interface ThemeContextType {
  theme: Theme;
  actualMode: 'light' | 'dark'; // Modo real após resolver 'system'
  setThemeMode: (mode: ThemeMode) => void;
  setThemeColors: (colors: Partial<ThemeColors>) => void;
  resetTheme: () => void;
}

// Temas padrão
const defaultLightColors: ThemeColors = {
  primary: '#16a34a',    // green-600
  secondary: '#0ea5e9',  // sky-500
  accent: '#8b5cf6',     // violet-500
  success: '#16a34a',
  warning: '#f59e0b',
  error: '#dc2626',
  info: '#0ea5e9'
};

const defaultDarkColors: ThemeColors = {
  primary: '#22c55e',    // green-500
  secondary: '#38bdf8',  // sky-400
  accent: '#a78bfa',     // violet-400
  success: '#22c55e',
  warning: '#fbbf24',
  error: '#ef4444',
  info: '#38bdf8'
};

// Context
const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

// Provider
export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setTheme] = useState<Theme>(() => {
    // Carregar do localStorage
    const saved = localStorage.getItem('agroadb-theme');
    if (saved) {
      try {
        return JSON.parse(saved);
      } catch {
        // Fallback
      }
    }
    return {
      mode: 'system' as ThemeMode,
      colors: defaultLightColors
    };
  });

  const [actualMode, setActualMode] = useState<'light' | 'dark'>('light');

  // Detectar preferência do sistema
  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    
    const updateActualMode = () => {
      if (theme.mode === 'system') {
        setActualMode(mediaQuery.matches ? 'dark' : 'light');
      } else {
        setActualMode(theme.mode);
      }
    };

    updateActualMode();
    
    // Listener para mudanças na preferência do sistema
    mediaQuery.addEventListener('change', updateActualMode);
    
    return () => mediaQuery.removeEventListener('change', updateActualMode);
  }, [theme.mode]);

  // Aplicar tema ao DOM
  useEffect(() => {
    const root = document.documentElement;
    
    // Aplicar modo (dark/light)
    if (actualMode === 'dark') {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }

    // Aplicar cores customizadas como CSS variables
    const colors = actualMode === 'dark' 
      ? { ...defaultDarkColors, ...theme.colors }
      : { ...defaultLightColors, ...theme.colors };

    Object.entries(colors).forEach(([key, value]) => {
      root.style.setProperty(`--color-${key}`, value);
    });

    // Salvar no localStorage
    localStorage.setItem('agroadb-theme', JSON.stringify(theme));
  }, [theme, actualMode]);

  const setThemeMode = (mode: ThemeMode) => {
    setTheme(prev => ({ ...prev, mode }));
  };

  const setThemeColors = (colors: Partial<ThemeColors>) => {
    setTheme(prev => ({
      ...prev,
      colors: { ...prev.colors, ...colors }
    }));
  };

  const resetTheme = () => {
    setTheme({
      mode: 'system',
      colors: defaultLightColors
    });
  };

  return (
    <ThemeContext.Provider
      value={{
        theme,
        actualMode,
        setThemeMode,
        setThemeColors,
        resetTheme
      }}
    >
      {children}
    </ThemeContext.Provider>
  );
}

// Hook
export function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider');
  }
  return context;
}
