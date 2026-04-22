import { Wifi, WifiOff } from 'lucide-react'
import { useEffect, useState } from 'react'
import { useNetworkStatus } from '@/hooks/useNetworkStatus'

export default function ConnectionStatus() {
  const { isOnline, lastChangedAt } = useNetworkStatus()
  const [visible, setVisible] = useState(!isOnline)

  useEffect(() => {
    if (!lastChangedAt) return
    setVisible(true)

    if (!isOnline) return

    const timer = window.setTimeout(() => {
      setVisible(false)
    }, 3500)

    return () => window.clearTimeout(timer)
  }, [isOnline, lastChangedAt])

  if (!visible) return null

  return (
    <div
      className={`mb-4 flex items-center justify-between gap-3 rounded-xl border px-4 py-3 text-sm shadow-sm transition ${
        isOnline
          ? 'border-emerald-200 bg-emerald-50 text-emerald-800'
          : 'border-amber-200 bg-amber-50 text-amber-900'
      }`}
      role="status"
      aria-live="polite"
    >
      <div className="flex items-center gap-2">
        {isOnline ? <Wifi className="h-4 w-4" /> : <WifiOff className="h-4 w-4" />}
        <span className="font-medium">
          {isOnline
            ? 'Conexao restabelecida. Os dados podem ser sincronizados novamente.'
            : 'Voce esta offline. Algumas informacoes podem ficar indisponiveis.'}
        </span>
      </div>
      <span className="text-xs opacity-80">{isOnline ? 'Online' : 'Offline'}</span>
    </div>
  )
}
