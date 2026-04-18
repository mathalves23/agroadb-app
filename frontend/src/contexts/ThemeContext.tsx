/**
 * Theme Context - Dark Mode e Temas Personalizáveis
 *
 * Gerencia tema da aplicação com suporte a dark mode e temas customizados
 */
import { useState, useEffect, type ReactNode } from 'react'
import {
  ThemeContext,
  type Theme,
  type ThemeColors,
  type ThemeContextType,
  type ThemeMode,
} from '@/contexts/themeRootContext'

export type { ThemeMode, ThemeColors, Theme }

const defaultLightColors: ThemeColors = {
  primary: '#16a34a',
  secondary: '#0ea5e9',
  accent: '#8b5cf6',
  success: '#16a34a',
  warning: '#f59e0b',
  error: '#dc2626',
  info: '#0ea5e9',
}

const defaultDarkColors: ThemeColors = {
  primary: '#22c55e',
  secondary: '#38bdf8',
  accent: '#a78bfa',
  success: '#22c55e',
  warning: '#fbbf24',
  error: '#ef4444',
  info: '#38bdf8',
}

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setTheme] = useState<Theme>(() => {
    const saved = localStorage.getItem('agroadb-theme')
    if (saved) {
      try {
        return JSON.parse(saved)
      } catch {
        // Fallback
      }
    }
    return {
      mode: 'system' as ThemeMode,
      colors: defaultLightColors,
    }
  })

  const [actualMode, setActualMode] = useState<'light' | 'dark'>('light')

  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')

    const updateActualMode = () => {
      if (theme.mode === 'system') {
        setActualMode(mediaQuery.matches ? 'dark' : 'light')
      } else {
        setActualMode(theme.mode)
      }
    }

    updateActualMode()

    mediaQuery.addEventListener('change', updateActualMode)

    return () => mediaQuery.removeEventListener('change', updateActualMode)
  }, [theme.mode])

  useEffect(() => {
    const root = document.documentElement

    if (actualMode === 'dark') {
      root.classList.add('dark')
    } else {
      root.classList.remove('dark')
    }

    const colors =
      actualMode === 'dark'
        ? { ...defaultDarkColors, ...theme.colors }
        : { ...defaultLightColors, ...theme.colors }

    Object.entries(colors).forEach(([key, value]) => {
      root.style.setProperty(`--color-${key}`, value)
    })

    localStorage.setItem('agroadb-theme', JSON.stringify(theme))
  }, [theme, actualMode])

  const setThemeMode = (mode: ThemeMode) => {
    setTheme((prev) => ({ ...prev, mode }))
  }

  const setThemeColors = (colors: Partial<ThemeColors>) => {
    setTheme((prev) => ({
      ...prev,
      colors: { ...prev.colors, ...colors },
    }))
  }

  const resetTheme = () => {
    setTheme({
      mode: 'system',
      colors: defaultLightColors,
    })
  }

  const value: ThemeContextType = {
    theme,
    actualMode,
    setThemeMode,
    setThemeColors,
    resetTheme,
  }

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>
}
