import { createContext } from 'react'
import type { ToastMessage } from '@/components/toastTypes'

export interface ToastContextValue {
  showToast: (toast: Omit<ToastMessage, 'id'>) => void
  success: (message: string, title?: string) => void
  error: (message: string, title?: string) => void
  warning: (message: string, title?: string) => void
  info: (message: string, title?: string) => void
}

export const ToastContext = createContext<ToastContextValue | undefined>(undefined)
