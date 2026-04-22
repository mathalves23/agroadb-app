import { useEffect, useState } from 'react'
import { RefreshCw } from 'lucide-react'
import { NoticeBanner } from '@/components/feedback'
import {
  AGROADB_API_RETRY_CLEAR,
  AGROADB_API_RETRY_WAIT,
  type ApiRetryWaitDetail,
} from '@/lib/integrationRetryEvents'

type Payload = ApiRetryWaitDetail & { startedAt: number }

export default function IntegrationRetryBanner() {
  const [payload, setPayload] = useState<Payload | null>(null)
  const [tick, setTick] = useState(0)

  useEffect(() => {
    const onWait = (e: Event) => {
      const ce = e as CustomEvent<ApiRetryWaitDetail>
      setPayload({ ...ce.detail, startedAt: Date.now() })
    }
    const onClear = () => setPayload(null)
    window.addEventListener(AGROADB_API_RETRY_WAIT, onWait as EventListener)
    window.addEventListener(AGROADB_API_RETRY_CLEAR, onClear)
    return () => {
      window.removeEventListener(AGROADB_API_RETRY_WAIT, onWait as EventListener)
      window.removeEventListener(AGROADB_API_RETRY_CLEAR, onClear)
    }
  }, [])

  useEffect(() => {
    if (!payload) return
    const id = window.setInterval(() => setTick((t) => t + 1), 200)
    return () => window.clearInterval(id)
  }, [payload])

  if (!payload) return null

  void tick
  const elapsed = Date.now() - payload.startedAt
  const remainingMs = Math.max(0, payload.waitMs - elapsed)
  const remainingSec = Math.ceil(remainingMs / 1000)
  const isWaiting = remainingMs > 0

  return (
    <NoticeBanner
      title="Servidor ou integração instável"
      tone="warning"
      icon={RefreshCw}
      iconClassName={!isWaiting ? '[&>svg]:animate-spin' : ''}
      description={
        isWaiting ? (
          <>
            Nova tentativa em{' '}
            <strong className="tabular-nums">{remainingSec}s</strong> (tentativa{' '}
            {payload.attempt}/{payload.maxAttempts}).
          </>
        ) : (
          <>
            Tentando de novo <span className="font-mono text-xs opacity-80">{payload.method}</span>{' '}
            <span className="truncate max-w-[200px] sm:max-w-xs align-bottom inline-block">
              {payload.url}
            </span>
            …
          </>
        )
      }
    />
  )
}
