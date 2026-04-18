/** Eventos para feedback visual de retry/backoff no cliente HTTP (axios). */

export const AGROADB_API_RETRY_WAIT = 'agroadb-api-retry-wait'
export const AGROADB_API_RETRY_CLEAR = 'agroadb-api-retry-clear'

export type ApiRetryWaitDetail = {
  waitMs: number
  attempt: number
  maxAttempts: number
  method: string
  url: string
}

export function dispatchApiRetryWait(detail: ApiRetryWaitDetail) {
  if (typeof window === 'undefined') return
  window.dispatchEvent(new CustomEvent(AGROADB_API_RETRY_WAIT, { detail }))
}

export function dispatchApiRetryClear() {
  if (typeof window === 'undefined') return
  window.dispatchEvent(new CustomEvent(AGROADB_API_RETRY_CLEAR))
}
