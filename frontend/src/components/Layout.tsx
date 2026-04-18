import { useEffect, useState } from 'react'
import { Outlet, useLocation } from 'react-router-dom'
import Navbar from './Navbar'
import Sidebar from './Sidebar'
import IntegrationRetryBanner from './IntegrationRetryBanner'
import SkipToMainLink from './SkipToMainLink'
import Breadcrumbs from './Breadcrumbs'

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
    <div className="min-h-screen bg-[#f8f9fb]">
      <SkipToMainLink />
      <Navbar
        onToggleMobileSidebar={() => setMobileSidebarOpen((o) => !o)}
        mobileSidebarOpen={mobileSidebarOpen}
      />
      <div className="flex relative">
        {mobileSidebarOpen && (
          <button
            type="button"
            className="fixed inset-0 z-30 bg-gray-900/40 md:hidden"
            aria-label="Fechar menu lateral"
            onClick={() => setMobileSidebarOpen(false)}
          />
        )}
        <Sidebar
          mobileOpen={mobileSidebarOpen}
          onNavigate={() => setMobileSidebarOpen(false)}
        />
        <main
          id="app-main-content"
          tabIndex={-1}
          className="flex-1 min-w-0 p-4 sm:p-6 lg:p-8 max-w-[1440px] outline-none focus-visible:ring-2 focus-visible:ring-emerald-500/30 rounded-sm"
          role="main"
          aria-label="Conteúdo principal"
        >
          <Breadcrumbs />
          <IntegrationRetryBanner />
          <Outlet />
        </main>
      </div>
    </div>
  )
}
