import { NavLink, useLocation } from 'react-router-dom'
import {
  LayoutDashboard,
  Search,
  Plus,
  Database,
  Settings,
  ChevronRight,
  Bell,
  UserCircle,
} from 'lucide-react'
import { cn } from '@/lib/utils'

const mainNav = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Investigações', href: '/investigations', icon: Search },
]

const quickActions = [{ name: 'Nova Investigação', href: '/investigations/new', icon: Plus }]

const accountNav = [
  { name: 'Notificações', href: '/notifications', icon: Bell },
  { name: 'Perfil', href: '/profile', icon: UserCircle },
]

type SidebarProps = {
  mobileOpen?: boolean
  onNavigate?: () => void
}

export default function Sidebar({ mobileOpen = false, onNavigate }: SidebarProps) {
  const location = useLocation()
  const settingsActive = location.pathname === '/settings'

  const linkClass = (isActive: boolean) =>
    cn(
      'group flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all',
      isActive
        ? 'bg-emerald-50 text-emerald-700 border border-emerald-100'
        : 'text-gray-600 hover:bg-gray-50 hover:text-gray-800'
    )

  return (
    <aside
      id="app-sidebar"
      className={cn(
        'w-56 shrink-0 bg-white border-r border-gray-200/60 flex flex-col z-40 transition-transform duration-200 ease-out',
        'max-md:fixed max-md:left-0 max-md:top-14 max-md:h-[calc(100vh-3.5rem)] max-md:shadow-xl',
        mobileOpen ? 'max-md:translate-x-0' : 'max-md:-translate-x-full',
        'md:relative md:top-auto md:translate-x-0 md:shadow-none md:min-h-[calc(100vh-3.5rem)]'
      )}
      aria-label="Navegação lateral"
    >
      <nav className="flex-1 px-3 py-5 space-y-1 overflow-y-auto" aria-label="Secções da aplicação">
        <p className="px-3 mb-2 text-[10px] font-semibold uppercase tracking-wider text-gray-400">Menu</p>
        {mainNav.map((item) => {
          const isActive =
            location.pathname === item.href ||
            (item.href !== '/dashboard' && location.pathname.startsWith(item.href))
          return (
            <NavLink
              key={item.name}
              to={item.href}
              onClick={() => onNavigate?.()}
              aria-current={isActive ? 'page' : undefined}
              data-tour={item.href === '/investigations' ? 'sidebar-investigations' : undefined}
              className={linkClass(isActive)}
            >
              <item.icon
                className={cn(
                  'h-4 w-4 shrink-0',
                  isActive ? 'text-emerald-600' : 'text-gray-400 group-hover:text-gray-600'
                )}
              />
              <span className="flex-1">{item.name}</span>
              {isActive && <ChevronRight className="h-3.5 w-3.5 text-emerald-400" aria-hidden />}
            </NavLink>
          )
        })}

        <div className="pt-4">
          <p className="px-3 mb-2 text-[10px] font-semibold uppercase tracking-wider text-gray-400">Ações rápidas</p>
          {quickActions.map((item) => (
            <NavLink
              key={item.name}
              to={item.href}
              onClick={() => onNavigate?.()}
              className="group flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-gray-600 hover:bg-gray-50 hover:text-gray-800 transition-all"
            >
              <item.icon className="h-4 w-4 text-gray-400 group-hover:text-gray-600 shrink-0" />
              <span>{item.name}</span>
            </NavLink>
          ))}
        </div>

        <div className="pt-4">
          <p className="px-3 mb-2 text-[10px] font-semibold uppercase tracking-wider text-gray-400">Conta</p>
          {accountNav.map((item) => {
            const isActive = location.pathname === item.href
            return (
              <NavLink
                key={item.name}
                to={item.href}
                onClick={() => onNavigate?.()}
                aria-current={isActive ? 'page' : undefined}
                className={linkClass(isActive)}
              >
                <item.icon
                  className={cn(
                    'h-4 w-4 shrink-0',
                    isActive ? 'text-emerald-600' : 'text-gray-400 group-hover:text-gray-600'
                  )}
                />
                <span className="flex-1">{item.name}</span>
                {isActive && <ChevronRight className="h-3.5 w-3.5 text-emerald-400" aria-hidden />}
              </NavLink>
            )
          })}
        </div>

        <div className="pt-4">
          <p className="px-3 mb-2 text-[10px] font-semibold uppercase tracking-wider text-gray-400">Configuração</p>
          <NavLink
            to="/settings"
            data-tour="sidebar-settings"
            onClick={() => onNavigate?.()}
            aria-current={settingsActive ? 'page' : undefined}
            className={linkClass(settingsActive)}
          >
            <Settings
              className={cn(
                'h-4 w-4 shrink-0',
                settingsActive ? 'text-emerald-600' : 'text-gray-400 group-hover:text-gray-600'
              )}
            />
            <span className="flex-1">Integrações</span>
            {settingsActive && <ChevronRight className="h-3.5 w-3.5 text-emerald-400" aria-hidden />}
          </NavLink>
        </div>
      </nav>

      <div className="px-3 py-4 border-t border-gray-200/60 mt-auto">
        <div className="flex items-center gap-3 px-3 py-2">
          <Database className="h-4 w-4 text-emerald-500 shrink-0" aria-hidden />
          <div>
            <p className="text-xs font-medium text-gray-700">Fontes públicas</p>
            <p className="text-[10px] text-gray-400 leading-relaxed">
              A disponibilidade depende da sua configuração e dos limites de cada órgão.
            </p>
          </div>
        </div>
      </div>
    </aside>
  )
}
