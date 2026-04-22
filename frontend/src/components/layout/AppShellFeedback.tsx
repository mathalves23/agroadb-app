import type { ReactNode } from 'react'

interface AppShellFeedbackProps {
  children: ReactNode
}

export function AppShellFeedback({ children }: AppShellFeedbackProps) {
  return <div className="[&>*:last-child]:mb-0">{children}</div>
}
