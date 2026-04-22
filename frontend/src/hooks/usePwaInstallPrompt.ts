import { useEffect, useState } from 'react'

type BeforeInstallPromptEvent = Event & {
  prompt: () => Promise<void>
  userChoice: Promise<{ outcome: 'accepted' | 'dismissed'; platform: string }>
}

const STORAGE_KEY = 'agroadb-pwa-dismissed-at'
const DISMISS_TTL_MS = 1000 * 60 * 60 * 24 * 7

function isStandaloneDisplayMode() {
  if (typeof window === 'undefined') return false
  return (
    window.matchMedia('(display-mode: standalone)').matches ||
    (window.navigator as Navigator & { standalone?: boolean }).standalone === true
  )
}

export function usePwaInstallPrompt() {
  const [deferredPrompt, setDeferredPrompt] = useState<BeforeInstallPromptEvent | null>(null)
  const [isInstalled, setIsInstalled] = useState(isStandaloneDisplayMode)
  const [dismissedAt, setDismissedAt] = useState<number | null>(null)

  useEffect(() => {
    const dismissed = Number(localStorage.getItem(STORAGE_KEY) || '')
    if (Number.isFinite(dismissed) && dismissed > 0) {
      setDismissedAt(dismissed)
    }

    const handleBeforeInstallPrompt = (event: Event) => {
      event.preventDefault()
      setDeferredPrompt(event as BeforeInstallPromptEvent)
    }

    const handleInstalled = () => {
      setIsInstalled(true)
      setDeferredPrompt(null)
    }

    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt)
    window.addEventListener('appinstalled', handleInstalled)

    return () => {
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt)
      window.removeEventListener('appinstalled', handleInstalled)
    }
  }, [])

  const canShowPrompt =
    !isInstalled &&
    Boolean(deferredPrompt) &&
    (!dismissedAt || Date.now() - dismissedAt > DISMISS_TTL_MS)

  async function install() {
    if (!deferredPrompt) return false
    await deferredPrompt.prompt()
    const choice = await deferredPrompt.userChoice
    setDeferredPrompt(null)
    return choice.outcome === 'accepted'
  }

  function dismiss() {
    const now = Date.now()
    localStorage.setItem(STORAGE_KEY, String(now))
    setDismissedAt(now)
  }

  return {
    canShowPrompt,
    isInstalled,
    install,
    dismiss,
  }
}
