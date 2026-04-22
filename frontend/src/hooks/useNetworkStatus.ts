import { useEffect, useState } from 'react'

export function useNetworkStatus() {
  const [isOnline, setIsOnline] = useState(
    typeof navigator === 'undefined' ? true : navigator.onLine
  )
  const [lastChangedAt, setLastChangedAt] = useState<number | null>(null)

  useEffect(() => {
    const updateStatus = (online: boolean) => {
      setIsOnline(online)
      setLastChangedAt(Date.now())
    }

    const handleOnline = () => updateStatus(true)
    const handleOffline = () => updateStatus(false)

    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)

    return () => {
      window.removeEventListener('online', handleOnline)
      window.removeEventListener('offline', handleOffline)
    }
  }, [])

  return { isOnline, lastChangedAt }
}
