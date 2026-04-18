export type ToastType = 'success' | 'error' | 'warning' | 'info'

export interface ToastMessage {
  id: string
  type: ToastType
  title?: string
  message: string
  duration?: number
  action?: {
    label: string
    onClick: () => void
  }
}
