import { useEffect, useState } from 'react'
import {
  flushOfflineQueue,
  getOfflineQueueState,
  initializeOfflineQueueSync,
  subscribeOfflineQueueState,
} from '@/lib/offlineQueue'

export function useOfflineQueue() {
  const [queueState, setQueueState] = useState(getOfflineQueueState)

  useEffect(() => {
    initializeOfflineQueueSync()
    return subscribeOfflineQueueState(setQueueState)
  }, [])

  return {
    ...queueState,
    retrySync: () => void flushOfflineQueue(),
  }
}
