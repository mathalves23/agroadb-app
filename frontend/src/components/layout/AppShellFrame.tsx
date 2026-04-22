import type { ReactNode } from 'react'

interface AppShellFrameProps {
  navbar: ReactNode
  sidebar: ReactNode
  mobileBackdrop?: ReactNode
  children: ReactNode
}

export function AppShellFrame({
  navbar,
  sidebar,
  mobileBackdrop,
  children,
}: AppShellFrameProps) {
  return (
    <div className="min-h-screen bg-[#f8f9fb]">
      {navbar}
      <div className="relative flex">
        {mobileBackdrop}
        {sidebar}
        {children}
      </div>
    </div>
  )
}
