import { AlertTriangle, CheckCircle2, CloudOff, RefreshCw, ServerCrash, Wifi, WifiOff } from 'lucide-react'
import { useEffect, useState } from 'react'
import { NoticeBanner } from '@/components/feedback'
import { useBackendAvailability } from '@/hooks/useBackendAvailability'
import { useNetworkStatus } from '@/hooks/useNetworkStatus'
import { useOfflineQueue } from '@/hooks/useOfflineQueue'
import { getOfflineActionLabel, type OfflineActionType } from '@/lib/offlineQueue'

function buildPendingSummary(pendingByAction: Partial<Record<OfflineActionType, number>>) {
  const labels = Object.entries(pendingByAction)
    .filter(([, count]) => Boolean(count))
    .map(([action, count]) => `${count} de ${getOfflineActionLabel(action as OfflineActionType)}`)

  if (labels.length === 0) return null
  return labels.slice(0, 2).join(' e ')
}

export default function ConnectionStatus() {
  const { isOnline, lastChangedAt } = useNetworkStatus()
  const { status, retry } = useBackendAvailability()
  const {
    pendingCount,
    pendingByAction,
    isFlushing,
    lastFlushResult,
    lastErrorMessage,
    flushedCount,
    retrySync,
  } = useOfflineQueue()
  const [visible, setVisible] = useState(!isOnline)
  const pendingSummary = buildPendingSummary(pendingByAction)
  const queueNeedsAttention =
    isOnline && pendingCount > 0 && !isFlushing && (lastFlushResult === 'partial' || lastFlushResult === 'failed')

  useEffect(() => {
    if (!lastChangedAt) return
    setVisible(true)

    if (!isOnline || status === 'waking' || status === 'unavailable' || queueNeedsAttention) return

    const timer = window.setTimeout(() => {
      setVisible(false)
    }, status === 'reconnected' || pendingCount > 0 || flushedCount > 0 ? 5000 : 3500)

    return () => window.clearTimeout(timer)
  }, [flushedCount, isOnline, lastChangedAt, pendingCount, queueNeedsAttention, status])

  const persistentIssue = !isOnline || status === 'waking' || status === 'unavailable' || queueNeedsAttention
  const showReconnect =
    status === 'reconnected' ||
    (isOnline && pendingCount > 0) ||
    (isOnline && lastFlushResult === 'success' && flushedCount > 0)

  if (!visible && !persistentIssue && !showReconnect) return null

  const config =
    !isOnline
      ? {
          title: 'Você está offline.',
          detail:
            pendingCount > 0
              ? `${pendingCount} ação(ões) aguardam reconexão para sincronizar${pendingSummary ? `: ${pendingSummary}.` : '.'}`
              : 'Algumas informações podem ficar indisponíveis até a internet voltar.',
          icon: WifiOff,
          badge: 'Offline',
        }
      : status === 'waking'
      ? {
          title: 'Conectado, mas o backend ainda não respondeu.',
          detail:
            pendingCount > 0
              ? `O AgroADB está tentando recuperar a API e retomar ${pendingCount} sincronização(ões) pendentes.`
              : 'O AgroADB está tentando recuperar a API e retomar as sincronizações.',
          icon: RefreshCw,
          badge: 'Waking up',
        }
      : status === 'unavailable'
      ? {
          title: 'Backend indisponível no momento.',
          detail:
            pendingCount > 0
              ? `A interface continua disponível, mas ${pendingCount} ação(ões) seguem pendentes até a recuperação do serviço.`
              : 'A interface continua disponível, mas chamadas críticas à API podem falhar até a recuperação do serviço.',
          icon: ServerCrash,
          badge: 'Indisponível',
        }
      : queueNeedsAttention
      ? {
          title: 'Ainda existem ações pendentes de sincronização.',
          detail:
            lastErrorMessage ??
            (pendingSummary
              ? `Pendências atuais: ${pendingSummary}.`
              : 'Algumas mudanças locais ainda aguardam novo envio.'),
          icon: CloudOff,
          badge: 'Pendências',
        }
      : {
          title:
            isFlushing && pendingCount > 0
              ? 'Conexão restabelecida.'
              : lastFlushResult === 'success' && flushedCount > 0
              ? 'Sincronização concluída.'
              : status === 'reconnected'
              ? 'Backend restabelecido.'
              : 'Conexão ativa.',
          detail:
            isFlushing && pendingCount > 0
              ? `Sincronizando ${pendingCount} ação(ões) pendentes agora.`
              : lastFlushResult === 'success' && flushedCount > 0
              ? `${flushedCount} ação(ões) local(is) foram sincronizadas com sucesso.`
              : 'Os dados podem ser sincronizados novamente.',
          icon: isFlushing && pendingCount > 0 ? CloudOff : lastFlushResult === 'success' && flushedCount > 0 ? CheckCircle2 : Wifi,
          badge:
            isFlushing && pendingCount > 0
              ? 'Sincronizando'
              : lastFlushResult === 'success' && flushedCount > 0
              ? 'Sincronizado'
              : 'Online',
        }

  const Icon = config.icon

  return (
    <NoticeBanner
      title={config.title}
      description={config.detail}
      badge={config.badge}
      icon={Icon}
      tone={
        !isOnline
          ? 'warning'
          : status === 'waking'
          ? 'info'
          : status === 'unavailable'
          ? 'danger'
          : queueNeedsAttention
          ? 'warning'
          : 'success'
      }
      iconClassName={status === 'waking' || isFlushing ? '[&>svg]:animate-spin' : ''}
      actions={
        <>
          {(status === 'waking' || status === 'unavailable') && (
            <button
              type="button"
              onClick={retry}
              className="inline-flex items-center gap-1 rounded-lg border border-current/15 bg-white/60 px-3 py-1.5 text-xs font-medium"
            >
              <AlertTriangle className="h-3.5 w-3.5" />
              Tentar de novo
            </button>
          )}
          {isOnline && pendingCount > 0 && !isFlushing && (
            <button
              type="button"
              onClick={retrySync}
              className="inline-flex items-center gap-1 rounded-lg border border-current/15 bg-white/60 px-3 py-1.5 text-xs font-medium"
            >
              <RefreshCw className="h-3.5 w-3.5" />
              Sincronizar agora
            </button>
          )}
        </>
      }
    />
  )
}
