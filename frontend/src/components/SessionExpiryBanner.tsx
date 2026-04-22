import { Clock3, RefreshCcw, X } from 'lucide-react'
import { NoticeBanner } from '@/components/feedback'
import { useSessionGuard } from '@/hooks/useSessionGuard'

export default function SessionExpiryBanner() {
  const { warningVisible, remainingText, renewing, renewSession, dismissWarning } =
    useSessionGuard()

  if (!warningVisible) return null

  return (
    <NoticeBanner
      title={`Sua sessão expira em ${remainingText}.`}
      description="Renove agora para evitar perda de trabalho em investigações longas."
      icon={Clock3}
      tone="info"
      className="border-violet-200 bg-violet-50 text-violet-900"
      actions={
        <>
          <button
            type="button"
            onClick={dismissWarning}
            className="inline-flex items-center gap-2 rounded-lg border border-current/15 bg-white px-3 py-1.5 text-xs font-medium"
          >
            <X className="h-3.5 w-3.5" />
            Fechar
          </button>
          <button
            type="button"
            disabled={renewing}
            onClick={() => {
              void renewSession()
            }}
            className="inline-flex items-center gap-2 rounded-lg bg-violet-700 px-3 py-1.5 text-xs font-semibold text-white transition hover:bg-violet-800 disabled:cursor-not-allowed disabled:opacity-70"
          >
            <RefreshCcw className={`h-3.5 w-3.5 ${renewing ? 'animate-spin' : ''}`} />
            {renewing ? 'Renovando...' : 'Renovar sessão'}
          </button>
        </>
      }
    />
  )
}
