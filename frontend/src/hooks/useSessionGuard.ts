import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { authService } from '@/services/authService'
import { useAuthStore } from '@/stores/authStore'
import {
  formatRemainingSessionTime,
  getTokenExpiry,
  shouldWarnAboutSession,
  updateSessionActivity,
} from '@/lib/session'

const CHECK_INTERVAL_MS = 30_000
const DISMISS_SNOOZE_MS = 60_000

export function useSessionGuard() {
  const navigate = useNavigate()
  const accessToken = useAuthStore((state) => state.accessToken)
  const refreshToken = useAuthStore((state) => state.refreshToken)
  const updateTokens = useAuthStore((state) => state.updateTokens)
  const logout = useAuthStore((state) => state.logout)
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated)
  const [warningVisible, setWarningVisible] = useState(false)
  const [renewing, setRenewing] = useState(false)
  const [now, setNow] = useState(Date.now())
  const [dismissedUntil, setDismissedUntil] = useState<number | null>(null)

  const expiryAt = useMemo(() => getTokenExpiry(accessToken), [accessToken])
  const remainingText = useMemo(() => formatRemainingSessionTime(expiryAt, now), [expiryAt, now])

  useEffect(() => {
    setDismissedUntil(null)
  }, [accessToken, refreshToken])

  useEffect(() => {
    if (!isAuthenticated) return

    const events = ['mousedown', 'keydown', 'touchstart', 'scroll', 'click'] as const
    const handleActivity = () => updateSessionActivity()
    handleActivity()
    for (const eventName of events) {
      window.addEventListener(eventName, handleActivity, { passive: true })
    }

    return () => {
      for (const eventName of events) {
        window.removeEventListener(eventName, handleActivity)
      }
    }
  }, [isAuthenticated])

  useEffect(() => {
    if (!isAuthenticated) {
      setWarningVisible(false)
      return
    }

    const checkSession = () => {
      const currentNow = Date.now()
      setNow(currentNow)
      if (!expiryAt) return
      if (expiryAt <= currentNow) {
        logout()
        navigate('/login', { replace: true })
        return
      }
      const shouldWarn = shouldWarnAboutSession(expiryAt, currentNow)
      const dismissedStillActive = dismissedUntil !== null && dismissedUntil > currentNow
      setWarningVisible(shouldWarn && !dismissedStillActive)
    }

    checkSession()
    const intervalId = window.setInterval(checkSession, CHECK_INTERVAL_MS)
    return () => window.clearInterval(intervalId)
  }, [dismissedUntil, expiryAt, isAuthenticated, logout, navigate])

  return {
    warningVisible,
    remainingText,
    renewing,
    renewSession: async () => {
      if (!refreshToken) return
      setRenewing(true)
      try {
        const tokens = await authService.refreshToken(refreshToken)
        updateTokens({
          access_token: tokens.access_token,
          refresh_token: tokens.refresh_token,
        })
        setWarningVisible(false)
        setDismissedUntil(null)
        updateSessionActivity()
      } finally {
        setRenewing(false)
      }
    },
    dismissWarning: () => {
      setWarningVisible(false)
      setDismissedUntil(Date.now() + DISMISS_SNOOZE_MS)
    },
  }
}
