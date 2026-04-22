import { useEffect, useState } from 'react'
import {
  activateWaitingServiceWorker,
  getPwaUpdateState,
  subscribePwaUpdates,
} from '@/lib/pwa'

const DISMISS_KEY = 'agroadb:pwa-update-dismissed'

export function usePwaUpdatePrompt() {
  const [needRefresh, setNeedRefresh] = useState(getPwaUpdateState().needRefresh)
  const [dismissed, setDismissed] = useState(
    typeof window !== 'undefined' && window.sessionStorage.getItem(DISMISS_KEY) === '1'
  )

  useEffect(() => subscribePwaUpdates((state) => setNeedRefresh(state.needRefresh)), [])

  useEffect(() => {
    if (needRefresh) return
    window.sessionStorage.removeItem(DISMISS_KEY)
    setDismissed(false)
  }, [needRefresh])

  const visible = needRefresh && !dismissed

  return {
    visible,
    dismiss: () => {
      window.sessionStorage.setItem(DISMISS_KEY, '1')
      setDismissed(true)
    },
    update: async () => {
      window.sessionStorage.removeItem(DISMISS_KEY)
      setDismissed(false)
      await activateWaitingServiceWorker()
    },
  }
}
