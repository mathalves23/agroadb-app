import { useCallback, useEffect, useRef, useState } from 'react'
import { checkBackendHealth } from '@/services/connectivityService'

export type BackendAvailabilityStatus =
  | 'offline'
  | 'checking'
  | 'ready'
  | 'reconnected'
  | 'waking'
  | 'unavailable'

type State = {
  status: BackendAvailabilityStatus
  checkedAt: number | null
}

const HEALTHCHECK_INTERVAL_MS = 60_000
function getInitialState(): State {
  if (typeof navigator !== 'undefined' && !navigator.onLine) {
    return { status: 'offline', checkedAt: null }
  }
  return { status: 'checking', checkedAt: null }
}

export function useBackendAvailability() {
  const [state, setState] = useState<State>(getInitialState)
  const previousStatus = useRef<BackendAvailabilityStatus>(state.status)

  const runCheck = useCallback(async () => {
    if (!navigator.onLine) {
      setState({ status: 'offline', checkedAt: Date.now() })
      return
    }

    setState((current) => ({
      status:
        current.status === 'ready' || current.status === 'reconnected' ? 'checking' : 'waking',
      checkedAt: current.checkedAt,
    }))

    try {
      const response = await checkBackendHealth()

      const nextStatus =
        response.ok &&
        previousStatus.current !== 'ready' &&
        previousStatus.current !== 'reconnected' &&
        previousStatus.current !== 'checking'
          ? 'reconnected'
          : response.ok
          ? 'ready'
          : response.status === 502 || response.status === 503 || response.status === 504
          ? 'waking'
          : 'unavailable'

      previousStatus.current = nextStatus
      setState({ status: nextStatus, checkedAt: Date.now() })
    } catch {
      const nextStatus = navigator.onLine ? 'waking' : 'offline'
      previousStatus.current = nextStatus
      setState({ status: nextStatus, checkedAt: Date.now() })
    }
  }, [])

  useEffect(() => {
    void runCheck()
    const intervalId = window.setInterval(() => {
      void runCheck()
    }, HEALTHCHECK_INTERVAL_MS)

    const handleOnline = () => void runCheck()
    const handleOffline = () => {
      previousStatus.current = 'offline'
      setState({ status: 'offline', checkedAt: Date.now() })
    }
    const handleVisibility = () => {
      if (document.visibilityState === 'visible') {
        void runCheck()
      }
    }

    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)
    document.addEventListener('visibilitychange', handleVisibility)

    return () => {
      window.clearInterval(intervalId)
      window.removeEventListener('online', handleOnline)
      window.removeEventListener('offline', handleOffline)
      document.removeEventListener('visibilitychange', handleVisibility)
    }
  }, [runCheck])

  return {
    ...state,
    retry: () => void runCheck(),
  }
}
