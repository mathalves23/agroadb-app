import axios, { type AxiosError, type InternalAxiosRequestConfig } from 'axios'
import { useAuthStore } from '@/stores/authStore'
import type { TokenResponse } from '@/types/api'
import { dispatchApiRetryClear, dispatchApiRetryWait } from '@/lib/integrationRetryEvents'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const API_BASE = `${API_URL}/api/v1`

export const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: false,
  timeout: 120_000,
})

type RetryableConfig = InternalAxiosRequestConfig & {
  _retry?: boolean
  _transportRetries?: number
}

let isRefreshing = false
type TokenCallback = (token: string | null) => void
let refreshQueue: TokenCallback[] = []

/** Contador para esconder o banner quando toda a cadeia de retries termina */
let transportRetryChains = 0

function drainQueue(token: string | null) {
  refreshQueue.forEach((cb) => cb(token))
  refreshQueue = []
}

async function fetchNewTokens(refreshToken: string): Promise<TokenResponse> {
  const { data } = await axios.post<TokenResponse>(
    `${API_BASE}/auth/refresh`,
    null,
    {
      params: { refresh_token: refreshToken },
      headers: { 'Content-Type': 'application/json' },
      timeout: 30_000,
    }
  )
  return data
}

function sleep(ms: number) {
  return new Promise((r) => setTimeout(r, ms))
}

function isAuthPath(url: string) {
  return (
    url.includes('/auth/login') ||
    url.includes('/auth/register') ||
    url.includes('/auth/refresh')
  )
}

function maxTransportAttempts(method: string, err: AxiosError): number {
  const m = method.toUpperCase()
  const safeRead = m === 'GET' || m === 'HEAD' || m === 'DELETE'

  if (!err.response) {
    return safeRead ? 4 : 2
  }
  const status = err.response.status
  if (status === 502 || status === 503 || status === 504) {
    return safeRead ? 4 : 3
  }
  if (status === 408 || status === 429) {
    return safeRead ? 4 : 0
  }
  return 0
}

function shouldRetryTransport(err: AxiosError, config: RetryableConfig): boolean {
  const url = config.url || ''
  if (!url || isAuthPath(url)) return false
  return maxTransportAttempts(config.method || 'get', err) > 0
}

function backoffMs(attemptIndex: number, retryAfterHeader?: string | null): number {
  if (retryAfterHeader) {
    const sec = parseInt(String(retryAfterHeader), 10)
    if (!Number.isNaN(sec) && sec > 0) return Math.min(sec * 1000, 60_000)
  }
  const base = Math.min(1000 * 2 ** attemptIndex, 16_000)
  const jitter = Math.random() * 400
  return base + jitter
}

function displayUrl(config: RetryableConfig): string {
  const raw = `${config.baseURL || ''}${config.url || ''}`
  return raw.replace(/^https?:\/\/[^/]+/i, '') || raw
}

api.interceptors.request.use(
  (config) => {
    const token = useAuthStore.getState().accessToken
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const status = error.response?.status
    const originalRequest = error.config as RetryableConfig | undefined

    if (!originalRequest) {
      return Promise.reject(error)
    }

    // --- Refresh JWT (401) ---
    if (status === 401) {
      const url = originalRequest.url || ''
      const isAuthEndpoint = isAuthPath(url)

      if (isAuthEndpoint) {
        return Promise.reject(error)
      }

      if (originalRequest._retry) {
        useAuthStore.getState().logout()
        if (window.location.pathname !== '/login') {
          window.location.href = '/login'
        }
        return Promise.reject(error)
      }

      const refreshToken = useAuthStore.getState().refreshToken
      if (!refreshToken) {
        useAuthStore.getState().logout()
        if (window.location.pathname !== '/login') {
          window.location.href = '/login'
        }
        return Promise.reject(error)
      }

      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          refreshQueue.push((token) => {
            if (!token || !originalRequest.headers) {
              reject(error)
              return
            }
            originalRequest.headers.Authorization = `Bearer ${token}`
            resolve(api(originalRequest))
          })
        })
      }

      originalRequest._retry = true
      isRefreshing = true

      try {
        const data = await fetchNewTokens(refreshToken)
        useAuthStore.getState().updateTokens({
          access_token: data.access_token,
          refresh_token: data.refresh_token,
        })
        drainQueue(data.access_token)
        originalRequest.headers = originalRequest.headers ?? {}
        originalRequest.headers.Authorization = `Bearer ${data.access_token}`
        return api(originalRequest)
      } catch {
        drainQueue(null)
        useAuthStore.getState().logout()
        if (window.location.pathname !== '/login') {
          window.location.href = '/login'
        }
        return Promise.reject(error)
      } finally {
        isRefreshing = false
      }
    }

    // --- Retry com backoff (502/503/504, rede, 429/408 em leituras) ---
    if (!shouldRetryTransport(error, originalRequest)) {
      return Promise.reject(error)
    }

    const method = (originalRequest.method || 'get').toUpperCase()
    const max = maxTransportAttempts(method, error)
    const count = originalRequest._transportRetries ?? 0
    if (count >= max) {
      return Promise.reject(error)
    }

    originalRequest._transportRetries = count + 1
    const retryAfter =
      error.response?.headers?.['retry-after'] ??
      error.response?.headers?.['Retry-After'] ??
      null
    const waitMs = Math.round(backoffMs(count, retryAfter))

    transportRetryChains += 1
    dispatchApiRetryWait({
      waitMs,
      attempt: originalRequest._transportRetries,
      maxAttempts: max,
      method,
      url: displayUrl(originalRequest),
    })

    try {
      await sleep(waitMs)
      return await api.request(originalRequest)
    } catch (e) {
      return Promise.reject(e)
    } finally {
      transportRetryChains -= 1
      if (transportRetryChains <= 0) {
        transportRetryChains = 0
        dispatchApiRetryClear()
      }
    }
  }
)
