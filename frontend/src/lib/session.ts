const WARNING_WINDOW_MS = 5 * 60 * 1000
const ACTIVITY_KEY = 'agroadb:session-last-activity'

type JwtPayload = {
  exp?: number
}

function decodeBase64Url(value: string) {
  const normalized = value.replace(/-/g, '+').replace(/_/g, '/')
  const padded = normalized + '='.repeat((4 - (normalized.length % 4)) % 4)
  return window.atob(padded)
}

export function decodeJwtPayload(token: string): JwtPayload | null {
  try {
    const [, payload] = token.split('.')
    if (!payload) return null
    return JSON.parse(decodeBase64Url(payload)) as JwtPayload
  } catch {
    return null
  }
}

export function getTokenExpiry(token: string | null) {
  if (!token) return null
  const payload = decodeJwtPayload(token)
  if (!payload?.exp) return null
  return payload.exp * 1000
}

export function updateSessionActivity() {
  if (typeof window === 'undefined') return
  window.localStorage.setItem(ACTIVITY_KEY, String(Date.now()))
}

export function getLastSessionActivity() {
  if (typeof window === 'undefined') return null
  const raw = Number(window.localStorage.getItem(ACTIVITY_KEY) || '')
  return Number.isFinite(raw) && raw > 0 ? raw : null
}

export function shouldWarnAboutSession(expiryAt: number | null, now = Date.now()) {
  if (!expiryAt) return false
  const timeLeft = expiryAt - now
  return timeLeft > 0 && timeLeft <= WARNING_WINDOW_MS
}

export function formatRemainingSessionTime(expiryAt: number | null, now = Date.now()) {
  if (!expiryAt) return ''
  const diff = Math.max(0, expiryAt - now)
  const totalMinutes = Math.ceil(diff / 60000)
  if (totalMinutes < 1) return 'menos de 1 minuto'
  if (totalMinutes === 1) return '1 minuto'
  return `${totalMinutes} minutos`
}
