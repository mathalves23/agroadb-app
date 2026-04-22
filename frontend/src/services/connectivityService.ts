export type BackendHealthCheckResult = {
  ok: boolean
  status: number | null
}

const DEFAULT_TIMEOUT_MS = 8_000

export async function checkBackendHealth(
  options?: { timeoutMs?: number }
): Promise<BackendHealthCheckResult> {
  const controller = new AbortController()
  const timeoutId = window.setTimeout(
    () => controller.abort(),
    options?.timeoutMs ?? DEFAULT_TIMEOUT_MS
  )

  try {
    const response = await fetch('/health', {
      method: 'GET',
      cache: 'no-store',
      signal: controller.signal,
    })

    return {
      ok: response.ok,
      status: response.status,
    }
  } catch {
    return {
      ok: false,
      status: null,
    }
  } finally {
    window.clearTimeout(timeoutId)
  }
}
