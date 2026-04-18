import { Link } from 'react-router-dom'
import { LogOut, User, Shield, Settings, ChevronDown, HelpCircle, Menu, X, BookOpen } from 'lucide-react'
import { useAuthStore } from '@/stores/authStore'
import { useState, useRef, useEffect } from 'react'
import NotificationDropdown from './NotificationDropdown'

type NavbarProps = {
  onToggleMobileSidebar?: () => void
  mobileSidebarOpen?: boolean
}

export default function Navbar({ onToggleMobileSidebar, mobileSidebarOpen }: NavbarProps) {
  const { user, logout } = useAuthStore()
  const [showUserMenu, setShowUserMenu] = useState(false)
  const menuRef = useRef<HTMLDivElement>(null)
  const menuPanelRef = useRef<HTMLDivElement>(null)

  const handleRestartTour = () => {
    localStorage.removeItem('tour_completed')
    setShowUserMenu(false)
    window.location.reload()
  }

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setShowUserMenu(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  useEffect(() => {
    if (!showUserMenu) return
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        setShowUserMenu(false)
      }
    }
    document.addEventListener('keydown', onKey)
    return () => document.removeEventListener('keydown', onKey)
  }, [showUserMenu])

  useEffect(() => {
    if (!showUserMenu || !menuPanelRef.current) return
    const t = window.requestAnimationFrame(() => {
      const el = menuPanelRef.current?.querySelector<HTMLElement>('a[href],button[type="button"]')
      el?.focus()
    })
    return () => window.cancelAnimationFrame(t)
  }, [showUserMenu])

  return (
    <nav className="bg-white/95 backdrop-blur-sm border-b border-gray-200/60 sticky top-0 z-50" role="banner" aria-label="Barra de navegação principal">
      <div className="mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-14">
          <div className="flex items-center gap-2 min-w-0">
            {onToggleMobileSidebar && (
              <button
                type="button"
                className="md:hidden shrink-0 rounded-lg p-2 text-gray-600 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-emerald-500/40"
                aria-label={mobileSidebarOpen ? 'Fechar menu de navegação' : 'Abrir menu de navegação'}
                aria-expanded={Boolean(mobileSidebarOpen)}
                aria-controls="app-sidebar"
                onClick={onToggleMobileSidebar}
              >
                {mobileSidebarOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
              </button>
            )}
            <Link to="/dashboard" className="flex items-center gap-2.5 min-w-0 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500/40">
              <div className="w-8 h-8 bg-gradient-to-br from-emerald-600 to-emerald-700 rounded-lg flex items-center justify-center shadow-sm shrink-0">
                <Shield className="h-4 w-4 text-white" />
              </div>
              <div className="flex items-baseline gap-1 min-w-0">
                <span className="text-lg font-bold text-gray-800 tracking-tight truncate">AgroADB</span>
                <span className="text-[10px] font-semibold text-emerald-600 uppercase tracking-wider shrink-0 hidden sm:inline">
                  Intel
                </span>
              </div>
            </Link>
          </div>

          <div className="flex items-center gap-3">
            <div data-tour="notifications">
              <NotificationDropdown />
            </div>

            <div className="relative" ref={menuRef} data-tour="user-menu">
              <button
                type="button"
                onClick={() => setShowUserMenu(!showUserMenu)}
                className="flex items-center gap-2.5 px-3 py-1.5 rounded-lg bg-gray-50/80 hover:bg-gray-100 transition focus:outline-none focus:ring-2 focus:ring-emerald-500/40"
                aria-label="Menu do usuário"
                aria-expanded={showUserMenu}
                aria-haspopup="menu"
                id="user-menu-button"
              >
                <div className="w-7 h-7 rounded-full bg-gradient-to-br from-emerald-500 to-emerald-700 flex items-center justify-center">
                  <span className="text-[10px] font-bold text-white">
                    {user?.full_name
                      ?.split(' ')
                      .map((n) => n[0])
                      .slice(0, 2)
                      .join('')
                      .toUpperCase() || 'U'}
                  </span>
                </div>
                <div className="hidden sm:block text-left">
                  <p className="text-xs font-medium text-gray-800 leading-tight">{user?.full_name || 'Usuário'}</p>
                  <p className="text-[10px] text-gray-400 leading-tight">{user?.organization || 'AgroADB'}</p>
                </div>
                <ChevronDown className={`h-3.5 w-3.5 text-gray-400 transition-transform ${showUserMenu ? 'rotate-180' : ''}`} />
              </button>

              {showUserMenu && (
                <div
                  ref={menuPanelRef}
                  id="user-menu-dropdown"
                  role="menu"
                  aria-labelledby="user-menu-button"
                  className="absolute right-0 mt-2 w-64 bg-white rounded-lg shadow-lg border border-gray-200 py-2 z-50"
                >
                  <div className="px-4 py-3 border-b border-gray-100" role="none">
                    <p className="text-sm font-semibold text-gray-900">{user?.full_name}</p>
                    <p className="text-xs text-gray-600 mt-0.5">{user?.email}</p>
                    {user?.organization && (
                      <p className="text-xs text-gray-500 mt-0.5">{user?.organization}</p>
                    )}
                  </div>

                  <div className="py-1" role="none">
                    <Link
                      to="/profile"
                      role="menuitem"
                      onClick={() => setShowUserMenu(false)}
                      className="flex items-center gap-3 px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-50 transition"
                    >
                      <User className="h-4 w-4 text-gray-400" />
                      Meu Perfil
                    </Link>

                    <Link
                      to="/settings"
                      role="menuitem"
                      onClick={() => setShowUserMenu(false)}
                      className="flex items-center gap-3 px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-50 transition"
                    >
                      <Settings className="h-4 w-4 text-gray-400" />
                      Configurações
                    </Link>

                    <Link
                      to="/guide"
                      role="menuitem"
                      onClick={() => setShowUserMenu(false)}
                      className="flex items-center gap-3 px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-50 transition"
                    >
                      <BookOpen className="h-4 w-4 text-gray-400" />
                      Manual do utilizador
                    </Link>

                    <button
                      type="button"
                      role="menuitem"
                      onClick={handleRestartTour}
                      className="flex items-center gap-3 w-full px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-50 transition text-left"
                    >
                      <HelpCircle className="h-4 w-4 text-gray-400" />
                      Tour Guiado
                    </button>
                  </div>

                  <div className="border-t border-gray-100 py-1 mt-1" role="none">
                    <button
                      type="button"
                      role="menuitem"
                      onClick={() => {
                        setShowUserMenu(false)
                        logout()
                      }}
                      className="flex items-center gap-3 w-full px-4 py-2.5 text-sm text-red-600 hover:bg-red-50 transition text-left"
                    >
                      <LogOut className="h-4 w-4" />
                      Sair da Conta
                    </button>
                  </div>
                </div>
              )}
            </div>

            <button
              type="button"
              onClick={logout}
              className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-gray-500 hover:text-red-600 hover:bg-red-50 rounded-lg transition sm:hidden"
              title="Sair"
              aria-label="Sair da conta"
            >
              <LogOut className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>
    </nav>
  )
}
