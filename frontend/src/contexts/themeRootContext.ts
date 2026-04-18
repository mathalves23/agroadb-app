import { createContext } from 'react'

export type ThemeMode = 'light' | 'dark' | 'system'

export interface ThemeColors {
  primary: string
  secondary: string
  accent: string
  success: string
  warning: string
  error: string
  info: string
}

export interface Theme {
  mode: ThemeMode
  colors: ThemeColors
}

export interface ThemeContextType {
  theme: Theme
  actualMode: 'light' | 'dark'
  setThemeMode: (mode: ThemeMode) => void
  setThemeColors: (colors: Partial<ThemeColors>) => void
  resetTheme: () => void
}

export const ThemeContext = createContext<ThemeContextType | undefined>(undefined)
