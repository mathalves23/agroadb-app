/**
 * Empty States — padrão visual alinhado ao restante da app (emerald, tipografia).
 */
import { type ReactNode } from 'react'
import { motion } from 'framer-motion'

interface EmptyStateProps {
  icon?: ReactNode
  title: string
  description?: string
  action?: {
    label: string
    onClick: () => void
  }
  illustration?: 'search' | 'folder' | 'data' | 'settings' | 'notification'
  /** `embedded`: listas e cartões; `full`: área ampla (omissão) */
  variant?: 'full' | 'embedded'
}

const illustrationClass = (embedded: boolean) =>
  embedded ? 'w-14 h-14 text-gray-400' : 'w-32 h-32 text-gray-400'

function DefaultIllustration({
  type,
  embedded,
}: {
  type: NonNullable<EmptyStateProps['illustration']>
  embedded: boolean
}) {
  const c = illustrationClass(embedded)
  const paths: Record<typeof type, ReactNode> = {
    search: (
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
    ),
    folder: (
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
    ),
    data: (
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
    ),
    settings: (
      <>
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
      </>
    ),
    notification: (
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
    ),
  }
  return (
    <svg className={c} fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden>
      {paths[type]}
    </svg>
  )
}

export function EmptyState({
  icon,
  title,
  description,
  action,
  illustration = 'folder',
  variant = 'full',
}: EmptyStateProps) {
  const embedded = variant === 'embedded'

  return (
    <motion.div
      initial={{ opacity: 0, y: embedded ? 8 : 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`flex flex-col items-center justify-center text-center ${
        embedded ? 'py-10 px-4' : 'py-12 px-4'
      }`}
      role="status"
    >
      <motion.div
        initial={{ scale: embedded ? 0.95 : 0 }}
        animate={{ scale: 1 }}
        transition={{ delay: embedded ? 0 : 0.1, type: embedded ? 'tween' : 'spring' }}
        className={embedded ? 'mb-3' : 'mb-6'}
      >
        {icon || <DefaultIllustration type={illustration} embedded={embedded} />}
      </motion.div>

      <h3
        className={`font-semibold text-gray-900 dark:text-white mb-1 ${
          embedded ? 'text-sm' : 'text-xl mb-2'
        }`}
      >
        {title}
      </h3>

      {description && (
        <p
          className={`text-gray-600 dark:text-gray-400 max-w-md ${
            embedded ? 'text-xs mb-4' : 'mb-6'
          }`}
        >
          {description}
        </p>
      )}

      {action && (
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          type="button"
          onClick={action.onClick}
          className={`px-6 py-3 bg-emerald-600 hover:bg-emerald-700 text-white font-medium rounded-lg transition-colors shadow-md shadow-emerald-600/15 ${
            embedded ? 'text-xs py-2 px-4' : ''
          }`}
        >
          {action.label}
        </motion.button>
      )}
    </motion.div>
  )
}

export function NoInvestigationsEmpty({ onCreate }: { onCreate: () => void }) {
  return (
    <EmptyState
      illustration="search"
      title="Nenhuma investigação ainda"
      description="Comece criando a sua primeira investigação para consolidar propriedades rurais, empresas e vínculos a partir de fontes públicas."
      action={{
        label: 'Criar primeira investigação',
        onClick: onCreate,
      }}
    />
  )
}

export function NoResultsEmpty({ onRetry }: { onRetry?: () => void }) {
  return (
    <EmptyState
      illustration="search"
      title="Nenhum resultado encontrado"
      description="Não foram encontrados dados para esta busca. Tente ajustar os filtros ou os critérios."
      action={
        onRetry
          ? {
              label: 'Tentar novamente',
              onClick: onRetry,
            }
          : undefined
      }
    />
  )
}

export function NoNotificationsEmpty(props?: { embedded?: boolean }) {
  const embedded = Boolean(props?.embedded)
  return (
    <EmptyState
      variant={embedded ? 'embedded' : 'full'}
      illustration="notification"
      title="Nenhuma notificação"
      description="Quando houver alertas sobre as suas investigações, aparecem aqui."
    />
  )
}

export function NoDataEmpty({ type = 'dados' }: { type?: string }) {
  return (
    <EmptyState
      illustration="data"
      title={`Nenhum ${type} disponível`}
      description={`Não há ${type} para mostrar neste momento.`}
    />
  )
}
