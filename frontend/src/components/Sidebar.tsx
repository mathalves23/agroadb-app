import { NavLink, useLocation } from 'react-router-dom'
import {
  LayoutDashboard,
  Search,
  Plus,
  Database,
  Settings,
  ChevronRight,
} from 'lucide-react'
import { cn } from '@/lib/utils'

const mainNav = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Investigações', href: '/investigations', icon: Search },
]

const quickActions = [
  { name: 'Nova Investigação', href: '/investigations/new', icon: Plus },
]

export default function Sidebar() {
  const location = useLocation()

  return (
    <aside className="w-56 bg-white border-r border-gray-200/60 min-h-[calc(100vh-3.5rem)] flex flex-col" role="navigation" aria-label="Menu principal">
      {/* Main navigation */}
      <nav className="flex-1 px-3 py-5 space-y-1">
        <p className="px-3 mb-2 text-[10px] font-semibold uppercase tracking-wider text-gray-400">
          Menu
        </p>
        {mainNav.map((item) => {
          const isActive =
            location.pathname === item.href ||
            (item.href !== '/dashboard' && location.pathname.startsWith(item.href))
          return (
            <NavLink
              key={item.name}
              to={item.href}
              aria-current={isActive ? 'page' : undefined}
              data-tour={item.href === '/investigations' ? 'sidebar-investigations' : undefined}
              className={cn(
                'group flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all',
                isActive
                  ? 'bg-emerald-50 text-emerald-700 border border-emerald-100'
                  : 'text-gray-600 hover:bg-gray-50 hover:text-gray-800'
              )}
            >
              <item.icon
                className={cn(
                  'h-4.5 w-4.5 shrink-0',
                  isActive ? 'text-emerald-600' : 'text-gray-400 group-hover:text-gray-600'
                )}
              />
              <span className="flex-1">{item.name}</span>
              {isActive && <ChevronRight className="h-3.5 w-3.5 text-emerald-400" />}
            </NavLink>
          )
        })}

        <div className="pt-4">
          <p className="px-3 mb-2 text-[10px] font-semibold uppercase tracking-wider text-gray-400">
            Ações Rápidas
          </p>
          {quickActions.map((item) => (
            <NavLink
              key={item.name}
              to={item.href}
              className="group flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-gray-600 hover:bg-gray-50 hover:text-gray-800 transition-all"
            >
              <item.icon className="h-4.5 w-4.5 text-gray-400 group-hover:text-gray-600 shrink-0" />
              <span>{item.name}</span>
            </NavLink>
          ))}
        </div>

        <div className="pt-4">
          <p className="px-3 mb-2 text-[10px] font-semibold uppercase tracking-wider text-gray-400">
            Configuração
          </p>
          <NavLink
            to="/settings"
            data-tour="sidebar-settings"
            className={({ isActive }) =>
              cn(
                'group flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all',
                isActive
                  ? 'bg-emerald-50 text-emerald-700 border border-emerald-100'
                  : 'text-gray-600 hover:bg-gray-50 hover:text-gray-800'
              )
            }
          >
            {({ isActive }) => (
              <span className="flex items-center gap-3" aria-current={isActive ? 'page' : undefined}>
                <Settings className="h-4.5 w-4.5 text-gray-400 group-hover:text-gray-600 shrink-0" />
                <span>Integrações</span>
              </span>
            )}
          </NavLink>
        </div>
      </nav>

      {/* Footer */}
      <div className="px-3 py-4 border-t border-gray-200/60">
        <div className="flex items-center gap-3 px-3 py-2">
          <Database className="h-4 w-4 text-emerald-500" />
          <div>
            <p className="text-xs font-medium text-gray-700">27 bases integradas</p>
            <p className="text-[10px] text-gray-400 leading-relaxed">SNCR, SIGEF, DataJud, TJMG, BNMP, SEEU, Receita CPF/CNPJ, BrasilAPI, CGU, IBGE, TSE, CVM...</p>
          </div>
        </div>
      </div>
    </aside>
  )
}
