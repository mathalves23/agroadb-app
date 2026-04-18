import { Link, useLocation } from 'react-router-dom'
import { ChevronRight, Home } from 'lucide-react'
import { getBreadcrumbs } from '@/lib/navigation'
import { cn } from '@/lib/utils'

export default function Breadcrumbs({ className }: { className?: string }) {
  const { pathname } = useLocation()
  const items = getBreadcrumbs(pathname)

  if (items.length <= 1) {
    return null
  }

  return (
    <nav aria-label="Trilha de navegação" className={cn('mb-5', className)}>
      <ol className="flex flex-wrap items-center gap-1 text-xs text-gray-500">
        {items.map((crumb, i) => {
          const isLast = i === items.length - 1
          return (
            <li key={`${crumb.to}-${i}`} className="flex items-center gap-1 min-w-0">
              {i > 0 && <ChevronRight className="h-3 w-3 shrink-0 text-gray-300" aria-hidden />}
              {isLast ? (
                <span
                  className="font-medium text-gray-800 truncate max-w-[min(100%,14rem)] sm:max-w-xs"
                  aria-current="page"
                >
                  {i === 0 ? (
                    <span className="inline-flex items-center gap-1">
                      <Home className="h-3.5 w-3.5 shrink-0 text-emerald-600" aria-hidden />
                      {crumb.label}
                    </span>
                  ) : (
                    crumb.label
                  )}
                </span>
              ) : (
                <Link
                  to={crumb.to}
                  className="hover:text-emerald-700 focus:outline-none focus:ring-2 focus:ring-emerald-500/40 rounded truncate max-w-[10rem] sm:max-w-[14rem]"
                >
                  {i === 0 ? (
                    <span className="inline-flex items-center gap-1">
                      <Home className="h-3.5 w-3.5 shrink-0" aria-hidden />
                      {crumb.label}
                    </span>
                  ) : (
                    crumb.label
                  )}
                </Link>
              )}
            </li>
          )
        })}
      </ol>
    </nav>
  )
}
