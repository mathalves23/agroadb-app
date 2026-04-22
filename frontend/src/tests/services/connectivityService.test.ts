import { checkBackendHealth } from '@/services/connectivityService'

describe('connectivityService', () => {
  beforeEach(() => {
    jest.useFakeTimers()
  })

  afterEach(() => {
    jest.restoreAllMocks()
    jest.runOnlyPendingTimers()
    jest.useRealTimers()
  })

  it('returns response status when healthcheck succeeds', async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      status: 200,
    }) as jest.Mock

    await expect(checkBackendHealth()).resolves.toEqual({ ok: true, status: 200 })
  })

  it('returns null status when request fails', async () => {
    global.fetch = jest.fn().mockRejectedValue(new Error('network down')) as jest.Mock

    await expect(checkBackendHealth()).resolves.toEqual({ ok: false, status: null })
  })

  it('aborts request after timeout', async () => {
    global.fetch = jest.fn(
      (_input, init) =>
        new Promise((_resolve, reject) => {
          init?.signal?.addEventListener('abort', () => reject(new Error('aborted')))
        })
    ) as jest.Mock

    const promise = checkBackendHealth({ timeoutMs: 100 })
    jest.advanceTimersByTime(100)

    await expect(promise).resolves.toEqual({ ok: false, status: null })
  })
})
