import { useEffect, useState } from 'react'
import { Outlet, useLocation } from 'react-router-dom'
import { AppShellFeedback } from './layout/AppShellFeedback'
import { AppShellFrame } from './layout/AppShellFrame'
import Navbar from './Navbar'
import Sidebar from './Sidebar'
import IntegrationRetryBanner from './IntegrationRetryBanner'
import SkipToMainLink from './SkipToMainLink'
import Breadcrumbs from './Breadcrumbs'
import ConnectionStatus from './ConnectionStatus'
import PwaInstallBanner from './PwaInstallBanner'
import PwaUpdatePrompt from './PwaUpdatePrompt'
import SessionExpiryBanner from './SessionExpiryBanner'
import GlobalCommandPalette from './GlobalCommandPalette'

export default function Layout() {
  const location = useLocation()
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false)

  useEffect(() => {
    setMobileSidebarOpen(false)
  }, [location.pathname])

  useEffect(() => {
    window.scrollTo(0, 0)
  }, [location.pathname])

  return (
    <>
      <SkipToMainLink />
      <AppShellFrame
        navbar={
          <Navbar
            onToggleMobileSidebar={() => setMobileSidebarOpen((o) => !o)}
            mobileSidebarOpen={mobileSidebarOpen}
          />
        }
        mobileBackdrop={
          mobileSidebarOpen ? (
            <button
              type="button"
              className="fixed inset-0 z-30 bg-gray-900/40 md:hidden"
              aria-label="Fechar menu lateral"
              onClick={() => setMobileSidebarOpen(false)}
            />
          ) : null
        }
        sidebar={
          <Sidebar
            mobileOpen={mobileSidebarOpen}
            onNavigate={() => setMobileSidebarOpen(false)}
          />
        }
      >
        <GlobalCommandPalette />
        <main
          id="app-main-content"
          tabIndex={-1}
          className="flex-1 min-w-0 max-w-[1440px] rounded-sm p-4 outline-none focus-visible:ring-2 focus-visible:ring-emerald-500/30 sm:p-6 lg:p-8"
          role="main"
          aria-label="Conteúdo principal"
        >
          <Breadcrumbs />
          <AppShellFeedback>
            <ConnectionStatus />
            <PwaInstallBanner />
            <PwaUpdatePrompt />
            <SessionExpiryBanner />
            <IntegrationRetryBanner />
          </AppShellFeedback>
          <Outlet />
        </main>
      </AppShellFrame>
    </>
  )
}
