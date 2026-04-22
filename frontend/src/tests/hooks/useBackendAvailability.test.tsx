import { act, renderHook, waitFor } from '@testing-library/react'

import { useBackendAvailability } from '@/hooks/useBackendAvailability'
import { checkBackendHealth } from '@/services/connectivityService'

jest.mock('@/services/connectivityService', () => ({
  checkBackendHealth: jest.fn(),
}))

describe('useBackendAvailability', () => {
  beforeEach(() => {
    jest.useFakeTimers()
    Object.defineProperty(window.navigator, 'onLine', {
      configurable: true,
      value: true,
    })
    jest.mocked(checkBackendHealth).mockReset()
  })

  afterEach(() => {
    jest.runOnlyPendingTimers()
    jest.useRealTimers()
  })

  it('starts as ready when backend healthcheck succeeds', async () => {
    jest.mocked(checkBackendHealth).mockResolvedValue({ ok: true, status: 200 })

    const { result } = renderHook(() => useBackendAvailability())

    await waitFor(() => expect(result.current.status).toBe('ready'))
  })

  it('moves to unavailable when backend responds with non-retryable error', async () => {
    jest.mocked(checkBackendHealth).mockResolvedValue({ ok: false, status: 500 })

    const { result } = renderHook(() => useBackendAvailability())

    await waitFor(() => expect(result.current.status).toBe('unavailable'))
  })

  it('reports reconnected after recovering from offline', async () => {
    jest.mocked(checkBackendHealth).mockImplementation(async () => ({
      ok: true,
      status: 200,
    }))

    Object.defineProperty(window.navigator, 'onLine', {
      configurable: true,
      value: false,
    })

    const { result } = renderHook(() => useBackendAvailability())

    await waitFor(() => expect(result.current.status).toBe('offline'))

    Object.defineProperty(window.navigator, 'onLine', {
      configurable: true,
      value: true,
    })

    await act(async () => {
      window.dispatchEvent(new Event('online'))
    })

    await waitFor(() => expect(result.current.status).toBe('reconnected'))
  })

  it('rechecks when retry is called', async () => {
    jest
      .mocked(checkBackendHealth)
      .mockResolvedValueOnce({ ok: false, status: 503 })
      .mockResolvedValueOnce({ ok: true, status: 200 })

    const { result } = renderHook(() => useBackendAvailability())

    await waitFor(() => expect(result.current.status).toBe('waking'))

    await act(async () => {
      result.current.retry()
    })

    await waitFor(() => expect(result.current.status).toBe('reconnected'))
  })
})
