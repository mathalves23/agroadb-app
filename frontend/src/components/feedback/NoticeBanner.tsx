import type { LucideIcon } from 'lucide-react'
import type { ReactNode } from 'react'

type NoticeTone = 'info' | 'success' | 'warning' | 'danger' | 'brand'

interface NoticeBannerProps {
  title: string
  description?: ReactNode
  badge?: string
  icon?: LucideIcon
  tone?: NoticeTone
  actions?: ReactNode
  className?: string
  iconClassName?: string
  fullBleed?: boolean
  role?: 'status' | 'alert'
}

const toneClasses: Record<NoticeTone, string> = {
  info: 'border-sky-200 bg-sky-50 text-sky-900',
  success: 'border-emerald-200 bg-emerald-50 text-emerald-900',
  warning: 'border-amber-200 bg-amber-50 text-amber-950',
  danger: 'border-rose-200 bg-rose-50 text-rose-900',
  brand:
    'border-sky-200 bg-gradient-to-r from-sky-600 via-cyan-600 to-teal-500 text-white shadow-lg',
}

export function NoticeBanner({
  title,
  description,
  badge,
  icon: Icon,
  tone = 'info',
  actions,
  className = '',
  iconClassName = '',
  fullBleed = false,
  role = 'status',
}: NoticeBannerProps) {
  const baseClassName = fullBleed
    ? 'mb-4 overflow-hidden rounded-2xl border shadow-sm'
    : 'mb-4 rounded-2xl border px-4 py-3 shadow-sm'

  return (
    <aside
      className={`${baseClassName} ${toneClasses[tone]} ${className}`.trim()}
      role={role}
      aria-live="polite"
      aria-atomic="true"
    >
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-start gap-3">
          {Icon && (
            <div
              className={`rounded-xl bg-white/15 p-2 ${tone !== 'brand' ? 'bg-white/60' : ''} ${iconClassName}`.trim()}
            >
              <Icon className="h-4 w-4" />
            </div>
          )}
          <div>
            <div className="flex flex-wrap items-center gap-2">
              <p className="font-semibold">{title}</p>
              {badge && <span className="text-xs font-medium opacity-80">{badge}</span>}
            </div>
            {description && <div className="mt-0.5 text-xs opacity-90">{description}</div>}
          </div>
        </div>
        {actions && <div className="flex items-center gap-2">{actions}</div>}
      </div>
    </aside>
  )
}
